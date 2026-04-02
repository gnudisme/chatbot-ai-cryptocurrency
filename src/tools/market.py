import requests
import pandas as pd
import ta
import threading
import time as _time
from langchain_core.tools import tool
from src.config import Config


class _TTLCache:
    """Thread-safe in-memory cache with per-entry TTL."""

    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            entry = self._store.get(key)
            if entry and _time.monotonic() < entry["exp"]:
                return entry["val"], True
            return None, False

    def set(self, key, value, ttl: int):
        with self._lock:
            self._store[key] = {"val": value, "exp": _time.monotonic() + ttl}

    def evict_expired(self):
        now = _time.monotonic()
        with self._lock:
            self._store = {k: v for k, v in self._store.items() if v["exp"] > now}


# TTL constants (seconds)
_TTL_TICKER = 30       # 30 s  – price changes every few seconds, 30 s acceptable
_TTL_OHLCV_PRICE = 60  # 1 min – "giá" intent, only needs latest candle
_TTL_OHLCV_FULL = 180  # 3 min – analysis/prediction candles, rarely changes
_TTL_TICKERS_ALL = 60  # 1 min – full ticker list (top10, all_coins, search)

_cache = _TTLCache()


def _requests_get_with_retry(url, params=None, headers=None, timeout=10, retries=2):
    """requests.get with linear retry on network/timeout errors."""
    last_exc = None
    for attempt in range(retries):
        try:
            return requests.get(url, params=params, headers=headers, timeout=timeout)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            if attempt < retries - 1:
                _time.sleep(1.5 * (attempt + 1))  # 1.5 s, then 3 s
    raise last_exc


