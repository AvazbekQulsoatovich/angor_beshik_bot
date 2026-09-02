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
