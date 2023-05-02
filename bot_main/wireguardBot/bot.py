import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand
import app.account as acc
import app.pay as pay
import app.common as common
import app.connect as connect
import app.check_balance as check
from datetime import datetime, timedelta
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils import States

logger = logging.getLogger(__name__)

f = open('env.json')
config = json.load(f)
f.close()

TOKEN = config["BOT_TOKEN"]
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, loop, storage=MemoryStorage())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/help", description="Как пользоваться"),
        BotCommand(command="/start", description="О боте"),
        BotCommand(command="/account", description="Подключиться к VPN"),
        BotCommand(command="/my_balance", description="Мой баланс")
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if len(message.text) > 7:
        ref = int(message.text.replace("/start", ""))
    else:
        ref = 0
    await common.welcome_message(message, bot, ref)


@dp.message_handler(commands=['account'])
async def start(message: types.Message):
    await acc.main_menu(message, bot)


@dp.callback_query_handler(Text(equals="balance"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.balance(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="add_balance"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.add_balance(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="add_balance"))
async def prfMenu(callback: types.CallbackQuery):
    value = int(callback.data.replace("add_balance_", ""))
    await pay.pay_buttons(callback.from_user.id, bot, value)
    await callback.answer()


@dp.callback_query_handler(Text(equals="choose_tariff_balace"))
async def prfMenu(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Введите сумму"
    )
    await callback.answer()
    await state.set_state(States.PAY_STATE)


@dp.message_handler(state=States.PAY_STATE)
async def prfMenu(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
    except Exception as ex:
        print(ex)
        await message.reply(text="Вы ввели некорректное значение!")
        return
    await pay.pay_buttons(message.from_user.id, bot, value)
    await state.finish()


@dp.callback_query_handler(Text(equals="buy_key"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.buy_key(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="partner"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.partner(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="my_vpn"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.my_vpn(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="vpn"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.get_config_file(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="pro_long"))
async def prfMenu(callback: types.CallbackQuery):
    vpn_id = callback.data.split('_')[-1]
    await pay.choose_tariff(callback, bot, prolong=vpn_id)
    await callback.answer()


@dp.callback_query_handler(Text(equals="config_file"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.get_config_file(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="help"))
async def prfMenu(callback: types.CallbackQuery):
    await common.help(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="get_access"))
async def prfMenu(callback: types.CallbackQuery):
    await common.get_access(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="aaccess_"))
async def prfMenu(callback: types.CallbackQuery):
    await common.get_access_operation_system(callback, bot, False)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="iaccess_"))
async def prfMenu(callback: types.CallbackQuery):
    await common.get_access_operation_system(callback, bot, True)
    await callback.answer()


@dp.callback_query_handler(Text(equals="android"))
async def prfMenu(callback: types.CallbackQuery):
    await common.operation_sys_help(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="iphone"))
async def prfMenu(callback: types.CallbackQuery):
    await common.operation_sys_help(callback, bot, True)
    await callback.answer()


@dp.callback_query_handler(Text(equals="write_to_help"))
async def prfMenu(callback: types.CallbackQuery):
    await common.write_to_help(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="update_data"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.update_data(callback, bot)
    await callback.answer(text="Данные обновлены", show_alert=True)


@dp.callback_query_handler(Text(equals="top_up_balance"))
async def prfMenu(callback: types.CallbackQuery):
    await pay.choose_tariff(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="main_menu"))
async def prfMenu(callback: types.CallbackQuery):
    # await acc.main_menu(callback.message, bot_main, True)
    await acc.main_menu(callback.message, bot)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="3_month"))
async def prfMenu(callback: types.CallbackQuery):
    pay = callback.data.split("_")[-1]
    if len(pay) > 5:
        await connect.add_new_key(callback, bot, 499, 1, prolong_id=pay)
        await callback.answer()
        return
    await connect.add_new_key(callback, bot, 499, 1, int(pay))
    await callback.answer()


@dp.callback_query_handler(Text(startswith="6_month"))
async def prfMenu(callback: types.CallbackQuery):
    pay = callback.data.split("_")[-1]
    if len(pay) > 5:
        await connect.add_new_key(callback, bot, 899, 1, prolong_id=pay)
        await callback.answer()
        return
    await connect.add_new_key(callback, bot, 899, 1, int(pay))
    await callback.answer()


@dp.callback_query_handler(Text(startswith="12_month"))
async def prfMenu(callback: types.CallbackQuery):
    pay = callback.data.split("_")[-1]
    if len(pay) > 5:
        await connect.add_new_key(callback, bot, 1399, 1, prolong_id=pay)
        await callback.answer()
        return
    await connect.add_new_key(callback, bot, 1399, 1, int(pay))
    await callback.answer()


@dp.callback_query_handler(Text(startswith="12_2_month"))
async def prfMenu(callback: types.CallbackQuery):
    pay = int(callback.data.split("_")[-1])
    await connect.add_new_key(callback, bot, 2399, 2, pay)
    await callback.answer()


@dp.callback_query_handler(Text(startswith="appr_pay"))
async def prfMenu(callback: types.CallbackQuery):
    prolong_id = callback.data.split("_")[-1]
    if len(prolong_id) > 5:
        await pay.get_operation_status(callback, prolong_id=prolong_id)
        await callback.answer()
        return
    await pay.get_operation_status(callback, bot)
    await callback.answer()


@dp.callback_query_handler(Text(equals="prolong_vpn"))
async def prfMenu(callback: types.CallbackQuery):
    await acc.my_vpn(callback, bot, prolong=True)
    await callback.answer()


async def check_message():
    while True:
        await check.check_balance(bot)
        dt = datetime.now() + timedelta(days=1)
        dt = dt.replace(hour=12, minute=0, second=0)
        time_for_wait = dt - datetime.now()
        await asyncio.sleep(time_for_wait.total_seconds())


if __name__ == '__main__':
    logging.basicConfig(filename="vpnbot.log",
                        level=logging.INFO,
                        format="%(asctime)s %(message)s",
                        filemode="w")
    logger.error("Starting bot_main")
    # pay.test()
    dp.loop.create_task(check_message())
    executor.start_polling(dp, skip_updates=True)
