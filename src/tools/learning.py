#!/usr/bin/env python
"""
Smart Question Learning System
Initialize learning database & create helper functions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import psycopg2
from src.config import Config

class QuestionLearningSystem:
    """Track repeated questions and provide learning context"""
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            self.conn.autocommit = True
            self.init_learning_db()
        except Exception as e:
            print(f"Learning system connection failed: {e}")
            self.conn = None
    
    def init_learning_db(self):
        """Create table for tracking question patterns"""
        if not self.conn:
            return
        
        with self.conn.cursor() as cur:
            # Table for tracking question frequency and patterns
            cur.execute("""
                CREATE TABLE IF NOT EXISTS question_learning (
                    id SERIAL PRIMARY KEY,
                    question_hash VARCHAR(100) UNIQUE,
                    original_question TEXT,
                    frequency INTEGER DEFAULT 1,
                    category VARCHAR(50),
                    is_learning_question BOOLEAN DEFAULT FALSE,
                    improved_prompt TEXT,
                    last_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_question UNIQUE(question_hash)
                );
            """)
    
    def find_similar_questions(self, user_question, similarity_threshold=0.70):
        """Find similar past questions from conversation history"""
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor() as cur:
                # Get recent similar questions from conversations
                cur.execute("""
                    SELECT message, timestamp FROM conversations 
                    WHERE role = 'user' 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """)
                past_questions = cur.fetchall()
            
            from difflib import SequenceMatcher
            
            similar = []
            for past_msg, timestamp in past_questions:
                ratio = SequenceMatcher(None, 
                                       user_question.lower(), 
                                       past_msg.lower()).ratio()
                
                if ratio > similarity_threshold:
                    similar.append({
                        'question': past_msg,
                        'similarity': ratio,
                        'timestamp': timestamp
                    })
            
            return sorted(similar, key=lambda x: -x['similarity'])[:3]  # Top 3
        
        except Exception as e:
            print(f"Error finding similar questions: {e}")
            return []
    
    def get_question_frequency(self, user_question):
        """Get how many times this question (or similar) has been asked"""
        if not self.conn:
            return 0
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE role = 'user' AND 
                    LOWER(message) ILIKE %s
                """, (f"%{user_question.strip().lower()}%",))
                
                count = cur.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error getting question frequency: {e}")
            return 0
    
    def get_learning_context(self, user_question):
        """
        Get learning context for a question.
        Returns info about: is it repeated? how many times? similar questions?
        """
        frequency = self.get_question_frequency(user_question)
        similar = self.find_similar_questions(user_question)
        
        context = {
            'is_repeated': frequency > 1,
            'frequency': frequency,
            'similar_questions': similar,
            'should_enhance': frequency > 2  # If asked 3+ times, enhance response
        }
        
        return context
    
    def build_enhanced_prompt(self, base_prompt, learning_context):
        """
        Enhance the base prompt with learning context.
        Make bot give better answers for repeated questions.
        """
        if not learning_context['should_enhance']:
            return base_prompt
        
        frequency = learning_context['frequency']
        
        enhancement = f"""
[LEARNING NOTE: This question has been asked {frequency} times before.
The user clearly cares about this topic. Provide a comprehensive, detailed answer.
Include examples and explain clearly.]
"""
        
        return base_prompt + enhancement
    
    def log_question_learning(self, question, frequency, category):
        """Log that we've learned about this question type"""
        if not self.conn:
            return
        
        try:
            import hashlib
            q_hash = hashlib.md5(question.lower().encode()).hexdigest()[:20]
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO question_learning 
                    (question_hash, original_question, frequency, category, is_learning_question)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (question_hash) DO UPDATE SET
                    frequency = question_learning.frequency + 1,
                    last_asked = CURRENT_TIMESTAMP
                """, (q_hash, question, frequency, category, frequency > 2))
        except Exception as e:
            print(f"Error logging question learning: {e}")
    
    def close(self):
        if self.conn:
            self.conn.close()


# Test the system
if __name__ == "__main__":
    print("🎓 Initializing Question Learning System...")
    
    system = QuestionLearningSystem()
    
    if system.conn:
        # Test with a common question
        test_q = "giá btc"
        
        print(f"\n📊 Learning Analysis for: '{test_q}'")
        print("-" * 60)
        
        context = system.get_learning_context(test_q)
        
        print(f"Is repeated: {context['is_repeated']}")
        print(f"Times asked: {context['frequency']}")
        print(f"Should enhance: {context['should_enhance']}")
        
        if context['similar_questions']:
            print(f"\nSimilar past questions:")
            for sim in context['similar_questions']:
                print(f"  - {sim['question']} (Match: {sim['similarity']:.0%})")
        
        print("\n✅ Learning system ready!")
        
        system.close()
    else:
        print("❌ Could not connect to database")
