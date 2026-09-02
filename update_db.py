import asyncio
import aiosqlite

async def update_db():
    async with aiosqlite.connect('c:/Users/Avaz/Desktop/beshikbot/beshik.db') as db:
        await db.execute("UPDATE transactions SET type = 'restock' WHERE description LIKE 'Omborga kirim%' OR description LIKE 'Tovar to''ldirildi%'")
        await db.commit()
        print('Updated local DB')
asyncio.run(update_db())
