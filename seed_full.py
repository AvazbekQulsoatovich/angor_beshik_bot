import asyncio
import json
import aiosqlite
from aiogram import Bot
from aiogram.types import URLInputFile

BOT_TOKEN = "8887963978:AAFRXZ63dUSmdHHvC7hzyVGUs0MTHdlxIW8"
ADMIN_ID = 8133521082
DB_PATH = "beshik.db"

CATEGORIES = [
    ("🪵 Yog'och beshiklar", "🪵"),
    ("🎵 Musiqali beshiklar", "🎵"),
    ("♻️ Plastik ko'chma beshiklar", "♻️"),
    ("🌙 Osma beshiklar", "🌙"),
    ("🔄 Transformer beshiklar", "🔄"),
    ("🎁 Beshik to'plamlari (Set)", "🎁"),
    ("🎪 Chaqaloqlar o'yin beshiklari", "🎪"),
    ("👯 Egizaklar uchun beshiklar", "👯"),
    ("📱 Zamonaviy smart beshiklar", "📱"),
    ("🛡 Beshik jihozlari va aksessuarlar", "🛡"),
]

PRODUCTS_TEMPLATE = [
    ("Classic {cat}", "An'anaviy uslubdagi qulay va chiroyli beshik. Bolaning sog'lom uxlashi uchun maxsus mo'ljallangan.", 850000, 500000),
    ("Premium {cat}", "Yuqori sifatli materiallardan tayyorlangan premium beshik. Uzoq xizmat qiladi.", 1200000, 750000),
    ("Mini {cat}", "Kichik o'lchamdagi kompakt beshik. Cheklangan joy uchun ideal.", 650000, 400000),
    ("Deluxe {cat}", "Deluxe seriyasi — maksimal qulaylik va chiroyli dizayn birlashgan.", 1500000, 950000),
    ("Standard {cat}", "Standart model — narxi hamyonbop, sifati yuqori.", 750000, 450000),
    ("Elite {cat}", "Elite seriyasi — faqat eng yaxshi materiallar ishlatilgan.", 1800000, 1100000),
    ("Comfort {cat}", "Comfort seriyasi — bolaning qulayligini birinchi o'ringa qo'ygan.", 950000, 580000),
    ("Smart {cat}", "Smart texnologiyali beshik — avtomatik tebranish va musiqali.", 2200000, 1400000),
    ("Junior {cat}", "Junior seriyasi — 0-12 oylik bolalar uchun maxsus.", 700000, 420000),
    ("Family {cat}", "Family seriyasi — oilangiz uchun eng zo'r tanlov.", 1100000, 680000),
]

async def main():
    print("Uploading sample photo to Telegram...")
    bot = Bot(token=BOT_TOKEN)
    
    try:
        photo = URLInputFile("https://picsum.photos/seed/beshik/600/400")
        msg = await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption="🌱 Default ma'lumotlar yuklanmoqda..."
        )
        file_id = msg.photo[-1].file_id
        print(f"Photo file_id: {file_id}")
    except Exception as e:
        print(f"Photo error: {e}")
        file_id = "AgACAgIAAxkDAANSapZa9zz1lu_MjHcYzSxOx7i1MMEAAsUcaxtxorFICIadBR3F6tgBAAMCAAN4AAM9BA"
    finally:
        await bot.session.close()

    photos_json = json.dumps([file_id])

    import sys
    sys.path.insert(0, '.')
    from database.db import init_db
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        # Clear existing data
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM categories")
        await db.execute("DELETE FROM transactions")
        await db.commit()
        print("Cleared existing data.")

        cat_ids = []
        for cat_name, emoji in CATEGORIES:
            cursor = await db.execute(
                "INSERT INTO categories (name, emoji, is_active) VALUES (?, ?, 1)",
                (cat_name, emoji)
            )
            cat_ids.append(cursor.lastrowid)
            print(f"Category added: {cat_name.encode('ascii','replace').decode()}")

        # Add products
        total = 0
        for i, cat_id in enumerate(cat_ids):
            cat_short = CATEGORIES[i][0].split(" ", 1)[1][:10]
            for tmpl in PRODUCTS_TEMPLATE:
                title = tmpl[0].format(cat=cat_short)
                desc = tmpl[1]
                price_str = f"{tmpl[2]:,} so'm"
                cost = tmpl[3]
                qty = 5  # 5 dona omborda
                await db.execute(
                    "INSERT INTO products (category_id, title, description, price, cost_price, sales_count, photo_file_ids, in_stock, is_active) VALUES (?,?,?,?,?,?,?,?,1)",
                    (cat_id, title, desc, price_str, cost, 0, photos_json, qty)
                )
                total += 1
        await db.commit()
        print(f"Added {total} products.")

        # Add sample transactions: expenses for inventory
        print("Adding sample transactions...")
        expenses = [
            ("expense", 5000000, "Yanvar: Yog'och beshiklar partiyasi (10 dona)"),
            ("expense", 3750000, "Fevral: Plastik beshiklar partiyasi (10 dona)"),
            ("expense", 2500000, "Mart: Osma beshiklar partiyasi (5 dona)"),
            ("expense", 200000, "Svet uchun to'lov — Yanvar"),
            ("expense", 150000, "Ijara — Fevral"),
            ("expense", 300000, "Yuk mashinasi — tovar tashish"),
        ]
        incomes = [
            ("income", 1200000, "Sotuv: Premium Yog'och beshik x1", None),
            ("income", 850000, "Sotuv: Classic Musiqali beshik x1", None),
            ("income", 1800000, "Sotuv: Elite Transformer beshik x1", None),
            ("income", 750000, "Sotuv: Standard Plastik beshik x1", None),
            ("income", 950000, "Sotuv: Comfort Osma beshik x1", None),
            ("income", 2200000, "Sotuv: Smart beshik x1", None),
            ("income", 1500000, "Sotuv: Deluxe Set x1", None),
            ("income", 700000, "Sotuv: Junior beshik x1", None),
            ("income", 1100000, "Sotuv: Family beshik x1", None),
            ("income", 650000, "Sotuv: Mini beshik x1", None),
        ]

        for t in expenses:
            await db.execute(
                "INSERT INTO transactions (type, amount, description) VALUES (?,?,?)",
                (t[0], t[1], t[2])
            )
        for t in incomes:
            await db.execute(
                "INSERT INTO transactions (type, amount, description, product_id) VALUES (?,?,?,?)",
                (t[0], t[1], t[2], t[3])
            )
        await db.commit()
        print("Sample transactions added.")

        # Update sales_count for some products to show top sellers
        await db.execute("UPDATE products SET sales_count = 15 WHERE title LIKE '%Smart%'")
        await db.execute("UPDATE products SET sales_count = 12 WHERE title LIKE '%Premium%'")
        await db.execute("UPDATE products SET sales_count = 10 WHERE title LIKE '%Elite%'")
        await db.execute("UPDATE products SET sales_count = 8 WHERE title LIKE '%Deluxe%'")
        await db.execute("UPDATE products SET sales_count = 2 WHERE title LIKE '%Mini%'")
        await db.execute("UPDATE products SET sales_count = 1 WHERE title LIKE '%Junior%'")
        await db.commit()
        print("Sales counts updated.")

    print("\nSEEDING COMPLETE!")
    print(f"  10 categories")
    print(f"  100 products (5 dona each)")
    print(f"  {len(expenses)} expense transactions")
    print(f"  {len(incomes)} income transactions")

if __name__ == "__main__":
    asyncio.run(main())
