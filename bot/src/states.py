from aiogram.fsm.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    waiting_action = State()


class RegistrationState(StatesGroup):
    waiting_username = State()
    waiting_fio = State()
    waiting_email = State()


class UpdateUserData(StatesGroup):
    waiting_what_to_update = State()


class SelectUserData(StatesGroup):
    waiting_what_to_get = State()


class UpdateUserDataForAdmin(StatesGroup):
    waiting_user = State()
    waiting_what_to_update = State()


class DeleteUserForAdmin(StatesGroup):
    waiting_user = State()


class TimeControl(StatesGroup):
    waiting_action = State()
    waiting_select_user = State()
    waiting_date_report = State()


class ObjectReport(StatesGroup):
    waiting_action = State()
    waiting_select_object = State()
    waiting_select_object_for_delete = State()
    waiting_date_report = State()
    waiting_report_format = State()


class ObjectCreateAdmin(StatesGroup):
    waiting_name_object = State()
    waiting_city_object = State()
    waiting_category_object = State()
