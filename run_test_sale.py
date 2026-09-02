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
    # 1. Get a product
    prods = await db.get_all_active_products_for_sale()
    p = prods[0]
    print(f"Selling {p['title']} for {p['price']}, cost is {p['cost_price']}")
    
    # Clean price string
    import re
    price_digits = re.sub(r'[^\\d]', '', str(p['price']))
    sale_price = int(price_digits)
    
    # Insert sale
    await db.add_transaction('income', sale_price, f"Sotuv TEST: {p['title']}", p['id'])
    
    # Fetch finances
    fin = await db.get_finances()
    print("Daily Income:", fin['daily_income'])
    print("Daily Sale Profit:", fin['daily_sale_profit'])

asyncio.run(run())
"""

sftp = ssh.open_sftp()
with sftp.file('/home/webdevaj/angor_beshik_bot/test_sale.py', 'w') as f:
    f.write(test_script)

stdin, stdout, stderr = ssh.exec_command('cd /home/webdevaj/angor_beshik_bot && ./venv/bin/python test_sale.py')
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))
ssh.close()
