from email.mime.text import MIMEText

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import db

from loader import dp, bot, _

b1 = KeyboardButton("O'zbekcha")
b2 = KeyboardButton('Русский')
b3 = KeyboardButton("Qoraqalpoqcha")

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).add(b3)

def sesionExceptionsState():
    def outer(func):
        async def wrapper(*args, **kwargs):
            # print(args)
            try:
                # this is where the "work" happens!
                if kwargs != {}:
                    res = await func(*args, kwargs['state'])
                else:
                    res = await func(*args, **kwargs)
            except:
                # if any kind of exception occurs, rollback transaction
                await db.session.rollback()
                raise
            finally:
                await db.session.close()
            return res
        return wrapper

    return outer

def sesionExceptions():
    def outer(func):
        async def wrapper(*args, **kwargs):
            # print(args)
            try:
                # this is where the "work" happens!
                res = await func(*args)
            except:
                # if any kind of exception occurs, rollback transaction
                await db.session.rollback()
                raise
            finally:
                await db.session.close()
            return res
        return wrapper

    return outer
class Regist(StatesGroup):
    name = State()
    phone = State()
    viloyat = State()
    tuman = State()
    mfy = State()
    sex = State()
    years = State()
    ad = State()
    user_id = State()
    lang = State()
    change_name = State()
    change_phone = State()
    change_viloyat = State()
    change_tuman = State()
    change_mfy = State()
    change_sex = State()


@dp.message_handler(commands=['start', 'help'])
@sesionExceptions()
async def commands_start(message: types.Message):
    user_id = message.from_user.id

    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    text = await db.session.execute(select(db.Text.greeting).filter_by(lang=user.lang if user else 'uz_kir'))
    text = text.scalar()

    if user:
        print('User')
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))

        return user
    else:
        print(user_id)
        print('No user')
        text = await db.session.execute(select(db.Text.greeting).filter_by(lang='uz'))
        text_ru = await db.session.execute(select(db.Text.greeting).filter_by(lang='ru'))
        text_kir = await db.session.execute(select(db.Text.greeting).filter_by(lang='uz_kir'))

        text = text.scalar()
        text_ru = text_ru.scalar()
        text_kir = text_kir.scalar()

        multitext = text + '\n' + text_ru + '\n' + text_kir

        lang_ru = 'Уважаемый гражданин, пожалуйста выберите язык интерфейса!'
        lang_uz = "Hurmatli fuqaro, iltimos interfeys tilini tanlang!"
        lang_kir = 'Húrmetli puxara, iltimas interfeys tilin tańlań!'

        multilang = lang_uz + '\n' + lang_ru + '\n' + lang_kir
        await bot.send_message(user_id, multitext, reply_markup=kb_client)
        await bot.send_message(user_id, multilang)

@sesionExceptions()
async def take_text(lang, step, user_id, message=None, ls=None):
    text = await db.session.execute(select(db.Text).filter_by(lang=lang))
    text = text.scalar()

    if step == 0:
        await bot.send_message(user_id, text.greeting)

    if step == 1:
        return text.step1
    if step == 2:
        return text.step2
    if step == 3:
        return text.step3
    if step == 4:
        return text.step4
    if step == 5:
        return text.step5
    if step == 6:
        return text.step6
    if step == 7:
        return text.step7
    if step == 8:
        return text.step8
    if step == 9:
        return text.step9


