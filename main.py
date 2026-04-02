import logging
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

import re

_PID_FILE = os.path.join(os.path.dirname(__file__), 'bot.pid')


def _acquire_pid_lock():
    """Prevent running more than one bot instance at a time.

    Writes current PID to bot.pid on startup; checks if an existing process
    from a previous run is still alive and exits early if so.
    """
    if os.path.exists(_PID_FILE):
        try:
            with open(_PID_FILE) as f:
                old_pid = int(f.read().strip())
            # On Windows, use tasklist to check if the PID is still alive.
            # os.kill(pid, 0) is unreliable on Windows (PermissionError for live procs).
            import subprocess
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {old_pid}', '/NH'],
                capture_output=True, text=True
            )
            if str(old_pid) in result.stdout:
                print(f"[ERROR] Another bot instance is already running (PID {old_pid}).")
                print("[INFO]  Stop it first, then retry. Or delete bot.pid manually.")
                sys.exit(1)
        except (ValueError, FileNotFoundError, Exception):
            pass  # Stale / unreadable PID file — safe to overwrite
    with open(_PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def _release_pid_lock():
    try:
        os.remove(_PID_FILE)
    except FileNotFoundError:
        pass

from src.config import Config
from src.agents.graph import app
from src.db.postgres import Database
from src.services.alert_manager import AlertManager
from src.services.demo_logger import save_interaction
from src.tools.market import MarketTools
from src.tools.visualization import LanguageDetector, ResponseFormatter, ChartGenerator


def clean_markdown(text: str) -> str:
    """Remove markdown formatting characters from bot responses for Telegram plain text."""
    # Remove bold/italic markers: ***text***, **text**, *text* (multi-line)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'\1', text)
    # Remove __bold__ and _italic_ markdown
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'(?<!\w)_([^_\n]+?)_(?!\w)', r'\1', text)
    # Remove heading markers (###, ##, #)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove any remaining standalone asterisks used as bullet points
    text = re.sub(r'^\s*[\*]\s+', '\u2022 ', text, flags=re.MULTILINE)
    # Remove leading dashes used as bullet points, replace with bullet
    text = re.sub(r'^\s*-\s+', '\u2022 ', text, flags=re.MULTILINE)
    # Remove backtick code formatting
    text = re.sub(r'```[^`]*```', lambda m: m.group(0).strip('`'), text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Clean up any leftover standalone * or ** not caught above
    text = re.sub(r'(?:^|(?<=\s))\*{1,3}(?=\s|$)', '', text, flags=re.MULTILINE)
    # Remove extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Database
db = Database()

# Per-user conversation history (managed here, not in LangGraph state)
# Keeps the last _MAX_HISTORY messages for context, preventing unbounded accumulation
# in the MemorySaver checkpointer.
_user_message_history: dict = {}
_MAX_HISTORY = 20

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Register user on start
    user = update.effective_user
    db.register_user(user.id, user.username)
    
    user_name = user.first_name or user.username or "bạn"
    welcome_msg = (
        f"Chào {user_name}! 👋\n\n"
        "Mình là trợ lý AI chuyên về Crypto. "
        "Bạn có thể hỏi mình bất cứ điều gì về thị trường tiền mã hoá — "
        "từ giá coin, phân tích kỹ thuật, dự đoán xu hướng, đến kiến thức cơ bản cho người mới.\n\n"
        "Thử hỏi mình kiểu như:\n"
        "  • \"Giá Bitcoin hiện tại bao nhiêu?\"\n"
        "  • \"Phân tích ETH giúp mình\"\n"
        "  • \"Thị trường hôm nay thế nào?\"\n"
        "  • \"Blockchain là gì?\"\n\n"
        "Ngoài ra bạn có thể dùng:\n"
        "  /alert <coin> <giá> — nhận thông báo khi giá đạt mức bạn muốn\n"
        "  /alerts — xem các cảnh báo đang theo dõi\n"
        "  /export <coin> — xuất dữ liệu ra CSV\n\n"
        "Cứ nhắn thoải mái nhé! 😊"
    )
    
    await update.message.reply_text(welcome_msg)

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "⚠️ Sử dụng: /alert <SYMBOL> <GIÁ_MỤC> [ABOVE|BELOW]\n"
            "Ví dụ:\n"
            "  /alert BTC 70000 ABOVE\n"
            "  /alert ETH 3000 BELOW\n\n"
            "Nếu không nhập điều kiện, mặc định là ABOVE."
        )
        return
    
    symbol = args[0].upper()
    try:
        target = float(args[1])
    except ValueError:
        await update.message.reply_text("❌ Lỗi: Giá phải là một số. Ví dụ: /alert BTC 70000")
        return

    condition_aliases = {
        "ABOVE": "ABOVE",
        "UP": "ABOVE",
        "OVER": "ABOVE",
        "HIGHER": "ABOVE",
        "TREN": "ABOVE",
        "TRÊN": "ABOVE",
        "BELOW": "BELOW",
        "DOWN": "BELOW",
        "UNDER": "BELOW",
        "LOWER": "BELOW",
        "DUOI": "BELOW",
        "DƯỚI": "BELOW",
    }

    condition = "ABOVE"  # Default fallback
    if len(args) > 2:
        raw_condition = args[2].upper()
        condition = condition_aliases.get(raw_condition)
        if condition is None:
            await update.message.reply_text(
                "❌ Điều kiện không hợp lệ. Dùng ABOVE/BELOW (hoặc TREN/DUOI).\n"
                "Ví dụ: /alert BTC 70000 ABOVE"
            )
            return
    else:
        # Keep default behavior explicit for users.
        await update.message.reply_text("ℹ️ Bạn chưa nhập điều kiện, mình dùng mặc định: ABOVE")

    if db.add_alert(user_id, symbol, target, condition):
         await update.message.reply_text(f"✅ Cảnh báo được lưu!\n{symbol} → ${target}\nTôi sẽ thông báo cho bạn nếu giá thay đổi.")
    else:
         await update.message.reply_text("❌ Lỗi: Không thể lưu cảnh báo. Vui lòng thử lại.")

