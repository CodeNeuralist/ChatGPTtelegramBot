import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, types, Dispatcher, F
import asyncio
from io import BytesIO
from pydub import AudioSegment
from handlers.user_com import generate_response
import tabulate
import db
from language import *
from handlers import user_com
import speech_recognition as sr

# Загрузка переменных окружения
load_dotenv()
r = sr.Recognizer()

# Выбор языка (здесь вы можете использовать "ru_strings" или "en_strings")
selected_language = ru_strings

# Инициализация Telegram-бота
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

logging.basicConfig(filename="bot.log", filemode="w", format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.INFO)

# Константы
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))


# Параметры ограничения по скорости
database = db.Database()


@dp.message(F.text == '/list_users')
async def list_users(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        users = database.get_all_users()
        table = [[user[1], user[2], user[3], user[4]] for user in users]
        table_str = tabulate.tabulate(table, headers=["ID пользователя", "Имя пользователя", "Дата регистрации", "Оставшиеся токены"], tablefmt="pretty")
        await message.answer(f"Список пользователей:\n{table_str}")
    else:
        await message.answer(selected_language['list_users_permission_denied'])

@dp.message(F.voice)
async def audio_message_handler(msg: types.Message):
    try:
       file_in_io = BytesIO()
       file = await bot.get_file(msg.voice.file_id)
       file_path = file.file_path
       
       print("Ok")
       await bot.download_file(file_path, destination=file_in_io)
       file_in_io.seek(0)
       
       voice_msg_text = voice_recognize(ogg_to_wav(file_in_io))
       
       await msg.reply(f"Распознанно: '{voice_msg_text}'")
    
       await msg.reply(await generate_response(voice_msg_text))
    except Exception as e:
        print(f"Ошибка: {e}")
    
def ogg_to_wav(ogg_data):
    audio = AudioSegment.from_file(ogg_data, format='ogg')
    wav_data = BytesIO()
    audio.export(wav_data, format='wav')
    wav_data.seek(0)
    return wav_data

def voice_recognize(voice: BytesIO) -> str:
    voice_rec = sr.AudioFile(voice)
    with voice_rec as source:
        audio = r.record(source)
    return r.recognize_google(audio, language="ru-RU")


async def main():
    dp.include_router(
        user_com.router
    )
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())