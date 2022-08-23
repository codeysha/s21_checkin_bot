from aiogram.dispatcher import FSMContext
from keyboards import *

import dal as data_layer
from kernel import Auth
import mailer as mail


def init_handlers_auth(dp, bot):
    @dp.message_handler(commands=['auth'], state="*")
    async def check_auth_step(message: types.Message):
        user = data_layer.get_user_by_id(message.from_user.id)
        if user != 0:
            if user['role'] == 'adm':
                await message.answer('Здравствуйте АДМ! Что прикажете сделать?')
            else:
                await message.answer('Привет Пир! Готов тебя зачекинить..')
        else:
            await message.answer('Укажи свою школьную почту:')
            await Auth.email.set()

    @dp.message_handler(state=Auth.email, content_types=types.ContentTypes.TEXT)
    async def email_step(message: types.Message, state: FSMContext):
        user_email = message.text
        role = data_layer.get_role_from_email(user_email)
        if role == 0:
            await message.reply('Как будто бы вы не из нашей школы. Если опечатались, попробуйте заново..')
            return
        await state.update_data(email=message.text.title())
        code = mail.generate_code(user_email)
        print('generated code: ', code)
        data_layer.save_access_code(code, user_email)
        mail.send(user_email, code, message.from_user.id)
        await message.reply('код отправлен на указанную почту')
        await message.answer(text='Введите код:')
        await Auth.code.set()

    @dp.message_handler(state=Auth.code, content_types=types.ContentTypes.TEXT)
    async def code_step(message: types.Message, state: FSMContext):
        entered_code = message.text
        code = data_layer.find_access_code(entered_code)
        if code == 0:
            await message.reply('Ошибка в коде или он просрочен')
            return
        await message.reply('Код верный, Добро пожаловать в систему!')
        await state.update_data(code=message.text.title())
        user_id = message.from_user.id
        user_email = code['email']
        # user_data = await state.get_data()
        data_layer.save_user(user_id, user_email)
        role = data_layer.get_role_from_email(user_email)
        if role == 'adm':
            await state.finish()
            await message.answer('Здравствуйте АДМ! Что прикажете сделать?', reply_markup=admin_kb())
        else:
            await state.finish()
            await message.answer('Привет Пир! Готов тебя зачекинить или может посмотрешь список мероприятии?', reply_markup=peer_kb())