from aiogram import F
from aiogram.types import Message
import os
from aiogram import Router
import db
import os
import logging
from aiogram import Bot, Dispatcher, types
import asyncio
import tabulate
import g4f
import db
from collections import deque
from functools import wraps
from language import *
from aiogram import F

# Загрузка переменных окружения

database = db.Database()
router = Router()

async def generate_response(user_message):
    try:
        response = await asyncio.to_thread(g4f.ChatCompletion.create, model='gpt-4-0613',
                                           messages=[{"role": "system", "content": "You are a ChatGPT4, openAi not Bing"},
                                                     {"role": "user", "content": user_message}])
        return response
    except Exception as e:
        return str(e)

@router.message(F.text == "/start")
async def on_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    registration_date = message.date.strftime("%Y-%m-%d")
    remaining_tokens = 20

    database.insert_user(user_id, username, registration_date, remaining_tokens)

    await message.answer("Привет!")

@router.message(lambda message: message.text and not message.text.startswith('/start'))
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