@dp.message_handler(Text(equals="Murojaatingizni qoldiring 📝"))
@dp.message_handler(Text(equals="O'zbekcha"))
@sesionExceptionsState()
async def murojat_handlers_uz(message: types.Message, state: FSMContext):

    user_id = message.from_user.id

    global status_lang

    status_lang = 'uz'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman_id
            text = await take_text(user.lang, 8, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('uz', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Bekor qilish')))
        await Regist.name.set()


@dp.message_handler(Text(equals="Оставьте обращение 📝"))
@dp.message_handler(Text(equals="Русский"))
@sesionExceptionsState()
async def murojat_handlers_ru(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    global status_lang

    status_lang = 'ru'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman_id
            text = await take_text(user.lang, 8, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('ru', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Bekor qilish', locale=status_lang))))
        await Regist.name.set()


@dp.message_handler(Text(equals="Múrájatlarıńıstı qaldıriń 📝"))
@dp.message_handler(Text(equals="Qoraqalpoqcha"))
@sesionExceptionsState()
async def murojat_handlers_uz_kir(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    global status_lang

    status_lang = 'uz_kir'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman_id
            text = await take_text(user.lang, 8, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('uz_kir', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Biykar etiw')))
        await Regist.name.set()


@dp.message_handler(state=Regist.name)
async def load_name(message: types.Message, state: FSMContext):
    step = 2

    async with state.proxy() as data:
        data['name'] = message.text
        data['lang'] = status_lang
        object = tuple(data.values())

    if object[0] == _('Bekor qilish', locale=data['lang']):
        await state.finish()
        await bot.send_message(message.from_user.id, _('Bekor qilish', locale=data['lang']), reply_markup=kb_client)
        return

    text = await take_text(data['lang'], step, message.from_user.id, message)
    req_cont = _("Telefon raqamni jo'natish", locale=data['lang'])
    print(req_cont)
    await bot.send_message(message.from_user.id, text,
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                               KeyboardButton(req_cont, request_contact=True)).add(_('Orqaga', locale=data['lang'])))

    await Regist.next()


@dp.message_handler(content_types=types.ContentType.ANY, state=Regist.phone)
async def load_phone(message: types.Message, state: FSMContext, editMessageReplyMarkup=None):
    step = 3

    async with state.proxy() as data:
        if message.text == _('Orqaga', locale=data['lang']):
            text = await take_text(data['lang'], 1, message.from_user.id, message)
            await bot.send_message(message.from_user.id, text,
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                       KeyboardButton(_('Bekor qilish', locale=data['lang']))))
            await Regist.previous()
            return

        data['phone'] = message.contact.phone_number

        await Regist.next()
        kb = await get_viloyats(data['lang'])
        text = await take_text(data['lang'], step, message.from_user.id, message)

        await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Orqaga', locale=data['lang'])))

@sesionExceptions()
async def generate_tuman_kb(viloyat: str, lang: str) -> ReplyKeyboardMarkup:
    try:
        if lang == 'uz':
            viloyat_m = await db.session.execute(select(db.Viloyat).filter_by(name_uz=viloyat))
            viloyat_m = viloyat_m.scalar()
            tumans = await db.session.execute(select(db.Tuman).filter_by(viloyat_id=viloyat_m.id))
            tumans = tumans.scalars()

            kb_generator = [x.name_uz2 for x in tumans]

        elif lang == 'ru':
            viloyat_m = await db.session.execute(select(db.Viloyat).filter_by(name_ru=viloyat))
            viloyat_m = viloyat_m.scalar()
            tumans = await db.session.execute(select(db.Tuman).filter_by(viloyat_id=viloyat_m.id))
            tumans = tumans.scalars()

            kb_generator = [x.name_ru2 for x in tumans]
        else:
            viloyat_m = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=viloyat))
            viloyat_m = viloyat_m.scalar()
            tumans = await db.session.execute(select(db.Tuman).filter_by(viloyat_id=viloyat_m.id))
            tumans = tumans.scalars()

            kb_generator = [x.name_uz_kir2 for x in tumans]

        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

        return kb
    except Exception as e:
        print(e)
        return None

@sesionExceptions()
async def generate_mahalla_kb(tuman: str, lang: str) -> ReplyKeyboardMarkup:
    if lang == 'uz':
        tuman_m = await db.session.execute(select(db.Tuman).filter_by(name_uz2=tuman))
        tuman_m = tuman_m.scalar()
        mfy = await db.session.execute(select(db.Mfy).filter_by(tuman_id=tuman_m.id))
        tumans = mfy.scalars()

        kb_generator = [x.name_uz for x in tumans]

    elif lang == 'ru':
        tuman_m = await db.session.execute(select(db.Tuman).filter_by(name_ru2=tuman))
        tuman_m = tuman_m.scalar()
        mfy = await db.session.execute(select(db.Mfy).filter_by(tuman_id=tuman_m.id))
        tumans = mfy.scalars()

        kb_generator = [x.name_ru for x in tumans]
    else:
        tuman_m = await db.session.execute(select(db.Tuman).filter_by(name_uz_kir2=tuman))
        tuman_m = tuman_m.scalar()
        tumans = await db.session.execute(select(db.Mfy).filter_by(tuman_id=tuman_m.id))
        tumans = tumans.scalars()

        kb_generator = [x.name_uz_kir for x in tumans]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

    return kb


@dp.message_handler(state=Regist.viloyat)
async def load_viloyat(message: types.Message, state: FSMContext):
    try:
        step = 4
        async with state.proxy() as data:
            if message.text == _('Orqaga', locale=data['lang']):
                text = await take_text(data['lang'], 2, message.from_user.id, message)
                await bot.send_message(message.from_user.id, text,
                                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                                        one_time_keyboard=True).add(
                                           KeyboardButton(_("Telefon raqamni jo'natish", locale=data['lang']),
                                                          request_contact=True)).add(_('Orqaga', locale=data['lang'])))
                await Regist.previous()
                return

            data['viloyat'] = message.text

        text = await take_text(data['lang'], step, message.from_user.id, message)
        kb = await generate_tuman_kb(message.text, data['lang'])

        await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Orqaga', locale=data['lang'])))
        await Regist.next()
    except Exception as e:
        print(e)
        text = await take_text(data['lang'], 3, message.from_user.id, message)
        await message.answer(text)
        return


@dp.message_handler(state=Regist.tuman)
async def load_tuman(message: types.Message, state: FSMContext):
    step = 5
    try:
        async with state.proxy() as data:
            if message.text == _('Orqaga', locale=data['lang']):
                text = await take_text(data['lang'], 3, message.from_user.id, message)
                kb = await get_viloyats(data['lang'])
                await bot.send_message(message.from_user.id, text,
                                       reply_markup=kb.add(_('Orqaga', locale=data['lang'])))
                await Regist.previous()
                return

            data['tuman'] = message.text

        text = await take_text(data['lang'], step, message.from_user.id, message)
        kb = await generate_mahalla_kb(message.text, data['lang'])

        await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Orqaga', locale=data['lang'])))
        await Regist.next()
    except Exception as e:
        print(e)
        text = await take_text(data['lang'], 4, message.from_user.id, message)
        await message.answer(text)
        return


@dp.message_handler(state=Regist.mfy)
async def load_mfy(message: types.Message, state: FSMContext):
    step = 6

    async with state.proxy() as data:

        if message.text == _('Orqaga', locale=data['lang']):
            text = await take_text(data['lang'], 4, message.from_user.id, message)
            kb = await generate_tuman_kb(data['viloyat'], data['lang'])
            await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Orqaga', locale=data['lang'])))
            await Regist.previous()
            return

        mfy = await db.session.execute(select(db.Mfy).filter_by(name_uz=message.text))
        mfy = mfy.scalar()
        if mfy is None:
            text = await take_text(data['lang'], 5, message.from_user.id, message)
            await message.answer(text)
            return

        data['mfy'] = message.text

        text = await take_text(data['lang'], step, message.from_user.id, message)

        await Regist.next()

        await bot.send_message(message.from_user.id, text,
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Erkak', locale=data['lang'])),
                                   KeyboardButton(_('Ayol', locale=data['lang']))).add(
                                   _('Orqaga', locale=data['lang'])))


@dp.message_handler(state=Regist.sex)
async def load_sex(message: types.Message, state: FSMContext):
    step = 7

    async with state.proxy() as data:

        if message.text == _('Orqaga', locale=data['lang']):
            text = await take_text(data['lang'], 5, message.from_user.id, message)
            kb = await generate_mahalla_kb(data['tuman'], data['lang'])
            await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Orqaga', locale=data['lang'])))
            await Regist.previous()
            return

        if message.text == _('Erkak', locale=data['lang']) or message.text == _('Ayol', locale=data['lang']):
            data['sex'] = message.text

            text = await take_text(data['lang'], step, message.from_user.id, message)

            await bot.send_message(message.from_user.id, text,
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                       _('Orqaga', locale=data['lang'])))
            await Regist.next()
        else:
            text = await take_text(data['lang'], 6, message.from_user.id, message)
            await message.answer(text)
            return


@dp.message_handler(state=Regist.years)  # regexp=r"^(\d+)$"
async def load_years(message: types.Message, state: FSMContext):
    step = 8
    try:
        if int(message.text) > 15 and int(message.text) < 31:
            print(message.text)
            async with state.proxy() as data:
                data['years'] = int(message.text)

                await Regist.next()

            text = await take_text(data['lang'], step, message.from_user.id, message)

            await bot.send_message(message.from_user.id, text,
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                       _('Orqaga', locale=data['lang'])))

        else:
            async with state.proxy() as data:

                await bot.send_message(message.from_user.id,
                                       _('Mazkur bot yoshlardan taklif va murojaatlarni qabul qilishga mo‘ljallangan. Sizga @agromurojaatbot dan foydalanish taklif etiladi.',
                                         locale=data['lang']),
                                       reply_markup=kb_client)

                await state.finish()
    except Exception as e:
        print(e)
        async with state.proxy() as data:
            if message.text == _('Orqaga', locale=data['lang']):
                text = await take_text(data['lang'], 6, message.from_user.id, message)
                await bot.send_message(message.from_user.id, text,
                                       reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                           KeyboardButton(_('Erkak', locale=data['lang'])),
                                           KeyboardButton(_('Ayol', locale=data['lang']))).add(
                                           _('Orqaga', locale=data['lang'])))
                await Regist.previous()
                return

            else:
                await bot.send_message(message.from_user.id, '16-30')
                return

