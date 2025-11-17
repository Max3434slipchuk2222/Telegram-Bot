from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
import json
from aiogram.filters import Command

from keyboards.inline_buttons import get_rated_quizzes_keyboard
from keyboards.buttons import menu_keyboard
from paths import RATINGS_FILE, QUIZZES_FILE

router = Router()

@router.message(F.text == "Рейтинг 🏆")
@router.message(Command("rating"))
async def show_rating_options(message: types.Message, state: FSMContext):
    await state.clear() 
    
    rated_quizzes_kb = get_rated_quizzes_keyboard()
    
    if rated_quizzes_kb:
        await message.answer(
            "Оберіть вікторину, щоб побачити рейтинг:",
            reply_markup=rated_quizzes_kb
        )
    else:
        await message.answer(
            "Поки що немає жодного результату гри для показу рейтингу.",
            reply_markup=menu_keyboard
        )
@router.callback_query(F.data.startswith("rating_"))
async def show_quiz_rating(callback: types.CallbackQuery, state: FSMContext):
    quiz_id = callback.data.split('_', 1)[1]

    try:
        with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
            ratings_data = json.load(f)
        with open(QUIZZES_FILE, 'r', encoding='utf-8') as f:
            quizzes_data = json.load(f)
    except Exception:
        await callback.message.edit_text("Помилка: не вдалося завантажити дані.")
        await callback.answer()
        return

    quiz_title = next((q['title'] for q in quizzes_data if q['id'] == quiz_id), "Невідома вікторина")
    
    results = ratings_data.get(quiz_id, [])

    if not results:
        await callback.message.edit_text("Помилка: для цієї вікторини немає результатів.")
        await callback.answer()
        return

    sorted_results = sorted(
        results, 
        key=lambda item: (-item['score'], item['timestamp'])
    )

    rating_text = f"<-- Рейтинг для вікторини '{quiz_title}' -->\n\n"
    
    for i, entry in enumerate(sorted_results[:10]):
        place_emoji = ""
        if i == 0: place_emoji = "🥇"
        elif i == 1: place_emoji = "🥈"
        elif i == 2: place_emoji = "🥉"
        else: place_emoji = f" {i+1}. "
        
        rating_text += f"{place_emoji}{entry['nickname']} - **{entry['score']}/{entry['total']}**\n"
    
    await callback.message.edit_text(rating_text)
    await callback.answer()