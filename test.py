import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import secmail


class UserDatabase:
    def __init__(self, db_name='user_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    email TEXT NOT NULL
                )
            ''')

    def add_user(self, chat_id, email):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (chat_id, email) VALUES (?, ?)', (chat_id, str(email)))

    def get_user_email(self, chat_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT email FROM users WHERE chat_id=?', (chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    def update_user_email(self, chat_id, new_email):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET email=? WHERE chat_id=?', (str(new_email), chat_id))
    def get_user_by_id(self, id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE chat_id=?', (id,))
            result = cursor.fetchone()
            return result[0] if result else None
        
    def remove_user(self, id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM users WHERE chat_id=?', (id,))
            

    def close(self):
        self.conn.close()


API_TOKEN = '6687469087:AAGbjmlFZvlpQOU7gDUWdIOLe-ltQ-RUQec'  # Получите токен бота от @BotFather
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_db = UserDatabase()

admin_id = 6918756613


async def is_admin(user_id):
    # Replace this with your logic to check if the user is an administrator
    # For example, you can compare the user_id with a list of admin user IDs
    admins = [6918756613]  # Replace with your admin user IDs
    return user_id in admins


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ... (your existing code)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.from_user.id
    print(chat_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buy_access_button = KeyboardButton('💰Купить доступ💰')
    markup.add(buy_access_button)
    # Check if the user is in the database
    if user_db.get_user_by_id(chat_id) is None:
        

        await message.answer(
            f"Привет {message.from_user.username}! Это бот создан, чтобы помочь вам избежать утечки данных в сеть! "
            f"Этот бот дает вам возможность использовать анонимную временную почту прямо в боте! "
            f"Первые 24 часа бесплатно. "
            f"Чтобы использовать бота, введите команду /get_email. "
            f"Чтобы использовать бесплатно, напишите разработчику @DevElantru",
            reply_markup=markup
        )
    else:
        await message.answer("Спасибо, что купили доступ к боту! =)", reply_markup = markup)

# ... (your existing code)
@dp.message_handler(lambda message: message.text == '💰Купить доступ💰')
async def buy_access(message: types.Message):
    print(user_db.get_user_by_id(message.from_user.id))
    if user_db.get_user_by_id(message.from_user.id) is None:
        chat_id = message.from_user.id
        username = message.from_user.username
        user_info = f"User ID: {chat_id}\nUsername: {username}"

        await bot.send_message(admin_id, f"Пользователь {username} ({chat_id}) хочет купить доступ.\n\n{user_info}")
        await message.answer(f"Для покупки доступа обратитесь к админу: @DevElantru")
    else:       
        await message.answer(f"Спасибо, что купили доступ к боту! =)")


@dp.message_handler(commands=['get_email'])
async def get_email(message: types.Message):
    chat_id = message.from_user.id
    print(user_db.get_user_by_id(chat_id))

    # Check if the user is in the database
    if user_db.get_user_by_id(chat_id) is None:
        await message.answer("❌ Вы не купили доступ к боту! @Elantru ❌")
        return
    else:
        await message.answer("Спасибо что купил доступ к боту=)")

    email = client.random_email(amount=1)[0]
    user_db.update_user_email(chat_id, email)
    await message.answer(f"✉️Ваша временная потча: {email}                   чтобы посмотреть ящик этой почты введите команду /check")


@dp.message_handler(commands=['add_user'])
async def add_user(message: types.Message):
    chat_id = message.from_user.id

    # Check if the user is an administrator
    if not await is_admin(chat_id):
        await message.answer("❗️Доступ запрещен. Вы не администратор❗️")
        return

    # Extract user_id from the message text
    try:
        user_id = int(message.text.split()[1])
        user_db.add_user(user_id, "")
        await message.answer(f"Пользаватель {user_id} добавлен")
    except (IndexError, ValueError):
        await message.answer("Недопустимая команда. Пожалуйста, укажите действительный идентификатор пользователя.")
@dp.message_handler(commands=['remove_user'])
async def remove_user(message: types.Message):
    chat_id = message.from_user.id

    # Check if the user is an administrator
    if not await is_admin(chat_id):
        await message.answer("❗️Доступ запрещен. Вы не администратор❗️")
        return

    # Extract user_id from the message text
    user_id = int(message.text.split()[1])
    user_db.remove_user(user_id)
    await message.answer(f"Пользаватель {user_id} удален.")


@dp.message_handler(commands=['check'])
async def get_email(message: types.Message):
    chat_id = message.chat.id
    email = user_db.get_user_email(chat_id)
    print(email)

    inbox = client.get_inbox(str(email))
    formatted_messages = ""

    if not inbox:
        # Если в почтовом ящике нет сообщений
        await bot.send_message(chat_id, "В почтовом ящике нет сообщений.")
    else:
        for msg in inbox:
            formatted_messages += f"Айди: {msg.id}\n"
            formatted_messages += f"От: {msg.from_address}\n"
            message = client.get_message(address=email, message_id=msg.id)
            msgBody = message.body
            msgBody = msgBody[15:-7]
            formatted_messages += f"Тема сообщения: {msgBody}\n"
            formatted_messages += f"Сообщение: {msg.subject}\n"
            formatted_messages += f"Дата отправки (МСК): {msg.date}\n\n"

        # Отправка сформированного сообщения в бота
        await bot.send_message(chat_id, formatted_messages)


if __name__ == '__main__':
    client = secmail.Client()
    from aiogram import executor

    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        user_db.close()
