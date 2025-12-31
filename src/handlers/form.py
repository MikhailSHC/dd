import asyncio
import os
import time

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from src.models.constants import users, MONTHS_RU, field_map, keyboards, keyboards_2, keyboards_3, keyboards_4, keyboards_5
from src.services.pdf_generator import generate_blanks
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


@router.message(CommandStart())
async def send_start(message: Message):
    await message.answer('👋 Здравствуйте! Пожалуйста, выберите в главном меню функцию',
                         reply_markup=keyboards)
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            'wr_dt': False,
            'aut_dep': False,
            'current_stp': "Выдано",
            'for_cancel': "",
            'field_to_change': "",
            'text': "",
            "status_corr_data": "",
            "blanks_count": {"А":0,"Б":0,"В":0,"ПП":0,"ОТ":0,
                 "С1":0,"С2":0,"С3":0,"Т1":0,"Т2":0,"Т3":0},  # ← РУССКИЕ БУКВЫ

            'Выдано': '',
            'Место работы': '',
            'Должность': '',
            'Удост_№': '',
            'ПРТ_№': '',
            'Дата': ''
        }
    else:
        users[message.from_user.id] = {
            'wr_dt': False,
            'aut_dep': False,
            'current_stp': "Выдано",
            'for_cancel': "",
            'field_to_change': "",
            'text': "",
            "status_corr_data": "",
            "blanks_count": {"А":0,"Б":0,"В":0,"ПП":0,"ОТ":0,
                 "С1":0,"С2":0,"С3":0,"Т1":0,"Т2":0,"Т3":0},  # ← РУССКИЕ БУКВЫ

            'Выдано': '',
            'Место работы': '',
            'Должность': '',
            'Удост_№': '',
            'ПРТ_№': '',
            'Дата': ''
        }


@router.message(lambda x: users[x.from_user.id]['current_stp'] == "numbers_blank")
async def send_number(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id)
    mess = message.text.split(" ")
    try:
        str_format = list(map(str, mess))
        for group in str_format:
            if group == "А":
                users[user_id]['blanks_count']["А"] = 1
            elif group == "Б":
                users[user_id]['blanks_count']["Б"] = 1
            elif group == "В":
                users[user_id]['blanks_count']["В"] = 1
            elif group == "ПП":
                users[user_id]['blanks_count']["ПП"] = 1
            elif group == "ОТ":
                users[user_id]['blanks_count']["ОТ"] = 1

            elif group == "С1":
                users[user_id]['blanks_count']["С1"] = 1
            elif group == "С2":
                users[user_id]['blanks_count']["С2"] = 1
            elif group == "С3":
                users[user_id]['blanks_count']["С3"] = 1
            elif group == "Т1":
                users[user_id]['blanks_count']["Т1"] = 1
            elif group == "Т2":
                users[user_id]['blanks_count']["Т2"] = 1
            elif group == "Т3":
                users[user_id]['blanks_count']["Т3"] = 1

        await asyncio.sleep(0.5)
        await message.answer("✅ Отлично! Начинается процесс генерации...", reply_markup=ReplyKeyboardRemove())
        filename = f"blanks_{user_id}_{int(time.time())}.pdf"
        output_file = generate_blanks(user_data, users[user_id]['blanks_count'], filename)

        if os.path.exists(output_file):
            await message.answer("📄 Файл готов, отправляю...")

            # Отправляем PDF
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(output_file),
                caption=f"✅ Бланки для {user_data['Выдано']}"
            )

            # Генерация и отправка DOCX
            try:
                output_file_for_docx = fill_docx_template(user_data)
                if output_file_for_docx and os.path.exists(output_file_for_docx):
                    await message.bot.send_document(
                        chat_id=message.chat.id,
                        document=FSInputFile(output_file_for_docx),
                        caption=f"📝 Документ для {user_data['Выдано']}"
                    )
                    # Удаляем временный DOCX файл
                    os.remove(output_file_for_docx)
                else:
                    print("❌ DOCX файл не был создан")
            except Exception as e:
                print(f"⚠️ Ошибка при работе с DOCX: {e}")

            # Удаляем PDF файл
            os.remove(output_file)

            # Меняем состояние пользователя
            users[user_id]['current_stp'] = 'all'
            await message.answer("Если хотите создать еще, нажмите кнопку 'Да' в меню", reply_markup=keyboards_2)

        else:
            await message.answer("❌ PDF файл не создался!")

    except ValueError:
        await message.answer(text="❌ Неправильная форма ввода. Попробуйте еще раз")
    except Exception as e:
        print(f"Общая ошибка в send_number: {e}")
        await message.answer("❌ Произошла ошибка при генерации файлов")