@sesionExceptions()
async def get_viloyats(lang: str) -> ReplyKeyboardMarkup:
    viloyats = await db.session.execute(select(db.Viloyat))

    viloyats = viloyats.scalars()

    if lang == 'ru':
        kb_generator = [x.name_ru for x in viloyats]
    elif lang == 'uz_kir':
        kb_generator = [x.name_uz_kir for x in viloyats]
    else:
        kb_generator = [x.name_uz for x in viloyats]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

    return kb

@sesionExceptions()
async def get_mfys(lang: str) -> ReplyKeyboardMarkup:
    mahalas = await db.session.execute(select(db.Mfy))

    mahalas = mahalas.scalars()

    if lang == 'ru':
        kb_generator = [x.name_ru for x in mahalas]
    elif lang == 'uz_kir':
        kb_generator = [x.name_uz_kir for x in mahalas]
    else:
        kb_generator = [x.name_uz for x in mahalas]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

    return kb

@sesionExceptions()
async def get_orders(user_id):
    apps = await db.session.execute(select(db.Application).join(db.User, db.User.id == db.Application.user_id).filter(
        db.User.tg_user_id == user_id).order_by(db.Application.id))

    apps = apps.scalars()

    kb_generator = [f'№{x.id}' for x in apps]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

    return kb


