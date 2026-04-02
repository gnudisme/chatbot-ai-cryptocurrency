"""
Language Detection & Chart Visualization Module
Supports English and Vietnamese responses
Generates price charts and market data visualizations
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — required for thread safety.
                       # TkAgg (default on Windows) is NOT thread-safe and causes
                       # "main thread is not in main loop" RuntimeErrors when chart
                       # generation runs in a worker thread (LangGraph executor /
                       # asyncio.to_thread). Agg renders to memory only, no GUI.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, List, Tuple, Optional
import numpy as np

class LanguageDetector:
    """Detect user language from message text"""
    
    # Vietnamese characters and keywords
    VI_KEYWORDS = {
        'là', 'gì', 'cái', 'có', 'không', 'được', 'giá', 'đợi', 'thị', 
        'trường', 'dự', 'đoán', 'tăng', 'giảm', 'mua', 'bán', 'ơi', 'anh',
        'em', 'tôi', 'bạn', 'ta', 'chúng', 'trong', 'ngoài', 'của', 'cho',
        'bao', 'nhiêu', 'khi', 'nào', 'nơi', 'đâu', 'như', 'thế', 'nào',
        'bitcoin', 'crypto', 'tiền', 'điện', 'tử', 'coin', 'token', 'ethereum',
        'blockchain', 'ví', 'sàn', 'giao', 'dịch', 'thẻ', 'ngân', 'hàng',
        'gia', 'bao', 'tien', 'dien', 'tử', 'hoạt động', 'hoạtdộng', 'bạn',
        'mua', 'bán', 'tăng', 'giảm', 'điều', 'chủ', 'chu'
    }
    
    # Vietnamese Unicode ranges for characters with diacritics
    VI_CHAR_RANGES = [
        (0x00C0, 0x00FF),  # Latin Extended-A
        (0x0100, 0x017F),  # Latin Extended-B
        (0x0180, 0x024F),  # Latin Extended Additional
    ]
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language from text
        Returns: 'vi' for Vietnamese, 'en' for English, 'mixed' for both
        """
        text_lower = text.lower()
        
        # Count Vietnamese diacritical characters
        vi_char_count = 0
        for char in text_lower:
            char_code = ord(char)
            # Check for Vietnamese characters (á, à, ả, ã, ạ, ă, ằ, ắ, ẳ, ẵ, ặ, â, ầ, ấ, ẩ, ẫ, ậ, etc.)
            if char_code >= 192 and char_code <= 591:  # Extended Latin range for Vietnamese
                vi_char_count += 1
        
        # Count Vietnamese keywords
        words = text_lower.replace('?', ' ').replace('!', ' ').replace(',', ' ').split()
        vi_keyword_count = sum(1 for word in words if word in LanguageDetector.VI_KEYWORDS)
        
        # Vietnamese-specific keywords that strongly indicate VI
        strong_vi_keywords = ['là gì', 'bao nhiêu', 'hoạt động', 'dự đoán', 'thị trường', 'giá hiện tại']
        strong_vi_count = sum(1 for kw in strong_vi_keywords if kw in text_lower)
        
        # Determine language
        # If we found Vietnamese characters or enough keywords, it's Vietnamese
        if vi_char_count >= 2 or vi_keyword_count >= 3 or strong_vi_count >= 1:
            return 'vi'
        elif vi_char_count > 0:
            return 'vi'
        else:
            return 'en'

