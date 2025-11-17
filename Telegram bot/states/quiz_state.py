from aiogram.fsm.state import State, StatesGroup

class QuizCreation(StatesGroup):
    wait_title = State()      
    wait_category = State()   
    wait_question = State()    
    wait_options = State()   
    wait_correctOption = State()
    wait_continue = State()
class QuizPlaying(StatesGroup):
    wait_nickname = State()
    wait_settings = State()
    playing_state = State()
    result_state = State()