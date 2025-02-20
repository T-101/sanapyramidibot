import asyncio
import tomllib
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

TOKEN = config["bot"]["token"]
CHANNELS = list(config["channels"].values())
HOUR = config["schedule"]["hour"]
MINUTE = config["schedule"]["minute"]

session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


async def send_message():
    message_text = (
        "Muistakaa tämän päivän Sanapyramidi!\n\nhttps://yle.fi/a/74-20131998"
    )
    for channel in CHANNELS:
        try:
            await bot.send_message(chat_id=channel, text=message_text)
            print(f"✅ Message sent to {channel}")
        except Exception as e:
            print(f"❌ Failed to send message to {channel}: {e}")


scheduler = AsyncIOScheduler()
scheduler.add_job(send_message, "cron", hour=HOUR, minute=MINUTE)


# This would say a greeting when bot is started
#
# @dp.message()
# async def echo(message):
#      await message.answer("I'm a scheduled bot! I post messages at specific times.")


async def main():
    scheduler.start()
    print(f"🤖 Bot is running and scheduling messages at {HOUR}:{MINUTE}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
