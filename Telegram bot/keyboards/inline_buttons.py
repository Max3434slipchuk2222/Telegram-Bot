from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
from paths import QUIZZES_FILE, BOT_USERNAME, RATINGS_FILE, USERS_FILE

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


def get_quizzes_keyboard(categoryName):
    builder = InlineKeyboardBuilder()
    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []

    category_quizzes = []

    for quiz in quizzes:
        if quiz.get('category') == categoryName:
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


def create_question_keyboard(question_data, selected_answers):
    builder = InlineKeyboardBuilder()
    
    for i, option_text in enumerate(question_data['options']):
        
        prefix = "✅ " if i in selected_answers else " "
        
        builder.add(InlineKeyboardButton(
            text=f"{prefix}{option_text}",
            callback_data=f"play_answer_{i}"
        ))

    has_chosen = len(selected_answers) > 0
    
    if has_chosen:
        builder.add(InlineKeyboardButton(
            text=" <-- Підтвердити --> ",
            callback_data="play_confirm"
        ))
    
    builder.adjust(1)
    return builder.as_markup()


def create_settings_keyboard(settings, quiz_id):
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

    quiz_title = {}
    for quiz in quizzes:
        quiz_title[quiz['id']] = quiz['title']

    found_quiz = False
    for quiz_id in ratings:
        if quiz_id in quiz_title:
            title = quiz_title[quiz_id]
            builder.add(InlineKeyboardButton(
                text=title,
                callback_data=f"rating_{quiz_id}" 
            ))
            found_quiz = True

    if not found_quiz:
        return None 

    builder.adjust(1)
    return builder.as_markup()
def create_profile_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="📝 Мої створені вікторини",
        callback_data="profile_created" 
    ))
    
    builder.add(InlineKeyboardButton(
        text="📝 Мої пройдені вікторини",
        callback_data="profile_played"
    ))
    
    builder.adjust(1)
    return builder.as_markup()
def create_my_quizzes_keyboard(user_id):
    builder = InlineKeyboardBuilder()

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []

    user_id_str = str(user_id)
    user_data = users.get(user_id_str)

    if user_data is None:
        created_quiz_ids = []
    else:
        created_quiz_ids = user_data.get('created_quizzes', [])

    if not created_quiz_ids:
        builder.add(InlineKeyboardButton(
            text="Ви ще не створили жодної вікторини.",
            callback_data="profile_noop" 
        ))
        builder.adjust(1)
        
    else:
        quiz_title = {}
        for quiz in quizzes:
            quiz_title[quiz['id']] = quiz['title']

        for quiz_id in created_quiz_ids:
            if quiz_id in quiz_title and BOT_USERNAME:
                title = quiz_title[quiz_id]
                
                link = f"https://t.me/{BOT_USERNAME}?start={quiz_id}"
                share_url = f"https://t.me/share/url?url={link}&text=Хочеш спробувати пройти цю телеграм-вікторину? Натисни на посилання!"
                
                builder.add(InlineKeyboardButton(
                    text=f"{title}", 
                    url=share_url 
                ))
    builder.add(InlineKeyboardButton(
        text="⬅ Назад до профілю",
        callback_data="profile_main" 
    ))
    
    builder.adjust(1) 
    return builder.as_markup()
def create_my_played_keyboard(user_id: int):
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

    played_quiz_ids = set()
    for quiz_id, results in ratings.items():
        for entry in results:
            print(user_id, entry.get('user_id'))
            if str(entry.get('user_id')) == str(user_id):
                played_quiz_ids.add(quiz_id)
                break 

    if not played_quiz_ids:
        builder.add(InlineKeyboardButton(
            text="Ви ще не пройшли жодної вікторини.",
            callback_data="profile_noop" 
        ))
    else:
        quiz_title = {}
        for quiz in quizzes:
            quiz_title[quiz['id']] = quiz['title']

        for quiz_id in played_quiz_ids:
            if quiz_id in quiz_title:
                title = quiz_title[quiz_id]
                builder.add(InlineKeyboardButton(
                    text=f"{title}", 
                    callback_data="profile_noop" 
                ))
    builder.add(InlineKeyboardButton(
        text="⬅ Назад до профілю",
        callback_data="profile_main"
    ))
    
    builder.adjust(1) 
    return builder.as_markup()