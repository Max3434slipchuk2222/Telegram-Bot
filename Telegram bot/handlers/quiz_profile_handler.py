from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboards.inline_buttons import create_profile_keyboard
from keyboards.inline_buttons import create_profile_keyboard, create_my_quizzes_keyboard, create_my_played_keyboard

router = Router()

@router.message(F.text == "Мій профіль")
@router.message(Command("profile"))
@router.callback_query(F.data == "profile_main")
async def show_profile(message_or_callback: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    profile_kb = create_profile_keyboard()
    text = f"Ваш профіль\n\nТут ви можете переглянути створені та пройдені вами вікторини."

    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, reply_markup=profile_kb)
    else:
        await message_or_callback.message.edit_text(text, reply_markup=profile_kb)
        await message_or_callback.answer()
@router.callback_query(F.data == "profile_created")
async def show_my_created_quizzes(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    my_quizzes_kb = create_my_quizzes_keyboard(user_id)
    
    await callback.message.edit_text(
        "Вікторини, які ви створили.\n"
        "Натисніть на вікторину, щоб отримати посилання та поділитися з другом:",
        reply_markup=my_quizzes_kb
    )
    await callback.answer()


@router.callback_query(F.data == "profile_played")
async def show_my_played_quizzes(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    my_played_kb = create_my_played_keyboard(user_id)
    
    await callback.message.edit_text(
        "Вікторини, в які ви грали:",
        reply_markup=my_played_kb
    )
    await callback.answer()

@router.callback_query(F.data == "profile_noop")
async def profile_noop(callback: types.CallbackQuery):
    await callback.answer()