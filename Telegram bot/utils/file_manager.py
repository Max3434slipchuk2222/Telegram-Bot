import json
import uuid
from paths import USERS_FILE, QUIZZES_FILE, RATINGS_FILE
import time

def register_user(user_id, first_name, username):
    user_id_modif = str(user_id)
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {} 

    if user_id_modif not in users:
        users[user_id_modif] = {
            'username': username,
            'first_name': first_name,
            'created_quizzes': []
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        print(f"Новий користувач зареєстрований: {first_name} ({user_id_modif})")
def add_quiz(user_id, quiz_data):
    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        quizzes = []
    
    quiz_id = str(uuid.uuid4())
    
    new_quiz = {
        'id': quiz_id,
        'author_id': user_id,
        'title': quiz_data.get('quiz_title'),
        'category': quiz_data.get('quiz_category'),
        'questions': quiz_data.get('questions', []) 
    }
    quizzes.append(new_quiz)

    with open(QUIZZES_FILE, 'w', encoding='utf-8') as f:
        json.dump(quizzes, f, indent=4, ensure_ascii=False)

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    
    user_id_str = str(user_id)
    if user_id_str in users:
        users[user_id_str]['created_quizzes'].append(quiz_id)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    
    print(f"Вікторина {quiz_id} збережена користувачем {user_id_str}")
def save_game_result(user_id, quiz_id, nickname, score, total_questions, duration):
    try:
        with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ratings = {} 

    new_result = {
        'user_id': user_id,
        'nickname': nickname,
        'score': score,
        'total': total_questions,
        'duration': duration 
    }

    if quiz_id in ratings:
        ratings[quiz_id].append(new_result)
    else:
        ratings[quiz_id] = [new_result]
        
    try:
        with open(RATINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ratings, f, indent=4, ensure_ascii=False)
        print(f"Новий результат для вікторини {quiz_id} збережено.")
    except Exception as e:
        print(f"Помилка при збереженні рейтингу: {e}")