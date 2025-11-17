import os
from dotenv import load_dotenv
load_dotenv() 

BOT_USERNAME = os.getenv("BOT_USERNAME")
DIR = 'data'
QUIZZES_FILE = os.path.join(DIR, 'quizzes.json')
USERS_FILE = os.path.join(DIR, 'users.json')
RATINGS_FILE = os.path.join(DIR, 'ratings.json')