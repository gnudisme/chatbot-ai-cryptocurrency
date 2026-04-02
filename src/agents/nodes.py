from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import Config
from src.state import AgentState
from src.tools.market import analyze_market, get_crypto_price, market_tools
from src.tools.learning import QuestionLearningSystem
import json
import re
import datetime as _dt

llm = ChatGoogleGenerativeAI(
    model=Config.MODEL_NAME, 
    google_api_key=Config.GOOGLE_API_KEY,
    temperature=0
)

# Module-level singletons — created once at startup, reused for every request
_learning_system = QuestionLearningSystem()
try:
    from src.tools.visualization import BinanceChartGenerator
    _chart_generator = BinanceChartGenerator()
except Exception:
    _chart_generator = None

_df_store: dict = {}

_COIN_NAME_TO_SYMBOL = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "binance coin": "BNB",
    "bnb": "BNB",
    "ripple": "XRP",
    "cardano": "ADA",
    "dogecoin": "DOGE",
    "shiba": "SHIB",
    "litecoin": "LTC",
    "tron": "TRX",
    "polkadot": "DOT",
    "avalanche": "AVAX",
    "chainlink": "LINK",
    "toncoin": "TON",
    "sui": "SUI",
    "pepe": "PEPE",
}

_COMMON_SYMBOLS = {
    "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "SHIB", "LTC", "TRX",
    "DOT", "AVAX", "LINK", "TON", "SUI", "PEPE", "MATIC", "ARB", "OP", "APT",
    "NEAR", "ATOM", "UNI", "AAVE", "FIL", "ETC", "BCH", "XLM", "HBAR", "INJ",
    "SEI", "TIA", "WIF", "BONK", "ONDO", "ENA", "JUP", "FET", "RENDER", "TAO"
}

_SYMBOL_STOPWORDS = {
    "USDT", "USD", "RSI", "MACD", "ATH", "ATL", "DCA", "FOMO", "FUD", "AI"
}

_VI_LANGUAGE_HINTS = {
    "là", "gì", "và", "của", "cho", "với", "đang", "thị", "trường", "giá",
    "xu", "hướng", "phân", "tích", "dự", "đoán", "rủi", "ro", "kháng", "cự",
    "hỗ", "trợ", "bạn", "mình", "không", "nên", "có", "điểm"
}


def _detect_text_language(text: str) -> str:
    if not text:
        return "unknown"

    lower_text = text.lower()

    # Vietnamese diacritics are strong signals.
    if any(ch in lower_text for ch in "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"):
        return "vi"

    words = re.findall(r"[a-zA-Z]+", lower_text)
    if not words:
        return "unknown"

    vi_hint_count = sum(1 for w in words if w in _VI_LANGUAGE_HINTS)
    if vi_hint_count >= 2:
        return "vi"

    common_en = {"the", "and", "is", "are", "for", "with", "price", "trend", "risk", "market"}
    en_hint_count = sum(1 for w in words if w in common_en)
    if en_hint_count >= 2:
        return "en"

    return "unknown"


def _enforce_response_language(text: str, target_language: str) -> str:
    return text if text else text


def _normalize_symbol(symbol: str | None) -> str | None:
    if not symbol:
        return None
    candidate = symbol.upper().replace("/", "").strip()
    if candidate.endswith("USDT") and len(candidate) > 4:
        candidate = candidate[:-4]
    if 2 <= len(candidate) <= 10 and candidate.isalnum() and candidate not in _SYMBOL_STOPWORDS:
        return candidate
    return None


def _extract_symbol_from_text(text: str) -> str | None:
    lower_text = text.lower()

    # Prefer explicit coin names first (e.g., "bitcoin" -> BTC).
    for coin_name, symbol in _COIN_NAME_TO_SYMBOL.items():
        if coin_name in lower_text:
            return symbol

    # Support pairs/symbols like BTC, BTCUSDT, ETH/USDT.
    normalized = text.replace("/", "")
    pair_matches = re.findall(r"\b([A-Za-z0-9]{2,10})USDT\b", normalized, flags=re.IGNORECASE)
    if pair_matches:
        symbol = _normalize_symbol(pair_matches[0])
        if symbol:
            return symbol

    # Keep uppercase-token detection strict to avoid matching Vietnamese words.
    explicit_uppercase_symbols = re.findall(r"\b[A-Z]{2,10}\b", text)
    for token in explicit_uppercase_symbols:
        symbol = _normalize_symbol(token)
        if symbol:
            return symbol

    # Also support lowercase symbol input like "btc" or "eth" for common coins.
    for token in re.findall(r"\b[a-zA-Z]{2,10}\b", text):
        token_upper = token.upper()
        if token_upper in _COMMON_SYMBOLS:
            return token_upper

    return None


def _find_recent_symbol_from_history(messages) -> str | None:
    # Scan recent messages backward to keep short-term topic continuity.
    for msg in reversed(messages[-12:]):
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        found = _extract_symbol_from_text(content)
        if found:
            return found
    return None


def _resolve_symbol_with_context(state: AgentState, current_message: str) -> str | None:
    explicit_symbol = _extract_symbol_from_text(current_message)
    if explicit_symbol:
        return explicit_symbol

    remembered_symbol = _normalize_symbol(state.get("symbol"))
    if remembered_symbol:
        return remembered_symbol

    return _find_recent_symbol_from_history(state.get("messages", []))


