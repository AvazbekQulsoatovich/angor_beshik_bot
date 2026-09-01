import asyncio
import json
import aiosqlite
from database.db import DB_PATH

async def seed():
    async with aiosqlite.connect(DB_PATH) as db:
        # Delete existing data
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM categories")
        await db.execute("DELETE FROM inquiries")
        await db.commit()

        # 10 Categories
        categories = [
            ("Yog'och beshiklar", "🪵"),
            ("Musiqali beshiklar", "🎶"),
            ("Plastik ko'chma beshiklar", "🧺"),
            ("Osma beshiklar (Lyulka)", "🌙"),
            ("Transformer beshiklar", "🔄"),
            ("Beshik-to'y to'plamlari", "🎁"),
            ("Chaqaloqlar maneji", "🎪"),
            ("Egizaklar uchun beshiklar", "👯‍♂️"),
            ("Zamonaviy smart beshiklar", "📱"),
            ("Beshik jihozlari", "🧵")
        ]
        
        for name, emoji in categories:
            await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

        async with db.execute("SELECT id, name FROM categories") as cursor:
            cats = await cursor.fetchall()
        
        photo = ["https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Cradle_in_Uzbekistan.jpg/800px-Cradle_in_Uzbekistan.jpg"]
        
        # 10 products per category
        for cat_id, cat_name in cats:
            for i in range(1, 11):
                title = f"{cat_name} - Model {i}"
                desc = f"Eng yuqori sifatli materiallardan tayyorlangan. O'lchami: 110x55 sm. Kafolat: 1 yil.\n\nSifat raqami: {i}00{cat_id}"
                price = f"{500000 + (i * 50000)} so'm"
                in_stock = True if i % 4 != 0 else False # Every 4th item is out of stock (buyurtma)
                photos_json = json.dumps(photo)
                
                await db.execute(
                    "INSERT INTO products (category_id, title, description, price, photo_file_ids, in_stock) VALUES (?, ?, ?, ?, ?, ?)",
                    (cat_id, title, desc, price, photos_json, in_stock)
                )
        await db.commit()
    print("Database seeded with 10 categories and 100 products (10 per category).")

if __name__ == "__main__":
    asyncio.run(seed())
