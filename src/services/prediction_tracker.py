"""
Prediction Tracker Service
Tracks crypto price predictions and validates them against actual prices
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from src.db.postgres import Database
from src.tools.market import MarketTools

logger = logging.getLogger(__name__)

class PredictionTracker:
    """
    Service to track predictions:
    1. Save predictions when users ask
    2. Monitor for prediction check times
    3. Fetch actual prices and compare
    4. Calculate accuracy metrics
    """
    
    def __init__(self):
        self.db = Database()
        self.market = MarketTools()
    
    def save_prediction(
        self, 
        user_id: int,
        symbol: str,
        predicted_price: float,
        predicted_direction: str,  # 'UP', 'DOWN', or 'RANGE_X_TO_Y'
        timeframe_minutes: int,
        additional_info: Optional[Dict] = None
    ) -> Optional[int]:
        """
        Save a new prediction to track.
        
        Args:
            user_id: Telegram user ID
            symbol: Crypto symbol (e.g., BTC, ETH)
            predicted_price: Predicted price
            predicted_direction: UP, DOWN, or specific range description
            timeframe_minutes: Minutes until prediction should be checked
            additional_info: Extra info (confidence, reasoning, etc.)
        
        Returns:
            Prediction ID if successful, None otherwise
        """
        try:
            pred_id = self.db.save_prediction(
                user_id=user_id,
                symbol=symbol,
                predicted_price=float(predicted_price),
                predicted_direction=predicted_direction,
                timeframe_minutes=timeframe_minutes,
                notes=additional_info
            )
            
            if pred_id:
                check_time = datetime.now() + timedelta(minutes=timeframe_minutes)
                logger.info(
                    f"Prediction saved: {symbol} → ${predicted_price} "
                    f"({predicted_direction}) in {timeframe_minutes}min "
                    f"(check at {check_time.strftime('%Y-%m-%d %H:%M:%S')})"
                )
            return pred_id
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def check_pending_predictions(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Check predictions that are ready for validation.
        Returns pending predictions without updating them.
        
        Args:
            user_id: Optional - check only this user's predictions
        
        Returns:
            List of pending predictions ready to check
        """
        try:
            pending = self.db.get_pending_predictions(user_id)
            logger.info(f"Found {len(pending)} pending predictions ready to check")
            return pending
        except Exception as e:
            logger.error(f"Error checking pending predictions: {e}")
            return []
    
    async def validate_prediction(self, prediction_id: int, symbol: str) -> Optional[Dict]:
        """
        Validate a single prediction by fetching actual price.
        
        Args:
            prediction_id: ID of prediction to validate
            symbol: Crypto symbol
        
        Returns:
            Result dict with comparison, or None if error
        """
        try:
            # Fetch current price
            actual_price, _ = self.market._fetch_ticker(symbol)
            
            if actual_price is None:
                logger.error(f"Could not fetch price for {symbol}")
                return None
            
            # Fetch the prediction to get predicted price
            pred = self.db.get_prediction_by_id(prediction_id)
            
            if not pred:
                logger.error(f"Prediction {prediction_id} not found")
                return None
            
            predicted_price = float(pred['predicted_price'])
            price_diff = actual_price - predicted_price
            
            # Determine actual direction
            if price_diff > 0:
                actual_direction = "UP"
            elif price_diff < 0:
                actual_direction = "DOWN"
            else:
                actual_direction = "NEUTRAL"
            
            # Update prediction
            success = self.db.update_prediction_result(prediction_id, actual_price, actual_direction)
            
            if success:
                result = {
                    'prediction_id': prediction_id,
                    'symbol': symbol,
                    'predicted_price': predicted_price,
                    'actual_price': actual_price,
                    'predicted_direction': pred['predicted_direction'],
                    'actual_direction': actual_direction,
                    'price_change': price_diff,
                    'percentage_change': (price_diff / predicted_price * 100) if predicted_price != 0 else 0,
                    'is_correct': pred['predicted_direction'] == actual_direction,
                    'created_at': pred['created_at'],
                    'checked_at': datetime.now()
                }
                return result
            
            return None
        except Exception as e:
            logger.error(f"Error validating prediction {prediction_id}: {e}")
            return None
    
    async def validate_all_pending(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Validate all pending predictions that are ready.
        
        Args:
            user_id: Optional - validate only this user's predictions
        
        Returns:
            List of validation results
        """
        pending = self.check_pending_predictions(user_id)
        results = []
        
        for pred in pending:
            result = await self.validate_prediction(pred['id'], pred['symbol'])
            if result:
                results.append(result)
        
        return results
    
    def get_user_prediction_stats(self, user_id: int) -> Dict:
        """
        Get prediction statistics for a user.
        
        Returns:
            Dict with accuracy rate, total predictions, etc.
        """
        try:
            history = self.db.get_prediction_history(user_id)
            stats = self.db.get_prediction_accuracy(user_id)
            
            return {
                'total_predictions': stats['total'],
                'correct_predictions': stats['correct'],
                'accuracy_rate': round(stats['accuracy_rate'], 2) if stats['accuracy_rate'] else 0,
                'avg_error_percentage': round(stats['avg_error'], 2) if stats['avg_error'] else 0,
                'recent_predictions': history[:5]
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def format_prediction_result(self, result: Dict) -> str:
        """
        Format prediction result as a readable message.
        
        Args:
            result: Result dict from validate_prediction
        
        Returns:
            Formatted message
        """
        symbol = result['symbol']
        pred_price = result['predicted_price']
        actual_price = result['actual_price']
        pred_dir = result['predicted_direction']
        actual_dir = result['actual_direction']
        pct_change = result['percentage_change']
        is_correct = result['is_correct']
        
        status_emoji = "✅" if is_correct else "❌"
        
        message = (
            f"{status_emoji} {symbol} Prediction Result\n\n"
            f"📊 Predicted: ${pred_price:.2f} ({pred_dir})\n"
            f"💹 Actual: ${actual_price:.2f} ({actual_dir})\n"
            f"📈 Change: {pct_change:+.2f}%\n"
        )
        
        if is_correct:
            message += f"\n🎯 Dự đoán CHÍNH XÁC!"
        else:
            message += f"\n❌ Dự đoán không chính xác"
        
        return message
    
    def get_prediction_summary_report(self, user_id: int) -> str:
        """
        Generate a summary report of user's predictions.
        
        Returns:
            Formatted report message
        """
        stats = self.get_user_prediction_stats(user_id)
        history = stats.get('recent_predictions', [])
        
        report = (
            f"📊 Báo Cáo Dự Đoán Của Bạn\n"
            f"{'=' * 40}\n"
            f"Total Predictions: {stats['total_predictions']}\n"
            f"Correct: {stats['correct_predictions']}\n"
            f"Accuracy Rate: {stats['accuracy_rate']:.1f}%\n"
            f"Avg Error: ±{stats['avg_error_percentage']:.2f}%\n\n"
        )
        
        if history:
            report += "📈 Recent Predictions:\n"
            for i, pred in enumerate(history, 1):
                status = "✅" if pred.get('accuracy') else "❌"
                report += (
                    f"{i}. {status} {pred['symbol']}: "
                    f"${pred['predicted_price']:.2f} → ${pred['actual_price']:.2f} "
                    f"({pred['percentage_change']:+.2f}%)\n"
                )
        
        return report
