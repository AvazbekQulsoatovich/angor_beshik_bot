import asyncio
import aiosqlite

DB_PATH = "beshik.db"

async def reset_data():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM categories")
        await db.commit()
    print("Mahsulotlar va kategoriyalar tozalandi.")

if __name__ == "__main__":
    asyncio.run(reset_data())
