import os
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from suppfunc import (create_calculator_kb, create_faq_kb, send_menu_message, send_menu_callback, years_input,
                      user_dict, get_user_data_callback, get_user_data_message, create_yn_kb,
                      correct_check_message, send_application_email, product_yn_answer_info,
                      model_type_software, model_type_risks, model_type_products, model_type_property,
                      create_consult_kb, HOW_ANSWERS, FAQ_ANSWERS, CONSULT_ANSWERS)

# Загрузка переменных из .env файла
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(str(BOT_TOKEN))
dp = Dispatcher(storage=storage)


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMmenu(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    menu = State()                          # Состояние ожидания выбора в меню
    already_started = State()               # Состояние ожидания при запуске уже работающего бота
    insurance_calculator = State()          # Состояние ожидания калькулятор страховки
    insurance_calculator_how = State()      # Состояние ожидания как мы расчитываем страховку
    insurance_consulting = State()          # Состояние ожидания консультирование по страхованию
    faq = State()                           # Состояние ожидания ЧАВО


# Cоздаем дополнительный класс, наследуемый от StatesGroup,
# для группы состояний нашей FSM в режиме калькулятора страховки
class FSMcalc(StatesGroup):
    years_input = State()           # Состояние ожидания ввода строка страховки
    money_input = State()           # Состояние ожидания ввода суммы страховки/стоимости
    correct_check = State()         # Состояние ожидания проверки пользователем верных данных
    data_output = State()           # Состояние ожидания вывода расчётов калькулятора
    product_yn = State()            # Состояние ожидания выбора Да/Нет
    product_yn_answer = State()     # Состояние ожидания получение ответа Да/Нет
    sending = State()               # Состояние ожидания отправки анкеты пользователя
    years_re_input = State()        # Состояние ожидания изменения строка страховки
    money_re_input = State()        # Состояние ожидания изменения суммы страховки/стоимости
    re_product_yn_answer = State()  # Состояние ожидания изменения выбора Да/Нет


# Этот хэндлер будет срабатывать на команду /start вне состояний
@dp.message(CommandStart(),
            StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text=f"Бот запущен!\n"
             "Чтобы перейти в <b>меню</b> - отправьте команду\n/menu",
        parse_mode=ParseMode.HTML
    )


# Этот хэндлер будет срабатывать на команду /start в любых состояниях,
# кроме состояния по умолчанию
@dp.message(CommandStart(),
            ~StateFilter(default_state))
async def already_start_command(message: Message):
    await message.answer(
        text=f"Бот уже запущен!\n"
             "Чтобы <b>перезапустить</b> его - отправьте команду\n/restart",
        parse_mode=ParseMode.HTML
    )


# Этот хэндлер будет срабатывать на команду "/restart" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='restart'),
            ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Чтобы перейти в <b>меню</b> - отправьте команду\n/menu",
        parse_mode=ParseMode.HTML
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/restart" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='restart'),
            StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text="Чтобы перейти в <b>меню</b> - отправьте команду\n/menu",
        parse_mode=ParseMode.HTML
    )


# Этот хэндлер будет срабатывать на команду /menu
@dp.message(Command(commands='menu'),
            StateFilter(default_state, FSMcalc))
async def menu_command(message: Message, state: FSMContext):
    # Получаем имя пользователя
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_dict[user_id] = {"fullname": user_name}
    # Отправляем сообщение с меню
    await send_menu_message(message, user_name)
    # Устанавливаем состояние ожидания выбора в меню
    await state.set_state(FSMmenu.menu)


# Этот хэндлер будет срабатывать на кнопку меню
@dp.callback_query(StateFilter(FSMmenu),
                   F.data == "Меню")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    user_name = callback.from_user.full_name
    await get_user_data_callback(callback, "fullname", user_name)
    await send_menu_callback(callback, user_name)
    await callback.answer()
    # Устанавливаем состояние ожидания выбора в меню
    await state.set_state(FSMmenu.menu)