class ChartGenerator:
    """Generate price and market charts for visualization"""
    
    @staticmethod
    def generate_price_chart(
        symbol: str,
        prices: List[float],
        dates: List[datetime],
        title: str = "",
        show_prediction: bool = False,
        predicted_price: Optional[float] = None
    ) -> str:
        """
        Generate price chart and return as base64-encoded image
        
        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, etc.)
            prices: List of prices
            dates: List of dates corresponding to prices
            title: Chart title
            show_prediction: Whether to show predicted price
            predicted_price: Predicted price point
        
        Returns:
            Base64-encoded image string
        """
        fig = None
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot price line
            ax.plot(dates, prices, linewidth=2, color='#0066CC', label='Current Price')
            
            # Add prediction point if provided
            if show_prediction and predicted_price:
                ax.scatter([dates[-1]], [predicted_price], color='#FF6600', s=200, 
                          marker='^', label=f'Predicted: ${predicted_price:.2f}', zorder=5)
                
                # Draw trend line from last price to prediction
                ax.plot([dates[-1], dates[-1]], [prices[-1], predicted_price], 
                       color='#FF6600', linestyle='--', alpha=0.7)
            
            # Fill under curve
            ax.fill_between(dates, prices, alpha=0.2, color='#0066CC')
            
            # Format chart
            ax.set_title(f'{symbol} Price Chart\n{title}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Price (USD)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=45)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return image_base64
        except Exception as e:
            print(f"Error generating price chart: {e}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)
    
    @staticmethod
    def generate_market_overview_chart(
        top_coins: List[Dict],
        metric: str = 'market_cap'
    ) -> str:
        """
        Generate market overview bar chart
        
        Args:
            top_coins: List of coin data with name, value
            metric: 'market_cap', 'volume_24h', 'price_change'
        
        Returns:
            Base64-encoded image string
        """
        fig = None
        try:
            coins = [coin['name'] for coin in top_coins[:10]]
            values = [coin.get(metric, 0) for coin in top_coins[:10]]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Determine color based on metric
            if metric == 'price_change':
                colors = ['#00AA00' if v > 0 else '#CC0000' for v in values]
            else:
                colors = plt.cm.viridis(np.linspace(0, 1, len(coins)))
            
            bars = ax.barh(coins, values, color=colors)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, values)):
                label = f'${value/1e9:.2f}B' if metric == 'market_cap' else f'${value:,.0f}'
                if metric == 'price_change':
                    label = f'{value:.2f}%'
                ax.text(value, i, f' {label}', va='center', fontweight='bold')
            
            # Format title based on metric
            metric_titles = {
                'market_cap': 'Top 10 Coins by Market Cap',
                'volume_24h': 'Top 10 Coins by 24h Volume',
                'price_change': 'Top 10 Coins by 24h Price Change (%)'
            }
            
            ax.set_title(metric_titles.get(metric, 'Market Overview'), 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Value', fontsize=12)
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            
            return image_base64
        except Exception as e:
            print(f"Error generating market overview chart: {e}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)
    
    @staticmethod
    def generate_volatility_chart(
        symbol: str,
        volatility_data: List[Dict],
        period: str = '30d'
    ) -> str:
        """
        Generate volatility analysis chart
        
        Args:
            symbol: Cryptocurrency symbol
            volatility_data: List with date and volatility %
            period: Time period (7d, 30d, 90d)
        
        Returns:
            Base64-encoded image string
        """
        try:
            dates = [d['date'] for d in volatility_data]
            volatility = [d['volatility'] for d in volatility_data]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Determine color based on volatility level
            colors = ['#00AA00' if v < 2 else '#FF9900' if v < 4 else '#CC0000' 
                     for v in volatility]
            
            ax.bar(dates, volatility, color=colors, alpha=0.8)
            ax.axhline(y=2, color='green', linestyle='--', alpha=0.5, label='Low (<2%)')
            ax.axhline(y=4, color='red', linestyle='--', alpha=0.5, label='High (>4%)')
            
            ax.set_title(f'{symbol} Volatility Analysis ({period})', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Volatility (%)', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            print(f"Error generating volatility chart: {e}")
            return None
    
    @staticmethod
    def generate_indicator_chart(
        symbol: str,
        prices: List[float],
        dates: List[datetime],
        rsi: Optional[List[float]] = None,
        macd: Optional[List[float]] = None,
        bollinger: Optional[Tuple[List, List, List]] = None
    ) -> str:
        """
        Generate technical indicator chart (price + RSI/MACD/Bollinger Bands)
        
        Args:
            symbol: Cryptocurrency symbol
            prices: List of prices
            dates: List of dates
            rsi: RSI values (optional)
            macd: MACD values (optional)
            bollinger: (upper_band, middle_band, lower_band) tuple (optional)
        
        Returns:
            Base64-encoded image string
        """
        try:
            fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # Price chart with Bollinger Bands
            ax1 = axes[0]
            ax1.plot(dates, prices, linewidth=2, color='#0066CC', label='Price')
            
            if bollinger:
                upper, middle, lower = bollinger
                ax1.fill_between(dates, lower, upper, alpha=0.2, color='#0066CC', label='Bollinger Bands')
                ax1.plot(dates, upper, '--', color='gray', alpha=0.5)
                ax1.plot(dates, lower, '--', color='gray', alpha=0.5)
            
            ax1.set_title(f'{symbol} Price with Technical Indicators', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USD)', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Indicator chart
            ax2 = axes[1]
            
            if rsi:
                ax2.plot(dates, rsi, linewidth=2, color='#FF6600', label='RSI (14)')
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
                ax2.fill_between(dates, 30, 70, alpha=0.1, color='gray')
            
            ax2.set_xlabel('Date', fontsize=12)
            ax2.set_ylabel('RSI', fontsize=11)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='best')
            
            # Format x-axis
            axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            axes[1].xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            print(f"Error generating indicator chart: {e}")
            return None

class ResponseFormatter:
    """Format bot responses in English or Vietnamese"""
    
    TEMPLATES = {
        'en': {
            'greeting': '👋 Hello! I\'m your crypto assistant. Ask me anything about prices, markets, or cryptocurrencies.',
            'price_info': '📊 {symbol} Price Information\n'
                         'Current Price: ${price:,.2f}\n'
                         '24h Change: {change_24h:.2f}%\n'
                         'Market Cap: ${market_cap:,.0f}\n'
                         '24h Volume: ${volume_24h:,.0f}',
            'prediction': '🔮 {symbol} Price Prediction\n'
                         'Predicted Price: ${predicted:,.2f}\n'
                         'Confidence: {confidence:.0f}%\n'
                         'Timeframe: {timeframe}',
            'market_overview': '📈 Top Cryptocurrencies by Market Cap\n',
            'error': '❌ Xin lỗi, tôi không thể xử lý điều đó. Vui lòng thử lại.',
        },
        'vi': {
            'greeting': '👋 Xin chào! Tôi là trợ lý crypto của bạn. Hỏi tôi bất cứ điều gì về giá, thị trường hoặc tiền điện tử.',
            'price_info': '📊 Thông Tin Giá {symbol}\n'
                         'Giá Hiện Tại: ${price:,.2f}\n'
                         'Thay Đổi 24h: {change_24h:.2f}%\n'
                         'Vốn Hóa: ${market_cap:,.0f}\n'
                         'Khối Lượng 24h: ${volume_24h:,.0f}',
            'prediction': '🔮 Dự Đoán Giá {symbol}\n'
                         'Giá Dự Đoán: ${predicted:,.2f}\n'
                         'Độ Tin Cậy: {confidence:.0f}%\n'
                         'Thời Gian: {timeframe}',
            'market_overview': '📈 Top Tiền Điện Tử Theo Vốn Hóa\n',
            'error': '❌ Xin lỗi, tôi không thể xử lý điều đó. Vui lòng thử lại.',
        }
    }
    
    @staticmethod
    def format_price_info(symbol: str, data: Dict, language: str = 'en') -> str:
        """Format price information response"""
        template = ResponseFormatter.TEMPLATES.get(language, ResponseFormatter.TEMPLATES['en'])
        
        return template['price_info'].format(
            symbol=symbol,
            price=data.get('price', 0),
            change_24h=data.get('change_24h', 0),
            market_cap=data.get('market_cap', 0),
            volume_24h=data.get('volume_24h', 0)
        )
    
    @staticmethod
    def format_prediction(symbol: str, predicted_price: float, confidence: float, 
                         timeframe: str, language: str = 'en') -> str:
        """Format prediction response"""
        template = ResponseFormatter.TEMPLATES.get(language, ResponseFormatter.TEMPLATES['en'])
        
        return template['prediction'].format(
            symbol=symbol,
            predicted=predicted_price,
            confidence=confidence,
            timeframe=timeframe
        )
    
    @staticmethod
    def format_market_overview(coins: List[Dict], language: str = 'en') -> str:
        """Format market overview response"""
        template = ResponseFormatter.TEMPLATES.get(language, ResponseFormatter.TEMPLATES['en'])
        
        msg = template['market_overview']
        for i, coin in enumerate(coins[:10], 1):
            change = coin.get('change_24h', 0)
            emoji = '📈' if change > 0 else '📉'
            msg += f"\n{i}. {emoji} {coin['name']} (${coin['price']:,.2f}) - {change:.2f}%"
        
        return msg


class BinanceChartGenerator:
    """Generate charts with real data from Binance API"""
    
    def __init__(self):
        from src.tools.market import MarketTools
        self.market_tools = MarketTools()
    
    def generate_price_chart_from_binance(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """
        Generate price chart using real data from Binance API
        Returns: base64-encoded PNG image
        """
        fig = None
        try:
            # Fetch OHLCV data from Binance
            df, pair = self.market_tools._fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            
            if df is None:
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot price line
            dates = df.index
            prices = df['close']
            
            ax.plot(dates, prices, linewidth=2.5, color='#1f77b4', label='Price')
            
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                ax.fill_between(dates, df['bb_upper'], df['bb_lower'], 
                               alpha=0.1, color='gray', label='Bollinger Bands')
                if 'bb_middle' in df.columns:
                    ax.plot(dates, df['bb_middle'], linewidth=1, color='orange', 
                           alpha=0.5, label='BB Middle')
                else:
                    bb_mid = (df['bb_upper'] + df['bb_lower']) / 2
                    ax.plot(dates, bb_mid, linewidth=1, color='orange',
                           alpha=0.5, label='BB Middle')
            
            # Styling
            ax.set_title(f'{pair} Price Chart ({timeframe})', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Price (USDT)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Tight layout
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode()
            
            return img_base64
        
        except Exception as e:
            print(f"Error generating chart: {str(e)}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)
    
    def generate_market_overview_from_binance(self, limit: int = 10):
        """
        Generate market overview chart with top coins from Binance
        Returns: base64-encoded PNG image
        """
        fig = None
        try:
            # Fetch top coins from Binance
            top_coins = self.market_tools._fetch_top_10()
            
            if not top_coins or len(top_coins) == 0:
                return None
            
            # Prepare data for chart
            symbols = [coin['symbol'].replace('USDT', '') for coin in top_coins[:10]]
            prices = [coin['price'] for coin in top_coins[:10]]
            changes = [coin['change_24h'] for coin in top_coins[:10]]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Colors: green for positive, red for negative
            colors = ['#2ecc71' if c > 0 else '#e74c3c' for c in changes]
            
            # Create bar chart
            bars = ax.barh(symbols, prices, color=colors, alpha=0.8)
            
            # Add value labels
            for i, (bar, price) in enumerate(zip(bars, prices)):
                ax.text(price, bar.get_y() + bar.get_height()/2, 
                       f' ${price:,.0f}', va='center', fontsize=9)
            
            # Styling
            ax.set_title('Top Cryptocurrencies by Binance Volume', fontsize=14, fontweight='bold')
            ax.set_xlabel('Price (USDT)', fontsize=12)
            ax.grid(True, axis='x', alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Tight layout
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode()
            
            return img_base64
        
        except Exception as e:
            print(f"Error generating market chart: {str(e)}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)
    
    def generate_technical_analysis_chart(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """
        Generate chart with technical indicators from Binance data
        Returns: base64-encoded PNG image
        """
        fig = None
        try:
            # Fetch OHLCV data from Binance
            df, pair = self.market_tools._fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            
            if df is None:
                return None
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            
            # Price chart
            ax1 = axes[0]
            dates = df.index
            
            ax1.plot(dates, df['close'], linewidth=2.5, color='#1f77b4', label='Close Price')
            ax1.fill_between(dates, df['open'], df['close'], 
                            where=(df['close'] >= df['open']), 
                            alpha=0.3, color='green', label='Up')
            ax1.fill_between(dates, df['open'], df['close'], 
                            where=(df['close'] < df['open']), 
                            alpha=0.3, color='red', label='Down')
            
            ax1.set_title(f'{pair} Technical Analysis ({timeframe})', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USDT)', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Indicator chart (RSI or Volume)
            ax2 = axes[1]
            
            if 'rsi' in df.columns:
                ax2.plot(dates, df['rsi'], linewidth=2, color='#FF6600', label='RSI (14)')
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
                ax2.fill_between(dates, 30, 70, alpha=0.1, color='gray')
                ax2.set_ylim(0, 100)
            else:
                ax2.bar(dates, df['volume'], color='#3498db', alpha=0.6, label='Volume')
            
            ax2.set_xlabel('Date', fontsize=11)
            ax2.set_ylabel('RSI / Volume', fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='best')
            
            # Format x-axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # Tight layout
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode()
            
            return img_base64
        
        except Exception as e:
            print(f"Error generating technical chart: {str(e)}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)

    # ------------------------------------------------------------------
    # DataFrame-based chart methods (reuse already-fetched data, no extra
    # Binance API call)
    # ------------------------------------------------------------------

    def generate_price_chart_from_df(self, df, pair: str, timeframe: str = '1h'):
        """Generate price chart from a pre-fetched DataFrame (no Binance re-fetch)."""
        if df is None or df.empty:
            return None
        fig = None
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            dates = df.index
            prices = df['close']
            ax.plot(dates, prices, linewidth=2.5, color='#1f77b4', label='Price')
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                ax.fill_between(dates, df['bb_upper'], df['bb_lower'],
                                alpha=0.1, color='gray', label='Bollinger Bands')
                if 'bb_middle' in df.columns:
                    ax.plot(dates, df['bb_middle'], linewidth=1, color='orange',
                            alpha=0.5, label='BB Middle')
                else:
                    bb_mid = (df['bb_upper'] + df['bb_lower']) / 2
                    ax.plot(dates, bb_mid, linewidth=1, color='orange',
                            alpha=0.5, label='BB Middle')
            ax.set_title(f'{pair} Price Chart ({timeframe})', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Price (USDT)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            plt.tight_layout()
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.read()).decode()
        except Exception as e:
            print(f"Error generating price chart from df: {str(e)}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)

    def generate_technical_analysis_chart_from_df(self, df, pair: str, timeframe: str = '1h'):
        """Generate technical analysis chart from a pre-fetched DataFrame (no Binance re-fetch)."""
        if df is None or df.empty:
            return None
        fig = None
        try:
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            ax1 = axes[0]
            dates = df.index
            ax1.plot(dates, df['close'], linewidth=2.5, color='#1f77b4', label='Close Price')
            ax1.fill_between(dates, df['open'], df['close'],
                             where=(df['close'] >= df['open']),
                             alpha=0.3, color='green', label='Up')
            ax1.fill_between(dates, df['open'], df['close'],
                             where=(df['close'] < df['open']),
                             alpha=0.3, color='red', label='Down')
            ax1.set_title(f'{pair} Technical Analysis ({timeframe})', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USDT)', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            ax2 = axes[1]
            if 'rsi' in df.columns:
                ax2.plot(dates, df['rsi'], linewidth=2, color='#FF6600', label='RSI (14)')
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
                ax2.fill_between(dates, 30, 70, alpha=0.1, color='gray')
                ax2.set_ylim(0, 100)
            else:
                ax2.bar(dates, df['volume'], color='#3498db', alpha=0.6, label='Volume')
            ax2.set_xlabel('Date', fontsize=11)
            ax2.set_ylabel('RSI / Volume', fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='best')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            plt.tight_layout()
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.read()).decode()
        except Exception as e:
            print(f"Error generating technical chart from df: {str(e)}")
            return None
        finally:
            if fig is not None:
                plt.close(fig)
