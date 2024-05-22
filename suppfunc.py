import os
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Загрузка переменных из .env файла
load_dotenv()

HOW_ANSWERS = {
    "Программное обеспечение": "Годовая страховая премия = страховая сумма * ставка страховой премии\n"
                               "Общая страховая премия = годовая страховая премия * кол-во лет страховки\n"
                               "Ежемесячный платеж = общая страховая премия / кол-во месяцев страхования",
    "Информационные риски": "Годовая страховая премия = страхвоая сумма * ставка страховой премии\n"
                            "Ставка страховой премии зависит от страховой суммы\n"
                            "Общая страховая премия = годовая страховая премия * кол-во лет страховки\n"
                            "Ежемесячный платеж = общая страховая премия / кол-во месяцев страхования",
    "Виртуальные товары": "Cтраховая премия = cтоимость виртуального товара * "
                          "вероятность потери * коэффициент, который учитывает дополнительные издержки\n"
                          "Ежемесячный платеж = страховая премия / кол-во месяцев страхования",
    "Интеллектуальная собственность": "Cтраховая премия = стоимость интеллектуальной собственности * "
                                      "вероятность нарушения ваших прав * коэффициент, "
                                      "который учитывает дополнительные издержки\n"
                                      "Ежемесячный платеж = страховая премия / кол-во месяцев страхования\n"
}


CONSULT_ANSWERS = {
    "Доступные страховые продукты": "1. Программное обеспечение:\n"
                                    "Это может включать в себя операционные системы, прикладное программное"
                                    "обеспечение, игры, веб-приложения и многое другое.\n"
                                    "2. Информационные риски:\n"
                                    "Это может включать в себя утечку конфиденциальных данных, кибератаки,"
                                    "потерю данных из-за аппаратных сбоев или человеческого фактора.\n"
                                    "3. Виртуальные товары:\n"
                                    "Это могут быть цифровые товары, такие как музыка, фильмы, электронные"
                                    "книги, игровые предметы, валюта в онлайн-играх и многое другое.\n"
                                    "4. Интеллектуальная собственность:\n"
                                    "Интеллектуальная собственность относится к правам на интеллектуальные идеи,"
                                    "творческие работы и изобретения, включая авторские права, патенты, товарные"
                                    "знаки и торговые секреты.\n",
    "Условия страхования": "Условия страхования\n"
                           "1. Определение покрытия: В полисе должно быть четко определено, какие риски и убытки"
                           "будут покрываться страхованием, такие как кибератаки, утеря данных, проблемы с"
                           "программным обеспечением и т. д.\n"
                           "2. Сумма покрытия: Указание максимальной суммы, которую страховая компания выплатит"
                           "в случае возникновения страхового случая.\n"
                           "3. Исключения: Описание событий и убытков, которые не будут покрываться страхованием."
                           "Например, это могут быть убытки, вызванные намеренными действиями или пренебрежением.\n"
                           "4. Обязанности страхователя: Указание на обязанности страхователя, такие как подача"
                           "заявления о страховом случае в установленные сроки и предоставление необходимой"
                           "информации и документов.\n"
                           "5. Период страхования: Указание временного периода, в течение которого действует"
                           "страхование, а также условия продления страхового полиса.\n"
                           "6. Ставка страховой премии: Определение размера страховой премии, который"
                           "страхователь должен будет уплатить за страхование.\n"
                           "7. Условия выплаты: Описание условий и процедур, по которым будет осуществляться"
                           "выплата страхового возмещения в случае страхового случая.\n"
                           "8. Ограничения ответственности: Указание максимальной ответственности страховой"
                           "компании за убытки, а также условий и исключений, касающихся объема и размера выплат.\n"
}

FAQ_ANSWERS = {
    "faq1": "Что такое страхование цифровых продуктов?\n"
            "Страхование цифровых продуктов предоставляет защиту от потерь, связанных с цифровыми товарами, "
            "такими как программное обеспечение, электронные книги, игры и другие цифровые активы",
    "faq2": "Какие типы цифровых продуктов можно застраховать?\n"
            "Вы можете застраховать широкий спектр цифровых продуктов, включая программное обеспечение, игры, "
            "электронные книги, аудио- и видеофайлы, а также цифровые коллекции и виртуальные активы",
    "faq3": "Каковы типичные исключения из покрытия страхования?\n"
            "Исключения могут включать в себя умышленные действия, неправомерное использование продуктов, "
            "недостаточные меры безопасности и другие специфические условия",
    "faq4": "Как проходит подача заявление на страхование?\n"
            "Выберите в меню калькулятор страховки и заполните форму, далее с вами свяжутся наши сотрудники"
}


