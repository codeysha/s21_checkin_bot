from datetime import date
import datetime
import types
from typing import Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from inline_timepicker.inline_timepicker import InlineTimepicker

import dal as data_layer
from keyboards import *
from kernel import Scenarios, AdminState

inline_timepicker = InlineTimepicker()
counter = 0
quizzes_database = {}  # здесь хранится информация о викторинах
quizzes_owners = {}  # здесь хранятся пары "id викторины <--> id её создателя"


def init_handlers_admin(dp, bot):

    @dp.message_handler(text="Админ", state=Scenarios.select_role)
    async def select_admin_role(message: Message, state: FSMContext):
        await AdminState.event_actions.set()
        async with state.proxy() as data:
            data['role'] = message.text.lower()
        await message.answer('Привет, уважаемый адм. Чем будем заниматься?', reply_markup=admin_kb())

    # Создание мероприятий
    @dp.message_handler(text="Создать мероприятие", state=AdminState.event_actions)
    async def create_event(message: types.Message, state: FSMContext):
        await AdminState.select_event_type.set()
        await message.answer('Как будет проходить мероприятие?', reply_markup=create_event_kb())

    # Список мероприятий
    @dp.message_handler(text="Список мероприятий", state=AdminState.event_actions)
    async def create_event(message: types.Message, state: FSMContext):
        dist = data_layer.get_all_events()
        print(dist)
        for el in dist:
            # await message.answer(el)
            await message.answer(f'Мероприятие \"{el[3]}\" для г.{el[2].capitalize()} в {el[8]} {".".join(el[7].split("/"))}\n{el[4]}')

    # Шаблон онлайн мероприятия
    @dp.message_handler(text="Онлайн", state=AdminState.select_event_type)
    async def online_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['type'] = message.text.lower()
        await AdminState.select_city.set()
        await message.answer('Ок. Какой кампус?', reply_markup=online_keyboard())

    # Шаблон оффлайн мероприятия
    @dp.message_handler(text="Оффлайн", state=AdminState.select_event_type)
    async def offline_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['type'] = message.text.lower()
        await AdminState.select_city.set()
        await message.answer('Ок. Какой кампус?', reply_markup=offline_keyboard())

    # онлайн-мероприятие для всех
    @dp.message_handler(text="Все вместе =)", state=AdminState.select_city)
    async def offline_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['city'] = 'all'
        await AdminState.create_name.set()
        await message.answer('Ого! Ничегошеньки как круто! Как назовём?', reply_markup=types.ReplyKeyboardRemove())

    # Шаблон выбора местоположения мероприятия
    @dp.message_handler(lambda message: message.text == "Казань" or
                                        message.text == "Москва" or
                                        message.text == "Новосибирск", state=AdminState.select_city)
    async def ask_offline_event_location(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['city'] = message.text.lower()

        if data['type'] == 'оффлайн':
            await AdminState.offline_placement.set()
            await message.answer('Так, а где именно?', reply_markup=city_keyboard())
        else:
            await AdminState.create_name.set()
            await message.answer('Ура, зум! Какое будет название?', reply_markup=types.ReplyKeyboardRemove())

    # Выбран Кампус
    @dp.message_handler(lambda message: message.text == "Кампус", state=AdminState.offline_placement)
    async def ask_event_location(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if data['city'] == 'казань':
                data['latitude'] = '55.7818298972536'
                data['longitude'] = '49.12492890025121'
            if data['city'] == 'москва':
                data['latitude'] = '55.79711171990413'
                data['longitude'] = '37.57975336628905'
            if data['city'] == 'новосибирск':
                data['latitude'] = '54.98031715955346'
                data['longitude'] = '82.89789611835465'
        await AdminState.create_name.set()
        await message.answer('Ладно. Как назовем мероприятие?', reply_markup=types.ReplyKeyboardRemove())

    # обрабатываем имя
    @dp.message_handler(state=AdminState.create_name)
    async def add_event_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['event_name'] = message.text

        await AdminState.create_description.set()
        await message.answer('О чем будет мероприятие?')

    @dp.message_handler(state=AdminState.create_description)
    async def add_event_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['description'] = message.text
        await state.reset_state(with_data=False)
        await message.answer("Приступим к выбору даты мероприятия", reply_markup=await SimpleCalendar().start_calendar())

    # simple calendar usage
    @dp.callback_query_handler(simple_cal_callback.filter())
    async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
        selected, chosen_date = await SimpleCalendar().process_selection(callback_query, callback_data)
        await AdminState.datetime_start.set()
        if selected:
            async with state.proxy() as data:
                if date.today() <= chosen_date.date():
                    data['date'] = chosen_date.strftime("%d/%m/%Y")
                    inline_timepicker.init(datetime.time(12),datetime.time(1),datetime.time(23),)
                    await callback_query.message.answer(f'Дата мероприятия: : {chosen_date.strftime("%d.%m.%Y")}')
                    await state.reset_state(with_data=False)
                    reply = "Выберите время начала мероприятия!"
                    await callback_query.message.answer(reply, reply_markup=inline_timepicker.get_keyboard())
                else:
                    await state.reset_state(with_data=False)
                    reply = "Полиция времени не дает создать мероприятие в прошлом, придется перевыбрать дату :("
                    await callback_query.message.answer(reply, reply_markup=await SimpleCalendar().start_calendar())

    @dp.callback_query_handler(inline_timepicker.filter())
    async def cb_handler(query: types.CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
        global counter
        await query.answer()
        handle_result = inline_timepicker.handle(query.from_user.id, callback_data)
        if handle_result is not None:
            async with state.proxy() as data:
                if counter == 0:
                    data['time_start'] = handle_result
                    await bot.edit_message_text(f'Время начала мероприятия: : {handle_result.isoformat(timespec="minutes")}',
                                                chat_id=query.from_user.id,
                                                message_id=query.message.message_id)
                    await AdminState.datetime_finish.set()
                    inline_timepicker.init(
                        datetime.time(12),
                        datetime.time(1),
                        datetime.time(23),
                    )
                    await state.reset_state(with_data=False)
                    reply = "Выберите время завершения мероприятия"
                    await query.message.answer(reply, reply_markup=inline_timepicker.get_keyboard())
                    counter += 1
                else:
                    data['time_finish'] = handle_result
                    await bot.edit_message_text(
                        f'Время конца мероприятия: : {handle_result.isoformat(timespec="minutes")}',
                        chat_id=query.from_user.id,
                        message_id=query.message.message_id)
                    await AdminState.create_poll.set()
                    await query.message.answer("Приступим к добавлению викторины!", reply_markup=create_poll_kb())
                    counter = 0

        else:
            await bot.edit_message_reply_markup(
                chat_id=query.from_user.id,
                message_id=query.message.message_id,
                reply_markup=inline_timepicker.get_keyboard())

    @dp.message_handler(lambda message: message.text == "Ещё где-то", state="*")
    async def get_event_place(message: types.Message, state: FSMContext):
        await AdminState.send_custom_location.set()
        await message.answer("Пришли локейшн", reply_markup=ReplyKeyboardRemove())

    @dp.message_handler(content_types=types.ContentType.LOCATION, state=AdminState.send_custom_location)
    async def get_event_location(geo_data: types.Message, state: FSMContext):
        print(geo_data.location)
        async with state.proxy() as data:
            data['longtitude'] = geo_data.location.longitude
            data['latitude'] = geo_data.location.latitude
        await AdminState.create_name.set()
        await geo_data.answer('Локация сохранена. Как назовем мероприятие?', reply_markup=types.ReplyKeyboardRemove())

    @dp.message_handler(content_types=types.ContentType.POLL, state=AdminState.create_poll)
    async def get_poll_back(message: types.poll, state: FSMContext):
        if not quizzes_database.get(str(message.from_user.id)):
            quizzes_database[str(message.from_user.id)] = []
        if message.poll.type != "quiz":
            await message.reply("Извините, я принимаю только викторины (quiz)!")
            return
        quizzes_database[str(message.from_user.id)].append({
            "quiz_id": message.poll.id,
            "question": message.poll.question,
            "options": [o.text for o in message.poll.options],
            "correct_option_id": message.poll.correct_option_id,
            "owner_id": message.from_user.id}
        )
        quizzes_owners[message.poll.id] = str(message.from_user.id)
        await message.reply(
            f"Викторина сохранена. Общее число сохранённых викторин: {len(quizzes_database[str(message.from_user.id)])}")
        await Scenarios.select_role.set()
        await message.answer('Мероприятие создано, хотите сделать что-нибудь еще?', reply_markup=admin_kb())
        async with state.proxy() as data:
            data_layer.save_event(data, message.poll.id)

    @dp.message_handler(state=AdminState.send_event_to_bd)
    async def send_event(message: types.Message, state: FSMContext):
        print('works')
        async with state.proxy() as data:
            print(data['city'])
            print(data['role'])
            print(data['type'])
            print(data['description'])
            print(data['event_name'])
            print(data['location'])
            print(data['longitude'])
            print(data['latitude'])
        await message.answer('Отправляем в бд ')
        # обрабатываем описание мероприятия
