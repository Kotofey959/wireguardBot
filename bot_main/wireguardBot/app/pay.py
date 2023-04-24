import aiogram
from aiogram import types
from yoomoney import Authorize, Quickpay, Client
import random
from bot_main.wireguardBot import database as db, api
import json


f = open('env.json')
config = json.load(f)
YOOMONEY_TOKEN = config['YOOMONEY_TOKEN']
DAY_PAY = config['DAY_PAY']
f.close()


def get_label():
    password = ""
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 10
    for i in range(length):
        password += random.choice(chars)
    print(password)
    return password


def test():
    Authorize(
        client_id="7EFDDD74E7779ED7B04433CEC694576B7253AB911A21D1C4AF5F84D25D16E9C7",
        redirect_uri="http://t.me/VPN15_bot",
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ]
    )


async def pay_buttons(
        chat_id: int,
        bot: aiogram.Bot,
        value: int,
        count: int = 1,
        pay: int = 0):

    label = get_label()
    label = label + f"_{count}_{pay}"
    quickpay = Quickpay(
        receiver="410011952023316",
        quickpay_form="shop",
        targets="VPN 15",
        paymentType="SB",
        sum=value,
        label=label
    )

    db.add_payment(chat_id, value, label)

    msg = "Счет уже выставлен, можете оплатить.После успешной оплаты платежа, обязательно нажмите кнопку '✅ Я оплатил(а)' "
    buttons = [
        [types.InlineKeyboardButton(text="Оплатить", url=quickpay.redirected_url)],
        [types.InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data="appr_pay")],
        [types.InlineKeyboardButton(text="🏡В главное меню", callback_data="main_menu")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=chat_id,
        text=msg,
        reply_markup=keyboard)


async def get_operation_status(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    chat_id = callback.from_user.id
    user = db.get_account_by_chat_id(chat_id)
    print(user)

    if user['is_paid'] == 0:
        client = Client(YOOMONEY_TOKEN)
        details = client.operation_history(label=user['label'])
        if len(details.operations) != 0 and details.operations[-1].status == "success":
            label_parse = user['label'].split("_")
            count = label_parse[-2]
            is_paid = label_parse[-1]
            if is_paid == 1:
                for i in range(count):
                    value_to_pay = int(user['value_to_pay'])
                    add_client_status = api.add_client(str(chat_id))
                    if add_client_status:
                        db.insert_or_update(chat_id, add_client_status, DAY_PAY * value_to_pay)
            else:
                db.update_payment_status(chat_id, 1, int(user['amount']) + int(user['value_to_pay']))
            # db.add_payment_in_history(chat_id, int(user['value_to_pay']), user['label'])
            await callback.answer(text="✅ Оплата успешно проведена!", show_alert=True)
        else:
            await callback.answer(text="Вы не оплатили товар или оплата еще в пути!", show_alert=True)
    else:
        await callback.answer(text="Оплата успешно проведена! Перейдите в 🔑 Мои VPN📱💻", show_alert=True)


async def choose_tariff(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot, pay: int = 0):
    chat_id = callback.from_user.id
    msg = "⬇️ ВЫБЕРИТЕ ТАРИФ:"
    buttons = [
        [types.InlineKeyboardButton(text="🔑 3 месяца - 499р.", callback_data=f"3_month_{pay}")],
        [types.InlineKeyboardButton(text="🔑 6 месяцев - 899р.", callback_data=f"6_month_{pay}")],
        [types.InlineKeyboardButton(text="🔑 12 месяцев - 1399р.", callback_data=f"12_month_{pay}")],
        [types.InlineKeyboardButton(text="🔑 2 ключа на год - 2399р.", callback_data=f"12_2_month_{pay}")],
        [types.InlineKeyboardButton(text="⬅️Назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    # await bot_main.edit_message_text(
    #     chat_id=chat_id,
    #     text=msg,
    #     reply_markup=keyboard,
    #     message_id=callback.message.message_id)
    await bot.send_message(
        chat_id=chat_id,
        text=msg,
        reply_markup=keyboard)

