"""
Demo Logger - Ghi lại toàn bộ dữ liệu bot dùng để trả lời.
Mỗi tin nhắn được lưu thành 1 record JSON gồm:
  - Câu hỏi người dùng
  - Intent được phát hiện
  - Dữ liệu thị trường thực (từ Binance)
  - Câu trả lời của bot
  - Thời gian xử lý
"""

import json
import os
from datetime import datetime


DEMO_LOG_FILE = "demo_data.jsonl"  # 1 dòng = 1 JSON record


def save_interaction(
    user_id: str,
    user_message: str,
    intent: str,
    symbol: str | None,
    language: str,
    market_data: dict,
    final_response: str,
    processing_time_ms: float = 0,
):
    """Lưu 1 interaction vào file demo_data.jsonl"""
    
    # Lọc market_data - bỏ base64 chart để file không quá lớn
    clean_market_data = {}
    if market_data:
        clean_market_data = {
            k: v for k, v in market_data.items()
            if k != "chart_image" and v is not None
        }

    record = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "question": user_message,
        "detected_intent": intent,
        "detected_symbol": symbol,
        "language": language,
        "market_data": clean_market_data,
        "bot_response": final_response,
        "processing_time_ms": round(processing_time_ms, 2),
    }

    try:
        with open(DEMO_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[DemoLogger] Không thể ghi file: {e}")


def load_recent_interactions(limit: int = 20) -> list[dict]:
    """Đọc các interaction gần nhất từ file"""
    if not os.path.exists(DEMO_LOG_FILE):
        return []
    
    records = []
    try:
        with open(DEMO_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-limit:]:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    except Exception as e:
        print(f"[DemoLogger] Không thể đọc file: {e}")
    
    return records


def print_demo_summary(limit: int = 5):
    """In tóm tắt các interaction gần nhất ra terminal"""
    records = load_recent_interactions(limit)
    if not records:
        print("[DemoLogger] Chưa có dữ liệu demo nào.")
        return
    
    print("\n" + "=" * 60)
    print(f"  DEMO DATA - {len(records)} INTERACTION GẦN NHẤT")
    print("=" * 60)
    
    for i, r in enumerate(records, 1):
        ts = r.get("timestamp", "")[:19].replace("T", " ")
        q = r.get("question", "")
        intent = r.get("detected_intent", "unknown")
        symbol = r.get("detected_symbol") or "-"
        lang = r.get("language", "vi")
        resp_preview = r.get("bot_response", "")[:80].replace("\n", " ")
        price = r.get("market_data", {}).get("current_price")
        
        print(f"\n[{i}] {ts}")
        print(f"  Hỏi   : {q}")
        print(f"  Intent: {intent}  |  Symbol: {symbol}  |  Lang: {lang}")
        if price:
            print(f"  Giá   : ${price:,.2f}")
        print(f"  Trả lời: {resp_preview}...")
    
    print("\n" + "=" * 60)
    print(f"  File lưu tại: {os.path.abspath(DEMO_LOG_FILE)}")
    print("=" * 60 + "\n")
