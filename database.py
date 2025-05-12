import aiosqlite
from config import Config

async def setup_db():
    """Create tables for storing poll data and options."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS poll_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option_text TEXT UNIQUE,
                sort_order INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT UNIQUE,
                channel_id TEXT,
                channel_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS poll_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT,
                user_id INTEGER,
                username TEXT,
                option_id INTEGER,
                channel_id TEXT,
                channel_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (option_id) REFERENCES poll_options(id)
            )
        """)
        await db.commit()
        await insert_poll_options()

async def insert_poll_options():
    """Load poll options from config and insert into database."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        for sort_order, option_text in enumerate(Config.POLL_OPTIONS):
            await db.execute("""
                INSERT OR IGNORE INTO poll_options (option_text, sort_order) 
                VALUES (?, ?)
            """, (option_text, sort_order))
        await db.commit()

async def get_option_id(option_text):
    """Retrieve the ID of a poll option by its text."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("SELECT id FROM poll_options WHERE option_text = ?", (option_text,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_poll_options():
    """Retrieve all poll options from the database."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("SELECT option_text FROM poll_options ORDER BY sort_order") as cursor:
            return [row[0] async for row in cursor]


async def save_poll_metadata(poll_id, channel_id, channel_name):
    """Save poll metadata to track which polls are ours."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        await db.execute("""
            INSERT OR IGNORE INTO daily_polls (poll_id, channel_id, channel_name)
            VALUES (?, ?, ?)
        """, (poll_id, channel_id, channel_name))
        await db.commit()

async def is_valid_poll(poll_id):
    """Check if a poll ID exists in our daily poll records."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("SELECT 1 FROM daily_polls WHERE poll_id = ?", (poll_id,)) as cursor:
            return await cursor.fetchone() is not None

async def save_poll_response(poll_id, user_id, username, option_text, channel_id, channel_name):
    """Save or update a user's poll response with an option ID instead of raw text."""
    option_id = await get_option_id(option_text)
    if option_id is None:
        print(f"⚠️ Option '{option_text}' not found in database!")
        return

    async with aiosqlite.connect(Config.DB_FILE) as db:
        # Check if there's already a response for this user and poll
        cursor = await db.execute("""
            SELECT id FROM poll_results
            WHERE poll_id = ? AND user_id = ?
        """, (poll_id, user_id))
        existing = await cursor.fetchone()

        if existing:
            # Update existing record
            await db.execute("""
                UPDATE poll_results
                SET option_id = ?, username = ?, channel_id = ?, channel_name = ?, timestamp = CURRENT_TIMESTAMP
                WHERE poll_id = ? AND user_id = ?
            """, (option_id, username, channel_id, channel_name, poll_id, user_id))
        else:
            # Insert new record
            await db.execute("""
                INSERT INTO poll_results (poll_id, user_id, username, option_id, channel_id, channel_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (poll_id, user_id, username, option_id, channel_id, channel_name))

        await db.commit()


async def get_monthly_stats(channel_id):
    """Retrieve poll stats for the last 30 days, filtered by channel, sorted properly."""
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("""
            SELECT po.option_text, COUNT(pr.id) 
            FROM poll_results pr
            JOIN poll_options po ON pr.option_id = po.id
            WHERE pr.timestamp >= date('now', '-30 days') AND pr.channel_id = ?
            GROUP BY pr.option_id
            ORDER BY po.sort_order
        """, (channel_id,)) as cursor:
            results = await cursor.fetchall()

    if not results:
        return "No votes recorded this month for this channel."

    stats = "\n".join([f"{option}: {count} votes" for option, count in results])
    return f"📊 **Monthly Poll Stats for this channel**:\n{stats}"


async def get_weekly_stats(channel_id):
    async with aiosqlite.connect(Config.DB_FILE) as db:
        async with db.execute("""
            SELECT pr.username, po.sort_order
            FROM poll_results pr
            JOIN poll_options po ON pr.option_id = po.id
            WHERE pr.timestamp >= date('now', '-7 days') AND pr.channel_id = ?
        """, (channel_id,)) as cursor:
            votes = await cursor.fetchall()
    return votes