class MarketTools:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.headers = {}
        if Config.BINANCE_API_KEY:
            self.headers["X-MBX-APIKEY"] = Config.BINANCE_API_KEY

    def _fetch_ticker(self, symbol: str):
        try:
            symbol = symbol.upper()
            if '/' in symbol:
                symbol = symbol.replace('/', '')
            elif not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"

            cache_key = f"ticker:{symbol}"
            cached, hit = _cache.get(cache_key)
            if hit:
                return cached

            url = f"{self.base_url}/ticker/24hr?symbol={symbol}"
            response = _requests_get_with_retry(url, headers=self.headers, timeout=10)
            data = response.json()

            if 'lastPrice' in data:
                result = (float(data['lastPrice']), symbol)
                _cache.set(cache_key, result, _TTL_TICKER)
                return result
            return None, symbol
        except Exception as e:
            return None, str(e)
    
    def get_crypto_price(self, symbol: str):
        """Public method to get current price of a cryptocurrency"""
        price, pair = self._fetch_ticker(symbol)
        if price is None:
            # Fallback: try OHLCV
            try:
                df, pair = self._fetch_ohlcv(symbol, limit=1)
                if df is not None and not df.empty:
                    price = float(df.iloc[-1]['close'])
            except:
                pass
        return price
    
    def _fetch_all_tickers_raw(self):
        """Fetch the full /ticker/24hr list once and cache it for 60 s."""
        cached, hit = _cache.get("all_tickers")
        if hit:
            return cached
        url = f"{self.base_url}/ticker/24hr"
        response = _requests_get_with_retry(url, headers=self.headers, timeout=15)
        data = response.json()
        if not isinstance(data, list):
            return []
        usdt = [t for t in data if t['symbol'].endswith('USDT')]
        _cache.set("all_tickers", usdt, _TTL_TICKERS_ALL)
        return usdt

    def _fetch_top_10(self):
        try:
            tickers = self._fetch_all_tickers_raw()
            sorted_tickers = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
            top_10 = sorted_tickers[:10]
            return [
                {
                    "symbol": t['symbol'],
                    "price": float(t['lastPrice']),
                    "volume": float(t['quoteVolume']),
                    "change_24h": float(t['priceChangePercent'])
                }
                for t in top_10
            ]
        except Exception as e:
            return []

    def _fetch_all_coins(self, limit=100):
        """Fetch all available USDT pairs from Binance, optionally limit the number"""
        try:
            tickers = self._fetch_all_tickers_raw()
            sorted_tickers = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
            return [
                {
                    "symbol": t['symbol'],
                    "price": float(t['lastPrice']),
                    "volume": float(t['quoteVolume']),
                    "change_24h": float(t['priceChangePercent'])
                }
                for t in sorted_tickers[:limit]
            ]
        except Exception as e:
            return []

    def get_market_recommendation(self, limit=100):
        """
        Get market overview and coin recommendations based on current market conditions.
        Returns:
        - Top winners (highest 24h change)
        - Top losers (lowest 24h change)
        - Top volume
        - Blue chips (safe)
        - Meme coins (risky/fun)
        - Altcoins (opportunity)
        """
        try:
            all_coins = self._fetch_all_coins(limit=limit)
            if not all_coins:
                return None
            
            # Calculate market statistics
            changes = [c['change_24h'] for c in all_coins]
            market_sentiment = "bullish" if sum(1 for c in changes if c > 0) > len(changes) / 2 else "bearish"
            avg_change = sum(changes) / len(changes)
            volatility = max(changes) - min(changes)
            
            # Sort by change for gainer/loser
            sorted_by_change = sorted(all_coins, key=lambda x: x['change_24h'], reverse=True)
            
            # Categorize coins
            recommendations = {
                "market_overview": {
                    "total_coins": len(all_coins),
                    "avg_change_24h": round(avg_change, 2),
                    "market_sentiment": market_sentiment,
                    "volatility_range": round(volatility, 2),
                    "top_gainer": sorted_by_change[0],
                    "top_loser": sorted_by_change[-1]
                },
                "recommendations": {
                    "top_gainers": sorted(all_coins, key=lambda x: x['change_24h'], reverse=True)[:5],
                    "top_losers": sorted(all_coins, key=lambda x: x['change_24h'])[:5],
                    "top_volume": sorted(all_coins, key=lambda x: x['volume'], reverse=True)[:5],
                    "blue_chips": [
                        c for c in all_coins 
                        if self.classify_coin_type(c['symbol'], c['price'], c['volume'], c['change_24h']) == 'blue_chip'
                    ][:5],
                    "meme_coins": [
                        c for c in all_coins 
                        if self.classify_coin_type(c['symbol'], c['price'], c['volume'], c['change_24h']) == 'meme'
                    ][:5],
                    "altcoins": [
                        c for c in all_coins 
                        if self.classify_coin_type(c['symbol'], c['price'], c['volume'], c['change_24h']) == 'altcoin'
                    ][:5]
                }
            }
            return recommendations
        except Exception as e:
            print(f"Error in get_market_recommendation: {e}")
            return None

    def _search_coins(self, keyword: str):
        """Search coins by keyword (symbol or partial match)"""
        try:
            tickers = self._fetch_all_tickers_raw()
            keyword_upper = keyword.upper()
            filtered = [t for t in tickers if keyword_upper in t['symbol']]
            sorted_results = sorted(filtered, key=lambda x: float(x['quoteVolume']), reverse=True)
            return [
                {
                    "symbol": t['symbol'],
                    "price": float(t['lastPrice']),
                    "volume": float(t['quoteVolume']),
                    "change_24h": float(t['priceChangePercent'])
                }
                for t in sorted_results
            ]
        except Exception as e:
            return []

    @staticmethod
    def classify_coin_type(symbol: str, price: float, volume: float, change_24h: float):
        """
        Classify coin type: 'blue_chip', 'stablecoin', 'meme', 'altcoin'
        
        Blue Chips: BTC, ETH, BNB (top market cap)
        Stablecoins: USDT, USDC, DAI, BUSD (stable price)
        Meme Coins: DOGE, SHIB, FLOKI (high volatility, community-driven)
        Altcoins: Everything else
        """
        symbol_upper = symbol.upper()
        
        # Blue Chips (Top 3)
        if symbol_upper in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
            return 'blue_chip'
        
        # Stablecoins (check both base symbol and price)
        stablecoins = ['USDTUSDT', 'USDCUSDT', 'DAIUSDT', 'BUSDUSDT', 'TUSDUSDT', 'USDPUSDT', 'FDUSDUSDT']
        if symbol_upper in stablecoins:
            return 'stablecoin'
        
        # Meme Coins (high volatility, known meme coins)
        meme_coins = ['DOGE', 'SHIB', 'FLOKI', 'PEPE', 'BONK', 'WIF', 'MEME']
        for meme in meme_coins:
            if meme in symbol_upper:
                return 'meme'
        
        # Default: Altcoin
        return 'altcoin'

    def _fetch_ohlcv(self, symbol: str, timeframe='1d', limit=730):
        try:
            symbol = symbol.upper()
            if '/' in symbol:
                symbol = symbol.replace('/', '')
            elif not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"

            limit = max(min(limit, 1000), 100)

            # Determine cache TTL based on how many candles are requested.
            # Few candles = price intent (short-lived), many = analysis (longer ok).
            ttl = _TTL_OHLCV_PRICE if limit <= 100 else _TTL_OHLCV_FULL
            cache_key = f"ohlcv:{symbol}:{timeframe}:{limit}"
            cached, hit = _cache.get(cache_key)
            if hit:
                return cached

            url = f"{self.base_url}/klines"
            params = {'symbol': symbol, 'interval': timeframe, 'limit': limit}
            response = _requests_get_with_retry(url, params=params, headers=self.headers, timeout=15)
            data = response.json()

            if isinstance(data, dict) and 'code' in data:
                return None, f"API Error: {data.get('msg', data)}"

            if not isinstance(data, list):
                return None, "API Error: Invalid format"

            parsed_data = [
                [
                    candle[0],
                    float(candle[1]), float(candle[2]),
                    float(candle[3]), float(candle[4]),
                    float(candle[5])
                ]
                for candle in data
            ]

            df = pd.DataFrame(parsed_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            result = (df, symbol)
            _cache.set(cache_key, result, ttl)
            return result
        except Exception as e:
            return None, str(e)

    def _fetch_price_at_date(self, symbol: str, end_time_ms: int) -> dict | None:
        """Fetch the closing price of a single daily candle ending at or before end_time_ms.

        Returns a dict with keys: timestamp (ms), close, high, low.
        Returns None on any error.
        """
        try:
            sym = symbol.upper()
            if not sym.endswith('USDT'):
                sym = f"{sym}USDT"
            # Cache keyed to day granularity (86400000 ms/day)
            cache_key = f"price_at:{sym}:{end_time_ms // 86400000}"
            cached, hit = _cache.get(cache_key)
            if hit:
                return cached
            url = f"{self.base_url}/klines"
            params = {'symbol': sym, 'interval': '1d', 'endTime': end_time_ms, 'limit': 3}
            response = _requests_get_with_retry(url, params=params, headers=self.headers, timeout=15)
            data = response.json()
            if isinstance(data, dict) and 'code' in data:
                return None
            if not isinstance(data, list) or not data:
                return None
            candle = data[-1]
            result = {
                'timestamp': int(candle[0]),
                'close': float(candle[4]),
                'high': float(candle[2]),
                'low': float(candle[3]),
            }
            _cache.set(cache_key, result, _TTL_OHLCV_FULL)
            return result
        except Exception:
            return None

    @staticmethod
    def calculate_technicals(df: pd.DataFrame, symbol: str = ""):
        try:
            if df is None or df.empty or len(df) < 50:
                # Not enough data - return basic stats
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    return {
                        "current_price": float(latest['close']),
                        "trend": "neutral",
                        "rsi": 50,
                        "macd": 0,
                        "predicted_next_close": float(latest['close']),
                        "prediction_method": "Insufficient Data",
                        "volatility": 0.01,
                        "coin_type": MarketTools.classify_coin_type(symbol, latest['close'], latest['volume'], 0),
                        "error": f"Need at least 50 candles, got {len(df) if df is not None else 0}"
                    }
                return {"error": "No data available"}
            
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            
            # EMA - Use shorter window if not enough data
            ema_50_window = min(50, len(df) - 1)
            ema_200_window = min(200, len(df) - 1)
            df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=max(5, ema_50_window)).ema_indicator()
            df['ema_200'] = ta.trend.EMAIndicator(df['close'], window=max(10, ema_200_window)).ema_indicator()

            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            
            # ATR (Volatility)
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
            
            # Additional features for better prediction
            # Price momentum (rate of change)
            df['roc'] = df['close'].pct_change(periods=10)
            
            # Volume trend
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma'].replace(0, 1)  # Avoid division by zero
            
            # Volatility (Standard Deviation)
            df['volatility'] = df['close'].pct_change().rolling(window=20).std()

            latest = df.iloc[-1]
            
            # Classify coin type
            coin_type = MarketTools.classify_coin_type(symbol, latest['close'], latest['volume'], 0)
            
            # --- Advanced Prediction Logic with Coin-Type Awareness ---
            next_close_pred = latest['close'] # Default fallback
            prediction_method = "Simple Moving Average"
            
            try:
                if len(df) > 50:
                    from sklearn.ensemble import GradientBoostingRegressor
                    import numpy as np

                    ml_df = df.copy()

                    ml_df['ret_1']  = ml_df['close'].pct_change()         # last 1-bar return
                    ml_df['ret_3']  = ml_df['close'].pct_change(3)         # 3-bar momentum
                    ml_df['ret_6']  = ml_df['close'].pct_change(6)         # 6-bar momentum
                    ml_df['ret_12'] = ml_df['close'].pct_change(12)        # 12-bar / 12h trend
                    ml_df['ret_24'] = ml_df['close'].pct_change(24)        # 24-bar / daily trend
                    ml_df['ema_ratio'] = ml_df['close'] / ml_df['ema_50'] - 1  # distance from EMA-50
                    ml_df['rsi_norm'] = (ml_df['rsi'] - 50) / 50          # centered RSI
                    _macd_signal = ta.trend.MACD(ml_df['close']).macd_signal()
                    ml_df['macd_hist'] = ml_df['macd'] - _macd_signal      # crossover histogram
                    ml_df['target'] = ml_df['close'].pct_change().shift(-1)  # RETURN to predict

                    # Features: returns, momentum, normalised indicators (all stationary)
                    features = [
                        'ret_1', 'ret_3', 'ret_6', 'ret_12', 'ret_24',
                        'rsi_norm', 'macd', 'macd_hist', 'atr',
                        'volume_ratio', 'volatility', 'ema_ratio',
                    ]
                    # blue-chips: add EMA-200 distance
                    if coin_type == 'blue_chip' and 'ema_200' in ml_df.columns:
                        ml_df['ema200_ratio'] = ml_df['close'] / ml_df['ema_200'] - 1
                        features.append('ema200_ratio')

                    ml_df = ml_df.dropna()
                    train_data = ml_df.iloc[:-1]

                    if not train_data.empty:
                        X_train = train_data[features]
                        y_train = train_data['target']

                        # Recency weighting: exponential decay so recent candles dominate
                        _n = len(X_train)
                        _ages = np.arange(_n)
                        _weights = np.exp(_ages * 0.015)

                        try:
                            from xgboost import XGBRegressor, XGBClassifier
                            regressor = XGBRegressor(
                                n_estimators=200, learning_rate=0.05, max_depth=4,
                                subsample=0.8, colsample_bytree=0.8, random_state=42,
                                verbosity=0
                            )
                            # Dedicated direction classifier (optimises accuracy, not MSE)
                            classifier = XGBClassifier(
                                n_estimators=200, learning_rate=0.05, max_depth=3,
                                subsample=0.8, colsample_bytree=0.8, random_state=42,
                                verbosity=0, eval_metric='logloss'
                            )
                            prediction_method = "XGBoost"
                        except ImportError:
                            from sklearn.ensemble import (
                                GradientBoostingRegressor, GradientBoostingClassifier
                            )
                            regressor = GradientBoostingRegressor(
                                n_estimators=200, learning_rate=0.05, max_depth=4,
                                subsample=0.8, random_state=42
                            )
                            classifier = GradientBoostingClassifier(
                                n_estimators=200, learning_rate=0.05, max_depth=3,
                                subsample=0.8, random_state=42
                            )
                            prediction_method = "GradBoost"

                        y_direction = (y_train > 0).astype(int)
                        regressor.fit(X_train, y_train, sample_weight=_weights)
                        classifier.fit(X_train, y_direction, sample_weight=_weights)

                        current_features = ml_df[features].iloc[[-1]]
                        pred_return = float(regressor.predict(current_features)[0])
                        prob_up = float(classifier.predict_proba(current_features)[0][1])

                        # Combine: use classifier's direction when it's confident (>55% / <45%)
                        if prob_up > 0.55:
                            final_return = abs(pred_return)
                        elif prob_up < 0.45:
                            final_return = -abs(pred_return)
                        else:
                            final_return = pred_return

                        # Convert predicted return back to price
                        next_close_pred = float(latest['close']) * (1 + final_return)
                else:
                    # Not enough data for complex models - use simple linear regression
                    import numpy as np
                    from sklearn.linear_model import LinearRegression

                    recent_df = df.tail(20).reset_index()
                    X = np.array(recent_df.index).reshape(-1, 1)
                    y = recent_df['close'].values

                    model = LinearRegression()
                    model.fit(X, y)
                    next_close_pred = model.predict([[20]])[0]
                    prediction_method = "Linear Regression"

            except Exception as e:
                # Final fallback - use last close price
                next_close_pred = latest['close']
                prediction_method = "Current Price"

            return {
                "current_price": float(latest['close']),
                "rsi": float(latest['rsi']) if not pd.isna(latest['rsi']) else 50,
                "macd": float(latest['macd']) if not pd.isna(latest['macd']) else 0,
                "macd_signal": float(latest['macd_signal']) if not pd.isna(latest['macd_signal']) else 0,
                "ema_50": float(latest['ema_50']) if not pd.isna(latest['ema_50']) else latest['close'],
                "ema_200": float(latest['ema_200']) if not pd.isna(latest['ema_200']) else latest['close'],
                "bb_upper": float(latest['bb_upper']) if not pd.isna(latest['bb_upper']) else latest['close'] * 1.02,
                "bb_lower": float(latest['bb_lower']) if not pd.isna(latest['bb_lower']) else latest['close'] * 0.98,
                "atr": float(latest['atr']) if not pd.isna(latest['atr']) else latest['close'] * 0.01,
                "volatility": float(latest['volatility']) if not pd.isna(latest['volatility']) else 0.01,
                "volume_ratio": float(latest['volume_ratio']) if not pd.isna(latest['volume_ratio']) else 1,
                "predicted_next_close": float(next_close_pred),
                "prediction_method": prediction_method,
                "trend": "bullish" if (not pd.isna(latest['ema_50']) and latest['close'] > latest['ema_50']) or (pd.isna(latest['ema_50']) and next_close_pred > latest['close']) else "bearish",
                "coin_type": coin_type
            }
        except Exception as e:
            return {"error": str(e), "current_price": 0}

