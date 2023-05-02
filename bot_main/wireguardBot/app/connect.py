from .pay import *
from bot_main.wireguardBot.database import get_vpn_by_vpn_id

f = open('env.json')
config = json.load(f)
DAY_PAY = config['DAY_PAY']
f.close()


def register(chat_id: int, ref: int = 0):
    user_exist = db.get_account_by_chat_id(chat_id)
    if user_exist is False:
        # add_client_status = api.add_client(str(chat_id))
        # if add_client_status:
        print(ref)
        # print(add_client_status)
        # db.insert_or_update(chat_id, add_client_status)
        db.add_or_update_user(chat_id)
        if ref != 0 and chat_id != ref:
            ref_user = db.get_account_by_chat_id(ref)
            db.update_amount(ref, 50 + int(ref_user['amount']))


async def add_new_key(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot,
                      value: int, count: int = 1, pay: int = 0, prolong_id: str = None):
    days_in_offer = 30*3
    if value == 899:
        days_in_offer = 30*6
    elif value > 899:
        days_in_offer = 30 * 12

    chat_id = callback.from_user.id
    user = db.get_account_by_chat_id(chat_id)
    if user is False:
        await bot.send_message(
            chat_id=chat_id,
            text="Вас нет в системе, сначала пройдите регистрацию"
        )
        return

    if pay:
        await pay_buttons(callback.from_user.id, bot, value, count, pay)
        return
    need_value = value
    if need_value > int(user['amount']):
        await bot.send_message(
            chat_id=chat_id,
            text="На вашем балансе недостаточно средств. Но вы можете оплатить сразу"
        )
        if prolong_id:
            await pay_buttons(callback.from_user.id, bot, value, count, 1, prolong_id)
            return
        await pay_buttons(callback.from_user.id, bot, value, count, 1)
        return
    if prolong_id:
        current_vpn = get_vpn_by_vpn_id(prolong_id)
        current_amount = current_vpn['amount']
        new_amount = current_amount+(days_in_offer*6)
        db.update_amount_vpn_id(prolong_id, new_amount)
        db.update_amount(chat_id, int(user['amount']) - need_value)
        await callback.answer(text="Все прошло успешно", show_alert=True)
        return
    for i in range(count):
        add_client_status = api.add_client(str(chat_id))
        if add_client_status:
            print(add_client_status)
            db.insert_or_update(chat_id, add_client_status, DAY_PAY * days_in_offer)
            db.update_amount(chat_id, int(user['amount']) - need_value)
    await callback.answer(text="Все прошло успешно", show_alert=True)


async def prolong_key(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, value: int, id_vpn: str):
    pass

