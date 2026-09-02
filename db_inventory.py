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
