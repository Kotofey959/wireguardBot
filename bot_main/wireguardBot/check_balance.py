import json

import aiogram
from aiogram import types

import api
import database as db
from messages import *

f = open('env.json')
config = json.load(f)
DAY_PAY = config['DAY_PAY']
f.close()


async def check_balance(bot: aiogram.Bot):
    all_vpn = db.get_all_users()
    if all_vpn is False:
        return
    for vpn in all_vpn:
        user = db.get_account_by_chat_id(vpn['id_tg'])
        if user is False:
            continue
        amount_vpm = int(vpn['amount'])
        if vpn['enabled'] == 0 and amount_vpm == 0:
            print('skip')
            buttons = [
                [types.InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

            try:
                await bot.send_message(chat_id=vpn['id'], text="Пополните баланс, либо получите новый ключ в разделе 'Купить VPN'",
                                   reply_markup=keyboard)
            except Exception as ex:
                print(ex)
            continue
        # if vpn['enabled'] == 0 and amount_vpm != 0:
        #     api.set_client_status(user_id=vpn['id_vpn'], status=True)
        #     db.update_enable_status(chat_id=vpn['id'], enabled=1)
        #     await bot_main.send_message(chat_id=vpn['id'], text="✅ Ваш счет опять активен")
        #     continue
        # if 0 < amount_vpm <= DAY_PAY:
        #     msg = ""
        #     buttons = [
        #         [types.InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")]
        #     ]
        #     keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        #     await bot_main.send_message(chat_id=vpn['id_tg'],
        #                            text=msg,
        #                            reply_markup=keyboard)
        if DAY_PAY*2 < amount_vpm <= DAY_PAY*3:
            msg = UP_BALANCE
            buttons = [
                [types.InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await bot.send_message(chat_id=vpn['id_tg'],
                                   text=msg,
                                   reply_markup=keyboard)
            except Exception as ex:
                print(ex)
            print("пора пополнить счет, через 3 дня вас отключат")
        elif amount_vpm == 0:
            if int(user['amount']) > DAY_PAY:
                db.add_or_update_user(user['id'], amount=int(user['amount']) - DAY_PAY)
                return
            api.set_client_status(user_id=vpn['id_vpn'], status=False)

            msg = "Пополните баланс, либо получите новый ключ в разделе 'Купить VPN'"
            buttons = [
                [types.InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            try:
                await bot.send_message(
                    chat_id=vpn['id_tg'],
                    text=msg,
                    reply_markup=keyboard
                )
            except Exception as ex:
                print(ex)
            db.update_enable_status(chat_id=vpn['id'], enabled=0)
            # return
        amount_vpm = amount_vpm - DAY_PAY
        if amount_vpm < 0:
            amount_vpm = 0
        db.update_amount_vpn(id=vpn['id'], amount=amount_vpm)