@dp.message_handler(state=Regist.ad)
async def load_ad(message: types.Message, state: FSMContext):
    step = 9

    async with state.proxy() as data:

        if message.text == _('Orqaga', locale=data['lang']):
            text = await take_text(data['lang'], 7, message.from_user.id, message)
            await bot.send_message(message.from_user.id, text,
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                       _('Orqaga', locale=data['lang'])))
            await Regist.previous()
            return

        data['ad'] = message.text
        data['user_id'] = message.from_user.id

    await createUser(state, message.from_user.id)
    await state.finish()

    object = tuple(data.values())

    if object[5] == _('Bekor qilish') or object[0] == _('Bekor qilish'):
        return

    id = await sql_read2(message, data['lang'], step)
    dp.register_message_handler(get_murojat, Text(equals=f'№{id}'), state=None)

    await bot.send_message(message.from_user.id, _('Asosiy menyu', locale=data['lang']),
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                               KeyboardButton(_('Mening murojaatlarim 🧾', locale=data['lang']))
                           ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝', locale=data['lang']))
                                 ).add(KeyboardButton(_("🇺🇿/🇷🇺", locale=data['lang']))).add(
                               KeyboardButton(_('Sozlamalar ⚙️', locale=data['lang']))))

@sesionExceptions()
async def sql_read2(message, lang, step):
    app = await db.session.execute(select(db.Application.id).join(db.User, db.User.id == db.Application.user_id).filter(
        db.User.tg_user_id == message.from_user.id))
    app = app.scalars()
    ls = []

    for i in app:
        ls.append(i)
    text = await take_text(lang, step, message.from_user.id, message, str(ls[-1]))
    text = str(text).replace('__', f'{ls[-1]}')
    await bot.send_message(message.from_user.id, text)
    return ls[-1]

