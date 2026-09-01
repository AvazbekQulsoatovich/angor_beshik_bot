import asyncio
import json
import aiosqlite
from database.db import DB_PATH

async def fix():
    async with aiosqlite.connect(DB_PATH) as db:
        # Delete existing
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM categories")
        await db.execute("DELETE FROM inquiries")
        await db.commit()

        # Re-insert
        categories = [
            ("Yog'och beshiklar", "🪵"),
            ("Elektron beshiklar", "🎶"),
            ("Beshik-to'y to'plamlari", "🎁")
        ]
        for name, emoji in categories:
            await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

        async with db.execute("SELECT id, name FROM categories") as cursor:
            cats = await cursor.fetchall()
            cat_map = {name: id for id, name in cats}
        
        # Using a reliable image from Wikipedia
        photo = ["https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Cradle_in_Uzbekistan.jpg/800px-Cradle_in_Uzbekistan.jpg"]
        
        products = [
            (
                cat_map["Yog'och beshiklar"], 
                "Qo'qon yog'och beshigi", 
                "Sifatli yong'oq daraxtidan yasalgan an'anaviy beshik. O'lchami: 110x55 sm. \nRanglar: Oq, Yong'oq rangi.", 
                "750 000 so'm", 
                photo, 
                True
            ),
            (
                cat_map["Elektron beshiklar"], 
                "Zamonaviy musiqali beshik", 
                "Avtomatik tebranadi, 5 xil musiqa va taymer. \nRangi: Oq, Havorang.", 
                "1 200 000 so'm", 
                photo, 
                True
            ),
            (
                cat_map["Beshik-to'y to'plamlari"], 
                "To'liq beshik to'plami VIP", 
                "Beshik, ko'rpacha, to'shakcha, yostiqcha, pashshaxona (moskit tarmog'i) va chaqaloq kiyimlari to'plami. \nRangi: Pushti/Bej.", 
                "1 800 000 so'm", 
                photo, 
                True
            )
        ]
        
        for p in products:
            photos_json = json.dumps(p[4])
            await db.execute(
                "INSERT INTO products (category_id, title, description, price, photo_file_ids, in_stock) VALUES (?, ?, ?, ?, ?, ?)",
                (p[0], p[1], p[2], p[3], photos_json, p[5])
            )
        await db.commit()
    print("Database fixed and re-seeded with reliable image URL.")

if __name__ == "__main__":
    asyncio.run(fix())
