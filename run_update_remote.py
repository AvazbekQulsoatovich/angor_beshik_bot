import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.119.84', username='webdevaj', password='yzNRMUE9ww')

test_script = """
import asyncio
import aiosqlite

async def update_db():
    async with aiosqlite.connect('/home/webdevaj/angor_beshik_bot/beshik.db') as db:
        await db.execute("UPDATE transactions SET type = 'restock' WHERE description LIKE 'Omborga kirim%' OR description LIKE 'Tovar to''ldirildi%'")
        await db.commit()
        print('Updated Remote DB')
asyncio.run(update_db())
"""

sftp = ssh.open_sftp()
with sftp.file('/home/webdevaj/angor_beshik_bot/update_remote_db.py', 'w') as f:
    f.write(test_script)

stdin, stdout, stderr = ssh.exec_command('cd /home/webdevaj/angor_beshik_bot && ./venv/bin/python update_remote_db.py')
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))
ssh.close()