def _parse_compare_periods(message: str):
    """Parse time-reference points from a comparison question.

    Returns a list of (label, end_time_ms) tuples.
    end_time_ms=None means the current/live price should be used.
    At most 3 points are returned.
    """
    lower = message.lower()
    now = _dt.datetime.utcnow()
    periods = []

    def _ms(d: _dt.datetime) -> int:
        return int(d.timestamp() * 1000)

    # --- Year-based patterns: "cuối 2025", "đầu 2025", "end of 2025" etc. ---
    # Context keywords with and without Vietnamese diacritics
    _end_kws   = ['cuối', 'cuoi', 'end of', 'end 20', 'cuồi']
    _start_kws = ['đầu', 'dau', 'start of', 'beginning of', 'early']
    for m in re.finditer(r'\b(20\d{2})\b', lower):
        yr = int(m.group(1))
        ctx = lower[max(0, m.start() - 20): m.end()]
        if any(k in ctx for k in _end_kws):
            target = _ms(now) if yr >= now.year else _ms(_dt.datetime(yr, 12, 28))
            periods.append((f"cuối {yr}", target))
        elif any(k in ctx for k in _start_kws):
            periods.append((f"đầu {yr}", _ms(_dt.datetime(yr, 1, 5, 12))))
        else:
            # Bare year — use end-of-year price (or today for current/future year)
            target = _ms(now) if yr >= now.year else _ms(_dt.datetime(yr, 12, 31, 23, 59))
            periods.append((str(yr), target))

    # --- Relative: N tháng trước / N months ago ---
    for m in re.finditer(r'(\d+)\s*(?:tháng|thang|months?)\s+(?:trước|truoc|ago)', lower):
        n = int(m.group(1))
        periods.append((f"{n} tháng trước", _ms(now - _dt.timedelta(days=n * 30))))

    # --- tháng trước (without number) / last month ---
    if re.search(r'(?:tháng|thang)\s+(?:trước|truoc)', lower) and not re.search(r'\d+\s*(?:tháng|thang)\s+(?:trước|truoc)', lower):
        periods.append(("tháng trước", _ms(now - _dt.timedelta(days=30))))
    if 'last month' in lower:
        periods.append(("last month", _ms(now - _dt.timedelta(days=30))))

    # --- tuần trước / last week ---
    if re.search(r'(?:tuần|tuan)\s+(?:trước|truoc)', lower):
        periods.append(("tuần trước", _ms(now - _dt.timedelta(days=7))))
    if 'last week' in lower:
        periods.append(("last week", _ms(now - _dt.timedelta(days=7))))

    # --- năm ngoái / last year ---
    if re.search(r'(?:năm|nam)\s+(?:ngoái|ngoai)', lower):
        periods.append(("năm ngoái", _ms(now.replace(year=now.year - 1))))
    elif 'last year' in lower:
        periods.append(("last year", _ms(now.replace(year=now.year - 1))))

    # --- hôm qua / yesterday ---
    if re.search(r'(?:hôm|hom)\s+(?:qua)', lower):
        periods.append(("hôm qua", _ms(now - _dt.timedelta(days=1))))
    elif 'yesterday' in lower:
        periods.append(("yesterday", _ms(now - _dt.timedelta(days=1))))

    # --- hiện tại / bây giờ / now / current / today / hôm nay ---
    now_kws = ['hiện tại', 'hien tai', 'bây giờ', 'bay gio', 'hiện nay', 'hien nay',
               'hôm nay', 'hom nay', 'now', 'current', 'today']
    if any(k in lower for k in now_kws):
        periods.append(("hiện tại", None))

    # Deduplicate by timestamp key
    seen: set = set()
    unique = []
    for label, ts in periods:
        key = str(ts)
        if key not in seen:
            seen.add(key)
            unique.append((label, ts))

    if not unique:
        return [("hiện tại", None)]

    # If only one historical point with no current, auto-add current
    has_current = any(ts is None for _, ts in unique)
    if not has_current and len(unique) == 1:
        unique.append(("hiện tại", None))

    return unique[:3]


