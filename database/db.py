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
                cost_price INTEGER DEFAULT 0,
                sales_count INTEGER DEFAULT 0,
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                product_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

async def add_product(category_id, title, description, price, cost_price, photo_file_ids, in_stock):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO products (category_id, title, description, price, cost_price, photo_file_ids, in_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category_id, title, description, price, cost_price, json.dumps(photo_file_ids), in_stock))
        await db.commit()

async def update_product_all(product_id, title, description, price, cost_price, in_stock, photos=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if photos is not None:
            photos_json = json.dumps(photos)
            await db.execute(
                "UPDATE products SET title = ?, description = ?, price = ?, cost_price = ?, in_stock = ?, photo_file_ids = ? WHERE id = ?",
                (title, description, price, cost_price, in_stock, photos_json, product_id)
            )
        else:
            await db.execute(
                "UPDATE products SET title = ?, description = ?, price = ?, cost_price = ?, in_stock = ? WHERE id = ?",
                (title, description, price, cost_price, in_stock, product_id)
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

# --- Finance ops ---
async def add_transaction(t_type, amount, description, product_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions (type, amount, description, product_id) VALUES (?, ?, ?, ?)",
            (t_type, amount, description, product_id)
        )
        if t_type == 'income' and product_id is not None:
            await db.execute("UPDATE products SET sales_count = sales_count + 1, in_stock = in_stock - 1 WHERE id = ?", (product_id,))
        await db.commit()

async def get_finances():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute("SELECT SUM(amount) as total FROM transactions WHERE type = 'income'") as cur:
            res = await cur.fetchone()
            total_income = res['total'] or 0
            
        async with db.execute("SELECT SUM(amount) as total FROM transactions WHERE type = 'expense'") as cur:
            res = await cur.fetchone()
            total_expense = res['total'] or 0
            
        async with db.execute("SELECT SUM(amount) as total FROM transactions WHERE type = 'income' AND date(created_at, 'localtime') = date('now', 'localtime')") as cur:
            res = await cur.fetchone()
            daily_income = res['total'] or 0

        async with db.execute("SELECT SUM(cost_price) as total FROM products WHERE in_stock = 1 AND is_active = 1") as cur:
            res = await cur.fetchone()
            inventory_value = res['total'] or 0
            
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
            'daily_income': daily_income,
            'inventory_value': inventory_value
        }

async def get_top_products():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT title, sales_count FROM products WHERE is_active = 1 ORDER BY sales_count DESC LIMIT 5") as cur:
            return await cur.fetchall()

async def get_worst_products():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT title, sales_count FROM products WHERE is_active = 1 ORDER BY sales_count ASC LIMIT 5") as cur:
            return await cur.fetchall()
async def get_all_active_products_for_sale():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, title, price, cost_price, in_stock, sales_count FROM products WHERE is_active = 1 ORDER BY in_stock DESC, title ASC") as cur:
            return await cur.fetchall()

async def get_new_inquiries():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT i.*, p.title as product_title FROM inquiries i LEFT JOIN products p ON i.product_id = p.id WHERE i.status = 'new' ORDER BY i.created_at DESC") as cur:
            return await cur.fetchall()

async def get_all_inquiries(limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT i.*, p.title as product_title FROM inquiries i LEFT JOIN products p ON i.product_id = p.id ORDER BY i.created_at DESC LIMIT ?", (limit,)) as cur:
            return await cur.fetchall()

async def find_product_by_title(title):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products WHERE LOWER(title) = LOWER(?) AND is_active = 1", (title,)) as cur:
            return await cur.fetchone()

async def add_stock_to_product(product_id, qty, cost_price):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET in_stock = in_stock + ?, cost_price = ? WHERE id = ?", (qty, cost_price, product_id))
        await db.commit()

async def get_inventory_analytics():
    import re
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Total stock count
        async with db.execute("SELECT COUNT(*) as cnt, SUM(in_stock) as total_qty FROM products WHERE is_active = 1 AND in_stock > 0") as cur:
            row = await cur.fetchone()
            total_products = row['cnt'] or 0
            total_qty = row['total_qty'] or 0

        # Total cost invested in stock
        async with db.execute("SELECT SUM(cost_price * in_stock) as total FROM products WHERE is_active = 1 AND in_stock > 0") as cur:
            row = await cur.fetchone()
            total_cost_invested = row['total'] or 0

        # Total potential revenue (all products at sale price)
        async with db.execute("SELECT price, in_stock FROM products WHERE is_active = 1 AND in_stock > 0") as cur:
            rows = await cur.fetchall()
            total_potential_revenue = 0
            for r in rows:
                digits = re.sub(r'[^\d]', '', str(r['price']))
                if digits:
                    total_potential_revenue += int(digits) * r['in_stock']

        potential_profit = total_potential_revenue - total_cost_invested

        return {
            'total_products': total_products,
            'total_qty': total_qty,
            'total_cost_invested': total_cost_invested,
            'total_potential_revenue': total_potential_revenue,
            'potential_profit': potential_profit
        }
