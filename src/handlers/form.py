import asyncio
import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from src.models.constants import users, MONTHS_RU, field_map, keyboards, keyboards_2, keyboards_3, keyboards_4, keyboards_5
from aiogram.types import ErrorEvent
from aiogram.filters.exception import ExceptionTypeFilter
from src.services.docx_generator import fill_docx_template

router = Router()


@router.error(ExceptionTypeFilter(KeyError))
async def key_error_handler(event: ErrorEvent):
    message = event.update.message
    if message:
        await message.answer(text='Пожалуйста, нажмите кнопку "Start" в главном меню слева внизу')


@router.error()
async def global_error_handler(event: ErrorEvent):
    print("Unexpected error:", repr(event.exception))


def _reset_user_state(user_id: int, wr_dt: bool = False, aut_dep: bool = False):

    users[user_id] = {
        'wr_dt': wr_dt,
        'aut_dep': aut_dep,
        'current_stp': "Выдано",
        'for_cancel': "",
        'field_to_change': "",
        'text': "",
        "status_corr_data": "",
        "blanks_count": {"А": 0, "Б": 0, "В": 0, "ПП": 0, "СИЗ": 0,
                        "З1": 0, "З2": 0, "З3": 0, "В1": 0, "В2": 0, "В3": 0},
        'Выдано': '',
        'Место работы': '',
        'Должность': '',
        'Удост_№': '',
        'ПРТ_№': '',
        'Дата': ''
    }


def _normalize_blank_token(raw: str) -> str:

    if raw is None:
        return ""

    s = str(raw).strip()
    if not s:
        return ""

    s_up = s.upper()

    # Частые случаи, когда “АБВ” набрали в EN-раскладке
    if s_up == "F":
        return "А"
    if s == "," or s_up == "<":
        return "Б"
    if s_up == "D":
        return "В"

    # Латиница для А/Б/В
    if s_up == "A":
        return "А"
    if s_up == "B":
        return "Б"
    if s_up == "V":
        return "В"

    # PP / OT / SIZ латиницей
    if s_up == "PP":
        return "ПП"
    if s_up in {"OT", "ОТ"}:
        return "СИЗ"
    if s_up == "SIZ" or s_up == "СИЗ":
        return "СИЗ"

    # C1..C3 / T1..T3 латиницей
    if len(s_up) == 2 and s_up[1].isdigit():
        letter, digit = s_up[0], s_up[1]
        if letter == "З" and digit in ("1", "2", "3"):
            return f"З{digit}"
        if letter == "В" and digit in ("1", "2", "3"):
            return f"В{digit}"

    # Русские токены (в любом регистре)
    if s_up in {"А", "Б", "В", "ПП", "СИЗ", "З1", "З2", "З3", "В1", "В2", "В3"}:
        return s_up

    return ""


@router.message(CommandStart())
async def send_start(message: Message):
    await message.answer('👋 Здравствуйте! Пожалуйста, выберите в главном меню функцию',
                         reply_markup=keyboards)
    _reset_user_state(message.from_user.id, wr_dt=False, aut_dep=False)


@router.message(lambda x: users[x.from_user.id]['current_stp'] == "numbers_blank")
async def send_number(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id)

    raw_tokens = [t for t in (message.text or "").split() if t.strip()]

    try:
        allowed = {"А", "Б", "В", "ПП", "СИЗ", "З1", "З2", "З3", "В1", "В2", "В3"}

        # Сбрасываем прошлый выбор бланков, чтобы новый ввод не “добавлялся” к старому
        users[user_id]["blanks_count"] = {k: 0 for k in users[user_id]["blanks_count"].keys()}

        for raw in raw_tokens:
            token = _normalize_blank_token(raw)
            if token in allowed:
                users[user_id]["blanks_count"][token] = 1

        await asyncio.sleep(0.5)
        await message.answer(
            "✅ Отлично! Начинается генерация DOCX...",
            reply_markup=ReplyKeyboardRemove()
        )

        # Генерируем один DOCX со всеми выбранными бланками
        output_file_for_docx = fill_docx_template(user_data)

        if output_file_for_docx and os.path.exists(output_file_for_docx):
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(output_file_for_docx),
                caption=f"📝 Бланки для {user_data.get('Выдано', '')}"
            )
            os.remove(output_file_for_docx)
        else:
            await message.answer("❌ DOCX файл не был создан!")
            users[user_id]["current_stp"] = "numbers_blank"
            return

        # ВАЖНО: fill_docx_template обновляет user_data["Удост_№"] (конечный номер)
        users[user_id]["Удост_№"] = user_data.get("Удост_№", users[user_id].get("Удост_№", ""))

        users[user_id]["current_stp"] = "all"
        await message.answer("Если хотите создать еще, нажмите кнопку 'Да' в меню", reply_markup=keyboards_2)

    except ValueError:
        await message.answer(text="❌ Неправильная форма ввода. Попробуйте еще раз")
    except Exception as e:
        print(f"Общая ошибка в send_number: {e}")
        await message.answer("❌ Произошла ошибка при генерации DOCX")


