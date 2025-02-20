import datetime
import asyncio
import tomllib
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

TOKEN = config["bot"]["token"]
CHANNELS = config["channels"]
POLL_CONFIG = config["polls"]
HOUR = config["schedule"]["hour"]
MINUTE = config["schedule"]["minute"]

session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


async def send_message():
    message_text = "Päivän Sanapyramidi!\n\nhttps://yle.fi/a/74-20131998"

    now = datetime.datetime.now()
    poll_question = f"Sanapyramidi {now.day}.{now.month}.{now.year}"
    poll_options = ["0 virhettä", "1 virhe", "2 virhettä", "3 virhettä", "Vituix män"]

    for key, channel in CHANNELS.items():
        try:
            await bot.send_message(chat_id=channel, text=message_text)
            print(f"✅ Message sent to {channel}")

            # Send a poll if configured
            if POLL_CONFIG.get(key, False):
                await bot.send_poll(
                    chat_id=channel,
                    question=poll_question,
                    options=poll_options,
                    is_anonymous=False,
                    allows_multiple_answers=False,
                )
                print(f"📊 Poll sent to {channel}")

        except Exception as e:
            print(f"❌ Failed to send message/poll to {channel}: {e}")


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
