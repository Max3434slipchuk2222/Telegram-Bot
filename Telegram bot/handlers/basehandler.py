from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, CommandStart,CommandObject 
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards.buttons import menu_keyboard
from utils.file_manager import register_user
from states.quiz_state import QuizCreation

router = Router()

@router.message(CommandStart(deep_link=False)) 
async def command_start(message: types.Message, state: FSMContext):
    await state.clear()
    register_user(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        username=message.from_user.username
    )

    await message.answer(
        f"Я бот для створення вікторин. \n\n"
        "Обери дію:",
        reply_markup=menu_keyboard
    )

@router.message(Command("help"))
async def command_help(message: types.Message):
    await message.answer(
        "Мої команди:\n"
        "/start - Запустити бота\n"
        "/create - Створення нової вікторини\n"
        "/play - Проходження вікторини\n"
        "/rating - Переглянути рейтинг\n"
        "/help - Показати довідку команд\n"
        "/cancel - Скасувати створення вікторини\n"
        "/profile - Вивести ваш профіль"
    )
    
@router.message(Command("cancel"), StateFilter(None))
async def command_cancel(message: types.Message, state: FSMContext):
    await message.answer("Немає активного процесу для скасування.", reply_markup=menu_keyboard)

@router.message(Command("create"))
@router.message(F.text == "Створити вікторину")
async def start_quiz_creation(message: types.Message, state: FSMContext):
    await state.set_state(QuizCreation.wait_title)
    
    await state.set_data({}) 
    await message.answer(
        "Для скасування створення вікторини використовуйте команду /cancel.\n\n"
        "Введіть назву вашої вікторини:",
        reply_markup=ReplyKeyboardRemove() 
    )