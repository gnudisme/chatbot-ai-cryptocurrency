import psycopg2
from psycopg2.extras import RealDictCursor
import json
from src.config import Config

class Database:
    def __init__(self):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            self.conn.autocommit = True
            self.init_db()
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.conn = None

    def init_db(self):
        if not self.conn: return
        with self.conn.cursor() as cur:
            # Table for Users
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences JSONB DEFAULT '{}'
                );
            """)

            # Table for conversation logs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    message TEXT,
                    role VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Table for analysis results
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20),
                    price DECIMAL,
                    prediction TEXT,
                    raw_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Alerts
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    symbol VARCHAR(20),
                    target_price DECIMAL,
                    condition VARCHAR(10), -- 'ABOVE' or 'BELOW'
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Table for Prediction Tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prediction_tracking (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    symbol VARCHAR(20),
                    predicted_price DECIMAL,
                    predicted_direction VARCHAR(20), -- 'UP', 'DOWN', or specific range
                    timeframe_minutes INTEGER, -- Duration in minutes
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    check_at TIMESTAMP,
                    actual_price DECIMAL,
                    actual_direction VARCHAR(20),
                    price_change DECIMAL,
                    percentage_change DECIMAL,
                    accuracy BOOLEAN,
                    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'COMPLETED', 'CANCELLED'
                    notes JSONB,
                    CHECK (status IN ('PENDING', 'COMPLETED', 'CANCELLED'))
                );
            """)

    def log_message(self, user_id, message, role):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO conversations (user_id, message, role) VALUES (%s, %s, %s)",
                    (user_id, message, role)
                )
        except Exception as e:
            print(f"Error logging message: {e}")

    def save_analysis(self, symbol, price, prediction, raw_data):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO analysis_results (symbol, price, prediction, raw_data) VALUES (%s, %s, %s, %s)",
                    (symbol, price, prediction, json.dumps(raw_data))
                )
        except Exception as e:
            print(f"Error saving analysis: {e}")

    def get_history(self, user_id, limit=5):
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT message, role FROM conversations WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
                    (user_id, limit)
                )
                rows = cur.fetchall()
                return rows[::-1] # Return in chronological order
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    # --- User Management ---
    def register_user(self, user_id, username):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (user_id, username) 
                    VALUES (%s, %s) 
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (user_id, username)
                )
        except Exception as e:
            print(f"Error registering user: {e}")

    # --- Alert Management ---
    def add_alert(self, user_id, symbol, target_price, condition):
        if not self.conn: return False
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO alerts (user_id, symbol, target_price, condition)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, symbol.upper(), target_price, condition)
                )
            return True
        except Exception as e:
            print(f"Error adding alert: {e}")
            return False

    def get_active_alerts(self):
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM alerts WHERE is_active = TRUE")
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []

    def deactivate_alert(self, alert_id):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE alerts SET is_active = FALSE WHERE id = %s", (alert_id,))
        except Exception as e:
            print(f"Error deactivating alert: {e}")

    def get_user_alerts(self, user_id):
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM alerts WHERE user_id = %s AND is_active = TRUE", (user_id,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching user alerts: {e}")
            return []

    # --- Prediction Tracking ---
    def save_prediction(self, user_id, symbol, predicted_price, predicted_direction, timeframe_minutes, notes=None):
        """Save a new prediction to track"""
        if not self.conn: return None
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO prediction_tracking 
                    (user_id, symbol, predicted_price, predicted_direction, timeframe_minutes, check_at, notes, status)
                    VALUES (%s, %s, %s, %s, %s, NOW() + (%s || ' minutes')::INTERVAL, %s, 'PENDING')
                    RETURNING id
                    """,
                    (user_id, symbol.upper(), predicted_price, predicted_direction, timeframe_minutes, 
                     str(int(timeframe_minutes)), json.dumps(notes) if notes else None)
                )
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return None

    def get_pending_predictions(self, user_id=None):
        """Get predictions that are ready to be checked"""
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if user_id:
                    cur.execute(
                        """
                        SELECT * FROM prediction_tracking 
                        WHERE status = 'PENDING' AND check_at <= NOW() AND user_id = %s
                        ORDER BY check_at ASC
                        """,
                        (user_id,)
                    )
                else:
                    cur.execute(
                        """
                        SELECT * FROM prediction_tracking 
                        WHERE status = 'PENDING' AND check_at <= NOW()
                        ORDER BY check_at ASC
                        """
                    )
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching pending predictions: {e}")
            return []

    def get_prediction_by_id(self, prediction_id):
        """Get a single prediction by ID"""
        if not self.conn: return None
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM prediction_tracking WHERE id = %s",
                    (prediction_id,)
                )
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching prediction {prediction_id}: {e}")
            return None

    def update_prediction_result(self, prediction_id, actual_price, actual_direction):
        """Update prediction with actual price and calculate accuracy"""
        if not self.conn: return False
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE prediction_tracking 
                    SET 
                        actual_price = %s,
                        actual_direction = %s,
                        price_change = %s - predicted_price,
                        percentage_change = ((%s - predicted_price) / predicted_price * 100),
                        accuracy = (
                            CASE 
                                WHEN predicted_direction = %s THEN TRUE
                                ELSE FALSE
                            END
                        ),
                        status = 'COMPLETED'
                    WHERE id = %s
                    """,
                    (actual_price, actual_direction, actual_price, actual_price, actual_direction, prediction_id)
                )
            return True
        except Exception as e:
            print(f"Error updating prediction result: {e}")
            return False

    def get_prediction_history(self, user_id, limit=10):
        """Get user's prediction history"""
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM prediction_tracking 
                    WHERE user_id = %s AND status = 'COMPLETED'
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching prediction history: {e}")
            return []

    def get_prediction_accuracy(self, user_id):
        """Calculate prediction accuracy statistics for user"""
        if not self.conn: return {}
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT 
                        COUNT(*) as total_predictions,
                        SUM(CASE WHEN accuracy = TRUE THEN 1 ELSE 0 END) as correct_predictions,
                        AVG(CASE WHEN accuracy = TRUE THEN 1 ELSE 0 END) * 100 as accuracy_rate,
                        AVG(ABS(percentage_change)) as avg_error_percentage
                    FROM prediction_tracking 
                    WHERE user_id = %s AND status = 'COMPLETED'
                    """,
                    (user_id,)
                )
                result = cur.fetchone()
                return {
                    'total': result['total_predictions'] or 0,
                    'correct': result['correct_predictions'] or 0,
                    'accuracy_rate': result['accuracy_rate'] or 0,
                    'avg_error': result['avg_error_percentage'] or 0
                }
        except Exception as e:
            print(f"Error calculating accuracy: {e}")
            return {}