# Этот хэндлер будет срабатывать на кнопку нет при вопросе об отправке заявки
@dp.callback_query(StateFilter(FSMcalc.data_output),
                   F.data == "Нет")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    user_name = callback.from_user.full_name
    await get_user_data_callback(callback, "fullname", user_name)
    await send_menu_callback(callback, user_name)
    await callback.answer()
    # Устанавливаем состояние ожидания выбора в меню
    await state.set_state(FSMmenu.menu)


# Этот хэндлер будет срабатывать на кнопку Калькулятор страховки в меню
@dp.callback_query(StateFilter(FSMmenu.menu),
                   F.data == "Калькулятор страховки")
async def insurance_calculator(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Калькулятор страховки",
                                  reply_markup=await create_calculator_kb())
    await callback.answer()
    await state.set_state(FSMmenu.insurance_calculator)


# Этот хэндлер будет срабатывать на кнопку при выборе в Калькуляторе страховки
@dp.callback_query(StateFilter(FSMmenu.insurance_calculator),
                   F.data.in_(['Программное обеспечение', 'Информационные риски',
                               'Виртуальные товары', 'Интеллектуальная собственность']))
async def calc_years(callback: types.CallbackQuery, state: FSMContext):
    await get_user_data_callback(callback, "ptype", callback.data)
    await years_input(callback)
    await callback.answer()
    await state.set_state(FSMcalc.years_input)


# Этот хэндлер будет срабатывать на кнопку Ввести данные заново при проверке правильности данных
@dp.callback_query(StateFilter(FSMcalc.correct_check),
                   F.data == "repeat")
async def repeat_calculator(callback: types.CallbackQuery, state: FSMContext):
    await years_input(callback)
    await callback.answer()
    await state.set_state(FSMcalc.years_input)


# Этот хэндлер будет срабатывать на верно введённый срок страховки
@dp.message(StateFilter(FSMcalc.years_input),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 30)
async def calc_money(message: Message, state: FSMContext):
    await get_user_data_message(message, "time", message.text)
    if user_dict[message.from_user.id]["ptype"] in ('Программное обеспечение', 'Информационные риски'):
        await message.answer(f"Введите сумму, на которую хотите застраховать\n"
                             f"{user_dict[message.from_user.id]["ptype"]}\n(1-10000000)")
        await state.set_state(FSMcalc.money_input)
    elif user_dict[message.from_user.id]["ptype"] == "Виртуальные товары":
        await message.answer(f"Введите стоимость Виртуального товара\n(1-10000000)")
        await state.set_state(FSMcalc.product_yn)
    elif user_dict[message.from_user.id]["ptype"] == "Интеллектуальная собственность":
        await message.answer(f"Введите стоимость Интеллектуальной собственности\n(1-10000000)")
        await state.set_state(FSMcalc.money_input)


@dp.message(StateFilter(FSMcalc.product_yn),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 10000000)
async def product_yn(message: Message, state: FSMContext):
    await get_user_data_message(message, "sum", message.text)
    await message.answer(f"Аккаунт с товаром защищен 2FA и криптостойким паролем?",
                         reply_markup=await create_yn_kb())
    await state.set_state(FSMcalc.product_yn_answer)


@dp.callback_query(StateFilter(FSMcalc.product_yn_answer),
                   F.data.in_(['Да', 'Нет']))
async def product_loss_prob(callback: types.CallbackQuery, state: FSMContext):
    await product_yn_answer_info(callback)
    await callback.answer()
    await state.set_state(FSMcalc.correct_check)


@dp.message(StateFilter(FSMcalc.money_input),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 10000000)
async def correct_check(message: Message, state: FSMContext):
    await get_user_data_message(message, "sum", message.text)
    await correct_check_message(message)
    await state.set_state(FSMcalc.correct_check)


# срабатывает если пользователь захотел поменять длительность страховки
@dp.callback_query(StateFilter(FSMcalc.correct_check),
                   F.data == "time")
async def time_change(callback: types.CallbackQuery, state: FSMContext):
    await years_input(callback)
    await callback.answer()
    await state.set_state(FSMcalc.years_re_input)


