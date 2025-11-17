from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
from paths import QUIZZES_FILE, BOT_USERNAME, RATINGS_FILE

def get_categories_keyboard():
    builder = InlineKeyboardBuilder()

    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []

    categories = set()

    for quiz in quizzes:
        
        category = quiz.get('category')
        
        if category:
            
            categories.add(category)
        
    if not categories:
        return None

    for category in sorted(list(categories)): 
        builder.add(InlineKeyboardButton(
            text=category,
            callback_data=f"category_{category}" 
        ))
    
    builder.adjust(1)
    return builder.as_markup()
def get_quizzes_keyboard(category: str):
    builder = InlineKeyboardBuilder()
    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []

    category_quizzes = []

    for quiz in quizzes:
        if quiz.get('category') == category:
            category_quizzes.append(quiz)

    if not category_quizzes:
        return None 

    for quiz in category_quizzes:
        builder.add(InlineKeyboardButton(
            text=quiz.get('title', 'Без назви'),
            callback_data=f"quiz_{quiz.get('id')}"
        ))
    

    builder.add(InlineKeyboardButton(
        text="Назад до категорій",
        callback_data="back_to_categories" 
    ))
    
    builder.adjust(1)
    return builder.as_markup()
def create_question_keyboard(question_data: dict, selected_indices: list = []):
    builder = InlineKeyboardBuilder()
    
    for i, option_text in enumerate(question_data['options']):
        
        prefix = "✅ " if i in selected_indices else " "
        
        builder.add(InlineKeyboardButton(
            text=f"{prefix}{option_text}",
            callback_data=f"play_answer_{i}"
        ))

    can_confirm = len(selected_indices) > 0
    
    if can_confirm:
        builder.add(InlineKeyboardButton(
            text=" <-- Підтвердити --> ",
            callback_data="play_confirm"
        ))
    
    builder.adjust(1)
    return builder.as_markup()
def create_settings_keyboard(settings: dict, quiz_id: str):
    builder = InlineKeyboardBuilder()

    show_answers = settings.get('show_answers', True) 
    prefix_answers = "✅" if show_answers else " "
    builder.add(InlineKeyboardButton(
        text=f"{prefix_answers}Показувати відповідь одразу",
        callback_data="setting_toggle_answers"
    ))

    show_review = settings.get('show_review', True)
    prefix_review = "✅" if show_review else ""
    builder.add(InlineKeyboardButton(
        text=f"{prefix_review}Показати огляд в кінці",
        callback_data="setting_toggle_review"
    ))
    if BOT_USERNAME and quiz_id:
        link = f"https://t.me/{BOT_USERNAME}?start={quiz_id}"
        
        share_url = f"https://t.me/share/url?url={link}&text=Хочеш спробувати пройти цю телеграм-вікторину? Натисни на посилання!"
        
        builder.add(InlineKeyboardButton(
            text="Поділитися з другом",
            url=share_url
        ))
    builder.add(InlineKeyboardButton(
        text="Почати гру!",
        callback_data="setting_start_game" 
    ))
    builder.adjust(1)
    return builder.as_markup()
def get_rated_quizzes_keyboard():
    builder = InlineKeyboardBuilder()
    try:
        with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ratings = {} 

    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []

    quiz_id_to_title = {quiz['id']: quiz['title'] for quiz in quizzes}

    quizzes_found = False
    for quiz_id in ratings:
        if quiz_id in quiz_id_to_title:
            title = quiz_id_to_title[quiz_id]
            builder.add(InlineKeyboardButton(
                text=title,
                callback_data=f"rating_{quiz_id}" 
            ))
            quizzes_found = True

    if not quizzes_found:
        return None 

    builder.adjust(1)
    return builder.as_markup()