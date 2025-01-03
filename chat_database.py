# Developer: Eric Neftali Paiz
import sqlite3
import json
from datetime import datetime, timedelta

class ChatDatabase:
    def __init__(self, db_name='chat_data.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create chatrooms table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS chatrooms (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        ''')

        # Create users table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            badges TEXT
        )
        ''')

        # Create messages table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chatroom_id INTEGER,
            user_id INTEGER,
            content TEXT,
            type TEXT,
            created_at TEXT,
            FOREIGN KEY (chatroom_id) REFERENCES chatrooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        # Create streamers table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS streamers (
            name TEXT PRIMARY KEY,
            channel_id INTEGER
        )
        ''')

        self.conn.commit()

    def insert_chatroom(self, chatroom_id):
        self.c.execute('''
        INSERT OR IGNORE INTO chatrooms (id) VALUES (?)
        ''', (chatroom_id,))
        self.conn.commit()

    def insert_user(self, user_id, username, badges):
        self.c.execute('''
        INSERT OR IGNORE INTO users (id, username, badges) VALUES (?, ?, ?)
        ''', (user_id, username, json.dumps(badges)))
        self.conn.commit()

    def insert_message(self, message_id, chatroom_id, user_id, content, message_type, created_at):
        self.c.execute('''
        INSERT OR REPLACE INTO messages (id, chatroom_id, user_id, content, type, created_at) VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, chatroom_id, user_id, content, message_type, created_at))
        self.conn.commit()

    def insert_streamer(self, streamer_name, channel_id):
        self.c.execute('''
        INSERT OR REPLACE INTO streamers (name, channel_id) VALUES (?, ?)
        ''', (streamer_name.lower(), channel_id))
        self.conn.commit()

    def get_channel_id(self, streamer_name):
        self.c.execute('''
        SELECT channel_id FROM streamers WHERE name = ?
        ''', (streamer_name.lower(),))
        result = self.c.fetchone()
        return result[0] if result else None

    def delete_old_messages(self, days=30):
        thirty_days_ago = (datetime.now() - timedelta(days=days)).isoformat()
        self.c.execute('''
        DELETE FROM messages WHERE created_at < ?
        ''', (thirty_days_ago,))
        self.conn.commit()

    def close(self):
        self.conn.close()
