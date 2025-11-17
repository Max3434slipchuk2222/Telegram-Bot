import asyncio
import logging
import json
import os
from dotenv import load_dotenv 
from aiogram import Bot, Dispatcher

from handlers import basehandler as bshandler
from handlers import quiz_create_handler as quiz_create
from paths import DIR, QUIZZES_FILE, USERS_FILE, RATINGS_FILE
from handlers import quiz_play_handler as quiz_play
from handlers import quiz_rating_handler as quiz_rating
from handlers import quiz_profile_handler as quiz_profile


load_dotenv() 

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logging.critical("Не знайдено TOKEN")
    exit()

logging.basicConfig(level=logging.INFO)

async def main():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    for filepath in [QUIZZES_FILE, USERS_FILE, RATINGS_FILE]:
        if not os.path.exists(filepath):
            if 'quizzes' in filepath:
                initial_data = [] 
            else:
                initial_data = {}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f)

    bot = Bot(token=TOKEN, default_parse_mode="Markdown")
    dp = Dispatcher(bot=bot)

    
    dp.include_router(quiz_create.router)
    dp.include_router(quiz_play.router)
    dp.include_router(quiz_rating.router)
    dp.include_router(quiz_profile.router)
    dp.include_router(bshandler.router)
    print("Бот запускається")
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())