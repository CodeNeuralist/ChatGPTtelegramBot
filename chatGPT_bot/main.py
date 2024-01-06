import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, types
import asyncio
import tabulate
import g4f
import db
from collections import deque
from functools import wraps
from language import *
from handlers import user_com
from aiogram import F

# Загрузка переменных окружения
load_dotenv()

# Выбор языка (здесь вы можете использовать "ru_strings" или "en_strings")
selected_language = ru_strings

# Инициализация Telegram-бота
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

logging.basicConfig(filename="bot.log", filemode="w", format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.INFO)

# Константы
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))
TOKENS_PER_DAY = 15

# Параметры ограничения по скорости
RATE_LIMIT_MESSAGES = 4  # Максимальное количество сообщений
RATE_LIMIT_PERIOD = 60  # Период времени (в секундах)

database = db.Database()



def is_user_banned(user_id):
    user = database.get_user(user_id)
    return user and user[5]

# Создание словаря для отслеживания количества сообщений для каждого пользователя
user_message_counts = {}

def rate_limit(limit: int, period: int):
    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id

            # Проверка, заблокирован ли пользователь
            if is_user_banned(user_id):
                await message.answer(selected_language['user_banned_message'])
                # Запись блокировки пользователя
                log_message = f"Пользователь {message.from_user.username} (ID: {user_id}) заблокирован из-за превышения ограничения по скорости."
                logging.info(log_message)
                # Уведомление администратора о блокировке пользователя
                await notify_administrator(message.from_user.username, user_id)
                return

            # Инициализация подсчета сообщений для пользователя, если еще не была проведена
            if user_id not in user_message_counts:
                user_message_counts[user_id] = deque(maxlen=limit)

            # Проверка, отправил ли пользователь слишком много сообщений в пределах ограничения по скорости
            current_time = asyncio.get_event_loop().time()
            if len(user_message_counts[user_id]) >= limit:
                earliest_timestamp = user_message_counts[user_id][0]
                if current_time - earliest_timestamp < period:
                    await message.answer(selected_language['user_banned_message'])
                    # Запись блокировки пользователя
                    log_message = f"Пользователь {message.from_user.username} (ID: {user_id}) заблокирован из-за превышения ограничения по скорости."
                    logging.info(log_message)
                    database.ban_user(user_id)  # Блокировка пользователя
                    # Уведомление администратора о блокировке пользователя
                    await notify_administrator(message.from_user.username, user_id)
                    return

            # Добавление текущей метки времени в список
            user_message_counts[user_id].append(current_time)

            # Вызов декорированной функции
            await func(message, *args, **kwargs)

        return wrapped

    return decorator

async def notify_administrator(username, user_id):
    admin_notification = selected_language['ban_notification'].format(username=username, user_id=user_id)
    await bot.send_message(ADMIN_USER_ID, admin_notification)

@dp.message(F.text == '/list_users')
async def list_users(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        users = database.get_all_users()
        table = [[user[1], user[2], user[3], user[4]] for user in users]
        table_str = tabulate.tabulate(table, headers=["ID пользователя", "Имя пользователя", "Дата регистрации", "Оставшиеся токены"], tablefmt="pretty")
        await message.answer(f"Список пользователей:\n{table_str}")
    else:
        await message.answer(selected_language['list_users_permission_denied'])

@dp.message(F.text == '/ban_user')
async def ban_user(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        user_id_to_ban = message.get_args()
        
        user_id_to_ban = int(user_id_to_ban)
        user = database.get_user(user_id_to_ban)
        if user:
            database.ban_user(user_id_to_ban)
            await message.answer(selected_language['user_ban_success'].format(username=user[2]))

                # Запись блокировки пользователя
            log_message = f"Пользователь {user[2]} с ID {user_id_to_ban} заблокирован администратором."
            logging.info(log_message)

        else:
            await message.answer(selected_language['user_not_found'])
    
    else:
        await message.answer(selected_language['unban_user_permission_denied'])

@dp.message(F.text == '/unban_user')
async def unban_user(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        user_id_to_unban = message.get_args()
        try:
            user_id_to_unban = int(user_id_to_unban)
            user = database.get_user(user_id_to_unban)
            if user:
                database.unban_user(user_id_to_unban)
                await message.answer(selected_language['user_unban_success'].format(username=user[2]))

                # Запись разблокировки пользователя
                log_message = f"Пользователь {user[2]} с ID {user_id_to_unban} разблокирован администратором."
                logging.info(log_message)

            else:
                await message.answer(selected_language['user_not_found'])
        except ValueError:
            await message.answer(selected_language['invalid_user_id'].format(command="unban_user"))
    else:
        await message.answer(selected_language['unban_user_permission_denied'])

@dp.message(F.text == '/add_tokens')
async def add_tokens(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        args = message.get_args().split()
        if len(args) == 2:
            user_id_to_add_tokens, tokens_to_add = map(int, args)
            user = database.get_user(user_id_to_add_tokens)
            if user:
                remaining_tokens = user[4]
                remaining_tokens += tokens_to_add
                database.update_tokens(user_id_to_add_tokens, remaining_tokens)
                await message.answer(selected_language['add_tokens_success'].format(tokens_to_add=tokens_to_add, username=user[2]))
            else:
                await message.answer(selected_language['user_not_found'])
        else:
            await message.answer(selected_language['invalid_user_id'].format(command="add_tokens"))
    else:
        await message.answer(selected_language['add_tokens_permission_denied'])

@dp.message(lambda message: message.text == selected_language['buy_tokens_prompt'])
async def buy_tokens(message: types.Message):
    await message.answer(selected_language['buy_tokens_prompt'])
    # Теперь давайте дождемся ответа пользователя.

@dp.message(F.text == '/Check_tokens')
async def check_tokens(message: types.Message):
    user_id = message.from_user.id
    user = database.get_user(user_id)

    if user:
        remaining_tokens = user[4]
        await message.answer(selected_language['check_tokens_message'].format(remaining_tokens=remaining_tokens))
    else:
        await message.answer(selected_language['not_registered'])

def add_tokens_daily():
    users = database.get_all_users()
    for user in users:
        user_id = user[1]
        remaining_tokens = user[4]
        remaining_tokens += TOKENS_PER_DAY
        database.update_tokens(user_id, remaining_tokens)

# Расписание для ежедневного добавления токенов


async def main():
    dp.include_router(
        user_com.router
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())