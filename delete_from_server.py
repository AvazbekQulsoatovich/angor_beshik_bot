import paramiko

HOST = '95.182.119.84'
USER = 'webdevaj'
PASS = 'yzNRMUE9ww'
REMOTE_DIR = '/home/webdevaj/angor_beshik_bot'

def clean_server():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    print("Stopping and disabling systemd service...")
    commands = [
        f"echo {PASS} | sudo -S systemctl stop beshikbot.service",
        f"echo {PASS} | sudo -S systemctl disable beshikbot.service",
        f"echo {PASS} | sudo -S rm -f /etc/systemd/system/beshikbot.service",
        f"echo {PASS} | sudo -S systemctl daemon-reload",
        f"rm -rf {REMOTE_DIR}"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
             print(f"Error executing {cmd}: {stderr.read().decode()}")
        else:
             print("Success.")

    ssh.close()
    print("Clean up complete!")

if __name__ == '__main__':
    clean_server()
