import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import init_db
from handlers.user import user_router
from handlers.admin import admin_router

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