async def create_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Калькулятор страховки",
        callback_data="Калькулятор страховки"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Как мы рассчитываем страховку",
        callback_data="Как мы рассчитываем страховку"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Консультирование по страхованию",
        callback_data="Консультирование по страхованию"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="ЧАВО",
        callback_data="ЧАВО"
    )
    )
    builder.adjust(1)  # 1 кнопка в ряду
    return builder.as_markup()


async def create_calculator_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Программное обеспечение",
        callback_data="Программное обеспечение"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Информационные риски",
        callback_data="Информационные риски"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Виртуальные товары",
        callback_data="Виртуальные товары"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Интеллектуальная собственность",
        callback_data="Интеллектуальная собственность"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="\u2B06️Меню",
        callback_data="Меню"
    )
    )
    builder.adjust(1)  # 1 кнопка в ряду
    return builder.as_markup()


async def create_consult_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Доступные страховые продукты",
        callback_data="Доступные страховые продукты"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Условия страхования",
        callback_data="Условия страхования"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="\u2B06️Меню",
        callback_data="Меню"
    )
    )
    builder.adjust(1)  # 1 кнопка в ряду
    return builder.as_markup()


async def create_yn_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да",
        callback_data="Да"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Нет",
        callback_data="Нет"
    )
    )
    builder.adjust(2)  # 2 кнопки в ряду
    return builder.as_markup()


async def create_faq_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Что такое страхование цифровых продуктов?",
        callback_data="faq1"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Какие типы цифровых продуктов можно застраховать?",
        callback_data="faq2"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Каковы типичные исключения из покрытия страхования?",
        callback_data="faq3"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Как проходит подача заявление на страхование?",
        callback_data="faq4"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="\u2B06️Меню",
        callback_data="Меню"
    )
    )
    builder.adjust(1)  # 1 кнопка в ряду
    return builder.as_markup()


async def correct_check_kb(ptype):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Данные верны",
        callback_data="correct"
    )
    )
    builder.add(types.InlineKeyboardButton(
        text="Изменить длительность",
        callback_data="time"
    )
    )
    if ptype in ('Программное обеспечение', 'Информационные риски'):
        builder.add(types.InlineKeyboardButton(
            text="Изменить сумму",
            callback_data="summ"
        )
        )
    elif ptype in ('Виртуальные товары', 'Интеллектуальная собственность'):
        builder.add(types.InlineKeyboardButton(
            text="Изменить стоимость",
            callback_data="summ"
        )
        )
    if ptype == "Виртуальные товары":
        builder.add(types.InlineKeyboardButton(
            text="Изменить степень защиты",
            callback_data="def"
        )
        )
    builder.add(types.InlineKeyboardButton(
        text="Ввести данные заново",
        callback_data="repeat"
    )
    )
    builder.adjust(1)  # 1 кнопка в ряду
    return builder.as_markup()


async def send_menu_message(message: Message, user_name: str):
    await message.answer(
        text=f"<b>МЕНЮ</b>\n\n"
             f"Здравствуй, <b>{user_name}</b>\n\n"
             "\U0001F447Выберите опцию",
        parse_mode=ParseMode.HTML,
        reply_markup=await create_menu_kb()
    )


async def send_menu_callback(callback: types.CallbackQuery, user_name: str):
    await callback.message.answer(
        text=f"<b>МЕНЮ</b>\n\n"
             f"Здравствуй, <b>{user_name}</b>\n\n"
             "\U0001F447Выберите опцию",
        parse_mode=ParseMode.HTML,
        reply_markup=await create_menu_kb()
    )


# Создаем "базу данных" пользователей. Создается словарь, в котором ключами являются
# целые числа (user_id), а значениями являются словари, содержащие строковые и
# целочисленные значения (user_name и другие данные пользователя).
user_dict: dict[int, dict[str, str | int | bool]] = {}


