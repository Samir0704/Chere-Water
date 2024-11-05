import json
import asyncio
from aiogram import Dispatcher, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
import environ
from django.contrib.auth.hashers import make_password
from pyexpat.errors import messages
from rest_framework_simplejwt.utils import aware_utcnow
from datetime import datetime, timedelta
import requests

from bot.db import create_user_db, get_company_contacts, get_my_orders, login_user, create_item_db, \
    create_order_from_cart, create_order_db
from bot.keyboards import get_languages, get_user_types, get_registration_keyboard, get_user_contacts, \
    get_main_menu, get_confirm_button, get_registration_and_login_keyboard, inline_create_order, location_user
from bot.states import LegalRegisterState, IndividualRegisterState, LoginStates, LegalAddressReminderState, \
    IndividualAddressReminderState
from bot.utils import default_languages, user_languages, introduction_template, calculate_total_water, \
    offer_text, order_text, local_user, fix_phone, message_history
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from aiogram.client.default import DefaultBotProperties
from asgiref.sync import sync_to_async
# from order.models import Order
# from users.models import CustomUser

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(".env")
# PROVIDER_TOKEN = env.str('PROVIDER_TOKEN')
dp = Dispatcher()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def welcome(message: Message):
    user_lang = user_languages.get(message.from_user.id, None)
    user_phone = local_user.get(message.from_user.id, None)
    if user_phone and user_lang:
        await message.answer_photo(
            photo="AgACAgIAAxkBAAISkGb30I5XavvJQVZN0LW83KGEUrXLAAKW6zEbXqG4SwJ-CmYiLzCSAQADAgADeQADNgQ",
            caption=introduction_template[user_lang], reply_markup=get_main_menu(user_lang))
    else:
        msg = default_languages['welcome_message']
        await message.answer(msg, reply_markup=get_languages())


@dp.callback_query(F.data == "cancel")
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    user_lang = user_languages[call.from_user.id]

    await state.clear()
    await call.message.answer("cancel", reply_markup=get_user_types(user_lang))


@dp.callback_query(F.data.startswith("lang"))
async def get_query_languages(call: CallbackQuery):
    user_id = call.from_user.id
    user_lang = call.data.split("_")[1]
    user_languages[user_id] = user_lang
    user = local_user.get(user_id, None)
    if user is None:
        await call.message.answer_photo(
            photo="AgACAgIAAxkBAAISkGb30I5XavvJQVZN0LW83KGEUrXLAAKW6zEbXqG4SwJ-CmYiLzCSAQADAgADeQADNgQ",
            caption=introduction_template[user_lang], reply_markup=get_registration_and_login_keyboard(user_lang))
    else:
        await call.message.answer_photo(
            photo="AgACAgIAAxkBAAISkGb30I5XavvJQVZN0LW83KGEUrXLAAKW6zEbXqG4SwJ-CmYiLzCSAQADAgADeQADNgQ",
            caption=introduction_template[user_lang], reply_markup=get_main_menu(user_lang))


@dp.callback_query(F.data == "registration")
async def reg_user_contact(call: CallbackQuery):
    user_id = call.from_user.id
    user_lang = user_languages[user_id]
    await call.message.answer(text=default_languages[user_lang]['select_user_type'],
                              reply_markup=get_user_types(user_lang))


@dp.callback_query(F.data == "login")
async def user_sign_in(call: CallbackQuery, state: FSMContext):
    user_lang = user_languages[call.from_user.id]
    await state.set_state(LoginStates.password)
    await call.message.answer(text=default_languages[user_lang]['sign_password'])


@dp.message(LoginStates.password)
async def sign_user_password(msg: Message, state: FSMContext):
    user_lang = user_languages[msg.from_user.id]
    await state.update_data(password=msg.text)
    await msg.answer(text=default_languages[user_lang]['contact'], reply_markup=get_user_contacts(user_lang))
    await state.set_state(LoginStates.phone)


@dp.message(LoginStates.phone)
async def sign_user_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    user_lang = user_languages[user_id]
    state_data = await state.get_data()
    password = state_data['password']
    if message.text is None:
        phone = fix_phone(message.contact.phone_number)
    else:
        phone = fix_phone(message.text)
    user = await login_user(phone, password, user_id, username, user_lang)
    if user:
        local_user[message.from_user.id] = user.phone_number
        user_languages[user_id] = user.user_lang
        await message.answer(
            text=default_languages[user.user_lang]['successful_login'],
            reply_markup=get_main_menu(user.user_lang))
    else:
        await message.answer(
            text=default_languages[user_lang]['user_not_found'],
            reply_markup=get_registration_keyboard(user_lang))
    await state.clear()