@sesionExceptionsState()
async def createUser(state, user_id):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    async with state.proxy() as data:
        object = tuple(data.values())

        if data['ad'] == 'Biykar etiw' or object[0] == 'Biykar etiw':
            await bot.send_message(user_id, 'Biykar etiw', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim 🧾'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
                  ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
                KeyboardButton(_('Sozlamalar ⚙️'))))
            return ''

        if data['ad'] == 'Отмена' or object[0] == 'Отмена':
            await bot.send_message(user_id, 'Отмена', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim 🧾'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
                  ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
                KeyboardButton(_('Sozlamalar ⚙️'))))
            return ''

        if data['ad'] == 'Bekor qilish' or object[0] == 'Bekor qilish':
            await bot.send_message(user_id, 'Bekor qilish', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim 🧾'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
                  ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
                KeyboardButton(_('Sozlamalar ⚙️'))))
            return ''

        else:

            if user:

                app = db.Application(application=data['ad'], user_id=user.id, lang=data['lang'])

                db.session.add(app)
                await db.session.commit()

                # message = f'''№{app.id}
                # Username: {user.fio}
                # User_phone: {user.phone}
                # {'Murojat kategoriyasi'}: {cat.name_uz}
                # {'sizning murojaatingiz'}: {app.application}
                # {'Murojat holati'}: {app.status}
                # {'murojatga javob'}: {app.answer if app.answer != None else ''}
                #             '''
                #
                # await send_mail2(message)

            else:

                if data['lang'] == 'uz':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz=data['viloyat']))
                    tuman_id = await get_tuman_id(data['tuman'], data['lang'])
                    mfy = await db.session.execute(select(db.Mfy).filter_by(name_uz=data['mfy']))

                if data['lang'] == 'ru':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_ru=data['viloyat']))
                    mfy = await db.session.execute(select(db.Mfy).filter_by(name_ru=data['mfy']))
                    tuman_id = await get_tuman_id(data['tuman'], data['lang'])
                if data['lang'] == 'uz_kir':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=data['viloyat']))
                    mfy = await db.session.execute(select(db.Mfy).filter_by(name_uz_kir=data['mfy']))
                    tuman_id = await get_tuman_id(data['tuman'], data['lang'])
                cat = cat.scalar()
                mfy = mfy.scalar()

                user = db.User(fio=data['name'], phone=data['phone'], viloyat_id=cat.id, year=data['years'],
                               mfy_id=mfy.id, sex=data['sex'], tuman_id=tuman_id,
                               tg_user_id=data['user_id'], lang=data['lang'])
                db.session.add(user)
                await db.session.flush()

                app = db.Application(application=data['ad'], user_id=user.id, lang=data['lang'])

                db.session.add_all([user, app])
                await db.session.commit()

@sesionExceptions()
async def get_tuman_id(tuman: str, lang: str) -> db.Tuman.id:
    if lang == 'uz':
        tuman = await db.session.execute(select(db.Tuman).filter_by(name_uz2=tuman))
    elif lang == 'ru':
        tuman = await db.session.execute(select(db.Tuman).filter_by(name_ru2=tuman))
    else:
        tuman = await db.session.execute(select(db.Tuman).filter_by(name_uz_kir2=tuman))

    tuman = tuman.scalar()
    return tuman.id


@dp.message_handler(Text(equals='Bekor qilish'))
@dp.message_handler(Text(equals='Отмена'))
@dp.message_handler(Text(equals='Biykar etiw'))
async def cancel_purchase(message: types.Message):
    await bot.send_message(message.from_user.id, _('Bekor qilish'),
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                               KeyboardButton(_('Mening murojaatlarim 🧾'))
                           ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
                                 ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
                               KeyboardButton(_('Sozlamalar ⚙️'))))
    return


import aiosmtplib


async def send_mail2(message: str) -> str:
    sender = "sarvarchikkamilov@gmail.com"
    # your password = "your password"
    password = 'aaywgssiujzhsirr'

    server = aiosmtplib.SMTP("smtp.gmail.com", 587)
    await server.connect()
    # await server.starttls()

    try:
        await server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "FROM TG BOT"
        await server.sendmail(sender, 'sarvar_kamilov2@mail.ru', msg.as_string())
        await server.quit()

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


