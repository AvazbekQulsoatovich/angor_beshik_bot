
# --- Finance ops ---
async def add_transaction(t_type, amount, description, product_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions (type, amount, description, product_id) VALUES (?, ?, ?, ?)",
            (t_type, amount, description, product_id)
        )
        if t_type == 'income' and product_id is not None:
            await db.execute("UPDATE products SET sales_count = sales_count + 1 WHERE id = ?", (product_id,))
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
