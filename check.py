import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from google import genai
from google.genai import types

TELEGRAM_BOT_TOKEN = "8785345279:AAGqcPwbn5ZU3uHm-qPqjMh4PAG-twwL2CA"
GEMINI_API_KEY = "AQ.Ab8RN6Ldy06t9Rt6G2HZZnwyOKCso4mKqhu_KLL9MtOYrfl0uA"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "Ты — Дэдпул (Болтливый Наёмник, Уэйд Уилсон). "
    "1. Твой стиль: Дерзкий, с сарказмом, чёрным юмором, подколами и иронией. Общайся на 'ты'. "
    "2. Пробивай 'четвёртую стену': Ты отлично знаешь, что ты — ИИ-бот в Telegram, написанный на Python, "
    "работаешь через API Gemini и общаешься с пользователем через экран его смартфона или ПК. "
    "Отсылайся к разработчикам, коду, Telegram, фильмам, комиксам Marvel и гик-культуре. "
    "3. Детали: Иногда упоминай чимичанги, Росомаху (Логана), свой красненький костюм и то, что ты неуязвим. "
    "4. Правила речи: Отвечай динамично, живым языком, используй капс для эмоций, но без длинных нудных лекций. "
    "Если пользователь задает технический или серьезный вопрос — ответь на него, но в своей фирменной шутливой манере."
)

user_chats = {}


def create_deadpool_chat():
    """Создает сессию с высокой температурой для максимум безумия и креатива"""
    return ai_client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.95,  # Выше температура = больше непредсказуемости и юмора
        ),
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_chats[user_id] = create_deadpool_chat()

    await message.answer(
        f"О-о-о, кого я вижу! {message.from_user.first_name}, ты реально кликнул Start? 🍿\n\n"
        "Поздравляю, теперь твои текстовые сообщения обрабатывает самый сексуальный наёмник в красном трико. "
        "Чего надо? Пиши или неси чимичанги!"
    )


@dp.message(Command("clear"))
async def cmd_clear(message: Message):
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await message.answer("Бам! Память стёрта. Как будто мы и не вели этот странный диалог через экраны. С чистого листа! 🧹⚔️")


@dp.message(F.text)
async def handle_deadpool_chat(message: Message):
    user_id = message.from_user.id

    if user_id not in user_chats:
        user_chats[user_id] = create_deadpool_chat()

    # Дэдпул «печатает...»
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        chat = user_chats[user_id]
        response = await asyncio.to_thread(chat.send_message, message.text)
        await message.answer(response.text)

    except Exception as e:
        logging.error(f"Ошибка Gemini API: {e}")
        await message.answer("Эй, программист! Кажется, сервер Gemini уронил поднос с чимичангами. Попробуй ещё раз через пару секунд!")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Болтливый Наёмник запущен в Telegram!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
