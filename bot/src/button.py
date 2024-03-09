from aiogram import types

from src.servises import check_is_admin


def get_main_button(is_auth: bool, tg_id: int | None) -> types.ReplyKeyboardMarkup:
    if is_auth:
        if check_is_admin(tg_id):
            bt = [
                [types.KeyboardButton(text="TimeControl")],
                [types.KeyboardButton(text="Отчеты объектов")],
                [types.KeyboardButton(text="Информация о пользователях")],
                [types.KeyboardButton(text="Редактировать свои данные")],
                [types.KeyboardButton(text="Редактировать пользователя")],
                [types.KeyboardButton(text="Удалить пользователя")],
                [types.KeyboardButton(text="Посмотреть свои данные")]
            ]
        else:
            bt = [
                [types.KeyboardButton(text="TimeControl")],
                [types.KeyboardButton(text="Отчеты объектов")],
                [types.KeyboardButton(text="Редактировать свои данные")],
                [types.KeyboardButton(text="Посмотреть свои данные")]
            ]
        button = types.ReplyKeyboardMarkup(
            keyboard=bt,
            resize_keyboard=True,
            input_field_placeholder="Выберете действие"
        )
        return button


def get_time_control_button(tg_id: int) -> types.ReplyKeyboardMarkup:
    from src.handlers import USER
    if USER.get(tg_id):
        bt = [
            [types.KeyboardButton(text="Поставить отметку о начале работы")],
            [types.KeyboardButton(text="Поставить отметку о конце работы")],
            [types.KeyboardButton(text="Посмотреть свои отчеты за период")],
            [types.KeyboardButton(text="Посмотреть отчеты выбранного пользователя")],
        ]
    else:
        bt = [
            [types.KeyboardButton(text="Поставить отметку о начале работы")],
            [types.KeyboardButton(text="Поставить отметку о конце работы")],
            [types.KeyboardButton(text="Посмотреть свои отчеты за период")],
        ]

    button = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберете действие"
    )
    return button


def get_report_to_object_button(tg_id: int) -> types.ReplyKeyboardMarkup:
    from src.handlers import USER
    if USER.get(tg_id):
        bt = [
            [types.KeyboardButton(text="Просмотр отчет по выбранному объекту за период")],
            [types.KeyboardButton(text="Создать объект")],
            [types.KeyboardButton(text="Удалить объект")],
        ]
    else:
        bt = [
            [types.KeyboardButton(text="Просмотр отчет по выбранной точке за период")],
            [types.KeyboardButton(text="Посмотреть итоговый отчет за месяц")],
        ]
    button = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберете действие"
    )
    return button


def format_to_object_report() -> types.ReplyKeyboardMarkup:
    bt = [
        [types.KeyboardButton(text="Сообщением")],
        [types.KeyboardButton(text="Excel")],
    ]
    button = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберете формат отчета"
    )
    return button


def get_update_user_for_admin_button(tg_id: int, users: list) -> types.ReplyKeyboardMarkup:
    if check_is_admin(tg_id):
        MAX_BUTTONS_IN_ROW = 3
        bt = []
        row = []

        for index, user in enumerate(users, start=1):
            row.append(types.KeyboardButton(text=f"{index}. {user}"))
            if len(row) == MAX_BUTTONS_IN_ROW or index == len(users):
                bt.append(row)
                row = []

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=bt,
            resize_keyboard=True,
            input_field_placeholder="Выберите пользователя или нажмите 'Отмена'"
        )
        return keyboard
    else:
        raise ValueError("Пользователь не является администратором")


def get_object_button(object_list: list) -> types.ReplyKeyboardMarkup:
    MAX_BUTTONS_IN_ROW = 2
    bt = []
    row = []

    for index, obj in enumerate(object_list, start=1):
        row.append(types.KeyboardButton(text=f"{index}. {obj}"))
        if len(row) == MAX_BUTTONS_IN_ROW or index == len(object_list):
            bt.append(row)
            row = []

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберите объект или нажмите 'Отмена'"
    )

    return keyboard


def city_object_select() -> types.ReplyKeyboardMarkup:
    bt = [
        [types.KeyboardButton(text="Норильск")],
        [types.KeyboardButton(text="Талнах")],
        [types.KeyboardButton(text="Кайркан")],
        [types.KeyboardButton(text="Кайркан")],
    ]
    button = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберете город"
    )
    return button


def category_object_select() -> types.ReplyKeyboardMarkup:
    bt = [
        [types.KeyboardButton(text="Рестаран")],
        [types.KeyboardButton(text="Fast food")],
        [types.KeyboardButton(text="Хостел")],
        [types.KeyboardButton(text="Десткий центр")],
    ]
    button = types.ReplyKeyboardMarkup(
        keyboard=bt,
        resize_keyboard=True,
        input_field_placeholder="Выберете категорию"
    )
    return button
