import asyncio
from src.db.postgres import Database
from src.tools.market import MarketTools
from telegram.ext import Application

class AlertManager:
    def __init__(self, db: Database, bot_application: Application):
        self.db = db
        self.app = bot_application
        self.market_tools = MarketTools()

    async def check_alerts(self):
        """
        Scheduled task to check active alerts against current market prices.
        """
        print("--- Checking Alerts ---")
        alerts = self.db.get_active_alerts()
        if not alerts:
            print("No active alerts.")
            return

        # 1. Get unique symbols to minimize API calls
        unique_symbols = list(set([a['symbol'] for a in alerts]))
        
        # 2. Fetch current prices
        current_prices = {}
        for symbol in unique_symbols:
            price, _ = self.market_tools._fetch_ticker(symbol)
            if price:
                current_prices[symbol] = price
        
        # 3. Check conditions
        for alert in alerts:
            symbol = alert['symbol']
            target = float(alert['target_price'])
            condition = alert['condition'] # 'ABOVE' or 'BELOW'
            user_id = alert['user_id']
            alert_id = alert['id']
            
            current = current_prices.get(symbol)
            if current is None:
                continue
            
            triggered = False
            if condition == 'ABOVE' and current >= target:
                triggered = True
            elif condition == 'BELOW' and current <= target:
                triggered = True
            
            if triggered:
                await self.trigger_alert(user_id, symbol, target, current, condition, alert_id)

    async def trigger_alert(self, user_id, symbol, target, current, condition, alert_id):
        """
        Sends notification to user and deactivates the alert.
        """
        message = (
            f"🚨 PRICE ALERT 🚨\n\n"
            f"{symbol} has reached your target!\n"
            f"Target: {target}\n"
            f"Current: {current}\n"
            f"Condition: {condition}\n"
        )
        
        try:
            print(f"Triggering alert {alert_id} for user {user_id}")
            await self.app.bot.send_message(chat_id=user_id, text=message)
            # Deactivate after firing
            self.db.deactivate_alert(alert_id)
        except Exception as e:
            print(f"Failed to send alert to {user_id}: {e}")
            # If the chat doesn't exist (user never started the bot, or blocked it),
            # deactivate to stop retrying every minute.
            error_str = str(e).lower()
            if "chat not found" in error_str or "user not found" in error_str or "blocked" in error_str:
                print(f"Deactivating unreachable alert {alert_id} for user {user_id}")
                self.db.deactivate_alert(alert_id)