# @dp.message_handler(Text(equals='Mening murojaatlarim'))
# @dp.message_handler(Text(equals='Мои обращения'))
# @dp.message_handler(Text(equals='Менинг мурожаатларим'))
# async def my_applications(message: types.Message):
#     user_id = message.from_user.id
#
#     apps = await db.session.execute(select(db.Application).join(db.User, db.User.id == db.Application.user_id).filter(
#         db.User.tg_user_id == user_id).order_by(db.Application.id))
#
#     user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
#     user = user.scalar()
#
#     apps = apps.scalars()
#
#     for i in apps:
#         if user.lang == 'uz':
#
#             message = f'''№{i.id}
# {'sizning murojaatingiz'}: {i.application}
# {'Murojat holati'}: {i.status}
# {'murojatga javob'}: {i.answer if i.answer != None else ''}
#             '''
#         elif user.lang == 'ru':
#
#             message = f'''№{i.id}
# {'Ваше обращение'}: {i.application}
# {'Cтатус обращения'}: {i.status}
# {'Ответ на обращение'}: {i.answer if i.answer != None else ''}
#             '''
#         else:
#
#             message = f'''№{i.id}
# {'Сизнинг мурожатингиз'}: {i.application}
# {'Мурожат холати'}: {i.status}
# {'Мурожатга жавоб'}: {i.answer if i.answer != None else ''}
#                     '''
#         await bot.send_message(user_id, message)

@dp.message_handler(Text(equals='Mening murojaatlarim 🧾'))
@dp.message_handler(Text(equals='Мои обращения 🧾'))
@dp.message_handler(Text(equals='Meniń múrájatlarım 🧾'))
async def my_applications(message: types.Message):
    user_id = message.from_user.id

    kb = await get_orders(user_id)

    await bot.send_message(user_id, _('Murojaati nomerni tanlang!'), reply_markup=kb.add(_('Bekor qilish')))


def lang_change_handler():
    langs = ["O'zbekchaga", 'На русский', "Qoraqolpoqchaga"]
    for i in langs:
        dp.register_message_handler(change_lang, Text(equals=i))


@dp.message_handler(Text(equals="🇺🇿/🇷🇺"))
@dp.message_handler(Text(equals="🇺🇿/🇷🇺"))
@dp.message_handler(Text(equals="🇺🇿/🇷🇺"))
@sesionExceptions()
async def select_lang(message: types.Message):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    c1 = KeyboardButton("O'zbekchaga")
    c2 = KeyboardButton('На русский')
    c3 = KeyboardButton("Qoraqolpoqchaga")
    kb_client_change = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(c1).add(c2).add(c3)

    if user.lang == 'uz':
        await bot.send_message(message.from_user.id, 'Hurmatli fuqaro, iltimos interfeys tilini tanlang!',
                               reply_markup=kb_client_change)
    if user.lang == 'ru':
        await bot.send_message(message.from_user.id, 'Уважаемый гражданин, пожалуйста выберите язык интерфейса!',
                               reply_markup=kb_client_change)
    if user.lang == 'uz_kir':
        await bot.send_message(message.from_user.id, 'Húrmetli puxara, iltimas interfeys tilin tańlań!',
                               reply_markup=kb_client_change)

@sesionExceptions()
async def change_lang(message: types.Message):
    if message.text == "O'zbekchaga":
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'uz'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Mening murojaatlarim 🧾')
                                                                ).add(KeyboardButton('Murojaatingizni qoldiring 📝')
                                                                      ).add(KeyboardButton("🇺🇿/🇷🇺")).add(
            KeyboardButton('Sozlamalar ⚙️'))
        await bot.send_message(message.from_user.id, "Til o'zgartirildi", reply_markup=user_kb)

    if message.text == 'На русский':
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'ru'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Мои обращения 🧾')
                                                                ).add(KeyboardButton('Оставьте обращение 📝')
                                                                      ).add(KeyboardButton("🇺🇿/🇷🇺")).add(
            KeyboardButton('Настройки ⚙️'))

        await bot.send_message(message.from_user.id, 'Язык изменен', reply_markup=user_kb)
    if message.text == "Qoraqolpoqchaga":
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'uz_kir'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Meniń múrájatlarım 🧾')
                                                                ).add(KeyboardButton('Múrájatlarıńıstı qaldıriń 📝')
                                                                      ).add(KeyboardButton("🇺🇿/🇷🇺")).add(
            KeyboardButton('Sazlamalar ⚙️'))
        await bot.send_message(message.from_user.id, 'Til ózgertildi', reply_markup=user_kb)


@dp.message_handler(Text(equals='Sozlamalar ⚙️'))
@dp.message_handler(Text(equals='Настройки ⚙️'))
@dp.message_handler(Text(equals='Sazlamalar ⚙️'))
async def settings(message: types.Message):
    uz_sets = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(_("Ma'lumotlarni ko'rish")))

    await bot.send_message(message.from_user.id, _('Sozlamalar ⚙️'), reply_markup=uz_sets)


