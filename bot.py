import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import PollAnswer
from config import Config
from database import setup_db, save_poll_response, get_monthly_stats, is_valid_poll, delete_poll_response
from scheduler import schedule_tasks

# Initialize bot and dispatcher
bot = Bot(token=Config.TOKEN)
dp = Dispatcher()

@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    """Handles the /stats command and returns stats for the issuing channel."""
    if not message.chat.id:
        await message.answer("❌ This command can only be used in channels.")
        return

    channel_id = str(message.chat.id)  # Convert to string for DB consistency
    stats = await get_monthly_stats(channel_id)
    await message.answer(stats)

@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    """Handles poll answers, ensuring only our daily poll is tracked."""
    user_id = poll_answer.user.id
    username = poll_answer.user.full_name or poll_answer.user.username or "Unknown"
    poll_id = poll_answer.poll_id
    # chosen_option_index = poll_answer.option_ids[0]
    option_ids = poll_answer.option_ids

    if not option_ids:
        # User retracted their vote – delete their previous vote from DB
        await delete_poll_response(poll_id, user_id)
        print(f"❌ User {user_id} retracted their vote from poll {poll_id}")
        return

    if not await is_valid_poll(poll_id):
        print(f"🚫 Ignoring poll response from {username} (not a daily poll)")
        return

    # Fetch channel ID and name from daily_polls table
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("SELECT channel_id, channel_name FROM daily_polls WHERE poll_id = ?", (poll_id,)) as cursor:
            row = await cursor.fetchone()

    if row is None:
        print(f"❌ Could not find channel info for poll_id {poll_id}")
        return

    channel_id, channel_name = row
    chosen_option_text = Config.POLL_OPTIONS[option_ids[0]]

    print(f"📝 {username} voted in {channel_name} ({channel_id}): {chosen_option_text}")
    await save_poll_response(poll_id, user_id, username, chosen_option_text, channel_id, channel_name)


async def main():
    """Main bot loop."""
    await setup_db()
    schedule_tasks(bot)
    print("🚀 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
