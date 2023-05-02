import aiogram
from aiogram import types
import json
from bot_main.wireguardBot import database as db, api

from .pay import choose_tariff
from base64 import b64decode
from aiogram.utils import exceptions
from aiogram.utils.markdown import bold, text
from aiogram.types import ParseMode
from .messages import *

f = open('env.json')
config = json.load(f)
DAY_PAY = config['DAY_PAY']
f.close()


def get_data(chat_id):
    user = db.get_vpn_by_chat_id(chat_id)
    days = int(user['amount']) // int(DAY_PAY)
    msg = text(
        "Ваш id в системе: ",
        bold(f"{user['id']}\n"),
        "Текущий баланс: ",
        bold(f"{user['amount']} ₽\n"),
        "Хватит на ",
        bold(f"{days}"), sep="")
    if days % 10 in [2, 3, 4]:
        msg += " дня"
    elif days % 10 == 1:
        msg += " день"
    else:
        msg += " дней"
    return msg


async def main_menu(message: aiogram.types.Message, bot: aiogram.Bot, edit: bool = False):
    chat_id = message.chat.id
    msg = "🏡Главное меню:"
    buttons = [
        [types.InlineKeyboardButton(text="🔑 Мои VPN📱💻", callback_data="my_vpn")],
        [
            types.InlineKeyboardButton(text="💰Баланс", callback_data="balance"),
            types.InlineKeyboardButton(text="📋Купить VPN", callback_data="top_up_balance")
        ],
        [
            types.InlineKeyboardButton(text="Пригласить 👫👫", callback_data="partner"),
            types.InlineKeyboardButton(text="📖Помощь", callback_data="help")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if edit:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message.message_id,
            text=msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


async def get_config_file(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    vpn_list_txt = callback.data
    chat_id = callback.from_user.id
    vpn_id = vpn_list_txt.replace("vpn_", "")
    vpn = db.get_vpn_by_vpn_id(vpn_id)
    if vpn is False:
        await bot.send_message(chat_id=chat_id, text="Что-то пошло не так")

    file_name = "VPN15_" + str(1000 + int(vpn['allocated_ips'].split("/")[0].split(".")[-1]))
    en = "Включен" if vpn['enabled'] else "Отключен"
    msg = SEND_CONFIG_MSG.format(name=file_name, enable=en, days=int(vpn['amount']) // DAY_PAY)
    await bot.send_message(chat_id=chat_id, text=msg)
    # await bot_main.delete_message(chat_id=callback.from_user.id,
    #                          message_id=callback.message.message_id)
    qrcode = api.get_client_by_id(vpn['id_vpn'])
    print(qrcode)
    if 'status' in qrcode and qrcode['status'] is False:
        await bot.send_message(
            chat_id=chat_id,
            text="Такого конфига больше не существует"
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
        [types.InlineKeyboardButton(text="🔑 Мои VPN📱💻", callback_data="my_vpn")],
        [types.InlineKeyboardButton(text="🏡Главное меню", callback_data="main_menu")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=chat_id,
        text="Возможные действия",
        reply_markup=keyboard
    )


async def update_data(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    chat_id = callback.from_user.id
    msg = get_data(chat_id)
    buttons = [
        [types.InlineKeyboardButton(text="Файл для подключения", callback_data="config_file")],
        [types.InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")],
        [types.InlineKeyboardButton(text="Обновить данные", callback_data="update_data")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await bot.edit_message_text(chat_id=chat_id,
                                    text=msg,
                                    reply_markup=keyboard,
                                    parse_mode=ParseMode.MARKDOWN,
                                    message_id=callback.message.message_id)
    except exceptions.MessageNotModified:
        pass


# https://t.me/freelance987654321_bot?start=54634548
async def partner(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    url = f"https://t.me/VPN15_bot?start={callback.from_user.id}"
    msg = f"""Пошлите другу ссылку: {url}
Когда ваш друг зайдет в наш бот по этой ссылке и создаст аккаунт, вы получите 50₽ на баланс!"""
    buttons = [
        [types.InlineKeyboardButton(text="⬅️Назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def balance(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    user = db.get_account_by_chat_id(callback.from_user.id)
    msg = f"💰 Ваш баланс: {user['amount']}₽"
    buttons = [
        [types.InlineKeyboardButton(text="➕ Пополнить баланс", callback_data="add_balance")],
        [types.InlineKeyboardButton(text="🔑 Купить ключ за баланс", callback_data="buy_key")],
        [types.InlineKeyboardButton(text="⬅️Назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def add_balance(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    msg = "На какую сумму вы хотите пополнить?"
    buttons = [
        [
            types.InlineKeyboardButton(text="200", callback_data="add_balance_200"),
            types.InlineKeyboardButton(text="500", callback_data="add_balance_500")
        ],
        [
            types.InlineKeyboardButton(text="1500", callback_data="add_balance_1500"),
            types.InlineKeyboardButton(text="Своя сумма", callback_data="choose_tariff_balace"),
        ],
        [types.InlineKeyboardButton(text="⬅️Назад", callback_data="balance")],
        [types.InlineKeyboardButton(text="🏡Главное меню", callback_data="main_menu")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg,
        reply_markup=keyboard
    )


async def buy_key(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, prolong=False):
    user = db.get_account_by_chat_id(callback.from_user.id)
    amount = int(user['amount'])
    msg = 'продлить' if prolong else 'купить'
    if amount < 499:
        msg = f"К сожалению, у Вас не достаточно средств😔. Но вы можете {msg} ключ сразу!"
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=msg
        )
        await choose_tariff(callback, bot, 1)
    else:
        await choose_tariff(callback, bot)


async def my_vpn(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, prolong: bool = False):
    chat_id = callback.from_user.id
    vpn_list = db.get_vpn_by_chat_id(chat_id)
    if vpn_list is False:
        msg = NO_VPN_TEXT
        await bot.send_message(chat_id=chat_id, text=msg)
    buttons = []
    for it, vpn in enumerate(vpn_list):
        file_name = f"{it + 1} 🔑 🚀  VPN15_" + str(1000 + int(vpn['allocated_ips'].split("/")[0].split(".")[-1])) + \
                    f" Осталось {int(vpn['amount']) // DAY_PAY} дней"
        buttons.append([types.InlineKeyboardButton(text=file_name,
                                                   callback_data=f"vpn_{vpn['id_vpn']}" if not prolong
                                                   else f"pro_long_{vpn['id_vpn']}")])
    if not prolong:
        buttons.append([types.InlineKeyboardButton(text="⌛Продлить VPN", callback_data="prolong_vpn")])
    buttons.append([types.InlineKeyboardButton(text="⬅️Назад", callback_data="main_menu")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    answer_text = "🔑Мои VPN:"
    if prolong:
        answer_text = "Какой VPN необходимо продлить?"
    await bot.send_message(
        chat_id=chat_id,
        text=answer_text,
        reply_markup=keyboard
    )