def classify_input(state: AgentState):
    """
    Determines the user's intent, extracts the crypto symbol, and detects language.
    Uses conversation history to infer context if symbol is missing.
    Supports multiple variations of how users ask the same question.
    """
    # Keep at most the last 20 messages to prevent unbounded state growth.
    # operator.add accumulates messages across turns; truncate early to avoid
    # large state that slows down the MemorySaver checkpoint and the LLM prompt.
    messages = state.get('messages', [])
    if len(messages) > 20:
        messages = messages[-20:]

    last_message = messages[-1]['content']
    lower_msg = last_message.lower()
    context_symbol = _resolve_symbol_with_context(state, last_message)
    detected_language = state.get("language", "vi")
    
    # Keyword-based fast detection with MANY variations for specific intents

    # Comparison intent — check FIRST before price/analysis to avoid "so sánh giá" 
    # being classified as 'price' due to the word "giá".
    compare_keywords = [
        "so sánh", "compare", "versus", " vs ", "đối chiếu",
        "so với trước", "trước và nay", "then and now",
        "thay đổi từ", "biến động từ", "change since",
    ]
    if any(kw in lower_msg for kw in compare_keywords):
        return {
            "intent": "compare",
            "symbol": context_symbol,
            "keyword": None,
            "language": detected_language
        }

    # List All Coins - Keywords variations
    list_keywords = [
        "list all coin", "show all coin", "danh sách tất cả", "tất cả coin", "all coin", "tất cả những",
        "list coins", "show me coins", "all coins", "list cryptocurrencies", "show cryptocurrencies",
        "tất cả tiền", "liệt kê tất cả", "cho xem tất cả", "những coin nào", "coin gì",
        "available coins", "what coins", "mình có coin nào", "coin available", "all available"
    ]
    if any(kw in lower_msg for kw in list_keywords):
        return {
            "intent": "list_all_coins", 
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }
    
    # Search Coins - Keywords variations
    search_keywords = [
        "search", "find", "look for", "tìm", "tìm kiếm", "tìm xem", "search coin",
        "find coin", "lookup", "search for", "tìm kiếm coin", "tìm coin nào",
        "có coin nào tên", "coin tên", "search symbol", "tìm token", "which coin",
        "what coin", "mình tìm", "bạn có biết", "bạn tìm thấy"
    ]
    if any(kw in lower_msg for kw in search_keywords):
        return {
            "intent": "search_coins", 
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }
    
    # Analysis - Keywords variations (CHECK BEFORE TOP_COINS!)
    analysis_keywords = [
        "analyze", "analysis", "technical", "technicals", "phân tích", "chi tiết", "details",
        "oscillator", "rsi", "macd", "bollinger",
        "support", "resistance", "price action", "supply", "demand", "deep dive"
    ]
    if any(kw in lower_msg for kw in analysis_keywords):
        return {
            "intent": "analysis",
            "symbol": context_symbol,
            "keyword": None,
            "language": detected_language
        }

    # Prediction - support short follow-up prompts like "predict đi"
    prediction_keywords = [
        "predict", "prediction", "forecast", "dự đoán", "đoán", "sẽ tăng", "sẽ giảm", "up or down"
    ]
    if any(kw in lower_msg for kw in prediction_keywords):
        return {
            "intent": "prediction",
            "symbol": context_symbol,
            "keyword": None,
            "language": detected_language
        }

    # Price - handle direct price asks and short forms like "giá hiện tại?"
    price_keywords = [
        "price", "current price", "giá", "bao nhiêu", "đang bao nhiêu", "hiện tại", "giá hiện tại"
    ]
    if any(kw in lower_msg for kw in price_keywords):
        return {
            "intent": "price",
            "symbol": context_symbol,
            "keyword": None,
            "language": detected_language
        }
    
    # Top Coins - Keywords variations
    top_keywords = [
        "top 10", "top 5", "top coin", "top crypto", "phổ biến", "popular coin", "ranking", "xếp hạng",
        "best coin", "top cryptocurrencies", "most popular", "top performer", "top gainer",
        "top volume", "highest volume", "most traded", "thịnh hành", "coin hot",
        "trending coin", "trending", "tren", "top meme coin", "top altcoin",
        "leader", "number one", "numero uno", "first place", "đứng đầu"
    ]
    if any(kw in lower_msg for kw in top_keywords):
        return {
            "intent": "top_coins", 
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }

    # Market Overview - Keywords variations
    market_overview_keywords = [
        "market how", "market outlook", "market condition", "thị trường như nào", "thị trường thế nào",
        "market overview", "current market", "market status", "market sentiment", "tình hình thị trường",
        "tình hình market", "bạn khuyên gì", "nên mua coin gì", "coin nào tốt", "coin tốt nhất",
        "recommended coin", "best to buy", "gợi ý coin", "advice coin", "nên mua",
        "what should i buy", "what's your recommendation", "coin tốt hiện tại", "coin nào lên",
        "give me recommendation", "suggest coin", "recommended", "what coin", "which coin should",
        "market right now", "how's the market"
    ]
    if any(kw in lower_msg for kw in market_overview_keywords):
        return {
            "intent": "market_overview",
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }

    # Learn/Education - Keywords for basic crypto questions
    learn_keywords = [
        # Basic questions - English
        "what is bitcoin", "what is ethereum", "what is crypto", "what is blockchain",
        "bitcoin là gì", "ethereum là gì", "crypto là gì", "blockchain là gì",
        "how does bitcoin work", "how does blockchain work", "how does crypto work",
        "bitcoin hoạt động như nào", "blockchain hoạt động thế nào", "crypto hoạt động sao",
        "explain bitcoin", "explain crypto", "explain blockchain", "giải thích bitcoin",
        "what's the difference between", "sự khác biệt giữa", "beginner guide", "hướng dẫn mới bắt đầu",
        "cryptocurrency for beginners", "crypto basics", "basic", "fundamental", "learn about",
        "i'm new", "i'm a beginner", "new to crypto", "tôi mới bắt đầu", "người mới",
        # Market and transaction related
        "bitcoin market", "thị trường bitcoin", "bitcoin price", "giá bitcoin",
        "bitcoin wallet", "ví bitcoin", "bitcoin mining", "khai thác bitcoin", "khai thác",
        "halving", "mining", "đào bitcoin", "đào coin",
        # Advanced concepts
        "decentralization", "phi tập trung", "smart contract", "hợp đồng thông minh",
        "defi", "tài chính phi tập trung",
        "volatility", "biến động", "bull market", "thị trường bò",
        "bear market", "thị trường gấu", "bull run",
        # Other crypto concepts
        "cryptocurrency", "tiền điện tử", "altcoin", "wallet", "ví", "exchange", "sàn giao dịch",
        "ethereum là gì", "what about", "tell me about",
        # DCA
        "dca", "dollar cost averaging", "mua đều đặn", "mua theo kỳ hạn", "đầu tư đều đặn",
        # HODL
        "hodl", "nên giữ coin", "giữ bitcoin", "hold coin", "nắm giữ crypto",
        # FOMO / FUD
        "fomo", "fud", "sợ bỏ lỡ", "fear of missing out",
        # ATH / ATL
        "ath", "atl", "all time high", "all time low", "đỉnh giá", "giá cao nhất lịch sử",
        # Staking
        "staking", "stake", "proof of stake", "kiếm lời từ staking", "lãi suất staking",
        # NFT
        "nft", "non fungible", "non-fungible token", "mua bán nft",
        # Layer 2
        "layer 2", "layer2", "lightning network", "mạng lightning",
        # Gas fee
        "gas fee", "gas fees", "phí gas", "phí giao dịch ethereum",
        # Market cap
        "market cap", "market capitalization", "vốn hóa thị trường", "vốn hóa",
        # Whale
        "whale", "cá voi", "crypto whale", "cá voi crypto",
        # Leverage
        "leverage", "đòn bẩy", "margin trading", "giao dịch ký quỹ", "liquidation", "thanh lý vị thế",
        # Whitepaper
        "whitepaper", "sách trắng", "bitcoin whitepaper",
        # Thị trường (giáo dục)
        "thị trường là gì", "thị trường crypto là gì", "thị trường tiền điện tử là gì",
        "thị trường coin là gì", "crypto market là gì",
    ]
    if any(kw in lower_msg for kw in learn_keywords):
        return {
            "intent": "learn",
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }

    # Construct simple history string for context
    history_str = ""
    for msg in messages[-6:]:  # use the already-truncated local list
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        history_str += f"{role}: {content}\n"

    prompt = f"""Bạn là một Chuyên Gia Phân Tích Ý Định Người Dùng Về Tiền Điện Tử.

Hiểu Ý Định Từ Các Ví Dụ Sau:

CÁC VÍ DỤ Ý ĐỊNH:
- giá: "Giá BTC bao nhiêu?", "Ethereum bao nhiêu tiền?", "BTC đang bao nhiêu?", "ETH giá bao nhiêu?", "Cho biết giá SOL", "Giá Ethereum?"
- phân tích: "Phân tích xu hướng BTC", "BTC có xu hướng gì?", "Phân tích kỹ thuật ETH?", "Phân tích DOGE?", "Phân tích kỹ thuật"
- dự đoán: "Dự đoán giá BTC", "ETH sẽ giá bao nhiêu ngày mai?", "BTC có tăng không?", "ETH tiếp theo lên hay xuống?", "Dự đoán giá BTC"
- tìm coin: "Tìm DOGE", "Tìm Bitcoin", "Có coin XRP không?", "Tìm SHIB", "Tìm Polkadot?"
- tất cả coin: "Cho xem tất cả coin", "Liệt kê coin", "Có bao nhiêu coin?"
- top coin: "Top 10 coin", "Coin nào phổ biến?", "Coin trending?", "Coin hot nhất", "Coin nổi tiếng"
- thị trường: "Thị trường như nào?", "Tâm lý thị trường?", "Nên mua coin gì?", "Tình hình thị trường?", "Bạn khuyên gì?"
- học: "Bitcoin là gì?", "Blockchain hoạt động như nào?", "Tiền điện tử cho người mới"
- chat: "Xin chào", "Bạn khỏe không?", "Trò chuyện"

YÊU CẦU QUAN TRỌNG:
- Hỏi gián tiếp: "Bitcoin thế nào?" = giá, "Ethereum tăng không?" = dự đoán
- Chỉ muốn ĐÃ CO RIÊNG TẠI THỜ ĐIỂM hiện tại với giá
- Phân tích cần CHI TIẾT KỸ THUẬT
- Dự đoán cần kỳ vọng TƯƠNG LAI với lý do
- Thị trường cần TRẠNG THÁI và KHUYẾN NGHỊ
- Học cần NỘI DUNG GIÁO DỤC cho người mới

TRÍCH XUẤT:
1. Ý định: [giá, phân tích, dự đoán, tìm coin, tất cả coin, top coin, thị trường, học, chat]
2. Coin: Ký hiệu coin (BTC, ETH, SOL, v.v.)
3. Từ khóa: Cho tìm coin thôi
4. Ngôn Ngữ: 'vi' hoặc 'en'

Conversation History:
{history_str}

Current User Message: "{last_message}"

Return ONLY valid JSON (no explanation):
{{"intent": "...", "symbol": "...", "keyword": "...", "language": "..."}}
"""
    
    try:
        response = llm.invoke(prompt)
        # Clean up code blocks if the LLM adds them
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content)
        
        # Map Vietnamese intents to English for consistency
        intent_map = {
            "giá": "price",
            "phân tích": "analysis",
            "dự đoán": "prediction",
            "tìm coin": "search_coins",
            "find_coin": "search_coins",
            "tất cả coin": "list_all_coins",
            "all_coins": "list_all_coins",
            "top coin": "top_coins",
            "thị trường": "market_overview",
            "học": "learn",
            "chat": "chat"
        }
        
        raw_intent = data.get("intent", "chat")
        intent = intent_map.get(raw_intent.lower().strip(), raw_intent)
        
        fallback_symbol = context_symbol if intent in ["price", "analysis", "prediction"] else None

        return {
            "intent": intent, 
            "symbol": _normalize_symbol(data.get("symbol")) or fallback_symbol,
            "keyword": data.get("keyword"),
            "language": detected_language
        }
    except Exception as e:
        import traceback
        print(f"Error in classify_input: {traceback.format_exc()}")
        return {
            "intent": "chat",
            "symbol": None,
            "keyword": None,
            "language": detected_language
        }