# функиця сохраняет в словарь коллбэк от пользователя с ключом user_id
async def get_user_data_callback(callback: types.CallbackQuery, key, value):
    user_id = callback.from_user.id
    if user_id not in user_dict:
        user_dict[user_id] = {}
    user_dict[user_id][key] = value


# функиця сохраняет в словарь сообщение от пользователя с ключом user_id
async def get_user_data_message(message: Message, key, value):
    user_id = message.from_user.id
    if user_id not in user_dict:
        user_dict[user_id] = {}
    user_dict[user_id][key] = value


async def correct_check_message(message: Message):
    if user_dict[message.from_user.id]["ptype"] in ('Программное обеспечение', 'Информационные риски'):
        await message.answer(f"Длительность страховки: <b>{user_dict[message.from_user.id]['time']}</b>\n"
                             f"Cумма: <b>{user_dict[message.from_user.id]['sum']}</b>",
                             parse_mode=ParseMode.HTML)
    elif user_dict[message.from_user.id]["ptype"] == "Интеллектуальная собственность":
        await message.answer(f"Длительность страховки: <b>{user_dict[message.from_user.id]['time']}</b>\n"
                             f"Стоимость Интеллектуальной собственности: "
                             f"<b>{user_dict[message.from_user.id]['sum']}</b>",
                             parse_mode=ParseMode.HTML)
    elif user_dict[message.from_user.id]["ptype"] == "Виртуальные товары":
        if user_dict[message.from_user.id]["loss"] == '0.02':
            loss = "Да"
        else:
            loss = "Нет"
        await message.answer(f"Длительность страховки: <b>{user_dict[message.from_user.id]['time']}</b>\n"
                             f"Стоимость Виртуального товара: <b>{user_dict[message.from_user.id]['sum']}</b>\n"
                             f"Аккаунт хорошо защищён: {loss}",
                             parse_mode=ParseMode.HTML)
    await message.answer(f"<b>{user_dict[message.from_user.id]['fullname']}</b>, проверьте, верны ли данные?",
                         reply_markup=await correct_check_kb(user_dict[message.from_user.id]["ptype"]),
                         parse_mode=ParseMode.HTML)


async def years_input(callback: types.CallbackQuery):
    if callback.data == 'Интеллектуальная собственность':
        await callback.message.answer(
            f"Введите кол-во лет, на которое хотите застраховать\nИнтеллектуальную собственность\n(1-30)")
    else:
        await callback.message.answer(
            f"Введите кол-во лет, на которое хотите застраховать\n{user_dict[callback.from_user.id]['ptype']}\n(1-30)")


async def product_yn_answer_info(callback: types.CallbackQuery):
    if callback.data == 'Да':
        loss_prob = 0.02
    else:
        loss_prob = 0.3
    await get_user_data_callback(callback, "loss", loss_prob)
    await callback.message.answer(f"Длительность страховки: <b>{user_dict[callback.from_user.id]['time']}</b>\n"
                                  f"Стоимость Виртуального товара: <b>{user_dict[callback.from_user.id]['sum']}</b>\n"
                                  f"Аккаунт хорошо защищён: {callback.data}",
                                  parse_mode=ParseMode.HTML)
    await callback.message.answer(f"<b>{user_dict[callback.from_user.id]['fullname']}</b>, проверьте, верны ли данные?",
                                  reply_markup=await correct_check_kb(user_dict[callback.from_user.id]["ptype"]),
                                  parse_mode=ParseMode.HTML)


# Просчёт страховок по моделям
async def years(time):
    dig = time % 10  # остаток от деления на 10
    if 10 < time < 20:
        year = "лет"
    elif 1 < dig < 5:
        year = "года"
    elif dig == 1:
        year = "год"
    else:
        year = "лет"
    return year


async def model_type_software(callback: types.CallbackQuery, user_data: dict):
    insurance_rate = 0.03  # ставка
    sum = int(user_data["sum"])
    time = int(user_data["time"])
    annual_insurance_premium = sum * insurance_rate  # Годовая страховая премия
    total_insurance_premium = annual_insurance_premium * time  # Общая страховая премия
    monthly_payment = int(total_insurance_premium / time / 12)
    await callback.message.answer(
        f"Годовая страховая премия при ставке страховой премии в 3 % составит"
        f" <b>{int(annual_insurance_premium)}</b>\n\n"
        f"Общая страховая премия на <b>{time}</b> {await years(time)} составит"
        f" <b>{int(total_insurance_premium)}</b> при ставке страховой премии в 3 %\n\n"
        f"Ежемесячный платеж составит <b>{int(monthly_payment)}</b>",
        parse_mode=ParseMode.HTML)


