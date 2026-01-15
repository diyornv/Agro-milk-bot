import aiosqlite

DB_NAME = "cows.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cows (
                cow_id INTEGER PRIMARY KEY,
                photo_file_id TEXT,
                description TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT,
                phone_number TEXT
            )
        """)
        # Simplistic migration for existing databases without phone_number
        try:
            await db.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
        except aiosqlite.OperationalError:
            pass # Column likely exists
            
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cow_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cow_id INTEGER,
                file_id TEXT
            )
        """)
        await db.commit()

async def add_cow(cow_id: int, description: str):
    async with aiosqlite.connect(DB_NAME) as db:
        # We replace the description. Photos are handled separately.
        # Check if cow exists to keep photos if we are just updating description? 
        # But usually add_cow is for new or overwrite. 
        # Let's assume overwrite logic for description, but we might want to clear old photos if re-adding.
        # For now, let's keep it simple: Add/Update description.
        await db.execute("""
            INSERT OR REPLACE INTO cows (cow_id, description)
            VALUES (?, ?)
        """, (cow_id, description))
        await db.commit()

async def add_cow_photo(cow_id: int, file_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO cow_photos (cow_id, file_id) VALUES (?, ?)", (cow_id, file_id))
        await db.commit()

async def clear_cow_photos(cow_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM cow_photos WHERE cow_id = ?", (cow_id,))
        await db.commit()

async def get_cow(cow_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT description FROM cows WHERE cow_id = ?", (cow_id,)) as cursor:
            desc_row = await cursor.fetchone()
        async with db.execute("SELECT file_id FROM cow_photos WHERE cow_id = ? LIMIT 1", (cow_id,)) as cursor:
            photo_row = await cursor.fetchone()
        if desc_row:
            description = desc_row[0]
            photo_file_id = photo_row[0] if photo_row else None
            return (photo_file_id, description)
        return None

async def get_cow_photos(cow_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT file_id FROM cow_photos WHERE cow_id = ?", (cow_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if user exists to preserve phone if updating only language
        async with db.execute("SELECT phone_number FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            phone = row[0] if row else None
            
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, language, phone_number)
            VALUES (?, ?, ?)
        """, (user_id, language, phone))
        await db.commit()

async def set_user_phone(user_id: int, phone_number: str):
    async with aiosqlite.connect(DB_NAME) as db:
        # Get language to preserve it
        async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            language = row[0] if row else None
            
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, language, phone_number)
            VALUES (?, ?, ?)
        """, (user_id, language, phone_number))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_language(user_id: int):
    user = await get_user(user_id)
    return user['language'] if user else None

async def delete_cow(cow_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("DELETE FROM cows WHERE cow_id = ?", (cow_id,))
        await db.commit()
        # Also clean up photos
        await db.execute("DELETE FROM cow_photos WHERE cow_id = ?", (cow_id,))
        await db.commit()
        return cursor.rowcount > 0