def fetch_market_data(state: AgentState):
    """
    Fetches market data based on the identified symbol or intent.
    """
    intent = state.get("intent")
    symbol = state.get("symbol")
    keyword = state.get("keyword")

    if intent in ["price", "analysis", "prediction"] and not symbol:
        symbol = _resolve_symbol_with_context(state, state['messages'][-1]['content'])
    
    # Handle Learn/Education Intent
    if intent == "learn":
        # Extract concept from message using variation mapping
        last_message = state['messages'][-1]['content']
        
        from src.tools.crypto_education import get_education_response, variations
        
        language = state.get("language", "en")
        message_lower = last_message.lower().strip()
        
        # Try to find exact match in variations first
        found_concept = None
        
        # Check if message contains any variation keys
        for variation_key in variations.keys():
            if variation_key in message_lower:
                found_concept = variations[variation_key]
                break
        
        # If not found in variations, provide educational response anyway
        # (get_education_response will handle unknown concepts with fallback)
        
        # Pass the resolved concept key (not the raw message) so that
        # get_education_response can do an exact dict lookup.
        lookup_query = found_concept if found_concept else message_lower
        educational_content = get_education_response(lookup_query, language)
        
        return {
            "market_data": {
                "type": "learn",
                "concept": lookup_query,
                "content": educational_content
            }
        }
    
    # Handle List All Coins Intent
    if intent == "list_all_coins":
        try:
            data = market_tools._fetch_all_coins(limit=50)  # Show top 50 coins
            return {"market_data": {"all_coins": data, "type": "list_all_coins", "count": len(data)}}
        except Exception as e:
            return {"market_data": {"error": str(e)}}
    
    # Handle Search Coins Intent
    if intent == "search_coins":
        try:
            # Extract keyword from message if not provided
            if not keyword:
                last_message = state['messages'][-1]['content']
                # Skip these common words that appear between the search verb
                # and the actual coin symbol (e.g. "tìm coin DOGE" → skip "coin")
                _SKIP = {"coin", "coins", "token", "tokens", "kiếm", "xem",
                         "cho", "tôi", "me", "the", "a", "an", "about"}
                search_verbs = ["tìm kiếm", "search for", "find", "search", "tìm", "look for"]
                for kw in search_verbs:
                    if kw in last_message.lower():
                        parts = last_message.lower().split(kw, 1)
                        if len(parts) > 1:
                            # Take the first word that is not a stop/skip word
                            for word in parts[1].strip().split():
                                candidate = word.strip('?.,!').upper()
                                if candidate.upper() not in {s.upper() for s in _SKIP} and candidate:
                                    keyword = candidate
                                    break
                        if keyword:
                            break
            
            if not keyword:
                return {"market_data": {"error": "Vui lòng nhập từ khóa tìm kiếm (ví dụ: 'Tìm DOGE')"}}
            
            data = market_tools._search_coins(keyword)
            if not data:
                return {"market_data": {"error": f"Không tìm thấy coin nào phù hợp với '{keyword}'"}}
            return {"market_data": {"search_results": data, "type": "search_coins", "keyword": keyword, "count": len(data)}}
        except Exception as e:
            return {"market_data": {"error": str(e)}}
    
    # Handle Top Coins Intent
    if intent == "top_coins":
        try:
            data = market_tools._fetch_top_10()
            return {"market_data": {"top_coins": data, "type": "top_coins"}}
        except Exception as e:
            return {"market_data": {"error": str(e)}}

    # Handle Market Overview Intent
    if intent == "market_overview":
        try:
            data = market_tools.get_market_recommendation(limit=100)
            if not data:
                return {"market_data": {"error": "Không thể lấy dữ liệu thị trường"}}
            return {"market_data": {**data, "type": "market_overview"}}
        except Exception as e:
            return {"market_data": {"error": str(e)}}

    # Handle Compare Intent
    if intent == "compare":
        try:
            last_message = state['messages'][-1]['content']
            if not symbol:
                return {"market_data": {"error": "Vui lòng cho biết coin cần so sánh (ví dụ: 'so sánh BTC cuối 2025 và hiện tại')"}}

            periods = _parse_compare_periods(last_message)
            sym_usdt = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol

            points = []
            for label, end_time_ms in periods:
                if end_time_ms is None:
                    # Current / live price
                    price, _ = market_tools._fetch_ticker(symbol)
                    if price is not None:
                        # Also grab 24h change from raw tickers
                        change_24h = 0.0
                        try:
                            raw = market_tools._fetch_all_tickers_raw()
                            matched = next((t for t in raw if t['symbol'] == sym_usdt), None)
                            if matched:
                                change_24h = float(matched['priceChangePercent'])
                        except Exception:
                            pass
                        points.append({
                            "period": label,
                            "price": float(price),
                            "change_24h": change_24h,
                            "is_current": True,
                        })
                else:
                    candle = market_tools._fetch_price_at_date(symbol, end_time_ms)
                    if candle:
                        import datetime as _dt2
                        ts_date = _dt2.datetime.utcfromtimestamp(candle['timestamp'] / 1000).strftime('%d/%m/%Y')
                        points.append({
                            "period": label,
                            "price": candle['close'],
                            "high": candle.get('high', 0),
                            "low": candle.get('low', 0),
                            "date": ts_date,
                            "is_current": False,
                        })

            if len(points) < 2:
                return {"market_data": {"error": f"Không đủ dữ liệu để so sánh. Chỉ tìm được {len(points)} điểm dữ liệu cho {symbol}."}}

            first_price = points[0]['price']
            last_price = points[-1]['price']
            pct_change = ((last_price - first_price) / first_price * 100) if first_price else 0

            return {"market_data": {
                "type": "compare",
                "symbol": sym_usdt,
                "points": points,
                "pct_change": round(pct_change, 2),
            }}
        except Exception as e:
            import traceback
            print(f"Error in compare fetch: {traceback.format_exc()}")
            return {"market_data": {"error": str(e)}}

    if not symbol:
        return {"market_data": {"error": "Vui lòng cung cấp tên coin (ví dụ: BTC, ETH, SOL)"}}
    
    # Get learning context - reuse module-level singleton to avoid a new DB connection per request
    last_message = state['messages'][-1]['content']
    try:
        learning_context = _learning_system.get_learning_context(last_message)
    except Exception:
        learning_context = {"should_enhance": False}
    
    # Reuse the tool logic directly
    try:
        # Get language for timeframe display
        language = state.get("language", "vi")
        
        # Determine timeframe and limit based on intent/message
        # Default is 1h, but if "long term" or "2 year" is detected, switch to 1d/730
        # IMPORTANT: Increased limit from 100 to 500+ to prevent calculate_technicals failures
        timeframe = '1h'
        timeframe_display = "1 giờ" if language == "vi" else "1 hour"

        last_message_lower = last_message.lower()
        if any(x in last_message_lower for x in ['2 năm', '2 years', 'long term', 'dài hạn']):
            limit = 730  # 2 years daily candles
            timeframe = '1d'
            timeframe_display = "1 ngày" if language == "vi" else "1 day"
        elif intent == 'price':
            # Price intent only needs current_price + basic trend; 50 candles is enough
            limit = 50
        else:
            # Analysis / prediction need EMA200, so 500 candles required
            limit = 500

        df, pair = market_tools._fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if df is None:
            return {"market_data": {"error": f"Không tìm thấy coin {symbol}. Kiểm tra lại tên coin?"}}

        data = market_tools.calculate_technicals(df, symbol=pair)
        data['symbol'] = pair
        data['type'] = 'single_coin'
        data['timeframe'] = timeframe
        data['timeframe_display'] = timeframe_display
        data['learning_context'] = learning_context
        # Store df out-of-band so analyze_and_predict can reuse it for chart
        # generation without re-fetching. Never put DataFrames in state — they
        # cannot be serialised by the LangGraph checkpointer.
        user_id = state.get('user_id', 'default')
        _df_store[user_id] = (df, pair, timeframe)
        return {"market_data": data}
    except Exception as e:
        import traceback
        print(f"Error in fetch_market_data: {traceback.format_exc()}")
        return {"market_data": {"error": str(e)}}