async def model_type_risks(callback: types.CallbackQuery, user_data: dict):
    sum = int(user_data["sum"])
    time = int(user_data["time"])
    if sum / time > 120000:
        insurance_rate = 0.03
    else:
        insurance_rate = 0.05  # ставка
    annual_insurance_premium = sum * insurance_rate  # Годовая страховая премия
    total_insurance_premium = annual_insurance_premium * time  # Общая страховая премия
    monthly_payment = int(total_insurance_premium / time / 12)
    await callback.message.answer(
        f"Годовая страховая премия при ставке страховой премии в <b>{int(insurance_rate * 100)}</b>"
        f" % составит <b>{int(annual_insurance_premium)}</b>\n\n"
        f"Общая страховая премия на <b>{time}</b> {await years(time)} составит"
        f" <b>{int(total_insurance_premium)}</b> при ставке страховой премии в {int(insurance_rate * 100)} %\n\n"
        f"Ежемесячный платеж составит <b>{int(monthly_payment)}</b>",
        parse_mode=ParseMode.HTML)


async def model_type_products(callback: types.CallbackQuery, user_data: dict):
    cost = int(user_data["sum"])
    time = int(user_data["time"])
    loss_prob = user_data["loss"]
    insurance_premium = cost * (1 - loss_prob) * 0.8
    monthly_payment = insurance_premium / 12 / time
    await callback.message.answer(f"Cтраховая премия составит <b>{int(insurance_premium)}</b>\n\n"
                                  f"Ежемесячный платеж составит <b>{int(monthly_payment)}</b>",
                                  parse_mode=ParseMode.HTML)


async def model_type_property(callback: types.CallbackQuery, user_data: dict):
    cost = int(user_data["sum"])
    time = int(user_data["time"])
    insurance_premium = cost * 0.2 * 1.2
    monthly_payment = insurance_premium / 12 / time
    await callback.message.answer(f"Cтраховая премия составит <b>{int(insurance_premium)}</b>\n\n"
                                  f"Ежемесячный платеж составит <b>{int(monthly_payment)}</b>",
                                  parse_mode=ParseMode.HTML)


async def send_application_email(user_data: dict):
    duration = user_data['time']
    # Формируем текст сообщения
    if user_data["ptype"] in ('Программное обеспечение', 'Информационные риски'):
        message_text = f"""
           Пользователь Telegram: {user_data['fullname']} хочет застраховать:
           - Тип товара: {user_data['ptype']}
           - Сумма страховки: {user_data['sum']}
           - Срок страхования: {duration} {await years(int(duration))}
           """
    elif user_data["ptype"] == "Виртуальные товары":
        if user_data["loss"] == '0.02':
            loss = "Да"
        else:
            loss = "Нет"
        message_text = f"""
            Пользователь Telegram: {user_data['fullname']} хочет застраховать:
            - Тип товара: {user_data['ptype']}
            - Стоимость вирт. товара: {user_data['sum']}
            - Срок страхования: {duration} {await years(int(duration))}
            - Аккаунт хорошо защищён: {loss}
            """
    else:
        message_text = f"""
            Пользователь Telegram: {user_data['fullname']} хочет застраховать:
            - Тип товара: {user_data['ptype']}
            - Стоимость ИС: {user_data['sum']}
            - Срок страхования: {duration} {await years(int(duration))}
            """

    # Настройки SMTP
    email_login = os.getenv('email_login')
    email_password = os.getenv('email_password')

    # Создаем объект MIMEText
    message = MIMEMultipart()
    message.attach(MIMEText(message_text))

    # Указываем адрес отправителя и получателя
    message['From'] = email_login
    message['To'] = 'krasovskiydiplom@gmail.com'
    message['Subject'] = 'Заявка на страхование'

    # Отправляем сообщение
    with smtplib.SMTP('smtp.mail.ru', 587) as server:
        server.starttls()
        server.login(email_login, email_password)
        server.sendmail(email_login, "krasovskiydiplom@gmail.com", message.as_string())