async def list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    alerts = db.get_user_alerts(user_id)
    if not alerts:
        await update.message.reply_text("📭 Bạn chưa có cảnh báo nào. Dùng /alert để tạo cảnh báo mới!")
        return
    
    msg = "📋 Danh Sách Cảnh Báo Của Bạn:\n\n"
    for i, a in enumerate(alerts, 1):
        msg += f"{i}. {a['symbol']}: ${a['target_price']} ({a['condition']})\n"
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    logging.info(f"[User {user_id}] Message: {user_message}")
    
    # Detect language
    language = LanguageDetector.detect_language(user_message)
    logging.info(f"[User {user_id}] Detected language: {language}")
    
    # Log User Message
    if db.conn:
        db.log_message(user_id, user_message, "user")

    # Show thinking message
    await update.message.reply_text("⏳ Đang xử lý...")

    # LangGraph Config (Thread per user)
    config = {"configurable": {"thread_id": user_id}}
    
    # Build conversation window (capped at _MAX_HISTORY to prevent unbounded growth).
    # We maintain history here instead of relying on MemorySaver operator.add
    # accumulation, which would cause the state to grow without bound.
    history = _user_message_history.get(user_id, [])
    history = history[-(  _MAX_HISTORY - 1):]  # make room for new message
    history = history + [{"role": "user", "content": user_message}]
    _user_message_history[user_id] = history

    initial_state = {
        "messages": history,
        "user_id": user_id,
        "language": language,
        "chart_image": None,
        "final_response": "",
    }

    try:
        # Use ainvoke (async LangGraph) directly on PTB's event loop.
        # asyncio.to_thread(app.invoke) was broken: app.invoke() internally calls
        # asyncio.get_event_loop().run_until_complete() — calling run_until_complete
        # on an already-running loop (PTB's loop) raises RuntimeError and crashes.
        # ainvoke() uses LangGraph's native async runner; sync nodes are wrapped
        # in run_in_executor automatically so they don't block the event loop.
        start_time = time.time()
        logging.info(f"[User {user_id}] Invoking LangGraph with state: {list(initial_state.keys())}")
        result = await app.ainvoke(initial_state, config)
        elapsed_ms = (time.time() - start_time) * 1000
        
        logging.info(f"[User {user_id}] LangGraph result keys: {list(result.keys())}")
        
        response_text = result.get("final_response", 
                                   "Xin lỗi, tôi không thể xử lý yêu cầu của bạn.")
        response_text = clean_markdown(response_text)
        
        logging.info(f"[User {user_id}] Response: {response_text[:100]}...")
        
        # Save interaction for demo purposes
        save_interaction(
            user_id=user_id,
            user_message=user_message,
            intent=result.get("intent", "unknown"),
            symbol=result.get("symbol"),
            language=language,
            market_data=result.get("market_data", {}),
            final_response=response_text,
            processing_time_ms=elapsed_ms,
        )
        
        # Log Bot Response
        if db.conn:
            db.log_message(user_id, response_text, "bot")
            
            # If analysis was performed, we could log that too specifically
            if result.get("intent") == "analysis" and result.get("market_data"):
                data = result["market_data"]
                db.save_analysis(
                    symbol=data.get("symbol", "UNKNOWN"),
                    price=data.get("current_price", 0),
                    prediction=response_text,
                    raw_data=data
                )

        # Send response text
        await update.message.reply_text(response_text)
        
        # Store bot reply in history so future turns have full context
        history = _user_message_history.get(user_id, [])
        history = history + [{"role": "assistant", "content": response_text}]
        _user_message_history[user_id] = history[-_MAX_HISTORY:]
        
        # Send chart image if available (from real Binance data)
        intent = result.get("intent", "")
        if result.get("chart_image") and intent in ["price", "analysis", "prediction"]:
            try:
                import io
                from base64 import b64decode
                
                # Decode base64 image
                chart_bytes = b64decode(result["chart_image"])
                chart_file = io.BytesIO(chart_bytes)
                
                symbol = result.get("symbol", initial_state.get("symbol", "Crypto"))
                
                # Different captions based on intent
                if intent == "analysis":
                    chart_caption = f"📊 Phân Tích Kỹ Thuật - {symbol}\n(Dữ liệu từ Binance)"
                elif intent == "prediction":
                    timeframe_info = result.get("timeframe_display", "1 giờ")
                    chart_caption = f"🔮 Dự Đoán Giá - {symbol}\n(Dự đoán cho {timeframe_info} tới)"
                else:  # price
                    chart_caption = f"💰 Giá Hiện Tại - {symbol}\n(Dữ liệu từ Binance)"
                
                await update.message.reply_photo(
                    photo=chart_file,
                    caption=chart_caption
                )
            except Exception as e:
                logging.error(f"Error sending chart image: {e}")
        
        # Also generate and send market overview chart if requested
        if result.get("intent") in ["market_overview", "top_coins"]:
            try:
                from src.tools.visualization import BinanceChartGenerator
                chart_gen = BinanceChartGenerator()
                overview_chart = chart_gen.generate_market_overview_from_binance(limit=10)
                
                if overview_chart:
                    import io
                    from base64 import b64decode
                    
                    chart_bytes = b64decode(overview_chart)
                    chart_file = io.BytesIO(chart_bytes)
                    
                    chart_caption = "📈 Top 10 Tiền Điện Tử (Theo Khối Lượng\nDữ liệu từ Binance)"
                    
                    await update.message.reply_photo(
                        photo=chart_file,
                        caption=chart_caption
                    )
            except Exception as e:
                logging.error(f"Error sending market overview chart: {e}")

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logging.error(f"[User {user_id}] Error processing message: {error_msg}")
        print(f"[ERROR] {error_msg}") # Print to console for user visibility
        
        error_response = "❌ Lỗi: Không thể xử lý câu hỏi của bạn lúc này. Vui lòng thử lại hoặc hỏi về đồng tiền khác."
        await update.message.reply_text(error_response)

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export 3 years of OHLCV data to CSV"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 1:
        await update.message.reply_text("ℹ️ Sử dụng: /export <SYMBOL>\nVí dụ: /export BTC\n\nTôi sẽ xuất toàn bộ dữ liệu lịch sử ra file CSV.")
        return
    
    symbol = args[0].upper()
    
    # Send processing message
    processing_msg = await update.message.reply_text(f"📥 Đang tải dữ liệu {symbol}... (có thể mất vài giây)")
    
    try:
        market_tools = MarketTools()
        
        # Fetch daily data
        # Binance API limit is 1000 per request
        # _fetch_ohlcv returns (DataFrame, symbol_string) — NOT (data, error)
        df, pair = market_tools._fetch_ohlcv(symbol, timeframe='1d', limit=1000)
        
        if df is None:
            await processing_msg.edit_text(f"❌ Không tìm thấy coin {symbol}. Kiểm tra lại ký hiệu?")
            return
        
        # Create exports directory if not exists
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Sort by timestamp ascending
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Create filename with symbol and date
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{export_dir}/{symbol}_{timestamp_str}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        # Prepare response message
        msg = f"✅ Xuất dữ liệu thành công!\n\n"
        msg += f"Đồng tiền: {symbol}\n"
        msg += f"Số bản ghi: {len(df)}\n"
        msg += f"Từ: {df['timestamp'].min().strftime('%d/%m/%Y')}\n"
        msg += f"Đến: {df['timestamp'].max().strftime('%d/%m/%Y')}\n"
        msg += f"📂 Tệp: {filename}\n\n"
        msg += "Dữ liệu gồm: Mở cửa, Cao, Thấp, Đóng cửa, Khối lượng"
        
        await processing_msg.edit_text(msg)
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logging.error(f"Export error: {error_msg}")
        await processing_msg.edit_text(f"❌ Lỗi: Không thể xuất dữ liệu. Vui lòng thử lại.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler — logs cleanly instead of spewing tracebacks."""
    error = context.error
    if isinstance(error, Conflict):
        logging.critical(
            "[409 Conflict] Another bot instance is polling Telegram. "
            "Stop the duplicate process and restart this one."
        )
        # Don't re-raise — let PTB retry polling; the other instance
        # will eventually time-out and this one will take over.
        return
    logging.error(f"Unhandled exception: {error}", exc_info=error)


if __name__ == '__main__':
    if not Config.TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found in .env")
        exit(1)

    _acquire_pid_lock()

    application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
    application.add_error_handler(error_handler)
    
    # --- Handlers ---
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('alert', set_alert))
    application.add_handler(CommandHandler('alerts', list_alerts))
    application.add_handler(CommandHandler('export', export_data))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # --- Alert Scheduler (via PTB JobQueue — runs on PTB's own event loop) ---
    # Using PTB's JobQueue instead of APScheduler avoids cross-event-loop issues
    # where asyncio.run() in a worker thread corrupts PTB's httpx client state.
    alert_manager = AlertManager(db, application)

    async def check_alerts_job(context: ContextTypes.DEFAULT_TYPE):
        """PTB job callback — runs on PTB's event loop, safe to await."""
        try:
            await alert_manager.check_alerts()
        except Exception as e:
            logging.error(f"Alert job error: {e}")

    # Schedule: first run 15s after start, then every 60s
    application.job_queue.run_repeating(check_alerts_job, interval=60, first=15)
    print("[OK] Alert Scheduler started.")

    print("Bot is running...")

    # Run with error handling for network issues
    try:
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        application.run_polling(
            # Long-poll timeout: Telegram waits this many seconds for a new update.
            timeout=60,
            read_timeout=60,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=30,
            bootstrap_retries=5,
            # Discard updates that piled up while the bot was offline.
            # This also helps clear a stale Telegram session after a crash.
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
    except Exception as e:
        print(f"[ERROR] Bot polling failed: {e}")
        raise
    finally:
        _release_pid_lock()