def analyze_and_predict(state: AgentState):
    """
    Uses the LLM to interpret market data and give a prediction in the requested language.
    Also generates charts with real Binance data.
    """
    market_data = state.get("market_data", {})
    if "error" in market_data:
        return {"final_response": f"❌ Lỗi: {market_data['error']}"}
    
    intent = state.get("intent")
    language = state.get("language", "vi")
    symbol = state.get("symbol")
    
    # Get timeframe info from market_data, with defaults
    timeframe_display = market_data.get('timeframe_display', "1 giờ" if language == "vi" else "1 hour")
    timeframe_lang = f"Dự đoán giá trong {timeframe_display} tới" if language == "vi" else f"Price prediction for the next {timeframe_display}"
    
    # Use module-level singleton (no per-request instantiation)
    chart_generator = _chart_generator
    chart_image = None

    # Generate chart: try to reuse the df stored in _df_store (no extra Binance call),
    # fall back to re-fetching if not available.
    if chart_generator and symbol and intent in ["price", "analysis", "prediction"]:
        try:
            user_id = state.get('user_id', 'default')
            df_entry = _df_store.pop(user_id, None)  # consume and remove
            timeframe_for_chart = market_data.get('timeframe', '1h')
            if df_entry is not None:
                df, pair_name, tf = df_entry
                if intent in ["price", "prediction"]:
                    chart_image = chart_generator.generate_price_chart_from_df(df, pair_name, tf)
                else:  # analysis
                    chart_image = chart_generator.generate_technical_analysis_chart_from_df(df, pair_name, tf)
            else:
                # Fallback: re-fetch (cache will likely serve it fast)
                if intent == "price":
                    chart_image = chart_generator.generate_price_chart_from_binance(symbol, timeframe='1h', limit=50)
                elif intent == "analysis":
                    chart_image = chart_generator.generate_technical_analysis_chart(symbol, timeframe='1h', limit=100)
                elif intent == "prediction":
                    chart_image = chart_generator.generate_price_chart_from_binance(symbol, timeframe='1h', limit=100)
        except Exception as e:
            print(f"[WARNING] Chart generation failed: {str(e)}")
    
    if market_data.get("type") == "learn":
        # Handle Educational Content
        concept = market_data.get("concept", "crypto")
        content = market_data.get("content", "")
        
        lang_intro = "Để bạn hiểu rõ" if language == "vi" else "Let me explain"
        lang_footer = "Bạn có thể hỏi về các khái niệm khác như Bitcoin, Ethereum, Blockchain, Ví, Sàn Giao Dịch, hoặc bất cứ điều gì khác! Tôi sẽ giải thích đơn giản." if language == "vi" else "Feel free to ask about other concepts like Bitcoin, Ethereum, Blockchain, Wallet, Exchange, or anything else! I'll keep it simple and beginner-friendly."
        
        response = f"""{lang_intro} {concept} một cách đơn giản:

{content}

{lang_footer}
"""
        result = {"final_response": response}
        if chart_image:
            result["chart_image"] = chart_image
        return result
    
    elif market_data.get("type") == "list_all_coins":
        all_coins = market_data.get("all_coins", [])
        count = market_data.get("count", 0)
        prompt = f"""Bạn là trợ lý crypto thân thiện. Liệt kê {count} coin phổ biến nhất trên Binance hiện tại theo dạng dễ đọc (thứ hạng, tên, giá, thay đổi 24h). Nói tự nhiên, thêm nhận xét ngắn về thị trường. Cuối cùng gợi ý người dùng hỏi thêm về bất kỳ coin nào.

Dữ liệu:
{json.dumps(all_coins, indent=2)}

KHÔNG dùng dấu * hay ** hay - hay # trong câu trả lời. Không dùng markdown. Chỉ dùng text thuần. Ngôn ngữ: {language}."""
    elif market_data.get("type") == "search_coins":
        search_results = market_data.get("search_results", [])
        keyword = market_data.get("keyword", "")
        count = market_data.get("count", 0)
        prompt = f"""Bạn là trợ lý crypto thân thiện. Tìm được {count} coin khớp với '{keyword}'. Liệt kê kết quả (tên, giá, thay đổi 24h) tự nhiên và gợi ý người dùng hỏi thêm nếu muốn phân tích.

Kết quả:
{json.dumps(search_results, indent=2)}

KHÔNG dùng dấu * hay ** hay - hay # trong câu trả lời. Không dùng markdown. Chỉ dùng text thuần. Ngôn ngữ: {language}."""
    elif market_data.get("type") == "top_coins":
        top_coins = market_data.get("top_coins", [])
        prompt = f"""Bạn là trợ lý crypto am hiểu thị trường. Trình bày top 10 coin theo khối lượng giao dịch trên Binance hiện tại. Liệt kê thứ hạng, tên, giá, % thay đổi 24h. Thêm nhận xét ngắn về xu hướng chung và gợi ý người dùng hỏi thêm.

Dữ liệu:
{json.dumps(top_coins, indent=2)}

KHÔNG dùng dấu * hay ** hay - hay # trong câu trả lời. Không dùng markdown. Chỉ dùng text thuần. Ngôn ngữ: {language}."""
    elif market_data.get("type") == "market_overview":
        overview = market_data.get("market_overview", {})
        recommendations = market_data.get("recommendations", {})
        prompt = f"""Bạn là trợ lý crypto thực tế và quan tâm đến lợi ích của người dùng.

Tình hình thị trường hôm nay:
- Số coin theo dõi: {overview.get('total_coins', 'N/A')}
- Thay đổi trung bình 24h: {overview.get('avg_change_24h', 'N/A')}%
- Tâm lý thị trường: {overview.get('market_sentiment', 'N/A')}
- Biến động: {overview.get('volatility_range', 'N/A')}
- Tăng mạnh nhất: {overview.get('top_gainer', {}).get('symbol', 'N/A')} (+{overview.get('top_gainer', {}).get('change_24h', 'N/A')}%)
- Giảm mạnh nhất: {overview.get('top_loser', {}).get('symbol', 'N/A')} ({overview.get('top_loser', {}).get('change_24h', 'N/A')}%)

Khuyến nghị theo mức rủi ro:
{json.dumps(recommendations, indent=2)}

Nhận xét thị trường tự nhiên, gợi ý coin theo từng mức rủi ro (thấp/trung/cao), nhắc nhở ngắn về rủi ro đầu tư. KHÔNG dùng dấu * hay ** hay - hay # trong câu trả lời. Không dùng markdown. Chỉ dùng text thuần. Ngôn ngữ: {language}."""
    elif market_data.get("type") == "compare":
        points = market_data.get("points", [])
        sym = market_data.get("symbol", symbol)
        pct_change = market_data.get("pct_change", 0)
        direction = "tăng" if pct_change >= 0 else "giảm"

        points_lines = []
        for p in points:
            date_str = f" (ngày {p['date']})" if p.get('date') else ""
            change_str = f", thay đổi 24h: {p['change_24h']:+.2f}%" if p.get('is_current') and p.get('change_24h') is not None else ""
            points_lines.append(f"  {p['period']}{date_str}: ${p['price']:,.2f}{change_str}")
        points_str = "\n".join(points_lines)

        if language == "vi":
            prompt = f"""Bạn là trợ lý crypto thân thiện. So sánh giá {sym} qua các thời điểm dưới đây và đưa ra nhận xét tự nhiên.

Dữ liệu so sánh:
{points_str}

Thay đổi tổng: {pct_change:+.2f}% ({direction})

Hãy trình bày so sánh tự nhiên như nói chuyện với bạn bè: nêu giá từng thời điểm, tính % thay đổi, nhận xét biến động đó là lớn hay nhỏ theo ngữ cảnh thị trường crypto. KHÔNG dùng dấu * hay ** hay - hay #. Không dùng markdown. Chỉ text thuần."""
        else:
            prompt = f"""You are a friendly crypto assistant. Compare {sym} prices across these periods.

Comparison data:
{points_str}

Total change: {pct_change:+.2f}% ({'up' if pct_change >= 0 else 'down'})

Present the comparison naturally like talking to a friend: state each price, the % change, and briefly comment whether the move is significant in crypto context. Do NOT use any markdown formatting: no *, **, -, #. Plain text only."""
    elif intent == "price":
        # Giá hiện tại - ngắn gọn, tự nhiên
        trend_emoji = "📈" if market_data.get('trend') == "bullish" else "📉"
        price = market_data.get('current_price', 0)
        trend = market_data.get('trend', 'neutral')
        sym = market_data.get('symbol', symbol)
        if language == "vi":
            prompt = f"""Bạn là trợ lý crypto thân thiện. Trả lời ngắn gọn như nói chuyện với bạn bè.

{sym} đang ở ${price:,.2f} {trend_emoji}, xu hướng {trend}.

Cho người dùng biết giá và xu hướng trong 1-2 câu tự nhiên. KHÔNG dùng dấu * hay ** hay - hay #. Không markdown. Chỉ text thuần."""
        else:
            prompt = f"""You are a friendly crypto assistant. Reply briefly like talking to a friend.

{sym} is at ${price:,.2f} {trend_emoji}, trend is {trend}.

Tell the user the price and trend in 1-2 natural sentences. Do NOT use any markdown formatting: no *, **, -, #, or backticks. Plain text only."""

    elif intent == "analysis":
        # Phân tích kỹ thuật - giải thích đơn giản
        rsi = market_data.get('rsi', 50) or 50
        trend = market_data.get('trend', 'neutral')
        volatility = market_data.get('volatility', 0) or 0
        price = market_data.get('current_price', 0)
        bb_upper = market_data.get('bb_upper') or 0
        price_vs_bb = "gần vùng kháng cự" if bb_upper and price > bb_upper * 0.95 else "trong vùng bình thường"
        rsi_signal = "quá mua - có thể điều chỉnh" if rsi > 70 else ("quá bán - có thể hồi phục" if rsi < 30 else "bình thường")
        vol_level = "Cao" if volatility > 0.05 else ("Trung bình" if volatility > 0.02 else "Thấp")

        if language == "vi":
            prompt = f"""Bạn là chuyên gia phân tích crypto, giải thích đơn giản như nói chuyện với người mới.

Dữ liệu {market_data.get('symbol')}:
- Giá: ${price:,.2f}
- RSI: {rsi:.1f} ({rsi_signal})
- Xu hướng: {trend}
- Biến động: {vol_level}
- Vị trí giá: {price_vs_bb}

Phân tích cho người dùng: xu hướng đang như thế nào, RSI báo hiệu gì, mức độ rủi ro, và điểm cần chú ý. Giải thích tự nhiên, không dùng jargon khó. KHÔNG dùng dấu * hay ** hay - hay #. Không markdown. Chỉ text thuần."""
        else:
            prompt = f"""You are a crypto analyst explaining things simply to a beginner.

Data for {market_data.get('symbol')}:
- Price: ${price:,.2f}
- RSI: {rsi:.1f} ({rsi_signal})
- Trend: {trend}
- Volatility: {vol_level}
- Price position: {price_vs_bb}

Analyze for the user: what's the trend, what RSI signals, risk level, and key things to watch. Keep it natural and beginner-friendly. Do NOT use any markdown formatting: no *, **, -, #, or backticks. Plain text only."""

    else:
        # Dự đoán giá - với lý do thực tế
        rsi = market_data.get('rsi', 50) or 50
        trend = market_data.get('trend', 'neutral')
        volatility = market_data.get('volatility', 0) or 0
        price = market_data.get('current_price', 0)
        predicted = market_data.get('predicted_next_close', price)
        method = market_data.get('prediction_method', 'ML')
        risk = "Cao" if volatility > 0.05 else ("Trung bình" if volatility > 0.02 else "Thấp")
        pct_change = ((predicted - price) / price * 100) if price else 0

        if language == "vi":
            trend_emoji = "🚀" if trend == "bullish" else "📉"
            prompt = f"""Bạn là trợ lý crypto thực tế và thẳng thắn.

Dữ liệu {market_data.get('symbol')}:
- Giá hiện tại: ${price:,.2f}
- Dự đoán trong {timeframe_display}: ${predicted:,.2f} ({pct_change:+.2f}%) {trend_emoji}
- Phương pháp: {method}
- RSI: {rsi:.1f}, Xu hướng: {trend}, Biến động: {risk}

Trả lời tự nhiên: nói dự đoán, giải thích lý do dựa trên RSI và xu hướng, mức rủi ro ({risk}), và thêm disclaimer ngắn cuối. Không cứng nhắc, nói như bạn bè. KHÔNG dùng dấu * hay ** hay - hay #. Không markdown. Chỉ text thuần."""
        else:
            trend_emoji = "🚀" if trend == "bullish" else "📉"
            prompt = f"""You are an honest and practical crypto assistant.

Data for {market_data.get('symbol')}:
- Current price: ${price:,.2f}
- Prediction in {timeframe_display}: ${predicted:,.2f} ({pct_change:+.2f}%) {trend_emoji}
- Method: {method}
- RSI: {rsi:.1f}, Trend: {trend}, Volatility risk: {risk}

Reply naturally: share the prediction, explain why based on RSI and trend, state the risk level ({risk}), and add a short disclaimer at the end. Be conversational, not stiff. Do NOT use any markdown formatting: no *, **, -, #, or backticks. Plain text only."""

    # Nếu người dùng hỏi nhiều lần, thêm ngữ cảnh
    learning_context = market_data.get('learning_context', {})
    if learning_context.get('should_enhance'):
        frequency = learning_context.get('frequency', 1)
        if language == "vi":
            prompt += f"\n\n[Người dùng đã hỏi về chủ đề này {frequency} lần - hãy trả lời chi tiết và đầy đủ hơn bình thường.]"
        else:
            prompt += f"\n\n[User has asked about this topic {frequency} times - give a more detailed and thorough answer than usual.]"

    try:
        response = llm.invoke(prompt)
        final_text = _enforce_response_language(response.content, language)
        result = {
            "analysis": final_text,
            "final_response": final_text,
            "timeframe_display": timeframe_display
        }
        if chart_image:
            result["chart_image"] = chart_image
        return result
    except Exception as e:
        import traceback
        print(f"LLM Error in analyze_and_predict: {traceback.format_exc()}")
        return {
            "analysis": "Error analyzing",
            "final_response": "Xin lỗi, không thể phân tích dữ liệu lúc này."
        }