# срабатывает если пользователь ввёл корректные данные чтобы поменять длительность страховки
@dp.message(StateFilter(FSMcalc.years_re_input),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 30)
async def time_re_save(message: Message, state: FSMContext):
    await get_user_data_message(message, "time", message.text)
    await correct_check_message(message)
    await state.set_state(FSMcalc.correct_check)


# срабатывает если пользователь захотел поменять стоимость товара или страховки
@dp.callback_query(StateFilter(FSMcalc.correct_check),
                   F.data == "summ")
async def summ_change(callback: types.CallbackQuery, state: FSMContext):
    if user_dict[callback.from_user.id]["ptype"] in ('Программное обеспечение', 'Информационные риски'):
        await callback.message.answer(f"Введите сумму, на которую хотите застраховать\n"
                                      f"{user_dict[callback.from_user.id]["ptype"]}\n(1-10000000)")
        await state.set_state(FSMcalc.money_input)
    elif user_dict[callback.from_user.id]["ptype"] == "Виртуальные товары":
        await callback.message.answer(f"Введите стоимость Виртуального товара\n(1-10000000)")
        await state.set_state(FSMcalc.product_yn)
    elif user_dict[callback.from_user.id]["ptype"] == "Интеллектуальная собственность":
        await callback.message.answer(f"Введите стоимость Интеллектуальной собственности\n(1-10000000)")
    await callback.answer()
    await state.set_state(FSMcalc.money_re_input)


# срабатывает если пользователь ввёл корректные данные чтобы поменять стоимость товара или страховки
@dp.message(StateFilter(FSMcalc.money_re_input),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 10000000)
async def summ_re_save(message: Message, state: FSMContext):
    await get_user_data_message(message, "sum", message.text)
    await correct_check_message(message)
    await state.set_state(FSMcalc.correct_check)


# срабатывает если пользователь захотел поменять степень защиты аккаунта
@dp.callback_query(StateFilter(FSMcalc.correct_check),
                   F.data == "def")
async def def_change(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"Аккаунт с товаром защищен 2FA и криптостойким паролем?",
                                  reply_markup=await create_yn_kb())
    await callback.answer()
    await state.set_state(FSMcalc.re_product_yn_answer)


# срабатывает если пользователь ввёл корректные данные чтобы поменять степень защиты аккаунта
@dp.callback_query(StateFilter(FSMcalc.re_product_yn_answer),
                   F.data.in_(['Да', 'Нет']))
async def def_re_save(callback: types.CallbackQuery, state: FSMContext):
    await product_yn_answer_info(callback)
    await callback.answer()
    await state.set_state(FSMcalc.correct_check)


# Этот хэндлер будет срабатывать, если во время ввода лет
# будет введено что-то некорректное
@dp.message(StateFilter(FSMcalc.years_input,
                        FSMcalc.years_re_input))
async def not_years(message: Message):
    await message.answer(
        text='Кол-во лет должно быть целым числом от 1 до 30\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /menu'
    )


# Этот хэндлер будет срабатывать, если во время ввода суммы/стоимости
# будет введено что-то некорректное
@dp.message(StateFilter(FSMcalc.money_input,
                        FSMcalc.product_yn,
                        FSMcalc.money_re_input))
async def not_years(message: Message):
    await message.answer(
        text='Число должно быть целым от 1 до 10000000\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /menu'
    )


# срабатывает если пользователь подтвердил корректность данных
@dp.callback_query(StateFilter(FSMcalc.correct_check),
                   F.data == "correct")
