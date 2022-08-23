from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


def init_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Админ", "Пир"]
    keyboard.add(*buttons)
    return keyboard


def peer_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Чекин", "Список мероприятий",]
    keyboard.add(*buttons)
    return keyboard


def admin_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Создать мероприятие", "Список мероприятий"]
    keyboard.add(*buttons)
    return keyboard


def create_event_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Онлайн", "Оффлайн"]
    keyboard.add(*buttons)
    return keyboard


def online_keyboard() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Казань", "Москва", "Новосибирск", "Все вместе =)"]
    keyboard.add(*buttons)
    return keyboard


def offline_keyboard() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Казань", "Москва", "Новосибирск"]
    keyboard.add(*buttons)
    return keyboard


def city_keyboard() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Кампус", "Ещё где-то"]
    keyboard.add(*buttons)
    return keyboard


def georequest_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Запросить геолокацию", request_location=True))
    return keyboard


def checkin_kb() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Геолокацией", "Квиз"]
    keyboard.add(*buttons)
    return keyboard


def create_poll_kb() -> ReplyKeyboardMarkup:
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Создать викторину",
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keyboard.add(types.KeyboardButton(text="Отмена"))
    return poll_keyboard
