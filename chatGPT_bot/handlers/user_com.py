import db
import logging
import asyncio
import g4f
import db
from language import *
from aiogram.filters.command import Command
from aiogram import F, Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Загрузка переменных окружения

database = db.Database()
router = Router()
selected_language = ru_strings
ADMIN_USER_ID = 

async def generate_response(user_message):
    try:
        response = await asyncio.to_thread(g4f.ChatCompletion.create, model='gpt-4-0613',
                                           messages=[{"role": "system", "content": "You are a ChatGPT4, openAi not Bing"},
                                                     {"role": "user", "content": user_message}])
        return response
    except Exception as e:
        return str(e)

@router.message(Command("start"))
async def on_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Купить токены! 💰"),
            types.KeyboardButton(text="Профиль 🧑‍💼")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )



    user_id = message.from_user.id
    username = message.from_user.username
    registration_date = message.date.strftime("%Y-%m-%d")
    remaining_tokens = 20

    database.insert_user(user_id, username, registration_date, remaining_tokens)

    await message.answer("Привет!", reply_markup=keyboard)

from aiogram import types

@router.message(F.text.startswith("Купить токены!"))
async def without_puree(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="20 рублей - 20 токенов 💰",
        callback_data="20tokens")
    )
    builder.add(types.InlineKeyboardButton(
        text="30 рублей - 30 токенов 💰",
        callback_data="30tokens")
    )
    builder.add(types.InlineKeyboardButton(
        text="40 рублей - 40 токенов 💰",
        callback_data="40tokens")
    )
    builder.add(types.InlineKeyboardButton(
        text="70 рублей - 70 токенов 💰",
        callback_data="70tokens")
    )
    await message.answer(
        "Выберите тариф (1 токен = запрос = 1 рубль):",
        reply_markup=builder.as_markup()
    )

@router.message(F.text.startswith("Профиль"))
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user = database.get_user(user_id)
    
    if user:
        user_id = user[0]
        username = user[2]
        remaining_tokens = user[4]
        
        emoji_wallet = "💰"  # Эмодзи для токенов
        profile_text = (
            f"Профиль пользователя @{username} (ID: {message.from_user.id}):\n"
            f"Оставшиеся токены: {remaining_tokens} {emoji_wallet}"
        )

        # Добавим эмодзи для уровня и достижений (ваш код)

        await message.answer(profile_text)
    else:
        await message.answer(selected_language['not_registered'])

    
@router.callback_query(F.data == "20tokens")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Выбрано 20 токенов! 💰")

    thank_you_message = (
            f"🌟 Спасибо большое за желание приобрести 20 токенов! 🌟\n"
            f"Чтобы завершить покупку, напишите на @CodeWarpX."
    )

    await callback.message.answer(thank_you_message)

@router.callback_query(F.data == "30tokens")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Выбрано 30 токенов! 💰")

    thank_you_message = (
            f"🌟 Спасибо большое за желание приобрести 30 токенов! 🌟\n"
            f"Чтобы завершить покупку, напишите на @CodeWarpX."
    )

    await callback.message.answer(thank_you_message)


@router.callback_query(F.data == "40tokens")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Выбрано 40 токенов! 💰")

    thank_you_message = (
            f"🌟 Спасибо большое за желание приобрести 40 токенов! 🌟\n"
            f"Чтобы завершить покупку, напишите на @CodeWarpX."
    )

    await callback.message.answer(thank_you_message)


@router.callback_query(F.data == "70tokens")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("Выбрано 70 токенов! 💰")

    thank_you_message = (
            f"🌟 Спасибо большое за желание приобрести 70 токенов! 🌟\n"
            f"Чтобы завершить покупку, напишите на @CodeWarpX."
    )

    await callback.message.answer(thank_you_message)

