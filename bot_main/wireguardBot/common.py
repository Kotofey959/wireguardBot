import json
from base64 import b64decode

import aiogram
from aiogram import types

import api
import database as db
from .account import main_menu
from .connect import register
from .messages import *

f = open('env.json')
config = json.load(f)
DAY_PAY = config['DAY_PAY']
f.close()


async def welcome_message(message: aiogram.types.Message,
                          bot: aiogram.Bot, ref: int = 0):
    buttons = []
    user_exist = db.get_account_by_chat_id(message.from_user.id)
    # register(message.from_user.id, ref)
    if user_exist is False:
        register(message.from_user.id, ref)
        buttons.append(
            [types.InlineKeyboardButton(text="🎉 Подключить VPN🎉", callback_data="get_access")]
        )
        msg = FIRST_TIME.format(user=message.from_user.username)
    else:
        users_vpn_list = db.get_vpn_by_chat_id(message.from_user.id)
        if users_vpn_list is False:
            msg = WELCOME_DONT_HAVE_VPN.format(user=message.from_user.username)
        else:
            msg = WELCOME_HAVE_VPN.format(user=message.from_user.username)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=message.from_user.id,
        text=msg,
        reply_markup=keyboard
    )
    if user_exist is not False:
        await main_menu(message, bot)


async def get_access(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    chat_id = callback.from_user.id
    user = db.get_account_by_chat_id(chat_id)
    add_client_status = api.add_client(str(chat_id))
    if add_client_status:
        print(add_client_status)
        db.insert_or_update(chat_id, add_client_status, DAY_PAY * 7)
        db.update_amount(chat_id, int(user['amount']) + 50)
    msg = CONGRATULATIONS
    buttons = [
        [types.InlineKeyboardButton(text="📱Android", callback_data=f"aaccess_{add_client_status['id']}")],
        [types.InlineKeyboardButton(text="🍎iOS (iPhone, iPad)", callback_data=f"iaccess_{add_client_status['id']}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def get_access_operation_system(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, iphone: bool = False):
    if iphone is False:
        msg = ANDROID
    else:
        msg = IPHONE
    vpn_list_txt = callback.data
    chat_id = callback.from_user.id
    vpn_id = vpn_list_txt.split("_")[-1]
    vpn = db.get_vpn_by_vpn_id(vpn_id)
    if vpn is False:
        await bot.send_message(chat_id=chat_id, text="Что-то пошло не так")

    # await bot_main.delete_message(chat_id=callback.from_user.id,
    #                          message_id=callback.message.message_id)
    qrcode = api.get_client_by_id(vpn['id_vpn'])
    print(qrcode)
    if 'status' in qrcode and qrcode['status'] is False:
        await bot.send_message(
            chat_id=chat_id,
            text="Такой конфига больше не существует"
        )
        return
    header, encoded = qrcode['QRCode'].split(",", 1)
    data = b64decode(encoded)
    await bot.send_photo(chat_id=callback.from_user.id, photo=data)
    # await bot_main.send_message(chat_id=callback.from_user.id,
    #                        text="Если вы не знаете, что с этим делать, то введите команду /help")
    config_file = api.download_client(vpn['id_vpn'])
    file_name = "VPN15_" + str(1000 + int(vpn['allocated_ips'].split("/")[0].split(".")[-1])) + ".conf"
    await bot.send_document(callback.from_user.id,
                            (file_name, config_file))

    buttons = [
        [types.InlineKeyboardButton(text="🏡Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def help(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    msg = "Выберите тип устройства, на который вы хотите установить vpn:"
    buttons = [
        [types.InlineKeyboardButton(text="📱Android", callback_data="android")],
        [types.InlineKeyboardButton(text="🍎iOS (iPhone, iPad)", callback_data="iphone")],
        [types.InlineKeyboardButton(text="Написать в поддержку📩", callback_data="write_to_help")],
        [types.InlineKeyboardButton(text="⬅️Назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def operation_sys_help(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, iphone: bool = False):
    if iphone is False:
        msg = ANDROID
    else:
        msg = IPHONE
    buttons = [
        [types.InlineKeyboardButton(text="🏡Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def write_to_help(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    msg = WRITE_TO_HELP
    buttons = [
        [types.InlineKeyboardButton(text="🏡Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )
