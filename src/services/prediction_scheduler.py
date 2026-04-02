"""
Prediction Scheduler - Automatically checks predictions and notifies users
Runs in the background and validates predictions when they're ready
"""

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.services.prediction_tracker import PredictionTracker
from src.db.postgres import Database

logger = logging.getLogger(__name__)

class PredictionScheduler:
    """
    Background scheduler that:
    1. Checks pending predictions periodically
    2. Fetches actual prices when prediction time expires
    3. Compares with predicted prices
    4. Stores results in database
    """
    
    def __init__(self):
        self.tracker = PredictionTracker()
        self.db = Database()
        self.scheduler = BackgroundScheduler()
        self.pending_notifications = {}  # Store notifications to send
    
    def start(self):
        """Start the background scheduler"""
        try:
            # Check every minute for predictions ready to validate
            self.scheduler.add_job(
                self.check_predictions_job,
                IntervalTrigger(minutes=1),
                id="check_predictions",
                name="Check Pending Predictions",
                replace_existing=True,
                misfire_grace_time=30
            )
            
            self.scheduler.start()
            logger.info("Prediction scheduler started - checking every minute")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the background scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Prediction scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def check_predictions_job(self):
        """Job that runs periodically to check predictions"""
        try:
            logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Checking pending predictions...")
            
            # Get all pending predictions ready to check
            pending = self.tracker.check_pending_predictions()
            
            if not pending:
                logger.debug("No pending predictions to check")
                return
            
            logger.info(f"Found {len(pending)} predictions ready to validate")
            
            # Validate each prediction
            for pred in pending:
                try:
                    result = asyncio.run(
                        self.tracker.validate_prediction(pred['id'], pred['symbol'])
                    )
                    
                    if result:
                        # Store notification for later sending via Telegram
                        user_id = pred['user_id']
                        if user_id not in self.pending_notifications:
                            self.pending_notifications[user_id] = []
                        
                        self.pending_notifications[user_id].append(result)
                        
                        logger.info(
                            f"Validated prediction {pred['id']}: "
                            f"{pred['symbol']} - "
                            f"Expected {result['predicted_direction']}, "
                            f"Got {result['actual_direction']} "
                            f"({result['percentage_change']:+.2f}%)"
                        )
                
                except Exception as e:
                    logger.error(f"Error validating prediction {pred['id']}: {e}")
        
        except Exception as e:
            logger.error(f"Error in check_predictions_job: {e}")
    
    def get_pending_notifications(self, user_id: int) -> list:
        """
        Get pending notifications for a user and clear them.
        Should be called when sending messages to user.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            List of prediction results ready to notify
        """
        notifications = self.pending_notifications.get(user_id, [])
        if user_id in self.pending_notifications:
            del self.pending_notifications[user_id]
        return notifications
    
    def has_pending_notifications(self, user_id: int) -> bool:
        """Check if user has pending notifications"""
        return user_id in self.pending_notifications and len(self.pending_notifications[user_id]) > 0


# Helper functions for integration with main bot

def start_prediction_scheduler():
    """Initialize and start the prediction scheduler"""
    scheduler = PredictionScheduler()
    scheduler.start()
    return scheduler

async def check_and_notify_predictions(app, user_id: int, scheduler: PredictionScheduler):
    """
    Check if user has pending prediction results and send notifications.
    
    Args:
        app: Telegram Application
        user_id: User's Telegram ID
        scheduler: PredictionScheduler instance
    """
    try:
        notifications = scheduler.get_pending_notifications(user_id)
        
        if not notifications:
            return
        
        for result in notifications:
            message = scheduler.tracker.format_prediction_result(result)
            try:
                await app.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Sent prediction notification to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending notification to {user_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in check_and_notify_predictions: {e}")
