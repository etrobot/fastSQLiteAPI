import aiosqlite
import sqlite3
from contextlib import asynccontextmanager

async def initialize_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                cookie TEXT NOT NULL,
                user TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(domain, user)
            )
        ''')
        await db.commit()

@asynccontextmanager
async def get_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        yield db 