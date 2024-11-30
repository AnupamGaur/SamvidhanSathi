from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
from datetime import datetime
import pandas as pd

class UserTracker:
    def __init__(self, db_name="bot_users.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                is_premium BOOLEAN,
                is_bot BOOLEAN,
                first_seen TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_content TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        self.conn.commit()
    
    def update_user(self, user):
        cursor = self.conn.cursor()
        now = datetime.now()
        
        # Update or insert user data
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, language_code, 
             is_premium, is_bot, first_seen, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 
                COALESCE((SELECT first_seen FROM users WHERE user_id = ?), ?),
                ?)
        ''', (user.id, user.username, user.first_name, user.last_name, 
              user.language_code, user.is_premium, user.is_bot, 
              user.id, now, now))
        self.conn.commit()
    
    def log_interaction(self, user_id, content):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO interactions (user_id, message_content, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, content, datetime.now()))
        self.conn.commit()

    def view_data(self):
        # Read data using pandas
        users_df = pd.read_sql_query("SELECT * FROM users", self.conn)
        interactions_df = pd.read_sql_query("SELECT * FROM interactions", self.conn)
        
        print("\n=== User Statistics ===")
        print(f"Total Users: {len(users_df)}")
        print("\nPremium Users:", len(users_df[users_df['is_premium'] == True]))
        print("\nTop Languages:")
        print(users_df['language_code'].value_counts())
        
        print("\n=== Recent Interactions ===")
        recent = interactions_df.merge(users_df[['user_id', 'username']], on='user_id')
        print(recent[['username', 'message_content', 'timestamp']].tail())

    def clear_all_(self):
        cursor = self.conn.cursor
        cursor.execute('''
        DELETE * from interactions 
                       ''')
        self.conn.commit()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    
    # Update user data
    tracker.update_user(user)
    
    # Log interaction
    # message_type = 'text'
    # if message.photo:
    #     message_type = 'photo'
    # elif message.voice:
    #     message_type = 'voice'
    # elif message.document:
    #     message_type = 'document'
    
    # content = message.text if message.text else f"{message_type} received"
    content = message.text
    tracker.log_interaction(user.id, content)

# Initialize bot and tracker
tracker = UserTracker()
# app = Application.builder().token("7559444556:AAGyexweSY_q0vaf3urds2FrsdUU-Mn1h-Q").build()

# Add message handler for all updates
# app.add_handler(MessageHandler(filters.ALL, handle_message))

# Run bot
# if __name__ == "__main__":
#     app.run_polling()

# To view data, run this in a separate script:
"""
from bot_script import UserTracker
tracker = UserTracker()
tracker.view_data()
"""