def handlers_settings_changes():
    ls = ["Ism sharifini o'zgartirish", "Telefonni o'zgartirish", "Изменить имя", "Изменить телефон",
          'Atı familiasın ózgertiw', "Telefon nomerin ózgertiw"]
    for x in ls:
        dp.register_message_handler(change_settings, Text(equals=x))

@sesionExceptions()
async def change_settings(message: types.Message):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    if message.text == _("Ism sharifini o'zgartirish"):
        await changes(message.from_user.id, message, Regist, user.lang, 'change_name')
    if message.text == _("Telefonni o'zgartirish"):
        await changes(message.from_user.id, message, Regist, user.lang, 'change_phone')


async def changes(user_id, message, Regist, lang, step):
    if step == 'change_name':
        await Regist.change_name.set()

        text = await take_text(lang, 1, user_id, message)

        await bot.send_message(user_id, text,
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Bekor qilish'))))
    if step == 'change_phone':
        await Regist.change_phone.set()
        await bot.send_message(user_id, _('Kontaktni yuboring'),
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Kontaktni yuboring'), request_contact=True)))


@dp.message_handler(state=Regist.change_name)
@sesionExceptionsState()
async def changeName(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    await state.finish()

    if new_name == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))
        return

    else:
        user.fio = new_name
        await db.session.commit()

        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Regist.change_phone)
@sesionExceptionsState()
async def changePhone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.contact.phone_number
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    await state.finish()
    if new_name == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))
        return

    else:
        user.phone = new_name
        await db.session.commit()

        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))


@dp.message_handler(Text(equals="Ma'lumotlarni ko'rish"))
@dp.message_handler(Text(equals="Посмотреть данные"))
@dp.message_handler(Text(equals="Maǵlıwmatlardı kóriw"))
@sesionExceptions()
async def sendMyName(message: types.Message):
    user_id = message.from_user.id
    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))

    user = user.scalar()

    tuman = await db.session.execute(select(db.Tuman).filter_by(id=user.tuman_id))
    tuman = tuman.scalar()

    sets_change = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(_("Ism sharifini o'zgartirish"))).add(KeyboardButton(_("Telefonni o'zgartirish"))).add(
        _("Hududni o'zgartirish")).add(
        _('Bekor qilish'))

    if user.lang == 'uz':
        await bot.send_message(user_id,
                               f'Sizning FISH {user.fio}, Sizning telefon raqamingiz: {user.phone}, {user.viloyati.name_uz}, {tuman.name_uz2}',
                               reply_markup=sets_change)
    elif user.lang == 'ru':
        await bot.send_message(user_id,
                               f'Ваше ФИО  {user.fio}, ваш номер телефона: {user.phone}, {user.viloyati.name_ru}, {tuman.name_ru2}',
                               reply_markup=sets_change)
    else:
        await bot.send_message(user_id,
                               f'Sizdiń FAA {user.fio}, Sizdiń telefon nomerińiz: {user.phone}, {user.viloyati.name_uz_kir}, {tuman.name_uz_kir2}',
                               reply_markup=sets_change)


@dp.message_handler(Text(equals="Hududni o'zgartirish"))
@dp.message_handler(Text(equals="Поменять область"))
@dp.message_handler(Text(equals="Aymaqtı ózgertiw"))
@sesionExceptions()
async def change_viloyat_button(message: types.Message):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    kb = await get_viloyats(user.lang)
    await Regist.change_viloyat.set()
    await bot.send_message(message.from_user.id, _("Tugmasini bosing"), reply_markup=kb.add(_('Bekor qilish')))

@sesionExceptions()
async def handlers_uz():
    cats = await db.session.execute(select(db.Viloyat))
    cats = cats.scalars()
    for x in cats:
        dp.register_message_handler(change_viloyat, Text(equals=x.name_uz), state=None)

@sesionExceptions()
async def handler_murojats():
    cats = await db.session.execute(select(db.Application))
    cats = cats.scalars()
    for x in cats:
        dp.register_message_handler(get_murojat, Text(equals=f'№{x.id}'), state=None)

