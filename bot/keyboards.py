from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from bot.utils import default_languages

web_app = WebAppInfo(url='https://chere-bot-test.vercel.app/ru')


def cancel_button():
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Cancel", callback_data="cancel")],
    ])
    return btn


def get_languages(flag="lang"):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="uz 🇺🇿", callback_data=f"{flag}_uz"),
         InlineKeyboardButton(text='ru 🇷🇺', callback_data=f"{flag}_ru")],])
    return keyboard


def get_languages_is_none():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="uz 🇺🇿", callback_data='not_found_lang_uz'),
         InlineKeyboardButton(text='ru 🇷🇺', callback_data='not_found_lang_ru')]])
    return keyboard


def get_registration_and_login_keyboard(user_language):
    registration_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=default_languages[user_language]['registration'], callback_data='registration')],
        [InlineKeyboardButton(text=default_languages[user_language]['login'], callback_data='login')],])

    return registration_keyboard if registration_keyboard else []

def get_registration_keyboard(user_lang):
    registration_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=default_languages[user_lang]['registration'], callback_data='registration')]])
    return registration_keyboard if registration_keyboard else []


def get_user_types(user_language):
    user_types_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=default_languages[user_language]['individual'], callback_data='individual'),
            InlineKeyboardButton(text=default_languages[user_language]['legal'], callback_data='legal')
        ]
    ])
    return user_types_keyboard if user_types_keyboard else []


def get_user_contacts(user_language):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=default_languages[user_language]['share_contact'], request_contact=True)],
    ], resize_keyboard=True)

    return keyboard


def get_main_menu(language):
    main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=default_languages[language]['web_app'], web_app=web_app),
         KeyboardButton(text=default_languages[language]['settings'])],

        [KeyboardButton(text=default_languages[language]['contact_us']),
         KeyboardButton(text=default_languages[language]['my_orders'])],
        [KeyboardButton(text=default_languages[language]['logout']),]

    ], resize_keyboard=True)
    return main_menu_keyboard

def get_confirm_button(user_lang):
    button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=default_languages[user_lang]['create_order']),
     KeyboardButton(text=default_languages[user_lang]['cancel'])],
    ], resize_keyboard=True)
    return button

def inline_create_order(u_lang, c_data):
    key = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=default_languages[u_lang]['create_order'], callback_data=c_data)],
    ])
    return key

def location_user(u_lang):
    kb = [
        [KeyboardButton(text=default_languages[u_lang]['order_address'], request_location=True)
         ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard