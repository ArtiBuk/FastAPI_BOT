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


def get_update_user_for_admin_button(tg_id: int, users: list) -> types.ReplyKeyboardMarkup:
    if check_is_admin(tg_id):
        buttons = [[types.KeyboardButton(text=f"{index + 1}. {user}") for index, user in enumerate(users)],
                   [types.KeyboardButton(text="Отмена")]]

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            input_field_placeholder="Выберите пользователя или нажмите 'Отмена'"
        )
        return keyboard
    else:
        raise ValueError("Пользователь не является администратором")