@sesionExceptions()
async def get_murojat(message: types.Message):
    user_id = message.from_user.id
    print(int(message.text[1:]))
    apps = await db.session.execute(select(db.Application).filter(
        db.Application.id == int(message.text[1:])))

    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    app = apps.scalar()

    if user.lang == 'uz':

        message = f'''№{app.id}
Sizning murojaatingiz: {app.application}
{app.created_at.strftime("%Y.%m.%d")}
            '''
    elif user.lang == 'ru':

        message = f'''№{app.id}
Ваше обращение: {app.application}
{app.created_at.strftime("%Y.%m.%d")}
            '''
    else:

        message = f'''№{app.id}
Sizdiń múrájatingiz: {app.application}
{app.created_at.strftime("%Y.%m.%d")}
                    '''
    await bot.send_message(user_id, message, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_('Mening murojaatlarim 🧾'))
    ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
          ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
        KeyboardButton(_('Sozlamalar ⚙️'))))


@dp.message_handler(state=Regist.change_viloyat)
@sesionExceptionsState()
async def change_viloyat(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if new_name == _('Bekor qilish'):
        await state.finish()
        await bot.send_message(user_id, _('Bekor qilish'),
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Mening murojaatlarim 🧾'))
                               ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
                                     ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
                                   KeyboardButton(_('Sozlamalar ⚙️'))))
        return

    else:
        async with state.proxy() as data:
            data['change_viloyat'] = message.text
            await Regist.next()
            kb = await generate_tuman_kb(message.text, user.lang)
            text = await take_text(user.lang, 4, message.from_user.id, message)
            await bot.send_message(message.from_user.id, text,
                                   reply_markup=kb.add(_('Bekor qilish')))


@dp.message_handler(state=Regist.change_tuman)
@sesionExceptionsState()
async def change_tuman(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_tuman = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if new_tuman == _('Bekor qilish'):
        await state.finish()
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))
        return

    else:
        async with state.proxy() as data:
            data['change_tuman'] = new_tuman
        #     object = tuple(data.values())
        #
        # if user.lang == 'uz':
        #     cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz=object[0]))
        # if user.lang == 'ru':
        #     cat = await db.session.execute(select(db.Viloyat).filter_by(name_ru=object[0]))
        # if user.lang == 'uz_kir':
        #     cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=object[0]))
        # cat = cat.scalar()
        #
        # user.viloyat_id = cat.id
        # user.tuman = new_tuman
        # await db.session.commit()
        await Regist.next()

        text = await take_text(user.lang, 5, message.from_user.id, message)
        kb = await generate_mahalla_kb(new_tuman, user.lang)
        await bot.send_message(message.from_user.id, text, reply_markup=kb.add(_('Bekor qilish')))

        # await state.finish()

        # await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
        #     KeyboardButton(_('Mening murojaatlarim'))
        # ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
        #       ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
        #     KeyboardButton(_('Sozlamalar'))))


@dp.message_handler(state=Regist.change_mfy)
@sesionExceptionsState()
async def change_mfy(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_mfy = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if new_mfy == _('Bekor qilish'):
        await state.finish()
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))
        return

    else:
        async with state.proxy() as data:
            object = tuple(data.values())

        if user.lang == 'uz':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz=object[0]))
            tuman = await db.session.execute(select(db.Tuman).filter_by(name_uz2=object[1]))
            mfy = await db.session.execute(select(db.Mfy).filter_by(name_uz=new_mfy))
        if user.lang == 'ru':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_ru=object[0]))
            tuman = await db.session.execute(select(db.Tuman).filter_by(name_ru2=object[1]))
            mfy = await db.session.execute(select(db.Mfy).filter_by(name_ru=new_mfy))
        if user.lang == 'uz_kir':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=object[0]))
            tuman = await db.session.execute(select(db.Tuman).filter_by(name_uz_kir2=object[1]))
            mfy = await db.session.execute(select(db.Mfy).filter_by(name_uz_kir=new_mfy))

        cat = cat.scalar()
        tuman = tuman.scalar()
        mfy = mfy.scalar()

        user.viloyat_id = cat.id
        user.tuman_id = tuman.id
        user.mfy_id = mfy.id
        await db.session.commit()

        await state.finish()

        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim 🧾'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring 📝'))
              ).add(KeyboardButton(_("🇺🇿/🇷🇺"))).add(
            KeyboardButton(_('Sozlamalar ⚙️'))))


@dp.message_handler(commands='logout')
@sesionExceptions()
async def logout(message: types.Message):
    user_id = message.from_user.id
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if user:

        await db.session.delete(user)
        await db.session.commit()

        await bot.send_message(user_id, 'you has been deleted!', reply_markup=kb_client)
    else:
        await bot.send_message(user_id, 'you are not registered!', reply_markup=kb_client)
