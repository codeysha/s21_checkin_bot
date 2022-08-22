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
counter = 0
quizzes_database = {}  # здесь хранится информация о викторинах
quizzes_owners = {}  # здесь хранятся пары "id викторины <--> id её создателя"


def init_handlers(dp, bot):
    @dp.message_handler(commands=['start'], state='*')
    async def cmd_start(message: types.Message):
        await Scenarios.select_role.set()
        await message.reply("Выберите вашу роль", reply_markup=init_kb())

    @dp.message_handler(text="Пир", state=Scenarios.select_role)
    async def select_peer_role(message: Message, state: FSMContext):
        async with state.proxy() as data:
            data['role'] = message.text.lower()
        await Scenarios.event_actions.set()
        await message.answer('Привет, ты походу пир. Сейчас будет чекин!', reply_markup=peer_kb())

    @dp.message_handler(text="Админ", state=Scenarios.select_role)
    async def select_admin_role(message: Message, state: FSMContext):
        await Scenarios.event_actions.set()
        async with state.proxy() as data:
            data['role'] = message.text.lower()
        await message.answer('Привет, уважаемый адм. Чем будем заниматься?', reply_markup=admin_kb())

    @dp.message_handler(commands="cancel", state='*')
    @dp.message_handler(Text(equals="отмена", ignore_case=True), state='*')
    async def cmd_cancel(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())

    # Создание мероприятий
    @dp.message_handler(text="Создать мероприятие", state=Scenarios.event_actions)
    async def create_event(message: types.Message, state: FSMContext):
        await Scenarios.select_event_type.set()
        await message.answer('Как будет проходить мероприятие?', reply_markup=create_event_kb())

    # Список мероприятий
    @dp.message_handler(text="Список мероприятий", state=Scenarios.event_actions)
    async def create_event(message: types.Message, state: FSMContext):
        print('asd')
        dist = data_layer.get_all_events()
        print(dist)
        for el in dist:
            await message.answer(el)

    # Шаблон онлайн мероприятия
    @dp.message_handler(text="Онлайн", state=Scenarios.select_event_type)
    async def online_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['type'] = message.text.lower()
        await Scenarios.select_city.set()
        await message.answer('Ок. Какой кампус?', reply_markup=online_keyboard())

    # Шаблон оффлайн мероприятия
    @dp.message_handler(text="Оффлайн", state=Scenarios.select_event_type)
    async def offline_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['type'] = message.text.lower()
        await Scenarios.select_city.set()
        await message.answer('Ок. Какой кампус?', reply_markup=offline_keyboard())

    # онлайн-мероприятие дял всех
    @dp.message_handler(text="Все вместе =)", state=Scenarios.select_city)
    async def offline_select_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['city'] = 'all'
        await Scenarios.create_name.set()
        await message.answer('Ого! Ничегошеньки как круто! Как назовём?', reply_markup=types.ReplyKeyboardRemove())

    # Шаблон выбора местоположения мероприятия
    @dp.message_handler(lambda message: message.text == "Казань" or
                                        message.text == "Москва" or
                                        message.text == "Новосибирск", state=Scenarios.select_city)
    async def ask_offline_event_location(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['city'] = message.text.lower()

        if data['type'] == 'оффлайн':
            await Scenarios.offline_placement.set()
            await message.answer('Так, а где именно?', reply_markup=city_keyboard())
        else:
            await Scenarios.create_name.set()
            await message.answer('Ура, зум! Какое будет название?', reply_markup=types.ReplyKeyboardRemove())

    # обрабатываем имя
    @dp.message_handler(state=Scenarios.create_name)
    async def add_event_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['event_name'] = message.text

        await Scenarios.create_description.set()
        await message.answer('О чем будет мероприятие?')

    # simple calendar usage
    @dp.callback_query_handler(simple_cal_callback.filter())
    async def process_simple_calendar(callback_query: CallbackQuery,
                                      callback_data: dict,
                                      state: FSMContext):
        selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
        await Scenarios.datetime_start.set()
        if selected:
            async with state.proxy() as data:
                if datetime.datetime.now() < date:
                    data['date'] = date.strftime("%d/%m/%Y")
                    await Scenarios.datetime_start.set()
                else:
                    await Scenarios.false_date.set()

    @dp.message_handler(state=Scenarios.false_date)
    async def handle_false_date(message: types.Message, state: FSMContext):
        await state.reset_state(with_data=False)
        await message.answer("Ты выбрал дату в прошлом! Так нельзя. Но теперь все нормально. Готов продолжить?",
                             reply_markup=await SimpleCalendar().start_calendar())

    @dp.errors_handler(exception=BotBlocked)
    async def error_bot_blocked(update: types.Update, exception: BotBlocked):
        # Update: объект события от Telegram. Exception: объект исключения
        # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
        print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

        # Такой хэндлер должен всегда возвращать True,
        # если дальнейшая обработка не требуется.
        return True

    # TODO: дать понять что за юзер
    @dp.message_handler(Text(equals="Геолокацией"), state=Scenarios.checkin)
    async def get_geo(message: types.Message, state: FSMContext):
        await Scenarios.send_location.set()
        await message.answer("Отличный выбор! Отправь свою геолокацию", reply_markup=georequest_kb())

    @dp.message_handler(lambda message: message.text == "Ещё где-то", state="*")
    async def get_event_place(message: types.Message, state: FSMContext):
        await Scenarios.send_custom_location.set()
        await message.answer("Пришли локейшн", reply_markup=ReplyKeyboardRemove())
        # await message.answer_location(longitude=12.123123, latitude=13.123123)

    @dp.message_handler(content_types=types.ContentType.LOCATION, state=Scenarios.send_custom_location)
    async def get_event_location(geo_data: types.Message, state: FSMContext):
        print(geo_data.location)
        async with state.proxy() as data:
            data['longtitude'] = geo_data.location.longitude
            data['latitude'] = geo_data.location.latitude
        await Scenarios.create_name.set()
        await geo_data.answer('Ладно. Как назовем мероприятие?', reply_markup=types.ReplyKeyboardRemove())

    @dp.message_handler(content_types=types.ContentType.LOCATION, state=Scenarios.send_location)
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
        await Scenarios.checkin.set()

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
            await Scenarios.checkin.set()
            await message.answer(f'Окей. Добро пожаловать на мероприятие,'
                                 f'{message.from_user.username}.'
                                 f'Каким способом зачекинить?',
                                 reply_markup=checkin_kb())

    @dp.message_handler(lambda message: message.text == "Кампус", state=Scenarios.offline_placement)
    async def ask_event_location(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['location'] = 'asd'
            print(data['city'])
            print(data['role'])
            print(data['type'])
            print('that is good')

        await Scenarios.create_name.set()
        await message.answer('Ладно. Как назовем мероприятие?', reply_markup=types.ReplyKeyboardRemove())

    @dp.message_handler(state=Scenarios.create_poll)
    async def create_poll(message: types.Message, state: FSMContext):
        await Scenarios.create_poll.set()
        await message.answer("Нажмите на кнопку ниже и создайте викторину!", reply_markup=create_poll_kb())

    @dp.message_handler(content_types=types.ContentType.POLL, state=Scenarios.create_poll)
    async def get_poll_back(message: types.poll, state: FSMContext):
        # Если юзер раньше не присылал запросы, выделяем под него запись
        if not quizzes_database.get(str(message.from_user.id)):
            quizzes_database[str(message.from_user.id)] = []

        # Если юзер решил вручную отправить не викторину, а опрос, откажем ему.
        if message.poll.type != "quiz":
            await message.reply("Извините, я принимаю только викторины (quiz)!")
            return

        # Сохраняем себе викторину в память
        quizzes_database[str(message.from_user.id)].append({
            "quiz_id": message.poll.id,
            "question": message.poll.question,
            "options": [o.text for o in message.poll.options],
            "correct_option_id": message.poll.correct_option_id,
            "owner_id": message.from_user.id}
        )
        # Сохраняем информацию о её владельце для быстрого поиска в дальнейшем
        quizzes_owners[message.poll.id] = str(message.from_user.id)

        await message.reply(
            f"Викторина сохранена. Общее число сохранённых викторин: {len(quizzes_database[str(message.from_user.id)])}")

        print(message)
        await Scenarios.select_role.set()
        await message.answer('Фух, получилось! ДО СВИДАНИЯ!', reply_markup=types.ReplyKeyboardRemove())

    @dp.message_handler(state=Scenarios.send_event_to_bd)
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

    @dp.message_handler(state=Scenarios.create_description)
    async def add_event_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['description'] = message.text

        await state.reset_state(with_data=False)  # Здесь выполняется сброс "state". Календарь начинает работать.
        await message.answer("Ха-ха, уже выбрали дату?", reply_markup=await SimpleCalendar().start_calendar())

    @dp.message_handler(state=Scenarios.datetime_start)
    async def time_start(message: types.Message, state=FSMContext):

        inline_timepicker.init(
            datetime.time(12),
            datetime.time(1),
            datetime.time(23),
        )

        await state.reset_state(with_data=False)
        await message.answer("Выберите время начала мероприятия!", reply_markup=inline_timepicker.get_keyboard())

    @dp.callback_query_handler(inline_timepicker.filter())
    async def cb_handler(query: types.CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
        global counter
        await query.answer()
        handle_result = inline_timepicker.handle(query.from_user.id, callback_data)
        reply = "Начало положено. Введем время завершения?" if counter == 0 else "Выбрали? Точно? Продолжим?"

        if handle_result is not None:
            await bot.edit_message_text(reply,
                                        chat_id=query.from_user.id,
                                        message_id=query.message.message_id)

            async with state.proxy() as data:

                if counter == 0:
                    print(handle_result)
                    data['time_start'] = handle_result
                    await Scenarios.datetime_finish.set()
                    counter += 1
                else:
                    print(handle_result)
                    data['time_finish'] = handle_result
                    await Scenarios.create_poll.set()
                    counter = 0

        else:
            await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                                message_id=query.message.message_id,
                                                reply_markup=inline_timepicker.get_keyboard())

    @dp.message_handler(state=Scenarios.datetime_finish)
    async def time_finish(message: types.Message, state=FSMContext):

        inline_timepicker.init(
            datetime.time(12),
            datetime.time(1),
            datetime.time(23),
        )

        await state.reset_state(with_data=False)
        await message.answer("Выберите время завершения мероприятия!", reply_markup=inline_timepicker.get_keyboard())
