from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Настройки стилей для разных типов бланков
style_css = {
    0: {
        "Выдано": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                   'margin': "0", "high": "1"},
        "Место работы": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                         'margin': "0", "high": "1"},
        "Должность": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                      'margin': "0", "high": "1"},
        "УДОСТОВЕРЕНИЕ №": {'size': '12px', "weight": "bold", 'align': "left", "family": "Times New Roman",
                           "padding": "-0.5", 'margin': "0", "high": "1"},
        "Протокол заседания комиссии №": {'size': '10px', "weight": "normal", 'align': "left",
                                         "family": "Times New Roman", "padding": "0", 'margin': "0", "high": "1"},
        "Дата": {'size': '10px', "weight": "normal", 'align': "left", "family": "Times New Roman", "padding": "0",
                 'margin': "0", "high": "1"},
    },
    1: {
        "Выдано": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                   'margin': "0", "high": "1"},
        "Место работы": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                         'margin': "0", "high": "1"},
        "Должность": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                      'margin': "0", "high": "1"},
        "УДОСТОВЕРЕНИЕ №": {'size': '12px', "weight": "bold", 'align': "left", "family": "Times New Roman",
                           "padding": "-0.5", 'margin': "0", "high": "1"},
        "Протокол заседания комиссии №": {'size': '10px', "weight": "normal", 'align': "left",
                                         "family": "Times New Roman", "padding": "0", 'margin': "0", "high": "1"},
        "Дата": {'size': '10px', "weight": "normal", 'align': "left", "family": "Times New Roman", "padding": "0",
                 'margin': "0", "high": "1"},
    },
    2: {
        "Выдано": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                   'margin': "0", "high": "1"},
        "Место работы": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                         'margin': "0", "high": "1"},
        "Должность": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                      'margin': "0", "high": "1"},
        "УДОСТОВЕРЕНИЕ №": {'size': '12px', "weight": "bold", 'align': "left", "family": "Times New Roman",
                           "padding": "-0.5", 'margin': "0", "high": "1"},
        "Протокол заседания комиссии №": {'size': '10px', "weight": "normal", 'align': "left",
                                         "family": "Times New Roman", "padding": "0", 'margin': "0", "high": "1"},
        "Дата": {'size': '10px', "weight": "normal", 'align': "left", "family": "Times New Roman", "padding": "0",
                 'margin': "0", "high": "1"}
    },
    3: {
        "Выдано": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                   'margin': "0", "high": "0.9"},
        "Место работы": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                         'margin': "0", "high": "0.9"},
        "Должность": {'size': "12px", "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                      'margin': "0", "high": "0.9"},
        "УДОСТОВЕРЕНИЕ №": {'size': '12px', "weight": "bold", 'align': "left", "family": "Times New Roman",
                           "padding": "-0.5", 'margin': "0", "high": "0.9"},
        "Протокол №": {'size': '10px', "weight": "bold", 'align': "left", "family": "Times New Roman", "padding": "0",
                       'margin': "0", "high": "0.9"},
        "Дата": {'size': '10px', "weight": "bold", 'align': "left", "family": "Times New Roman", "padding": "0",
                 'margin': "0", "high": "0.9"},
    },
    4: {
        "Выдано": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                   'margin': "0", "high": "1"},
        "Место работы": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                         'margin': "0", "high": "1"},
        "Должность": {'size': '12px', "weight": "bold", 'align': "center", "family": "Georgia", "padding": "0",
                      'margin': "0", "high": "1"},
        "УДОСТОВЕРЕНИЕ №": {'size': '12px', "weight": "bold", 'align': "left", "family": "Times New Roman",
                           "padding": "-0.5", 'margin': "0", "high": "1"},
        "Протокол заседания комиссии №": {'size': '10px', "weight": "bold", "font-style": "italic", 'align': "left",
                                         "family": "Times New Roman", "padding": "0", 'margin': "0", "high": "1"},
        "Дата": {'size': '10px', "weight": "bold", "font-style": "italic", 'align': "left", "family": "Times New Roman",
                 "padding": "0", 'margin': "0", "high": "1"},
    }
}

correct_form_in_class = {
    0: {
        "Выдано": '<div class = "abx" style = "line-height: 1">',
        "Место работы": '<div class = "abx" style = "line-height: 1">',
        "Должность": '<div class = "abx">',
        "УДОСТОВЕРЕНИЕ №": '<div class = "abx">',
        "Протокол заседания комиссии №": '<div class = "abx">',
        "Дата": '<div class = "abx">'
    },
    1: {
        "Выдано": '<div class = "abx" style = "line-height: 1">',
        "Место работы": '<div class = "abx" style = "line-height: 1">',
        "Должность": '<div class = "abx">',
        "УДОСТОВЕРЕНИЕ №": '<div class = "abx">',
        "Протокол заседания комиссии №": '<div class = "abx">',
        "Дата": '<div class = "abx">'
    },
    2: {
        "Выдано": '<div class = "abx" style = "line-height: 1">',
        "Место работы": '<div class = "abx" style = "line-height: 1">',
        "Должность": '<div class = "abx">',
        "УДОСТОВЕРЕНИЕ №": '<div class = "abx">',
        "Протокол заседания комиссии №": '<div class = "abx">',
        "Дата": '<div class = "abx">'
    },
    3: {
        "Выдано": '<div class = "abx" style = "line-height: 0.9">',
        "Место работы": '<div class = "abx" style = "line-height: 0.9">',
        "Должность": '<div class = "abx" style = "line-height: 0.9">',
        "УДОСТОВЕРЕНИЕ №": '<div class = "abx">',
        "Протокол №": '<div class = "abx">',
        "Дата": '<div class = "abx">'
    },
    4: {
        "Выдано": '<div class = "abx" style = "line-height: 0.9">',
        "Место работы": '<div class = "abx" style = "line-height: 0.9">',
        "Должность": '<div class = "abx" style = "line-height: 0.9">',
        "УДОСТОВЕРЕНИЕ №": '<div class = "abx">',
        "Протокол заседания комиссии №": '<div class = "abx">',
        "Дата": '<div class = "abx">'
    },
}

