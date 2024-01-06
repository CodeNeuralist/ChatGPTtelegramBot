import sqlite3

class Database:
    CREATE_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        registration_date TEXT,
        remaining_tokens INTEGER,
        is_banned INTEGER DEFAULT 0
    )'''

    SELECT_USER_SQL = 'SELECT * FROM users WHERE user_id = ?'

    INSERT_USER_SQL = '''INSERT INTO users (user_id, username, registration_date, remaining_tokens)
                        VALUES (?, ?, ?, ?)'''

    UPDATE_TOKENS_SQL = 'UPDATE users SET remaining_tokens = ? WHERE user_id = ?'

    BAN_USER_SQL = 'UPDATE users SET is_banned = 1 WHERE user_id = ?'

    UNBAN_USER_SQL = 'UPDATE users SET is_banned = 0 WHERE user_id = ?'

    SELECT_ALL_USERS_SQL = 'SELECT * FROM users'

    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(self.CREATE_TABLE_SQL)
        self.conn.commit()
    
    def deduct_token(self, user_id):
        user = self.get_user(user_id)
        if user:
            remaining_tokens = user[4]
            if remaining_tokens > 0:
                remaining_tokens -= 1
                self.update_tokens(user_id, remaining_tokens)
                return True
        return False

    def user_exists(self, user_id):
        self.cur.execute(self.SELECT_USER_SQL, (user_id,))
        user = self.cur.fetchone()
        return user is not None

    def insert_user(self, user_id, username, registration_date, remaining_tokens):
        if self.user_exists(user_id):
            pass
        else:
            self.cur.execute(self.INSERT_USER_SQL, (user_id, username, registration_date, remaining_tokens))
        self.conn.commit()

    def get_user(self, user_id):
        self.cur.execute(self.SELECT_USER_SQL, (user_id,))
        user = self.cur.fetchone()
        return user

    def update_tokens(self, user_id, remaining_tokens):
        self.cur.execute(self.UPDATE_TOKENS_SQL, (remaining_tokens, user_id))
        self.conn.commit()

    def ban_user(self, user_id):
        self.cur.execute(self.BAN_USER_SQL, (user_id,))
        self.conn.commit()

    def unban_user(self, user_id):
        self.cur.execute(self.UNBAN_USER_SQL, (user_id,))
        self.conn.commit()

    def get_all_users(self):
        self.cur.execute(self.SELECT_ALL_USERS_SQL)
        users = self.cur.fetchall()
        return users

    def close(self):
        self.conn.close()