@router.message(F.text == "✅ Верно")
async def corr_datas(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id)
    if not user_data:
        await message.answer('Пожалуйста, нажмите /start')
        return

    users[user_id]['current_stp'] = "numbers_blank"
    await message.answer(text="✅ Отлично! Остался последний шаг")
    await asyncio.sleep(0.5)
    await message.answer(
        text="Пожалуйста, введите типы бланков для генерации. Формат:\n\n"
             "📋 Типы бланков: А Б В ПП СИЗ З1 З2 З3 В1 В2 В3\n"
             "💡 Пример: А П1 В2\n\n"
             "Введите: ",
        reply_markup = ReplyKeyboardRemove())


@router.message(F.text == "❌ Неверно")
async def not_corr_datas(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    users[user_id]['status_corr_data'] = 'in_process'
    await message.answer(text="❗ Пожалуйста,выберите неправильный пункт", reply_markup=keyboards_5)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['status_corr_data'] == "change_dt")
async def change_wrong_field(message: Message):
    user_id = message.from_user.id
    field_value = message.text.strip()
    target = users[user_id]['for_cancel']
    field_key = users[user_id].get('field_to_change')

    if target == 'Место работы':
        parts = field_value.split()
        if len(parts) < 2:
            await message.answer('Неправильная форма ввода! Пожалуйста, введите в формате: ООО Конус')
            return
        value = f'{parts[0]} «{parts[1]}»'
        users[user_id]['Место работы'] = value

    elif target == 'Дата':
        parts = field_value.split()
        if len(parts) != 3:
            await message.answer('Неправильная форма ввода! Пожалуйста, введите дату в формате: 26 09 25')
            return

        day, month_num, year_suffix = parts

        if month_num not in MONTHS_RU:
            await message.answer('Неправильный месяц! Используйте формат: 26 09 25 (месяц числом, например 09)')
            return

        users[user_id]['Дата'] = f'«{day}» {MONTHS_RU[month_num]} 20{year_suffix}г'

    else:
        if field_key:
            users[user_id][field_key] = field_value
        else:
            for key, val in users[user_id].items():
                if val == '':
                    users[user_id][key] = field_value
                    break

    users[user_id]["status_corr_data"] = "stop_process"
    await message.answer(text='✅ Данные успешно изменены. Проверьте правильность вновь')
    await asyncio.sleep(0.5)
    await message.answer(
        text=f"🟡 ФИО: {users[user_id]['Выдано']},\n"
             f"🟡 Место работы: {users[user_id]['Место работы']},\n"
             f"🟡 Должность: {users[user_id]['Должность']},\n"
             f"🟡 № Удостоверения: {users[user_id]['Удост_№']},\n"
             f"🟡 № Протокола: {users[user_id]['ПРТ_№']},\n"
             f"🟡 Дата: {users[user_id]['Дата']}\n",
        reply_markup=keyboards_4
    )
    users[user_id]['status_corr_data'] = 'stop'
    users[user_id]['field_to_change'] = ""


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['status_corr_data'] == "in_process")
async def edit_wrong_field(message: Message):
    user_id = message.from_user.id
    field_name = message.text.strip()

    if field_name not in field_map:
        await message.answer(text="❗ Выберите поле из клавиатуры!", reply_markup=keyboards_5)
        return

    field_key = field_map[field_name][0]
    users[user_id][field_key] = ''
    users[user_id]["status_corr_data"] = "change_dt"
    users[user_id]["for_cancel"] = field_name
    users[user_id]["field_to_change"] = field_key

    # ---- FIX ошибки (6): убрать меню кнопок на время ввода нового значения ----
    await message.answer(text='✅ Поле успешно очищено...', reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.5)
    await message.answer(text='❗ Пожалуйста, введите корректные данные')


