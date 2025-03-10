from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import save_poll_metadata, get_poll_options, get_weekly_stats
from config import Config

# Define point values for each poll option (indexed from 0)
POINTS_MAPPING = {1: 5, 2: 3, 3: 2, 4: 1, 5: 0}

scheduler = AsyncIOScheduler()

async def send_message(bot: Bot):
    """Send scheduled messages and a poll (if enabled)."""
    message_text = "Päivän Sanapyramidi!\n\nhttps://yle.fi/a/74-20131998"
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


async def weekly_stats(channel_id):
    """Calculate and return the weekly leaderboard for a given channel."""
    votes = await get_weekly_stats(channel_id)

    if not votes:
        return "No votes recorded in the last 7 days for this channel."

    # Calculate scores
    user_scores = {}
    for username, sort_order in votes:
        points = POINTS_MAPPING.get(sort_order + 1, 0)  # Convert 0-based index to 1-based
        user_scores[username] = user_scores.get(username, 0) + points

    # Sort users by score (highest first) & apply sports-style ranking
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    # Generate ranking with sports-style placement
    result_lines = []
    prev_score = None
    rank = 0
    actual_position = 0

    for i, (username, score) in enumerate(sorted_scores):
        actual_position += 1
        if score != prev_score:  # Only update rank if score is different
            rank = actual_position

        result_lines.append(f"{rank}. {username} - {score}p")
        prev_score = score

    return "🏆 **Edellisviikon tulokset** 🏆\n" + "\n".join(result_lines)


async def send_weekly_stats(bot: Bot):
    """Send weekly stats to all configured channels."""
    for channel in Config.CHANNELS:
        chat = await bot.get_chat(chat_id=channel)
        channel_id = chat.id
        channel_name = chat.title or chat.username or "Unknown Channel"
        stats = await weekly_stats(channel_id)

        try:
            await bot.send_message(chat_id=channel_id, text=stats)
            print(f"✅ Weekly stats sent to {channel_name} ({channel_id})")

        except Exception as e:
            print(f"❌ Error sending weekly stats to {channel_name} ({channel_id}): {e}")



def schedule_tasks(bot: Bot):
    """Schedule daily messages and polls."""
    scheduler.add_job(send_message, "cron", hour=Config.HOUR, minute=Config.MINUTE, args=[bot])
    scheduler.add_job(send_weekly_stats, "cron", day_of_week="mon", hour=Config.HOUR, minute=0, args=[bot])
    scheduler.start()
