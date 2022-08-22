from aiogram import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from misc import dp, bot

# Заводим максимальынй стейт
class Scenarios(StatesGroup):
    welcome = State()
    registration = State()
    select_role = State()
    event_actions = State()
    select_event_type = State()
    select_city = State()
    offline_placement = State()
    create_name = State()
    create_description = State()
    datetime_start = State()
    datetime_finish = State()
    create_poll = State()
    send_location = State()
    checkin = State()
    false_date = State()
    send_event_to_bd = State()
    send_custom_location = State()
    # select_admin = State()
    # select_peer = State()
    # waiting_for_food_size = State()


class Auth(StatesGroup):
    email = State()
    code = State()

from src.prototype.handlers import handlers, auth_handlers


def main():
    # init_handlers(dp, bot)
    handlers.init_handlers(dp, bot)
    auth_handlers.init_auth_handlers(dp, bot)
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    # Запуск бота
    main()
    # executor.start_polling(dp, skip_updates=True)