@router.message(F.text == "⬅️ Назад")
async def send_button1(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    # ---- FIX ошибки (5): если человек нажал "назад" в самом начале/сломался stp ----
    if users[user_id].get('wr_dt') and users[user_id].get('current_stp') == "Выдано":
        users[user_id]['Выдано'] = ""
        users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
        await message.answer("↩️ Возврат к вводу ФИО", reply_markup=keyboards_3)
        await message.answer(text="❗ Пожалуйста, отправьте ФИО", reply_markup=keyboards_3)
        return

    await message.answer("✅ Хорошо, исправим предыдущий шаг!")

    # если for_cancel пустой — возвращаем в начало ввода ФИО
    if not users[user_id].get('for_cancel'):
        users[user_id]['current_stp'] = "Выдано"
        users[user_id]['Выдано'] = ""
        users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
        await message.answer(text="❗ Пожалуйста, отправьте ФИО", reply_markup=keyboards_3)
        return

    users[user_id]['current_stp'] = users[user_id]['for_cancel']
    tem = users[user_id]['current_stp']
    if tem in users[user_id]:
        users[user_id][tem] = ""

    await asyncio.sleep(0.5)
    await message.answer(f'{users[user_id]["text"]}', reply_markup=keyboards_3)


@router.message(F.text == "Самописное определение")
async def send_button2(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    await message.answer(text="✅ Отлично, заполняйте данные следуя инструкциям",
                         reply_markup=ReplyKeyboardRemove())

    users[user_id]['wr_dt'] = True
    users[user_id]['aut_dep'] = False
    users[user_id]['current_stp'] = "Выдано"
    users[user_id]['for_cancel'] = ""
    users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
    users[user_id]['Выдано'] = ""

    await asyncio.sleep(0.3)
    await message.answer(text="❗ Пожалуйста, отправьте ФИО", reply_markup=keyboards_3)


@router.message(F.text == "Определение через документ")
async def send_button3(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    await message.answer(text="❗ Пожалуйста, отправьте файл с данными", reply_markup=ReplyKeyboardRemove())
    users[user_id]['aut_dep'] = True


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "Выдано"
                and users[x.from_user.id]['Выдано'] == "")
async def send_wr_dt1(message: Message):
    user_id = message.from_user.id

    fio = (message.text or "").strip()
    parts = [p for p in fio.split() if p]
    if len(parts) < 3:
        await message.answer(
            "❌ Неправильная форма ввода!\n"
            "Введите ФИО в формате: Фамилия Имя Отчество"
        )
        return

    await message.answer("✅ Отлично! Переходим к следующему шагу")
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'Место работы'
    users[user_id]['Выдано'] = fio
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
    await message.answer(
        text='❗ Пожалуйста, введите Место работы (Форма: ООО Конус (без кавычек))',
        reply_markup=keyboards_3
    )


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "Место работы"
                and users[x.from_user.id]['Место работы'] == "")
async def send_wr_dt2(message: Message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(text='Неправильная форма ввода! Пожалуйста, введите корректную форму: ООО Конус')
        return

    users[user_id]['Место работы'] = f'{parts[0]} «{parts[1]}»'
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'Должность'
    await message.answer("✅ Отлично! Переходим к следующему шагу")
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, введите Место работы (Форма: ООО Конус (без кавычек))'
    await message.answer(text='❗ Пожалуйста, введите Должность', reply_markup=keyboards_3)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "Должность"
                and users[x.from_user.id]['Должность'] == "")
async def send_wr_dt3(message: Message):
    user_id = message.from_user.id
    await message.answer("✅ Отлично! Переходим к следующему шагу")
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'Удост_№'
    users[user_id]['Должность'] = message.text
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, введите Должность'
    await message.answer(text='❗ Пожалуйста, введите Номер Удостоверения (Форма: 25665)',
                         reply_markup=keyboards_3)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "Удост_№"
                and users[x.from_user.id]['Удост_№'] == "" and x.text and x.text.isdigit())