@router.message(F.text == "✅ Верно")
async def corr_datas(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id)
    if not user_data:
        await message.answer('Пожалуйста, нажмите /start')
        return

    users[message.from_user.id]['current_stp'] = "numbers_blank"
    await message.answer(text="✅ Отлично! Остался последний шаг")
    await asyncio.sleep(0.5)
    await message.answer(text="Пожалуйста, введите количество бланков для генерации. Форма:\n\n"
                              "📋 Количество бланков (А Б В ПП ОТ):\n"
                              "💡 Пример: 1 2 1 0 3\n\n"
                              "Введите: """)


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
    field_value = message.text.strip()          # новое значение
    target = users[user_id]['for_cancel']       # человекочитаемое имя поля
    field_key = users[user_id].get('field_to_change')  # ключ в словаре users[user_id]

    # Если исправляем "Место работы" — проверяем формат "ООО Конус"
    if target == 'Место работы':
        parts = field_value.split()
        if len(parts) < 2:
            await message.answer(
                'Неправильная форма ввода! Пожалуйста, введите в формате: ООО Конус'
            )
            return
        value = f'{parts[0]} «{parts[1]}»'
        users[user_id]['Место работы'] = value

    # Если исправляем "Дата" — проверяем формат "26 09 25"
    elif target == 'Дата':
        parts = field_value.split()
        if len(parts) != 3:
            await message.answer(
                'Неправильная форма ввода! Пожалуйста, введите дату в формате: 26 09 25'
            )
            return

        day, month_num, year_suffix = parts

        if month_num not in MONTHS_RU:
            await message.answer(
                'Неправильный месяц! Используйте формат: 26 09 25 (месяц числом, например 09)'
            )
            return

        users[user_id]['Дата'] = f'«{day}» {MONTHS_RU[month_num]} 20{year_suffix}г'

    # Все остальные поля: записываем по field_key, если он есть
    else:
        if field_key:
            users[user_id][field_key] = field_value
        else:
            # fallback: старое поведение через поиск первого пустого
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
    await message.answer(text='✅ Поле успешно очищено...')
    await asyncio.sleep(0.5)
    await message.answer(text='❗ Пожалуйста, введите корректные данные')


@router.message(F.text == "⬅️ Назад")
async def send_button1(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    await message.answer("✅ Хорошо, исправим предыдущий шаг!")
    users[user_id]['current_stp'] = users[user_id]['for_cancel']
    tem = users[user_id]['current_stp']
    if tem in users[user_id]:
        users[user_id][tem] = ""
    await asyncio.sleep(0.5)
    await message.answer(f'{users[user_id]["text"]}')


@router.message(F.text == "Самописное определение")
async def send_button2(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Пожалуйста, нажмите /start')
        return

    await message.answer(text="✅ Отлично, заполняйте данные следуя инструкциям",
                         reply_markup=ReplyKeyboardRemove())
    users[user_id]['wr_dt'] = True
    await asyncio.sleep(1)
    users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
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
    await message.answer("✅ Отлично! Переходим к следующему шагу")
    users[user_id]['for_cancel'] = users[user_id]['current_stp']
    users[user_id]['current_stp'] = 'Место работы'
    users[user_id]['Выдано'] = message.text
    await asyncio.sleep(0.5)
    users[user_id]['text'] = '❗ Пожалуйста, отправьте ФИО'
    await message.answer(text='❗ Пожалуйста, введите Место работы (Форма: ООО Конус (без кавычек))',
                         reply_markup=keyboards_3)


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

    users[user_id]['Дата'] = f'«{day}» {MONTHS_RU[month_num]} 20{year_suffix}г'
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
    users[user_id] = {
        'wr_dt': True,
        'aut_dep': False,
        'current_stp': "Выдано",
        'for_cancel': "",
        'field_to_change': "",
        'text': "",
        "status_corr_data": "",
        "blanks_count": {"А":0,"Б":0,"В":0,"ПП":0,"ОТ":0,
                             "C1":0,"C2":0,"C3":0,"T1":0,"T2":0,"T3":0},
        'Выдано': '',
        'Место работы': '',
        'Должность': '',
        'Удост_№': '',
        'ПРТ_№': '',
        'Дата': ''
    }
    await message.answer(text='✅ Отлично! Приступим к заполнению!',
                         reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await message.answer(text='❗ Пожалуйста, отправьте ФИО')


@router.message(lambda x: x.from_user.id in users and users[x.from_user.id]['current_stp'] == 'all'
                and x.text == 'Нет')
async def send_wr_dt_no(message: Message):
    user_id = message.from_user.id
    users[user_id] = {
        'wr_dt': False,
        'aut_dep': False,
        'current_stp': "Выдано",
        'for_cancel': "",
        'field_to_change': "",
        'text': "",
        "status_corr_data": "",
        "blanks_count": {"А":0,"Б":0,"В":0,"ПП":0,"ОТ":0,
                             "C1":0,"C2":0,"C3":0,"T1":0,"T2":0,"T3":0},
        'Выдано': '',
        'Место работы': '',
        'Должность': '',
        'Удост_№': '',
        'ПРТ_№': '',
        'Дата': ''
    }
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
