import asyncio
from database import db

async def test_db():
    print("Testing DB functions...")
    
    # Categories
    await db.add_category("Test Cat", "🛠")
    cats = await db.get_all_categories()
    test_cat_id = cats[-1]['id']
    await db.update_category(test_cat_id, "Test Cat Edited", "✅")
    await db.soft_delete_category(test_cat_id)
    
    # Products
    await db.add_product(test_cat_id, "Test Prod", "Desc", "100", ["photo_id"], True)
    prods = await db.get_products_by_category(test_cat_id, active_only=False)
    test_prod_id = prods[-1]['id']
    await db.update_product_all(test_prod_id, "Test Prod Edited", "Desc", "200", False, None)
    await db.update_product_all(test_prod_id, "Test Prod Edited", "Desc", "200", False, ["new_photo_id"])
    await db.soft_delete_product(test_prod_id)
    
    # Admins
    await db.add_admin_db(999999)
    await db.remove_admin_db(999999)
    
    print("All DB functions passed successfully without SQL errors.")

if __name__ == "__main__":
    asyncio.run(test_db())
