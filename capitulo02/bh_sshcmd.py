import paramiko

# este programa se conecta a un servidor ssh y ejecuta 1 comando

def comando_ssh(ip, user, passwd, command):
    client = paramiko.SSHClient()

    # el cliente tambien puede usar archivos key
    # esto se hace asi: client.load_host_keys('/home/user/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    return


comando_ssh('ip', 'usuario', 'contraseña', 'comandoSSH')
