import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('chat.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                               (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, salt TEXT, permissions INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats 
                               (id INTEGER PRIMARY KEY, name TEXT, permissions INTEGER)''')
        self.conn.commit()

    def add_user(self, username, password, salt, permissions):
        self.cursor.execute('INSERT INTO users (username, password, salt, permissions) VALUES (?, ?, ?, ?)', 
                            (username, password, salt, permissions))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def get_chats_for_user(self, permissions):
        self.cursor.execute('SELECT * FROM chats WHERE permissions <= ?', (permissions,))
        return self.cursor.fetchall()

    def save_message(self, chat_id, username, message):
        # Здесь нужно реализовать сохранение сообщений в базу данных
        pass
