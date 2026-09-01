import asyncio
import json
import aiosqlite
from aiogram import Bot
from aiogram.types import URLInputFile

BOT_TOKEN = "8887963978:AAFRXZ63dUSmdHHvC7hzyVGUs0MTHdlxIW8"
ADMIN_ID = 8133521082
DB_PATH = "beshik.db"

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    url = "https://picsum.photos/600/400"
    photo = URLInputFile(url)
    
    try:
        msg = await bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption="📸 Ushbu rasm test uchun bazadagi barcha 100 ta mahsulotga biriktirildi. \n\nEndi bot xatosiz ishlaydi!")
        file_id = msg.photo[-1].file_id
        
        async with aiosqlite.connect(DB_PATH) as db:
            photos_json = json.dumps([file_id])
            await db.execute("UPDATE products SET photo_file_ids = ?", (photos_json,))
            await db.commit()
        print("Success! File ID:", file_id)
    except Exception as e:
        print("Error:", e)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
