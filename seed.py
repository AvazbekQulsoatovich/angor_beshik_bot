import asyncio
import json
import aiosqlite
from database.db import DB_PATH

async def seed():
    async with aiosqlite.connect(DB_PATH) as db:
        # Kategoriyalar
        categories = [
            ("Yog'och beshiklar", "🪵"),
            ("Elektron beshiklar", "🎶"),
            ("Beshik-to'y to'plamlari", "🎁")
        ]
        for name, emoji in categories:
            await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

        # Kategoriya ID larini olish
        async with db.execute("SELECT id, name FROM categories") as cursor:
            cats = await cursor.fetchall()
            cat_map = {name: id for id, name in cats}
        
        # Mahsulotlar (Rasmlar Unsplash'dan vaqtinchalik URL sifatida olinmoqda)
        products = [
            (
                cat_map["Yog'och beshiklar"], 
                "Qo'qon yog'och beshigi", 
                "Sifatli yong'oq daraxtidan yasalgan an'anaviy beshik. O'lchami: 110x55 sm. \nRanglar: Oq, Yong'oq rangi.", 
                "750 000 so'm", 
                ["https://images.unsplash.com/photo-1595166258079-7a0e38a2e5cb?auto=format&fit=crop&w=500"], 
                True
            ),
            (
                cat_map["Elektron beshiklar"], 
                "Zamonaviy musiqali beshik", 
                "Avtomatik tebranadi (bluetooth orgali boshqarish mumkin), 5 xil musiqa va taymer. \nRangi: Oq, Havorang.", 
                "1 200 000 so'm", 
                ["https://images.unsplash.com/photo-1505692794401-b3b44b6b6697?auto=format&fit=crop&w=500"], 
                True
            ),
            (
                cat_map["Beshik-to'y to'plamlari"], 
                "To'liq beshik to'plami VIP", 
                "Beshik, ko'rpacha, to'shakcha, yostiqcha, pashshaxona (moskit tarmog'i) va chaqaloq kiyimlari to'plami. \nRangi: Pushti/Bej.", 
                "1 800 000 so'm", 
                ["https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=500"], 
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
    print("Baza muvaffaqiyatli to'ldirildi!")

if __name__ == "__main__":
    asyncio.run(seed())