market_tools = MarketTools()

@tool
def get_crypto_price(symbol: str):
    """Get the current price of a cryptocurrency. Input should be a symbol like 'BTC' or 'ETH'."""
    try:
        price, pair = market_tools._fetch_ticker(symbol)
        if price is None:
            # Fallback to OHLCV if ticker fails
            df, pair = market_tools._fetch_ohlcv(symbol, limit=1)
            if df is None:
                return f"Could not fetch data for {symbol}: {pair}"
            price = df.iloc[-1]['close']
        
        return f"The current price of {pair} is ${price}"
    except Exception as e:
        return f"Error fetching price: {str(e)}"

@tool
def get_top_crypto():
    """Get the top 10 cryptocurrencies by 24h volume on Binance."""
    try:
        data = market_tools._fetch_top_10()
        if not data:
            return "Could not fetch top crypto data."
        
        report = "Top 10 Crypto by Volume (Binance):\n"
        for i, coin in enumerate(data, 1):
            report += f"{i}. {coin['symbol']}: ${coin['price']} (24h Change: {coin['change_24h']:.2f}%)\n"
        return report
    except Exception as e:
        return f"Error fetching top crypto: {str(e)}"

@tool
def analyze_market(symbol: str):
    """Analyze the market trend for a cryptocurrency using technical indicators (RSI, MACD, EMA). Input: symbol like 'BTC'."""
    try:
        df, pair = market_tools._fetch_ohlcv(symbol, limit=200)
        if df is None:
            return f"Could not fetch data for {symbol}: {pair}"
        
        indicators = market_tools.calculate_technicals(df)
        return {
            "symbol": pair,
            "data": indicators,
            "summary": f"Market analysis for {pair}: RSI={indicators['rsi']:.2f}, Trend={indicators['trend']}"
        }
    except Exception as e:
        return f"Error analyzing market: {str(e)}"
