from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import save_poll_metadata, get_poll_options
from config import Config

scheduler = AsyncIOScheduler()

async def send_daily_poll(bot: Bot):
    """Sends a daily poll to all configured channels and saves poll metadata."""
    question = Config.POLL_QUESTION
    options = await get_poll_options()

    for channel in Config.CHANNELS:
        channel_id = channel["id"]
        channel_name = channel["name"]
        include_poll = channel.get("include_poll", True)  # Default to True

        try:
            poll_message = await bot.send_poll(
                chat_id=channel_id,
                question=question,
                options=options,
                is_anonymous=False
            )

            poll_id = poll_message.poll.id
            await save_poll_metadata(poll_id, channel_id, channel_name)
            print(f"✅ Poll sent to {channel_name} ({channel_id})")

        except Exception as e:
            print(f"❌ Failed to send poll to {channel_name} ({channel_id}): {e}")

async def send_message(bot: Bot):
    """Send scheduled messages and a poll (if enabled)."""
    message_text = "Good morning! ☀️ Have a great day!"
    options = await get_poll_options()

    for channel in Config.CHANNELS:
        try:
            chat = await bot.get_chat(chat_id=channel)
            channel_id = chat.id
            channel_name = chat.title or chat.username or "Unknown Channel"

            await bot.send_message(chat_id=channel, text=message_text)
            print(f"✅ Message sent to {channel_name} ({channel_id})")

            poll_msg = await bot.send_poll(
                chat_id=channel,
                question=Config.POLL_QUESTION,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=False,
            )
            print(f"📊 Poll sent to {channel_name}")

            await save_poll_metadata(poll_msg.poll.id, channel_id, channel_name)

        except Exception as e:
            print(f"❌ Error sending message/poll to {channel}: {e}")


def schedule_tasks(bot: Bot):
    """Schedule daily messages and polls."""
    # scheduler.add_job(send_daily_poll, "cron", hour=Config.HOUR, minute=Config.MINUTE, args=[bot])
    scheduler.add_job(send_message, "cron", hour=Config.HOUR, minute=Config.MINUTE, args=[bot])
    scheduler.start()
