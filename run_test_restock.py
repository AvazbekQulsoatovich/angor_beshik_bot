import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.119.84', username='webdevaj', password='yzNRMUE9ww')

test_script = """
import asyncio
import sys
sys.path.insert(0, '/home/webdevaj/angor_beshik_bot')
from database import db

async def run():
    inv_before = await db.get_inventory_analytics()
    fin_before = await db.get_finances()
    
    prods = await db.get_all_active_products_for_sale()
    p_before = prods[0]
    pid = p_before['id']
    
    print(f"--- BEFORE RESTOCK ---")
    print(f"Product: {p_before['title']} | Stock: {p_before['in_stock']} | Cost: {p_before['cost_price']} | Price: {p_before['price']}")
    print(f"Total Inv Qty: {inv_before['total_qty']} | Total Inv Cost: {inv_before['total_cost_invested']}")
    print(f"Daily Expenses: {fin_before['daily_expense']}")
    
    qty_added = 10
    new_cost_price = 600000
    new_sale_price = "900,000 so'm"
    
    await db.add_stock_to_product(pid, qty_added, new_cost_price, new_sale_price)
    total_expense = qty_added * new_cost_price
    await db.add_transaction('expense', total_expense, f"Omborga kirim TEST: {p_before['title']} x{qty_added} dona")
    
    inv_after = await db.get_inventory_analytics()
    fin_after = await db.get_finances()
    p_after = await db.get_product_by_id(pid)
    
    print(f"\\n--- AFTER RESTOCK ---")
    print(f"Product Stock: {p_after['in_stock']} (Expected: {p_before['in_stock'] + qty_added})")
    print(f"Product Cost: {p_after['cost_price']} (Expected: {new_cost_price})")
    print(f"Product Price: {p_after['price']} (Expected: {new_sale_price})")
    print(f"Total Inv Qty: {inv_after['total_qty']} (Expected: {inv_before['total_qty'] + qty_added})")
    print(f"Total Inv Cost: {inv_after['total_cost_invested']}")
    print(f"Daily Expenses: {fin_after['daily_expense']} (Expected: {fin_before['daily_expense'] + total_expense})")

asyncio.run(run())
"""

sftp = ssh.open_sftp()
with sftp.file('/home/webdevaj/angor_beshik_bot/test_restock.py', 'w') as f:
    f.write(test_script)

stdin, stdout, stderr = ssh.exec_command('cd /home/webdevaj/angor_beshik_bot && ./venv/bin/python test_restock.py')
print("STDOUT:\\n", stdout.read().decode('utf-8'))
print("STDERR:\\n", stderr.read().decode('utf-8'))
ssh.close()
