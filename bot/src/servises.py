import re
from datetime import datetime

from src.schemas import UpdateForAdminApi, UpdateUserApi


def check_is_admin(tg_id: int) -> bool:
    from src.handlers import USER
    if USER.get(tg_id):
        return True
    else:
        return False


def get_id_from_message(message: str) -> int | str:
    pattern = r'\(tg_id:\s*(\d+)\)'
    match = re.search(pattern, message)
    if match:
        tg_id = match.group(1)
        return int(tg_id)
    else:
        print("tg_id не найден")


def parse_update_by_admin_message(message: str) -> UpdateForAdminApi:
    lines = message.split('\n')
    username = lines[0].strip()
    last_name = lines[1].strip()
    first_name = lines[2].strip()
    middle_name = lines[3].strip()
    email = (lines[4].strip())
    is_admin = True if lines[5].strip().lower() == 'да' else False

    return UpdateForAdminApi(
        username=username if username != '0' else None,
        first_name=first_name if first_name != '0' else None,
        last_name=last_name if last_name != '0' else None,
        middle_name=middle_name if middle_name != '0' else None,
        tg_id=None,
        email=email if email != '0' else None,
        is_admin=is_admin if is_admin != '0' else None,
        right=None
    )


def parse_update_message(message: str) -> UpdateUserApi:
    lines = message.split('\n')
    last_name = lines[0].strip()
    first_name = lines[1].strip()
    middle_name = lines[2].strip()
    email = (lines[3].strip())

    return UpdateUserApi(
        first_name=first_name if first_name != '0' else None,
        last_name=last_name if last_name != '0' else None,
        middle_name=middle_name if middle_name != '0' else None,
        tg_id=None,
        email=email if email != '0' else None,
    )


def format_user_get_me(response: dict) -> str:
    access_info = response.get('access')
    if access_info is None:
        access_message = "Не имеет доступа"
    else:
        access_message = "Имеет доступ:"
        for obj in access_info['object']:
            access_message += f"\n- {obj['name']} ({obj['category']}, {obj['city']})"

    result_message = (
        f"Логин: {response.get('username')}\n"
        f"Фамилия: {response.get('first_name')}\n"
        f"Имя: {response.get('last_name')}\n"
        f"Отчетсво: {response.get('middle_name')}\n"
        f"Твой ID в телеграм: {response.get('tg_id')}\n"
        f"Email: {response.get('email')}\n"
        f"Является ли админом: {'Да' if response.get('is_admin') else 'Нет'}\n"
        f"{access_message}\n"
        f"\nЧем я вам могу помочь еще?"
    )

    return result_message


def parse_dates_from_message(message_text: str) -> tuple[datetime, datetime]:
    date_strings = message_text.split('\n')
    date_start = None
    date_end = None
    for idx, date_string in enumerate(date_strings):
        try:
            date_object = datetime.strptime(date_string.strip(), '%d.%m.%Y')
            if idx == 0:
                date_start = date_object
            elif idx == 1:
                date_end = date_object
        except ValueError:
            print(f"Ошибка при парсинге даты: {date_string}")
    if date_start and date_end:
        if date_start >= date_end:
            raise ValueError("Дата начала должна быть раньше даты окончания")

    return date_start, date_end


def parse_date_from_response(reports: list[dict]):
    message = ""
    for idx, report in enumerate(reports, start=1):
        message += f"Отчет #{idx}:\n"
        message += f"Дата начала: {report['date_start']}\n"
        message += f"Дата окончания: {report['date_end']}\n"
        message += f"Отработанные часы: {int(report['working_hours']) // 60}\n"
        message += f"Отработанные минуты: {(int(report['working_hours']) % 60):02d}\n"
        message += "-------------------------------------\n\n"

    return message
