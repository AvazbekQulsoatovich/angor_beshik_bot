async def get_all_active_products_for_sale():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, title, price, cost_price, in_stock, sales_count FROM products WHERE is_active = 1 ORDER BY in_stock DESC, title ASC") as cur:
            return await cur.fetchall()
