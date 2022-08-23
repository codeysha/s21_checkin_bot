import datetime
import types
from typing import Dict

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from inline_timepicker.inline_timepicker import InlineTimepicker

import src.prototype.dal as data_layer
from src.prototype.basicui.keyboards import *
from src.prototype.kernel import Scenarios

inline_timepicker = InlineTimepicker()


def init_handlers(dp, bot):
    @dp.message_handler(commands=['start'], state='*')
    async def cmd_start(message: types.Message):
        await Scenarios.select_role.set()
        await message.reply("Выберите вашу роль", reply_markup=init_kb())

    @dp.message_handler(commands="cancel", state='*')
    @dp.message_handler(Text(equals="отмена", ignore_case=True), state='*')
    async def cmd_cancel(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())

    @dp.errors_handler(exception=BotBlocked)
    async def error_bot_blocked(update: types.Update, exception: BotBlocked):
        # Update: объект события от Telegram. Exception: объект исключения
        # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
        print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

        # Такой хэндлер должен всегда возвращать True,
        # если дальнейшая обработка не требуется.
        return True