@router.message(F.text.startswith('/ban_user'))
async def ban_user(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        command_parts = message.text.split(maxsplit=1)
        
        if len(command_parts) > 1:
            user_id_to_ban = command_parts[1]
            
            try:
                user_id_to_ban = int(user_id_to_ban)
                user = database.get_user(user_id_to_ban)

                if user:
                    database.ban_user(user_id_to_ban)
                    ban_success_message = f"Пользователь {user[2]} с ID {user_id_to_ban} заблокирован администратором."
                    logging.info(ban_success_message)
                    await message.answer(ban_success_message)
                else:
                    user_not_found_message = "Пользователь не найден."
                    await message.answer(user_not_found_message)
            except ValueError:
                invalid_user_id_message = "Неверный ID пользователя. Пожалуйста, введите числовой ID пользователя."
                await message.answer(invalid_user_id_message)
        else:
            missing_user_id_message = "Не указан ID пользователя. Пожалуйста, введите числовой ID пользователя."
            await message.answer(missing_user_id_message)
    else:
        unban_user_permission_denied_message = "Отсутствует разрешение на блокировку пользователя."
        await message.answer(unban_user_permission_denied_message)

@router.message(F.text.startswith('/add_tokens'))
async def add_tokens(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) == 3:
            try:
                user_id_to_add_tokens, tokens_to_add = map(int, command_parts[1:])
                user = database.get_user(user_id_to_add_tokens)
                if user:
                    remaining_tokens = user[4]
                    remaining_tokens += tokens_to_add
                    database.update_tokens(user_id_to_add_tokens, remaining_tokens)
                    add_tokens_success_message = f"Добавлено {tokens_to_add} токенов пользователю {user[2]} (ID: {user_id_to_add_tokens})."
                    await message.answer(add_tokens_success_message)
                else:
                    user_not_found_message = "Пользователь не найден."
                    await message.answer(user_not_found_message)
            except ValueError:
                invalid_command_format_message = "Неверный формат команды. Используйте /add_tokens [user_id] [количество токенов]."
                await message.answer(invalid_command_format_message)
        else:
            invalid_command_format_message = "Неверный формат команды. Используйте /add_tokens [user_id] [количество токенов]."
            await message.answer(invalid_command_format_message)
    else:
        add_tokens_permission_denied_message = "Отсутствует разрешение на добавление токенов."
        await message.answer(add_tokens_permission_denied_message)



from aiogram import types

@router.message(F.text.startswith('/unban_user'))
async def unban_user(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        command_parts = message.text.split(maxsplit=1)

        if len(command_parts) == 2:
            command, user_id_to_unban = command_parts
            try:
                user_id_to_unban = int(user_id_to_unban)
                user = database.get_user(user_id_to_unban)
                if user:
                    database.unban_user(user_id_to_unban)
                    user_unban_success_message = f"Пользователь {user[2]} с ID {user_id_to_unban} разблокирован администратором."
                    logging.info(user_unban_success_message)
                    await message.answer(user_unban_success_message)
                else:
                    user_not_found_message = "Пользователь не найден."
                    await message.answer(user_not_found_message)
            except ValueError:
                invalid_user_id_message = "Неверный ID пользователя. Пожалуйста, введите числовой ID пользователя."
                await message.answer(invalid_user_id_message)
        else:
            invalid_command_format_message = "Неверный формат команды. Используйте /unban_user [user_id]."
            await message.answer(invalid_command_format_message)
    else:
        unban_user_permission_denied_message = "Отсутствует разрешение на разблокировку пользователя."
        await message.answer(unban_user_permission_denied_message)


@router.message(lambda message: message.text and not message.text.startswith('/start') and not message.text.startswith('/ban_user')
                and not message.text.startswith('/unban_user') and not message.text.startswith('/add_tokens') and not message.text.startswith('Купить токены!') 
                and not message.text.startswith('Профиль'))
# @rate_limit(RATE_LIMIT_MESSAGES, RATE_LIMIT_PERIOD)
async def on_text(message: types.Message):
    user_message = message.text
    user_id = message.from_user.id
    user = database.get_user(user_id)

    if user:
        if user[5]:  # Check if the user is banned
            await message.answer("You are banned and cannot send messages. 🚫")
        else:
            # Check if the user has enough tokens
            if database.deduct_token(user_id=user_id):
                try:
                    await message.answer("Processing... Please wait... ⌛")
                    response = await generate_response(user_message)
                    await message.answer(response, parse_mode="MARKDOWN")
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    logging.error(f"An error occurred: {str(e)}")
                    await message.answer(error_message)
            else:
                await message.answer("Not enough tokens. You can buy more using the 'Buy Tokens 💰' command.")
    else:
        await message.answer("You are not registered. Please use /start to register. 📝")