async def send_wr_dt4(message: Message):
    user_id = message.from_user.id
    await message.answer("✅ Отлично! Переходим к следующему шагу")
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'ПРТ_№'
    users[user_id]['Удост_№'] = message.text
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, введите Номер Удостоверения (Форма: 25665)'
    await message.answer(text='❗ Пожалуйста, введите Номер Протокола', reply_markup=keyboards_3)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "ПРТ_№"
                and users[x.from_user.id]['ПРТ_№'] == "" and x.text and x.text.isdigit())
async def send_wr_dt5(message: Message):
    user_id = message.from_user.id
    await message.answer("✅ Отлично! Переходим к следующему шагу")
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'Дата'
    users[user_id]['ПРТ_№'] = message.text
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, введите Номер Протокола'
    await message.answer(text='❗ Пожалуйста, введите Дату (Пример: 26 09 25 )',
                         reply_markup=keyboards_3)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['wr_dt'] is True
                and users[x.from_user.id]['current_stp'] == "Дата"
                and users[x.from_user.id]['Дата'] == "")
async def send_wr_dt6(message: Message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(text='Неправильная форма ввода! Пожалуйста, введите дату в формате: 26 09 25')
        return

    day, month_num, year_suffix = parts
    if month_num not in MONTHS_RU:
        await message.answer(
            text='Неправильный месяц! Используйте формат: 26 09 25 (месяц числом, например 09)'
        )
        return

    users[user_id]['Дата'] = f'«{int(day):02d}» {MONTHS_RU[month_num]} 20{year_suffix}г'
    await message.answer(text="❗ Пожалуйста, проверьте правильность полученных данных",
                         reply_markup=keyboards_4)
    await asyncio.sleep(1)
    await message.answer(text=f"🟡 ФИО: {users[user_id]['Выдано']},\n"
                              f"🟡 Место работы: {users[user_id]['Место работы']},\n"
                              f"🟡 Должность: {users[user_id]['Должность']},\n"
                              f"🟡 № Удостоверения: {users[user_id]['Удост_№']},\n"
                              f"🟡 № Протокола: {users[user_id]['ПРТ_№']},\n"
                              f"🟡 Дата: {users[user_id]['Дата']}\n")


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['current_stp'] == 'all'
                and x.text == 'Да')
async def send_wr_dt_yes(message: Message):
    user_id = message.from_user.id
    _reset_user_state(user_id, wr_dt=True, aut_dep=False)
    await message.answer(text='✅ Отлично! Приступим к заполнению!',
                         reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.3)
    await message.answer(text='❗ Пожалуйста, отправьте ФИО', reply_markup=keyboards_3)


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['current_stp'] == 'all'
                and x.text == 'Нет')
async def send_wr_dt_no(message: Message):
    user_id = message.from_user.id
    _reset_user_state(user_id, wr_dt=False, aut_dep=False)
    await message.answer(text='Понадобится помощь - пишите!',
                         reply_markup=ReplyKeyboardRemove())


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['aut_dep'] is True and x.document)
async def handle_document(message: Message):
    user_id = message.from_user.id
    await message.answer(
        text='Функция обработки документов находится в разработке. Пожалуйста, используйте "Самописное определение".')
    users[user_id]['aut_dep'] = False
    await message.answer("Пожалуйста, выберите в главном меню функцию", reply_markup=keyboards)


@router.message()
async def send_msg(message: Message):
    user_state = users.get(message.from_user.id)
    if not user_state:
        await message.answer('Пожалуйста, нажмите /start')
        return

    if not user_state['wr_dt'] and not user_state['aut_dep']:
        await message.answer("❗ Пожалуйста, выберите в главном меню функцию",
                             reply_markup=keyboards)
    else:
        await message.answer("❗ Возможно, вы неправильно заполнили форму. Попробуйте еще раз")
