import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

BOT_TOKEN = "8984289945:AAFwifPYYfbd_8QQFdhRRrgfzEsjsW5jdMw"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_balances = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 100  # Сразу даем 100 токенов для теста!
        
    await message.answer(
        f"👋 Привет! Добро пожаловать в игру.\n\n"
        f"💰 Ваш баланс: {user_balances[user_id]} токенов.\n"
        f"🎲 Одна игра стоит 1 токен. Чтобы сыграть, введите: /game\n"
        f"⭐️ Чтобы купить 10 токенов за Звезды, введите: /buy"
    )

@dp.message(Command("buy"))
async def send_invoice_handler(message: types.Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка 10 Токенов",
        description="Токены для игры в виртуальный кубик.",
        payload="pack_10_tokens",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="10 Токенов", amount=10)]
    )

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: types.Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    
    if payload == "pack_10_tokens":
        if user_id not in user_balances:
            user_balances[user_id] = 0
        user_balances[user_id] += 10
        await message.answer(f"⭐️ Начислено 10 токенов! Ваш баланс: {user_balances[user_id]}")

@dp.message(Command("game"))
async def play_game_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0
        
    if user_balances[user_id] < 1:
        await message.answer("❌ У вас нет токенов! Введите /buy.")
        return

    user_balances[user_id] -= 1
    dice_msg = await bot.send_dice(chat_id=message.chat.id, emoji="🎲")
    value = dice_msg.dice.value
    await asyncio.sleep(4)

    if value == 6:
        user_balances[user_id] += 5
        await message.answer(f"🎉 УРА! Выпала 6! Вы выиграли 5 токенов!\n💰 Баланс: {user_balances[user_id]}")
    else:
        await message.answer(f"Выпало число {value}.\n💰 Баланс: {user_balances[user_id]}. Еще раз: /game")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
