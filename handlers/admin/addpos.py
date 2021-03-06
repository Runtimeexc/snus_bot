from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

import dbfunc
import fastdb
import fastdb
from handlers.allstat import OrderAddPos, OrderRedPos, MainMenu, StateAdminMenu, OrderDelPos
from misc import dp, bot

#
#
#
#
#
#

from ui import keyboards


@dp.message_handler(state=OrderAddPos.waiting_pos_name, content_types=types.ContentTypes.TEXT)
async def step_getname(message: types.Message, state: FSMContext):
    fastdb.CURRENT_RED_POSITION.name = message.text
    mes_text = 'Шаг 2 из 7\n' + 'Введите цену за 1ед: '
    await message.answer(mes_text)
    await OrderAddPos.waiting_pos_cost.set()


@dp.message_handler(state=OrderAddPos.waiting_pos_cost, content_types=types.ContentTypes.TEXT)
async def step_getcost(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        fastdb.CURRENT_RED_POSITION.cost = message.text
        mes_text = 'Шаг 3 из 7\n' + 'Введите глобальную секцию, или выберите из списка\n'
        await message.answer(mes_text, reply_markup=keyboards.get_admin_sectionpick_rkeyb())
        await OrderAddPos.waiting_pos_section.set()
    else:
        await message.answer('Похоже,\'' + message.text + '\' - не число')


@dp.message_handler(state=OrderAddPos.waiting_pos_section, content_types=types.ContentTypes.TEXT)
async def step_getsection(message: types.Message, state: FSMContext):
    print("Функция работает")
    fastdb.CURRENT_RED_POSITION.section = message.text
    mes_text = 'Шаг 4 из 7\nВведите вторичную секцию, или выберите из списка:\n'

    await OrderAddPos.waiting_pos_brand.set()
    await message.answer(mes_text, reply_markup=keyboards.get_admin_fsectionpick_rkeyb())


@dp.message_handler(state=OrderAddPos.waiting_pos_brand, content_types=types.ContentTypes.TEXT)
async def step_getbrand(message: types.Message, state: FSMContext):
    fastdb.CURRENT_RED_POSITION.fsection = message.text
    mes_text = 'Шаг 5 из 7\nВведите описмание товара'

    await OrderAddPos.waiting_pos_definition.set()
    await message.answer(mes_text, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=OrderAddPos.waiting_pos_definition, content_types=types.ContentTypes.TEXT)
async def step_getdefinition(message: types.Message, state: FSMContext):
    mes_text = 'Шаг 6 из 7\nВведите количество товара на складе'
    fastdb.CURRENT_RED_POSITION.definition = message.text
    await message.answer(mes_text)
    await OrderAddPos.waiting_pos_col.set()


@dp.message_handler(state=OrderAddPos.waiting_pos_col, content_types=types.ContentTypes.TEXT)
async def step_getcol(message: types.Message, state: FSMContext):
    mes_text = 'Шаг 7 из 7\nОтправьте фото'
    if message.text.isnumeric():
        fastdb.CURRENT_RED_POSITION.col = message.text
        await OrderAddPos.waiting_pos_cap.set()
        await message.answer(mes_text)
    else:
        await message.answer('похоже, это не число :(')


@dp.message_handler(lambda message: message.text, state=OrderAddPos.waiting_pos_cap)
async def step_nophoto(message: types.Message):
    await message.answer('ожидается фото')


@dp.message_handler(content_types=['photo'], state=OrderAddPos.waiting_pos_cap)
async def step_getphoto(message: types.InputMediaPhoto):
    print(message.photo[0].file_id)
    fastdb.CURRENT_RED_POSITION.cap = message.photo[0].file_id
    dbfunc.add_position(fastdb.CURRENT_RED_POSITION)
    mes_text = fastdb.get_adminposliststr()
    await message.answer('добавлено', reply_markup=keyboards.get_main_menu_rkeyb(fastdb.is_admin(message.from_user.id)))
    await message.answer(mes_text, reply_markup=keyboards.get_admin_redactpos_ikeyb())
    await StateAdminMenu.waiting_redadd.set()


# хэндлеры добавления позиций
#
#
#
#
#####
#
#
#
##
#
#
#
#
#
#
#

@dp.message_handler(state=OrderRedPos.waiting_pos_selection, content_types=types.ContentTypes.ANY)
async def step_getselection(message: types.Message, state: FSMContext):
    mes_text = ''
    print('ждем selection')
    if message.text.isnumeric():
        if len(fastdb.ALL_POSITIONS) < int(message.text) or int(message.text) < 1:
            mes_text = '\'' + message.text + '\' не попадает в диапозон списка :('
        else:
            fastdb.CURRENT_RED_POSITION = fastdb.ALL_POSITIONS[int(message.text)-1]
            fastdb.CURRENT_RED_POSITION_OLDNAME = fastdb.CURRENT_RED_POSITION.name
            mes_text = "Шаг 1 из 7\nВведите название позиции или \'00\', чтобы оставить текущее\nname: " +\
                       fastdb.CURRENT_RED_POSITION.name
            await OrderRedPos.waiting_pos_name.set()
    else:
        mes_text = '\'' + message.text + '\' не число!'
    await message.answer(mes_text)


@dp.message_handler(state=OrderRedPos.waiting_pos_name, content_types=types.ContentTypes.TEXT)
async def step_getname(message: types.Message, state: FSMContext):
    if message.text != '00':
        fastdb.CURRENT_RED_POSITION.name = message.text
    mes_text = 'Шаг 2 из 7\nВведите цену за 1ед или \'00\', чтобы оставить текущую\ncost: ' + \
                       str(fastdb.CURRENT_RED_POSITION.cost)
    await message.answer(mes_text)
    await OrderRedPos.waiting_pos_cost.set()


@dp.message_handler(state=OrderRedPos.waiting_pos_cost, content_types=types.ContentTypes.TEXT)
async def step_getcost(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        if message.text != '00':
            fastdb.CURRENT_RED_POSITION.cost = message.text

        mes_text = 'Шаг 3 из 7\nВведите глобальную секцию, или выберите из списка, или \'00\', чтобы оставить текущую\n' \
                   'текущая секция: ' + fastdb.CURRENT_RED_POSITION.section + '\n\n'
        i = 0
        for sec in fastdb.ALL_SECTIONS:
            i += 1
            mes_text += str(i) + '. ' + sec + '\n'
        await message.answer(mes_text)
        await OrderRedPos.waiting_pos_section.set()
    else:
        await message.answer('Похоже,\'' + message.text + '\' - не число')


@dp.message_handler(state=OrderRedPos.waiting_pos_section, content_types=types.ContentTypes.TEXT)
async def step_getsection(message: types.Message, state: FSMContext):
    mes_text = ''
    if message.text != '00':
        if message.text.isnumeric():
            if 0 < int(message.text) <= len(fastdb.ALL_SECTIONS):
                fastdb.CURRENT_RED_POSITION.section = fastdb.ALL_SECTIONS[int(message.text) - 1]
            else:
                mes_text = "Число не попадает в диапозон списка."
                return
        else:
            fastdb.CURRENT_RED_POSITION.section = message.text

    mes_text = 'Шаг 4 из 7\nВведите вторичную секцию, или выберите из списка, или \'00\', чтобы оставить текущую\n' \
                   'текущая подсекция: ' + fastdb.CURRENT_RED_POSITION.fsection + '\n\n'
    iter = 0
    for brend in fastdb.ALL_FSECTIONS:
        iter += 1
        mes_text += str(iter) + '. ' + brend + '\n'
    await message.answer(mes_text)
    await OrderRedPos.waiting_pos_brand.set()


@dp.message_handler(state=OrderRedPos.waiting_pos_brand, content_types=types.ContentTypes.TEXT)
async def step_getbrand(message: types.Message, state: FSMContext):
    mes_text = ''
    if message.text != '00':
        if message.text.isnumeric():
            if 0 < int(message.text) <= len(fastdb.ALL_FSECTIONS):
                fastdb.CURRENT_RED_POSITION.fsection = fastdb.ALL_FSECTIONS[int(message.text) - 1]
            else:
                mes_text = "Число не попадает в диапозон списка."
                return
        else:
            fastdb.CURRENT_RED_POSITION.fsection = message.text

    mes_text = 'Шаг 5 из 7\nВведите описмание товара, или \'00\', чтобы оставить текущее\n' \
                   'Definition:\n' + fastdb.CURRENT_RED_POSITION.definition
    await message.answer(mes_text)
    await OrderRedPos.waiting_pos_definition.set()


@dp.message_handler(state=OrderRedPos.waiting_pos_definition, content_types=types.ContentTypes.TEXT)
async def step_getdefinition(message: types.Message, state: FSMContext):
    mes_text = 'Шаг 6 из 7\nВведите количество товара на складе, или \'00\', чтобы оставить текущее\n' \
                   'Количество: ' + str(fastdb.CURRENT_RED_POSITION.col)
    if message.text != '00':
        fastdb.CURRENT_RED_POSITION.definition = message.text

    await message.answer(mes_text)
    await OrderRedPos.waiting_pos_col.set()


@dp.message_handler(state=OrderRedPos.waiting_pos_col, content_types=types.ContentTypes.TEXT)
async def step_getcol(message: types.Message, state: FSMContext):
    mes_text = 'Шаг 7 из 7\nОтправьте фото, или введите \'00\', чтобы оставить текущее'

    if message.text != '00':
        if message.text.isnumeric():
            fastdb.CURRENT_RED_POSITION.col = int(message.text)
        else:
            mes_text = "Похоже, что \"" + message.text + "\" - не число"
            await message.answer(mes_text)
            return

    await OrderRedPos.waiting_pos_cap.set()
    await bot.send_photo(message.from_user.id, fastdb.CURRENT_RED_POSITION.cap, caption=mes_text)


@dp.message_handler(lambda message: message.text, state=OrderRedPos.waiting_pos_cap)
async def step_nophoto(message: types.Message):
    mes_text = ''
    if message.text != '00':
        await message.answer('ожидается фото')
    else:
        await message.answer('позиция изменена')
        inline_keyb = InlineKeyboardMarkup()
        iter = 0
        for text_btn in fastdb.INLINE_ADMIN_REDACTPOS:
            iter += 1
            inline_btn = InlineKeyboardButton(text_btn, callback_data='adminredactpos' + str(iter))
            print('adminredactpos' + str(iter))
            inline_keyb.add(inline_btn)
        iter = 0
        for position in fastdb.ALL_POSITIONS:
            iter += 1
            mes_text += str(iter) + '. ' + position.name + '\n'
        await message.answer(mes_text, reply_markup=inline_keyb)
        await StateAdminMenu.waiting_redadd.set()


@dp.message_handler(content_types=['photo'], state=OrderRedPos.waiting_pos_cap)
async def step_getphoto(message: types.InputMediaPhoto):
    mes_text = ''
    print(message.photo[0].file_id)
    fastdb.CURRENT_RED_POSITION.cap = message.photo[0].file_id
    dbfunc.red_position(fastdb.CURRENT_RED_POSITION, fastdb.CURRENT_RED_POSITION_OLDNAME)
    iter = 0
    for position in fastdb.ALL_POSITIONS:
        iter += 1
        mes_text += str(iter) + '. ' + position.name + '\n'

    await message.answer(mes_text, reply_markup=keyboards.get_admin_redactpos_ikeyb())
    await StateAdminMenu.waiting_redadd.set()
#
#
#data = await state.get_data()
#хэндлеры удаления позиции
#
#
#
@dp.message_handler(state=OrderDelPos.waiting_del_selection, content_types=types.ContentTypes.ANY)
async def step_getdelselection(message: types.Message, state: FSMContext):
    mes_text = ''
    print('ждем selection для удаления')
    if message.text.isnumeric():
        if len(fastdb.ALL_POSITIONS) < int(message.text) or int(message.text) < 1:
            mes_text = '\'' + message.text + '\' не попадает в диапозон списка :('
        else:
            fastdb.CURRENT_RED_POSITION = fastdb.ALL_POSITIONS[int(message.text)-1]
            dbfunc.delete_position(fastdb.CURRENT_RED_POSITION.name)
            fastdb.refresh_all_fastdb()

            iter =0
            for position in fastdb.ALL_POSITIONS:
                iter += 1
                mes_text += str(iter) + '. ' + position.name + '\n'
            data = await state.get_data()
            print(data['message_id'])
            print("следуюшая строка ошибка")
            await message.answer(mes_text, reply_markup=keyboards.get_admin_redactpos_ikeyb())
            await StateAdminMenu.waiting_redadd.set()
    else:
        mes_text = '\'' + message.text + '\' не число!'
        await message.answer(mes_text)