@dp.callback_query(F.data.in_(['legal', 'individual']))
async def legal_individual_registration(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_lang = user_languages[user_id]
    if call.data == 'legal':
        await call.message.answer(text=default_languages[user_lang]['company_name'])
        await state.set_state(LegalRegisterState.company_name)
    elif call.data == 'individual':
        await call.message.answer(text=default_languages[user_lang]['full_name'])
        await state.set_state(IndividualRegisterState.full_name)


@dp.message(LegalRegisterState.company_name)
async def company_name(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(company_name=message.text)
    await message.answer(text=default_languages[user_lang]['employee_name'])
    await state.set_state(LegalRegisterState.employee_name)


@dp.message(LegalRegisterState.employee_name)
async def employee_name(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(employee_name=message.text)
    await message.answer(text=default_languages[user_lang]['company_contact'],
                         reply_markup=get_user_contacts(user_lang))
    await state.set_state(LegalRegisterState.company_contact)


@dp.message(LegalRegisterState.company_contact)
async def company_contact(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    if message.text is None:
        phone = fix_phone(message.contact.phone_number)
        await state.update_data(company_contact=phone)
    else:
        phone = fix_phone(message.text)
        await state.update_data(company_contact=phone)
    await message.answer(text=default_languages[user_lang]['employee_count'])
    await state.set_state(LegalRegisterState.employee_count)


@dp.message(LegalRegisterState.employee_count)
async def employee_count(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(employee_count=message.text)
    await message.answer(text=default_languages[user_lang]['duration_days'])
    await state.set_state(LegalRegisterState.duration_days)


@dp.message(LegalRegisterState.duration_days)
async def duration_days(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(duration_days=message.text)
    await message.answer(text=default_languages[user_lang]['working_days'])
    await state.set_state(LegalRegisterState.working_days)


@dp.message(LegalRegisterState.working_days)
async def working_days(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(working_days=message.text)
    await message.answer(text=default_languages[user_lang]['password'])
    await state.set_state(LegalRegisterState.password)


@dp.message(LegalRegisterState.password)
async def working_days(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = user_languages[user_id]
    state_data = await state.get_data()
    employees_count = int(state_data['employee_count'])
    durations_days = int(state_data['duration_days'])
    total_water = calculate_total_water(state_data['working_days'], employees_count, durations_days)
    message_history[user_id] = total_water
    data = {
        "full_name": state_data['employee_name'],
        "username": message.from_user.username,
        "password": make_password(message.text),
        "company_name": state_data['company_name'],
        "phone_number": state_data['company_contact'],
        "user_type": "legal",
        "user_lang": user_lang,
        "telegram_id": user_id,
        "tg_username": f"https://t.me/{message.from_user.username}",
    }
    await create_user_db(data)
    local_user[user_id] = state_data['company_contact']

    await message.answer(offer_text[user_lang].format(employees_count, durations_days, total_water),
                         reply_markup=get_confirm_button(user_lang))
    await state.clear()


@dp.message(IndividualRegisterState.full_name)
async def full_name(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(full_name=message.text)
    await message.answer(text=default_languages[user_lang]['password'])
    await state.set_state(IndividualRegisterState.password)


@dp.message(IndividualRegisterState.password)
async def get_individual_password(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    await state.update_data(password=make_password(message.text))
    await message.answer(text=default_languages[user_lang]['contact'], reply_markup=get_user_contacts(user_lang))
    await state.set_state(IndividualRegisterState.contact)


@dp.message(IndividualRegisterState.contact)
async def contact(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]
    data = await state.get_data()
    if message.text is None:
        data['phone_number'] = fix_phone(message.contact.phone_number)
    else:
        data['phone_number'] = fix_phone(message.text)
    data['user_type'] = 'individual'
    data['telegram_id'] = message.from_user.id
    data['username'] = message.from_user.username
    data['tg_username'] = f"https://t.me/{message.from_user.username}"
    data['user_lang'] = user_lang
    await create_user_db(data)
    await message.answer(text=default_languages[user_lang]['successful_registration'],
                         reply_markup=get_main_menu(user_lang))
    local_user[message.from_user.id] = data['phone_number']

    await state.clear()


@dp.message(F.text.in_(["↩️ Akkauntdan chiqish", "↩️ Выйти из аккаунта"]))
async def logout(message: Message):
    user_lang = user_languages[message.from_user.id]
    local_user.pop(message.from_user.id)
    await message.answer(
        text=default_languages[user_lang]['exit'],
        reply_markup=get_registration_and_login_keyboard(user_lang)
    )


@dp.message(F.text.in_(["⚙️ Настройки", "⚙️ Sozlamalar"]))
async def settings(message: Message):
    user_lang = user_languages[message.from_user.id]
    await message.answer(text=default_languages[user_lang]['select_language'], reply_markup=get_languages("setLang"))


@dp.callback_query(F.data.startswith("setLang"))
async def change_language(call: CallbackQuery):
    user_lang = call.data.split("_")[1]
    user_languages[call.from_user.id] = user_lang
    await call.message.answer(text=default_languages[user_lang]['successful_changed'],
                              reply_markup=get_main_menu(user_lang))


@dp.message(F.text.in_(["📲 Biz bilan bog'lanish", "📲 Связаться с нами"]))
async def contact_us(message: Message):
    contacts = await get_company_contacts()
    user_lang = user_languages[message.from_user.id]
    await message.answer(
        text=default_languages[user_lang]['contact_us_message'].format(
            contacts.address, contacts.phone_number1, contacts.phone_number2, contacts.work_time), )


@dp.message(F.text.in_(["📦 Mening buyurtmalarim", "📦 Мои заказы"]))
async def get_orders(message: Message):
    phone_number = local_user[message.from_user.id]
    user_lang = user_languages[message.from_user.id]
    my_orders = await get_my_orders(phone_number)
    msg = ""
    if my_orders:
        for order in my_orders:
            msg += f"{order_text[user_lang].format(order.order_number, order.status)}\n"
            msg += "----------------------------\n"
        await message.answer(text=f"{default_languages[user_lang]['order']}\n {msg}")
    else:
        await message.answer(text=default_languages[user_lang]['order_not_found'],
                             reply_markup=get_main_menu(user_lang))


@dp.message(F.func(lambda msg: msg.web_app_data.data if msg.web_app_data else None))
async def get_btn(msg: Message):
    user_lang = user_languages[msg.from_user.id]
    web_data = json.loads(msg.web_app_data.data)
    product_lines = []
    product_ids = []
    total_sum = 0
    for product in web_data:
        title = product['title']
        quantity = product['quantity']
        price = float(product['price'])  # Преобразуем строку в float
        product_lines.append(f"{title} ({quantity})")
        total_sum += price * quantity  # Считаем общую сумму
        product_ids.append(product['id'])
        await create_item_db(msg.from_user.id, product['id'], product['quantity'])

    text = "Products:\n" + "\n".join(product_lines)
    text += f"\n\nTotal Sum: {total_sum:.2f}"  # Форматируем общую сумму
    await msg.answer(text=text, reply_markup=inline_create_order(user_lang, "web_key"))


@dp.callback_query(F.data == "web_key")
async def web_create_order(call: CallbackQuery, state: FSMContext):
    user_lang = user_languages[call.from_user.id]
    await call.message.answer(text=default_languages[user_lang]['order_address'])
    await state.set_state(IndividualAddressReminderState.order_address)


@dp.message(IndividualAddressReminderState.order_address)
async def get_user_address_state(msg: Message, state: FSMContext):
    user_lang = user_languages[msg.from_user.id]
    user_address = msg.text
    await state.update_data(order_address=user_address)
    await msg.answer(text=default_languages[user_lang]['reminder_days'])
    await state.set_state(IndividualAddressReminderState.reminder_days)


@dp.message(IndividualAddressReminderState.reminder_days)
async def get_reminder_days(msg: Message, state: FSMContext):
    user_lang = user_languages[msg.from_user.id]
    user_address = await state.get_data()
    order_address = user_address['order_address']
    if msg.text.isdigit():
        reminder_days = int(msg.text)
        order = await create_order_from_cart(msg.from_user.id, order_address, reminder_days)
        if order:
            await msg.answer(text=default_languages[user_lang]['order_created'].format(order.order_number),
                             reply_markup=get_main_menu(user_lang))
        else:
            await msg.answer(text=default_languages[user_lang]['order_not_created'], markup=get_main_menu(user_lang))
        await state.clear()


    else:
        await msg.answer(text=default_languages[user_lang]['enter_number'])
        await state.set_state(IndividualAddressReminderState.reminder_days)


@dp.message(F.text.in_(["✅ Place an order", "✅ Сделать заказ"]))
async def ask_for_location(message: Message, state: FSMContext):
    user_lang = user_languages[message.from_user.id]

    # First send the message with the location request keyboard
    await message.answer(
        text=default_languages[user_lang]['order_address'],
        reply_markup=location_user(user_lang)
    )

    # Then set the state without the reply_markup argument
    await state.set_state(LegalAddressReminderState.order_address)


@dp.message(LegalAddressReminderState.order_address)
async def get_legal_order_address(msg: Message, state: FSMContext):
    user_lang = user_languages[msg.from_user.id]

    if msg.location:  # Geolokatsiya mavjudligini tekshiramiz
        latitude = msg.location.latitude
        longitude = msg.location.longitude
        address = await sync_to_async(get_address)(latitude, longitude)
        if not address:
            await msg.answer("Manzilni topib bo'lmadi. Iltimos, qo'lda manzilni kiriting.")
        else:
            await state.update_data(order_address=address)  # Manzilni yangilaymiz
    else:
        await state.update_data(order_address=msg.text)  # Agar location yuborilmasa, qo'lda manzil

    await msg.answer(text=default_languages[user_lang]['reminder_days'])
    await state.set_state(LegalAddressReminderState.reminder_days)


def get_address(latitude, longitude):
    try:
        response = requests.get(f'https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}')
        data = response.json()

        if 'display_name' in data:
            address = data['display_name']
        else:
            # Ma'lumotni to'g'ri olmagan bo'lsa
            address = None

        return address
    except Exception as e:
        print(f"Error in get_address: {str(e)}")  # Log qilish
        return None


@dp.message(LegalAddressReminderState.reminder_days)
async def get_reminder_days(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user_lang = user_languages[msg.from_user.id]

    await state.update_data(reminder_days=msg.text)
    state_data = await state.get_data()

    total_water = message_history.pop(user_id, None)
    product_price = 15000
    total_price = total_water * product_price

    try:
        user = await CustomUser.objects.aget(telegram_id=msg.from_user.id)
        phone_number = user.phone_number
        await sync_to_async(user.save)()
    except ObjectDoesNotExist:
        await msg.answer("Foydalanuvchi ma'lumotlar bazasida topilmadi.")
        return

    # Latitude va Longitude orqali geolokatsiyani olish
    location = msg.location
    if location:
        latitude = location.latitude
        longitude = location.longitude
        address = await sync_to_async(get_address)(latitude, longitude)
        if not address:
            await msg.answer("Manzilni topib bo'lmadi.")
            return
    else:
        address = state_data['order_address']  # Geolokatsiya bo'lmasa, manzil state'dan olinadi

    # Buyurtma ma'lumotlarini shakllantirish
    order_data = {
        "user": user,
        "phone_number": phone_number,
        "address": address,  # Olingan manzilni bu yerga kiritamiz
        "total_price": total_price
    }

    # Buyurtmani yaratish
    await create_order_db(order_data, state_data['reminder_days'], user_id)
    await msg.answer(text=default_languages[user_lang]['order_created'], reply_markup=get_main_menu(user_lang))

    await state.clear()


@dp.message(F.text.in_(["❌ Отменить", "❌ Bekor qilish"]))
async def order_cancel(message: Message):
    user_lang = user_languages[message.from_user.id]
    await message.answer(text=default_languages[user_lang]['order_not_created'],
                         reply_markup=get_main_menu(user_lang))


async def schedule_reminder(telegram_id, delay):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=telegram_id, text="Sizning buyurtmangiz uchun eslatma: Vaqt tugadi!")


async def create_order_db_(order_data):
    order = await sync_to_async(Order.objects.create)(**order_data)

    reminder_days = order.user.reminder_days

    if reminder_days:
        reminder_date = order.created_at + timedelta(days=reminder_days)

        time_until_reminder = (reminder_date - datetime.now()).total_seconds()

        asyncio.create_task(schedule_reminder(order.user.telegram_id, time_until_reminder))

async def on_shutdown(dp):
    await bot.session.close()
    print("Bot has shut down cleanly.")