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
from src.prototype.kernel import PeerState, Scenarios

inline_timepicker = InlineTimepicker()
counter = 0
quizzes_database = {}  # здесь хранится информация о викторинах


def init_handlers_peer(dp, bot):

    @dp.message_handler(text="Пир", state=Scenarios.select_role)
    async def select_peer_role(message: Message, state: FSMContext):
        print("Peer selected!!")
        async with state.proxy() as data:
            data['role'] = message.text.lower()
        # await PeerState.event_actions.set()
        await message.answer('Привет, ты походу пир. Сейчас будет чекин!', reply_markup=peer_kb())

    # TODO: дать понять что за юзер
    @dp.message_handler(Text(equals="Геолокацией"), state=PeerState.checkin)
    async def get_geo(message: types.Message, state: FSMContext):
        await PeerState.send_location.set()
        await message.answer("Отличный выбор! Отправь свою геолокацию", reply_markup=georequest_kb())

    @dp.message_handler(content_types=types.ContentType.LOCATION, state=PeerState.send_location)
    async def geo_output(geo_data: types.Message, state: FSMContext):
        print("geo was sent")
        # city = dal.get_all_events()
        # print(city)
        # if city == 'kazan':
        #     campus_longtitude = 49.125365
        #     campus_latitude = 55.781877
        # elif city == 'moscow':
        #     campus_longtitude = 37.579888
        #     campus_latitude = 55.797109
        # elif city == 'novosibirsk':
        #     campus_longtitude = 82.898014
        #     campus_latitude = 54.980327
        # else:

        # current_state = await state.get_state()
        # print(current_state)

        async with state.proxy() as data:
            print(data)
            campus_longtitude = data.get('longtitude')
            campus_latitude = data.get('latitude')

        # async with state.proxy() as data:
        #     data['longitude'] = campus_longtitude
        #     data['latitude'] = campus_latitude

        print(geo_data)
        if campus_latitude - 0.005 < geo_data.location.latitude < campus_latitude + 0.005 \
                and campus_longtitude - 0.005 < geo_data.location.longitude < campus_longtitude + 0.005:
            print("he is in")
            await geo_data.answer(text="Ты в деле", reply_markup=types.ReplyKeyboardRemove())
        else:
            print("врет, не в кампусе")
            await geo_data.answer(text="Ты ж не на мероприятии, дружок", reply_markup=types.ReplyKeyboardRemove())
        await PeerState.checkin.set()

    # {"latitude": 55.781877, "longitude": 49.125365}

    @dp.message_handler(text="Квиз", state="*")
    async def start_quiz(message: types.Message, state: FSMContext):
        print(quizzes_database)
        for key, value in quizzes_database.items():
            print(key, ": ", value)
            saved_quiz = value[0]
            if saved_quiz:
                await bot.send_poll(chat_id=message.chat.id, question=saved_quiz.get('question'),
                                    is_anonymous=False, options=saved_quiz.get('options'), type="quiz",
                                    correct_option_id=saved_quiz.get('correct_option_id'))

    @dp.poll_answer_handler()
    async def poll_answer(poll_answer: types.PollAnswer):
        print(poll_answer)
        for key, value in quizzes_database.items():
            print(key, ": ", value)
            correct_answer_id = value[0]['correct_option_id']
        if poll_answer.option_ids[0] == correct_answer_id:
            await bot.send_message(chat_id=poll_answer.user.id, text="Молодцом!")
        else:
            await bot.send_message(chat_id=poll_answer.user.id, text="Не надо обманывать")

    @dp.message_handler(text="Чекин", state="*")
    async def checkin_handler(message: types.Message, state: FSMContext):
        dist = data_layer.get_all_events()
        print(dist)
        counter = 0
        timenow = datetime.datetime.now().strftime('%H::%M::%S')
        print(timenow)
        for el in dist:
            if el[7] == datetime.date.today().strftime('%Y-%m-%d') and el[8] < timenow < el[9]:
                counter = 1
            else:
                await message.answer('Сейчас мероприятий нет!')

        if counter == 1:
            await PeerState.checkin.set()
            await message.answer(f'Окей. Добро пожаловать на мероприятие,'
                                 f'{message.from_user.username}.'
                                 f'Каким способом зачекинить?',
                                 reply_markup=checkin_kb())
