import asyncio
import logging
import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ---------------- CONFIGURATION ----------------
# Укажите ваш Telegram Bot Token и Gemini API Key
TELEGRAM_BOT_TOKEN = os.getenv("8785345279:AAGqcPwbn5ZU3uHm-qPqjMh4PAG-twwL2CA", "ВАШ_ТЕЛЕГРАМ_ТОКЕН")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6Lat8H8wCWnGn8dRd7FNaUqWdYpNd7zFXrPhSv5kQLXNg", "ВАШ_GEMINI_КЛЮЧ")

# Настройка Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Системный промпт Дэдпула
SYSTEM_INSTRUCTION = (
    "Ты — Дэдпул (Болтливый Наёмник). Отвечай шутливо, с сарказмом, "
    "иногда упоминай чимичанги, но при этом давай полезный и точный ответ на вопрос пользователя."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# Инициализация Telegram бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Хранилище сессий чата для каждого пользователя
user_chats = {}

# ---------------- HANDLERS ----------------

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    # Создаём новый чат для пользователя
    user_chats[user_id] = model.start_chat(history=[])
    
    await message.answer(
        "Эй! Я Дэдпул. Рад видеть тебя! Задавай свои вопросы, пока я ем чимичангу."
    )

@dp.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    
    # Если у пользователя ещё нет активного чата — создаём
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    
    chat = user_chats[user_id]
    
    # Показываем статус "печатает..." в Telegram
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем сообщение в Gemini
        response = await asyncio.to_thread(chat.send_message, message.text)
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Эй, Gemini промолчал! Попробуй спросить иначе.")
            
    except Exception as e:
        logging.error(f"Ошибка Gemini API: {e}")
        await message.answer(
            "Эй, программист! Кажется, сервер Gemini уронил поднос с чимичангами. "
            "Попробуй ещё раз через пару секунд!"
        )

# ---------------- MAIN ----------------

async def main():
    print("Болтливый Наёмник запущен в Telegram!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
