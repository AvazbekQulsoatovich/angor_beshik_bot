import paramiko
import os

HOST = '95.182.119.84'
USER = 'webdevaj'
PASS = 'yzNRMUE9ww'
LOCAL_DIR = r'c:\Users\Avaz\Desktop\beshikbot'
REMOTE_DIR = '/home/webdevaj/angor_beshik_bot'

def deploy():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    print("Creating remote directory...")
    ssh.exec_command(f'mkdir -p {REMOTE_DIR}')

    print("Transferring files via SFTP...")
    sftp = ssh.open_sftp()
    
    # Upload files, ignoring .git and __pycache__
    for root, dirs, files in os.walk(LOCAL_DIR):
        if '.git' in root or '__pycache__' in root or '.system_generated' in root:
            continue
            
        relative_path = os.path.relpath(root, LOCAL_DIR)
        remote_path = os.path.join(REMOTE_DIR, relative_path).replace('\\', '/')
        if relative_path != '.':
            try:
                sftp.mkdir(remote_path)
            except IOError:
                pass
                
        for file in files:
            if file in ['beshik.db', '.env', 'deploy.py']:
                continue
            local_file = os.path.join(root, file)
            remote_file = os.path.join(remote_path, file).replace('\\', '/')
            sftp.put(local_file, remote_file)
            
    sftp.close()
    print("Files transferred.")

    # Setup environment and dependencies
    commands = [
        f"cd {REMOTE_DIR} && python3 -m venv venv",
        f"cd {REMOTE_DIR} && ./venv/bin/pip install -r requirements.txt",
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"Error executing {cmd}: {stderr.read().decode()}")

    # Setup systemd service
    service_content = f"""[Unit]
Description=Angor Beshik Telegram Bot
After=network.target

[Service]
User={USER}
WorkingDirectory={REMOTE_DIR}
ExecStart={REMOTE_DIR}/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file to a temporary location on server
    sftp = ssh.open_sftp()
    with sftp.file(f'{REMOTE_DIR}/beshikbot.service', 'w') as f:
        f.write(service_content)
    sftp.close()

    # Move service file to systemd and enable it
    print("Setting up systemd service...")
    sudo_commands = [
        f"echo {PASS} | sudo -S cp {REMOTE_DIR}/beshikbot.service /etc/systemd/system/",
        f"echo {PASS} | sudo -S systemctl daemon-reload",
        f"echo {PASS} | sudo -S systemctl enable beshikbot.service",
        f"echo {PASS} | sudo -S systemctl restart beshikbot.service"
    ]

    for cmd in sudo_commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
             print(f"Error executing {cmd}: {stderr.read().decode()}")

    ssh.close()
    print("Deployment complete!")

if __name__ == '__main__':
    deploy()
