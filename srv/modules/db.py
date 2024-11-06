import sqlite3
from modules.utils import Utils

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('chat.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                               (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, salt TEXT, permissions INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats 
                               (id INTEGER PRIMARY KEY, name TEXT UNIQUE, permissions INTEGER, status TEXT)''')
        self.conn.commit()

    def add_user(self, username, password, salt, permissions):
        self.cursor.execute('INSERT INTO users (username, password, salt, permissions) VALUES (?, ?, ?, ?)', 
                            (username, password, salt, permissions))
        self.conn.commit()

    def add_chat(self, chatname, permissions, status):
        self.cursor.execute('INSERT INTO chats (name, permissions, status) VALUES (?,?,?)', (chatname, permissions, status,))        
        self.conn.commit
    
    def change_user_perm(self, username, new_permissions):
        self.cursor.execute('UPDATE users SET permissions = ? WHERE username = ?', (new_permissions, username))
        self.conn.commit()

    def change_chat_perm(self, chatid,  new_permissions):
        self.cursor.execute('UPDATE chats SET permissions = ? WHERE id = ?', (new_permissions, chatid))
        self.conn.commit() 

    def change_chat_stat(self, chatid, new_status):
        self.cursor.execute('UPDATE chats SET status = ? WHERE id = ?', (new_status, chatid))
        self.conn.commit() 

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()
    
    def get_chat(self, chatname):
        self.cursor.execute('SELECT * FROM chats WHERE name = ?', (chatname,))
        return self.cursor.fetchone()

    def get_user_adm(self):
        self.cursor.execute('SELECT * FROM users WHERE permissions = 4')
        return self.cursor.fetchall()

    def get_chats_for_user(self, permissions):
        self.cursor.execute('SELECT * FROM chats WHERE permissions <= ? AND status = "Online" ', (permissions,))
        return self.cursor.fetchall()

    def get_all_chats(self):
        self.cursor.execute('SELECT * FROM chats')
        return self.cursor.fetchall()
    
    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def save_message(self, chat_id, username, message):
        # Здесь нужно реализовать сохранение сообщений в базу данных
        logger = Utils.setup_chat_logger(chat_id)
        logger.info(f"User [{username}] sent message to chat {chat_id}: {message}")
        return