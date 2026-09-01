import aiosqlite
import json

DB_PATH = "beshik.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT,
                is_active BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                price TEXT,
                photo_file_ids TEXT,
                in_stock BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                user_id INTEGER,
                user_name TEXT,
                message_text TEXT,
                status TEXT DEFAULT 'new',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE
            )
        """)
        await db.commit()

# --- Admin ops ---
async def get_all_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM admins") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def add_admin_db(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO admins (telegram_id) VALUES (?)", (telegram_id,))
            await db.commit()
            return True
        except:
            return False

async def remove_admin_db(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
        await db.commit()

# --- Category operations ---
async def get_all_categories(active_only=True):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM categories"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY sort_order ASC, id ASC"
        async with db.execute(query) as cursor:
            return await cursor.fetchall()

async def get_category(cat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)) as cursor:
            return await cursor.fetchone()

async def add_category(name, emoji):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

async def update_category(cat_id, name, emoji):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET name = ?, emoji = ? WHERE id = ?", (name, emoji, cat_id))
        await db.commit()

async def soft_delete_category(category_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (category_id,))
        await db.commit()

# --- Product operations ---
async def get_products_by_category(category_id, active_only=True, page=1, limit=5):
    offset = (page - 1) * limit
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM products WHERE category_id = ?"
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        async with db.execute(query, (category_id, limit, offset)) as cursor:
            return await cursor.fetchall()

async def get_products_count_by_category(category_id, active_only=True):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT COUNT(*) FROM products WHERE category_id = ?"
        if active_only:
            query += " AND is_active = 1"
        async with db.execute(query, (category_id,)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

async def get_product_by_id(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products WHERE id = ?", (product_id,)) as cursor:
            return await cursor.fetchone()

async def add_product(category_id, title, description, price, photo_file_ids_list, in_stock):
    photos_json = json.dumps(photo_file_ids_list)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO products (category_id, title, description, price, photo_file_ids, in_stock) VALUES (?, ?, ?, ?, ?, ?)",
            (category_id, title, description, price, photos_json, in_stock)
        )
        await db.commit()

async def update_product_all(product_id, title, description, price, in_stock, photos=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if photos is not None:
            photos_json = json.dumps(photos)
            await db.execute(
                "UPDATE products SET title = ?, description = ?, price = ?, in_stock = ?, photo_file_ids = ? WHERE id = ?",
                (title, description, price, in_stock, photos_json, product_id)
            )
        else:
            await db.execute(
                "UPDATE products SET title = ?, description = ?, price = ?, in_stock = ? WHERE id = ?",
                (title, description, price, in_stock, product_id)
            )
        await db.commit()

async def soft_delete_product(product_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
        await db.commit()

# --- Inquiry operations ---
async def add_inquiry(product_id, user_id, user_name, message_text):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO inquiries (product_id, user_id, user_name, message_text) VALUES (?, ?, ?, ?)",
            (product_id, user_id, user_name, message_text)
        )
        await db.commit()
        return cursor.lastrowid

async def get_inquiry(inquiry_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)) as cursor:
            return await cursor.fetchone()

async def update_inquiry_status(inquiry_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE inquiries SET status = ? WHERE id = ?", (status, inquiry_id))
        await db.commit()

async def get_new_inquiries():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM inquiries WHERE status = 'new' ORDER BY id ASC") as cursor:
            return await cursor.fetchall()
