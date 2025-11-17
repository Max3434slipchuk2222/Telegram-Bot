from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Створити вікторину")],
        [
            KeyboardButton(text="Пройти вікторину"),
            KeyboardButton(text="Рейтинг")
        ],
        [KeyboardButton(text="Мій профіль")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False 
)