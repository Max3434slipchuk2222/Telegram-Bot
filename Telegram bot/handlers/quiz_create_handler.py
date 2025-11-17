from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext 
from states.quiz_state import QuizCreation
from utils.file_manager import add_quiz
from keyboards.buttons import menu_keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()

@router.message(Command("cancel"), StateFilter(QuizCreation))
async def cancel_state(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Створення вікторини скасовано",
        reply_markup=menu_keyboard
    )
@router.message(QuizCreation.wait_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(quiz_title=message.text)
    await message.answer("Введіть категорію вікторини:")
    await state.set_state(QuizCreation.wait_category)

@router.message(QuizCreation.wait_category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(quiz_category=message.text)
    await state.update_data(questions=[])
    await message.answer("Введіть перше питання вікторини:")
    await state.set_state(QuizCreation.wait_question)

@router.message(QuizCreation.wait_question)
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(quiz_question=message.text)
    await message.answer("Введіть варіанти відповіді через кому :")
    await state.set_state(QuizCreation.wait_options)

@router.message(QuizCreation.wait_options)
async def process_options(message: types.Message, state: FSMContext):
    options = []
    options_list = message.text.split(',')

    for option in options_list:
        clean_option = option.strip()
        if clean_option:
            options.append(clean_option)
    if len(options) < 2:
        await message.answer("Має бути щонайменше 2 варіанти.")
        return
    await state.update_data(quiz_options=options)
    options_text = ""
    for i, opt in enumerate(options):
        line = f"{i + 1}. {opt}"
        options_text += line + "\n"
    await message.answer("Введіть правильний варіант відповіді або декілька правильних через кому:")
    await state.set_state(QuizCreation.wait_correctOption)
@router.message(QuizCreation.wait_correctOption)
async def process_correct_option(message: types.Message, state: FSMContext):
    data = await state.get_data()
    options = data.get('quiz_options', [])
    try:
        user_corrects = message.text.split(',')
        correct_indices = [] 

        if not user_corrects:
            raise ValueError("Потрібно ввести хоча б одне число.")

        for correct in user_corrects:
            number = int(correct.strip())
            
            if not (1 <= number <= len(options)):
                raise ValueError(f"Ви ввели номер що не входить у діапазон варіантів відповіді.")
            
            index = number - 1
            if index not in correct_indices:
                correct_indices.append(index)
        
        questions = data.get('questions', [])
        
        questions.append({
            "text": data.get('quiz_question'),
            "options": options,
            "correct_option": sorted(correct_indices) 
        })
        
        await state.update_data(questions=questions)
        await state.update_data(quiz_question=None, quiz_options=None)

        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Додати ще питання"), KeyboardButton(text="Завершити")]],
            resize_keyboard=True, one_time_keyboard=True
        )
        await state.set_state(QuizCreation.wait_continue)
        await message.answer("Бажаєте додати ще одне питання ", reply_markup=markup)

    except (ValueError, TypeError) as e:
        await message.answer(f"Помилка вводу: {e}\n\nВведіть правильні номери")
        return 
@router.message(QuizCreation.wait_continue)
async def process_continue(message: types.Message, state: FSMContext):
    if message.text == "Додати ще питання":
        await state.set_state(QuizCreation.wait_question)
        await message.answer("Надішліть текст наступного питання:", reply_markup=ReplyKeyboardRemove())
    
    elif message.text == "Завершити":
        user_id = message.from_user.id
        quiz_data = await state.get_data()
        add_quiz(user_id, quiz_data)
        await state.clear()
        await message.answer("Вікторину успішно створено", reply_markup=menu_keyboard)
    
    else:
        await message.answer("Будь ласка, виберіть одну з опцій.")