def general_chat(state: AgentState):
    """
    Handles general conversation - responses in Vietnamese only.
    """
    from langchain_core.messages import AIMessage
    language = state.get("language", "vi")
    language_instruction = "BẮT BUỘC trả lời bằng tiếng Việt." if language == "vi" else "You MUST reply in English."
    
    messages = [
        SystemMessage(content=f"""Bạn là trợ lý crypto AI thân thiện và hiểu biết. Trả lời tự nhiên như người bạn am hiểu crypto.

Nguyên tắc:
1. Ngôn ngữ: nhận diện ngôn ngữ người dùng và trả lời đúng ngôn ngữ đó (Việt hoặc Anh)
2. Giải thích đơn giản, không jargon khó
3. KHÔNG BAO GIỊ dùng dấu * hay ** hay *** hay - hay # hay ` trong câu trả lời. Không dùng bất kỳ định dạng markdown nào. Chỉ dùng text thuần và emoji.
4. Nếu hỏi về giá/phân tích/dự đoán → gợi ý họ hỏi thẳng về coin đó
    5. Ngắn gọn, đúng trọng tâm, 2-4 câu là đủ

    {language_instruction}""")
    ]
    # Add recent history (simplified)
    for msg in state['messages'][-6:]:
        if isinstance(msg, dict):
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'user':
                messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                messages.append(AIMessage(content=content))
    
    try:
        response = llm.invoke(messages)
        final_text = _enforce_response_language(response.content, language)
        return {
            "final_response": final_text
        }
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"LLM Error in general_chat: {error_msg}")
        return {
            "final_response": "Xin lỗi, tôi gặp sự cố tạm thời. Vui lòng thử lại hoặc hỏi về đồng tiền khác."
        }