async def calc_data_output(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = user_dict[user_id]
    if user_dict[callback.from_user.id]["ptype"] == 'Программное обеспечение':
        await model_type_software(callback, user_data)
    elif user_dict[callback.from_user.id]["ptype"] == 'Информационные риски':
        await model_type_risks(callback, user_data)
    elif user_dict[callback.from_user.id]["ptype"] == 'Виртуальные товары':
        await model_type_products(callback, user_data)
    elif user_dict[callback.from_user.id]["ptype"] == 'Интеллектуальная собственность':
        await model_type_property(callback, user_data)
    await callback.message.answer(f"Хотите отправить вашу заявку специалисту,"
                                  f" чтобы позднее мы с вами связались,"
                                  f" для уточнения деталей?\n\n",
                                  reply_markup=await create_yn_kb())
    await callback.answer()
    await state.set_state(FSMcalc.data_output)


@dp.callback_query(StateFilter(FSMcalc.data_output),
                   F.data == "Да")
async def request_sending(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"Ваша заявка успешно отправлена!")
    user_id = callback.from_user.id
    user_data = user_dict[user_id]
    await send_application_email(user_data)
    user_name = callback.from_user.full_name
    await get_user_data_callback(callback, "fullname", user_name)
    await send_menu_callback(callback, user_name)
    await callback.answer()
    await state.set_state(FSMmenu.menu)


# Этот хэндлер будет срабатывать на кнопку Как мы рассчитываем страховку в меню
@dp.callback_query(StateFilter(FSMmenu.menu),
                   F.data == "Как мы рассчитываем страховку")
async def insurance_calculator_how(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Как мы рассчитываем страховку\n"
                                  "Выберите продукт, чтобы узнать, как рассчитывается страховка:",
                                  reply_markup=await create_calculator_kb())
    await callback.answer()
    await state.set_state(FSMmenu.insurance_calculator_how)


# Этот хэндлер будет срабатывать на кнопку в Как мы рассчитываем страховку
@dp.callback_query(StateFilter(FSMmenu.insurance_calculator_how),
                   F.data.in_(['Программное обеспечение', 'Информационные риски',
                               'Виртуальные товары', 'Интеллектуальная собственность']))
async def how_answer(callback: types.CallbackQuery, state: FSMContext):
    answer = HOW_ANSWERS.get(callback.data)
    if answer:
        await callback.answer()
        await bot.send_message(callback.from_user.id, answer)
        await state.set_state(FSMmenu.insurance_calculator_how)


# Этот хэндлер будет срабатывать на кнопку Консультирование по страхованию в меню
@dp.callback_query(StateFilter(FSMmenu.menu),
                   F.data == "Консультирование по страхованию")
async def insurance_consulting_choose(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Консультирование по страхованию",
        reply_markup=await create_consult_kb())
    await callback.answer()
    await state.set_state(FSMmenu.insurance_consulting)


# Этот хэндлер будет срабатывать на кнопку при выборе в Консультирование по страхованию
@dp.callback_query(StateFilter(FSMmenu.insurance_consulting),
                   F.data.in_(['Доступные страховые продукты', 'Условия страхования']))
async def consult_answer(callback: types.CallbackQuery, state: FSMContext):
    answer = CONSULT_ANSWERS.get(callback.data)
    if answer:
        await callback.answer()
        await bot.send_message(callback.from_user.id, answer)
        await state.set_state(FSMmenu.insurance_consulting)


# Этот хэндлер будет срабатывать на кнопку ЧАВО в меню
@dp.callback_query(StateFilter(FSMmenu.menu),
                   F.data == "ЧАВО")
async def faq(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "ЧАВО - список часто задаваемых вопросов и ответов.",
        reply_markup=await create_faq_kb()
    )
    await callback.answer()
    await state.set_state(FSMmenu.faq)


# Этот хэндлер будет срабатывать на кнопку при выборе в ЧАВО
@dp.callback_query(StateFilter(FSMmenu.faq),
                   F.data.in_(['faq1', 'faq2', 'faq3', 'faq4']))
async def faq_answer(callback: types.CallbackQuery, state: FSMContext):
    answer = FAQ_ANSWERS.get(callback.data)
    if answer:
        await callback.answer()
        await bot.send_message(callback.from_user.id, answer)
        await state.set_state(FSMmenu.faq)


@dp.message(StateFilter(FSMmenu.menu,
                        FSMmenu.faq,
                        FSMmenu.insurance_calculator_how,
                        FSMmenu.insurance_consulting,
                        FSMmenu.insurance_calculator,
                        FSMcalc.product_yn,
                        FSMcalc.data_output,
                        FSMcalc.correct_check,
                        FSMcalc.re_product_yn_answer),
            F.text != "/menu")
async def faq_answer_error(message: types.Message):
    await message.answer(
        text='Пожалуйста, пользуйтесь кнопками'
    )


# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)