coordinates = {
    0: {
        "Выдано": [-6, -1, 30, 1], "Место работы": [-37, 0, 60, 0], "Должность": [-15, 0, 30, 3],
        "УДОСТОВЕРЕНИЕ №": [0, 0, 0, 0], "Протокол заседания комиссии №": [0, 0, 0, 0],
        "Протокол №": [0, 0, 0, 0], "Дата": [0, 0, 0, 0]
    },
    1: {
        "Выдано": [-6, -1, 10, 1], "Место работы": [-35, 0, 60, 0], "Должность": [-45, 0, 50, 3],
        "УДОСТОВЕРЕНИЕ №": [0, 0, 0, 0], "Протокол заседания комиссии №": [0, 0, 0, 0],
        "Протокол №": [0, 0, 0, 0], "Дата": [0, 0, 0, 0]
    },
    2: {
        "Выдано": [-20, -1, 15, 1], "Место работы": [-40, 0, 65, 0], "Должность": [-35, 0, 50, 3],
        "УДОСТОВЕРЕНИЕ №": [0, 0, 0, 0], "Протокол заседания комиссии №": [0, 0, 0, 0],
        "Протокол №": [0, 0, 0, 0], "Дата": [0, 0, 0, 0]
    },
    3: {
        "Выдано": [-17, -1, 30, 1], "Место работы": [-40, 0, 60, 0], "Должность": [-20, 0, 40, 3],
        "УДОСТОВЕРЕНИЕ №": [0, 0, 0, 0], "Протокол заседания комиссии №": [0, 0, 0, 0],
        "Протокол №": [0, 0, 0, 0], "Дата": [0, 0, 0, 0]
    },
    4: {
        "Выдано": [-4, -1, 16, 1], "Место работы": [-40, 0, 70, 0], "Должность": [-60, 0, 75, 3],
        "УДОСТОВЕРЕНИЕ №": [0, 0, 0, 0], "Протокол заседания комиссии №": [0, 0, 0, 0],
        "Протокол №": [0, 0, 0, 0], "Дата": [0, 0, 0, 0]
    }
}

MONTHS_RU = {
    '01': "января",
    "02": "февраля",
    "03": "марта",
    "04": "апреля",
    "05": "мая",
    "06": "июня",
    "07": "июля",
    "08": "августа",
    "09": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря",
}


field_map = {
        "ФИО": ("Выдано", "Пожалуйста, отправьте ФИО (Александр Александров)"),
        "Место работы": ("Место работы", "Пожалуйста, введите Место работы (ООО Конус)"),
        "Должность": ("Должность", "Пожалуйста, введите Должность (электросварщик)"),
        "№ Удостоверения": ("Удост_№", "Пожалуйста, введите Номер Удостоверения (25665)"),
        "№ Протокола": ("ПРТ_№", "Пожалуйста, введите Номер Протокола"),
        "Дата": ("Дата", "Пожалуйста, введите Дату (26 янв 2025)")
    }

button_1 = KeyboardButton(text="Самописное определение")
button_2 = KeyboardButton(text="Определение через документ")
button_3 = KeyboardButton(text='Да')
button_4 = KeyboardButton(text='Нет')
button_5 = KeyboardButton(text='⬅️ Назад')
button_6 = KeyboardButton(text='❌ Неверно')
button_7 = KeyboardButton(text="✅ Верно")


button_8 = KeyboardButton(text="ФИО")
button_9 = KeyboardButton(text="Место работы")
button_10 = KeyboardButton(text="Должность")
button_11 = KeyboardButton(text="№ Удостоверения")
button_12 = KeyboardButton(text="№ Протокола")
button_13 = KeyboardButton(text="Дата")

keyboards = ReplyKeyboardMarkup(keyboard=[[button_1, button_2]], resize_keyboard=True)
keyboards_2 = ReplyKeyboardMarkup(keyboard=[[button_3, button_4]], resize_keyboard=True)
keyboards_3 = ReplyKeyboardMarkup(keyboard=[[button_5]], resize_keyboard=True)
keyboards_4 = ReplyKeyboardMarkup(keyboard=[[button_7],[button_6]], resize_keyboard=True)
keyboards_5 = ReplyKeyboardMarkup(keyboard=[[button_8],[button_9],[button_10],[button_11],[button_12],[button_13],], resize_keyboard=True)
# Хранение данных пользователей
users = {}
total_users = {}