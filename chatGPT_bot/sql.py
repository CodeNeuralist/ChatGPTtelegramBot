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
