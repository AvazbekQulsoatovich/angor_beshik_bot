import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.119.84', username='webdevaj', password='yzNRMUE9ww')

test_script = """
import asyncio
import aiosqlite
import sys
sys.path.insert(0, '/home/webdevaj/angor_beshik_bot')
from database import db

async def check():
    fin = await db.get_finances()
    print('Finances:', fin)
    inv = await db.get_inventory_analytics()
    print('Inventory:', inv)

asyncio.run(check())
"""

sftp = ssh.open_sftp()
with sftp.file('/home/webdevaj/angor_beshik_bot/test_fin.py', 'w') as f:
    f.write(test_script)

stdin, stdout, stderr = ssh.exec_command('cd /home/webdevaj/angor_beshik_bot && ./venv/bin/python test_fin.py')
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))
ssh.close()
