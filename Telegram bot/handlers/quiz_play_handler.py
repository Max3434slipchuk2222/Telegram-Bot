from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import json

from keyboards.inline_buttons import (
    get_categories_keyboard, 
    get_quizzes_keyboard, 
    create_question_keyboard,
    create_settings_keyboard
)
from utils.file_manager import save_game_result,add_quiz
from keyboards.buttons import menu_keyboard
from states.quiz_state import QuizPlaying 
from paths import QUIZZES_FILE, BOT_USERNAME
from aiogram.exceptions import TelegramBadRequest
router = Router()


@router.message(F.text == "Пройти вікторину")
@router.message(Command("play"))
async def start_playing(message: types.Message, state: FSMContext):
    await state.clear()
    categories = get_categories_keyboard()
    if categories:
        await message.answer("Оберіть категорію вікторини:", reply_markup=categories)
    else:
        await message.answer("Ще не створено жодної вікторини.", reply_markup=menu_keyboard)

@router.callback_query(F.data.startswith("category_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split('_', 1)[1]
    quizzes_kb = get_quizzes_keyboard(category)
    if quizzes_kb:
        await callback.message.edit_text(f"Оберіть вікторину з категорії '{category}':", reply_markup=quizzes_kb)
    else:
        await callback.message.edit_text(f"У категорії '{category}' немає вікторин.", reply_markup=get_categories_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Оберіть категорію вікторини:", reply_markup=get_categories_keyboard())
    await callback.answer()

async def _init_quiz_session(message_or_callback: types.Message | types.CallbackQuery, state: FSMContext, quiz_id: str):
    try:
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
        
        current_quiz = next((q for q in quizzes if q['id'] == quiz_id), None)
        
        answer_target = message_or_callback if isinstance(message_or_callback, types.Message) else message_or_callback.message

        if not current_quiz:
            await answer_target.answer("Помилка: Вікторину не знайдено.", reply_markup=menu_keyboard)
            return

        await state.set_state(QuizPlaying.wait_nickname)
        await state.update_data(
            quiz_id=quiz_id,
            quiz_title=current_quiz['title'],
            questions=current_quiz['questions']
        )
        
        text = f"Ви обрали вікторину: **{current_quiz['title']}**\n\n" \
               f"Будь ласка, введіть ваш **нікнейм** для цієї гри:"
        
        if isinstance(message_or_callback, types.Message):
            await answer_target.answer(text)
        else: 
            try:
                await message_or_callback.message.delete()
            except TelegramBadRequest:
                pass 
            await answer_target.answer(text)

    except Exception as e:
        answer_target = message_or_callback if isinstance(message_or_callback, types.Message) else message_or_callback.message
        await answer_target.answer(f"Сталася помилка: {e}", reply_markup=menu_keyboard)

@router.callback_query(F.data.startswith("quiz_"))
async def start_quiz_ask_nickname(callback: types.CallbackQuery, state: FSMContext):
    quiz_id = callback.data.split('_', 1)[1]
    await _init_quiz_session(callback, state, quiz_id)
    await callback.answer()
@router.message(QuizPlaying.wait_nickname)
async def handle_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    default_settings = {
        'show_answers': True,
        'show_review': True
    }
    await state.update_data(settings=default_settings)

    data = await state.get_data() 
    quiz_id = data.get('quiz_id') 

    keyboard = create_settings_keyboard(default_settings, quiz_id)
    
    await state.set_state(QuizPlaying.wait_settings)
    
    await message.answer(
        f"Оберіть налаштування гри:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("setting_toggle_"), QuizPlaying.wait_settings)
async def handle_settings_toggle(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    settings = data.get('settings', {})
    
    setting_key = callback.data.split('_')[-1] 
    
    if setting_key == "answers":
        settings['show_answers'] = not settings.get('show_answers', True)
    elif setting_key == "review":
        settings['show_review'] = not settings.get('show_review', True)
        
    await state.update_data(settings=settings)
    data = await state.get_data() 
    quiz_id = data.get('quiz_id')
    new_keyboard = create_settings_keyboard(settings, quiz_id)
    await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    await callback.answer()
@router.callback_query(F.data == "setting_start_game", QuizPlaying.wait_settings)
async def handle_start_game(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass 
    
    await state.set_state(QuizPlaying.playing_state)
    
    await state.update_data(
        current_question_index=0,
        score=0,
        current_selections=[],
        user_answers=[]
    )
    await send_next_question(callback.message, state)
    
    await callback.answer()

def review_text(questions: list, all_user_answers: list):
    review_text = "--- Робота над помилками ---\n\n"
    
    for i, q in enumerate(questions):
        review_text += f"Питання {i+1}: {q['text']}\n"
        
        correct_indices = q['correct_option']
        correct_options_text = [q['options'][idx] for idx in correct_indices]
        review_text += f"▪️ *Правильно:*✅ {', '.join(correct_options_text)}\n"

        try:
            user_indices = all_user_answers[i]
            user_options_text = [q['options'][idx] for idx in user_indices] if user_indices else ["(Немає відповіді)"]
        except IndexError:
            user_options_text = ["(Немає відповіді)"]
            user_indices = []
        
        is_correct = sorted(user_indices) == sorted(correct_indices)
        
        if is_correct:
            review_text += f"▪️ *Ваша відповідь:* ✅ {', '.join(user_options_text)}\n\n"
        else:
            review_text += f"▪️ *Ваша відповідь:* ❌ {', '.join(user_options_text)}\n\n"

    return review_text
async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get('questions', [])
    index = data.get('current_question_index', 0)

    if index < len(questions):
        ques = questions[index]
        await state.update_data(current_selections=[]) 
        
        keyboard = create_question_keyboard(ques, [])
        
        await message.answer(f"Питання {index + 1}/{len(questions)}:\n\n{ques['text']}", reply_markup=keyboard)
    else:
        score = data.get('score', 0)
        title = data.get('quiz_title', '')
        nickname = data.get('nickname', 'Гравець')
        quiz_id = data.get('quiz_id')
        settings = data.get('settings', {})
        total_questions = len(questions)

        if quiz_id:
            save_game_result(quiz_id, title, nickname, score, total_questions)

        final_text = f"Вікторину '{title}' завершено!\n\n" \
                     f"{nickname}, ваш результат: {score} з {total_questions}"
        
        if settings.get('show_review', True):
            all_answers = data.get('user_answers', [])
            review = review_text(questions, all_answers)
            final_text += f"\n\n{review}"
        
        await message.answer(final_text, reply_markup=menu_keyboard)
        
        await state.clear()


@router.callback_query(F.data.startswith("play_answer_"), QuizPlaying.playing_state)
async def handle_answer_toggle(callback: types.CallbackQuery, state: FSMContext):
    
    selected_index = int(callback.data.split('_')[-1])
    
    data = await state.get_data()
    current_selections = data.get('current_selections', [])
    
    if selected_index in current_selections:
        current_selections.remove(selected_index) 
    else:
        current_selections.append(selected_index) 
    
    await state.update_data(current_selections=current_selections)
    
    ques_index = data.get('current_question_index', 0)
    question_data = data.get('questions', [])[ques_index]
    
    new_keyboard = create_question_keyboard(question_data, current_selections)

    await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    
    await callback.answer()



@router.callback_query(F.data == "play_confirm", QuizPlaying.playing_state)
async def handle_answer_confirm(callback: types.CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    q_index = data.get('current_question_index', 0)
    questions = data.get('questions', [])
    q = questions[q_index] 
    
    user_selections = data.get('current_selections', [])
    correct_indices = q['correct_option'] 
    
    is_correct = sorted(user_selections) == sorted(correct_indices)
    
    new_score = data.get('score', 0) + (1 if is_correct else 0)
    new_index = q_index + 1
    
    user_answers = data.get('user_answers', [])
    user_answers.append(user_selections.copy())
    await state.update_data(
        score=new_score,
        current_question_index=new_index,
        user_answers=user_answers
    )
    
    settings = data.get('settings', {})
    if settings.get('show_answers', True):
        if is_correct:
            await callback.answer(text="Правильно!", show_alert=True)
        else:
            await callback.answer(text="Неправильно!", show_alert=True)
    else:
        await callback.answer() 

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass 
    await send_next_question(callback.message, state)