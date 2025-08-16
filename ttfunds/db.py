import aiosqlite
import pandas as pd
from .config import CONFIG


async def init_db():
    async with aiosqlite.connect(CONFIG["db_path"]) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS fund_realtime (
            code TEXT,
            name TEXT,
            gztime TEXT,
            dwjz REAL,
            gsz REAL,
            gszzl REAL,
            PRIMARY KEY(code, gztime)
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS fund_history (
            code TEXT,
            x REAL,
            y REAL,
            equityReturn REAL,
            unitMoney TEXT,
            cumulative REAL,
            PRIMARY KEY(code, x)
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS fund_list (
            fund_code TEXT PRIMARY KEY,
            abbr TEXT,
            name TEXT,
            type TEXT,
            pinyin TEXT
        )
        """)
        await db.commit()


async def save_realtime(code, data):
    await init_db()
    async with aiosqlite.connect(CONFIG["db_path"]) as db:
        await db.execute(
            "INSERT OR REPLACE INTO fund_realtime VALUES (?,?,?,?,?,?)",
            (code, data.get("name"), data.get("gztime"), data.get("dwjz"), data.get("gsz"), data.get("gszzl"))
        )
        await db.commit()


async def save_history(code, df: pd.DataFrame):
    await init_db()
    async with aiosqlite.connect(CONFIG["db_path"]) as db:
        for _, row in df.iterrows():
            await db.execute(
                "INSERT OR REPLACE INTO fund_history VALUES (?,?,?,?,?,?)",
                (code, row.get("x"), row.get("y"), row.get("equityReturn"), row.get("unitMoney"), row.get("cumulative"))
            )
        await db.commit()


async def save_fund_list(df: pd.DataFrame):
    await init_db()
    async with aiosqlite.connect(CONFIG["db_path"]) as db:
        await db.execute("DELETE FROM fund_list")
        for _, row in df.iterrows():
            await db.execute(
                "INSERT OR REPLACE INTO fund_list VALUES (?,?,?,?,?)",
                (row.get("fund_code"), row.get("abbr"), row.get("name"), row.get("type"), row.get("pinyin"))
            )
        await db.commit()