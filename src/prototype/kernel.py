from aiogram import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from misc import dp, bot


# Заводим максимальынй стейт
class Scenarios(StatesGroup):
    welcome = State()
    registration = State()
    select_role = State()


class AdminState(StatesGroup):
    event_actions = State()
    select_event_type = State()
    select_city = State()
    offline_placement = State()
    create_name = State()
    create_description = State()
    datetime_start = State()
    datetime_finish = State()
    create_poll = State()
    false_date = State()
    send_event_to_bd = State()
    send_custom_location = State()


class PeerState(StatesGroup):
    checkin = State()
    send_location = State()


class Auth(StatesGroup):
    email = State()
    code = State()


import handlers_auth, handlers_peer, handlers_admin
import handlers


def main():
    # init handlers
    handlers.init_handlers(dp, bot)
    handlers_auth.init_handlers_auth(dp, bot)
    handlers_admin.init_handlers_admin(dp, bot)
    handlers_peer.init_handlers_peer(dp, bot)

    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    # Запуск бота
    main()
