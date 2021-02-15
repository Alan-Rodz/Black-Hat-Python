import sys
import socket
import getopt
import threading
import subprocess

# este programa es un reemplazo de netcat escrito en python
# si usamos -c tenemos que usar CTRL-D para que se detecte el enter

# variables globales
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

# ejecuta un comando y regresa el output del mismo
def run_command(cmd):

    # recortamos la newline
    cmd = cmd.rstrip()

    # ejecutamos el comando y recibimos el output
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                         shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output

    # regresamos el output al cliente
    return output


# maneja las conexiones que recibimos de los clientes
def client_handler(client_socket):
    global upload
    global execute
    global command

    # checamos el upload
    if len(upload_destination):

        # leemos todos los bytes y los escribimos en su destino
        file_buffer = ""

        # continuamos leyendo informacion hasta que ya no haya mas disponible
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # ahora podemos tomar estos bytes e intentamos escribirlos
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer.encode('utf-8'))
            file_descriptor.close()

            # le hacemos saber al cliente que escribimos el archivo exitosamente
            client_socket.send(
                "Se guardo el archivo de manera exitosa en %s\r\n" % upload_destination)
        except OSError:
            client_socket.send(
                "No se pudo guardar el archivo a %s\r\n" % upload_destination)

    # checamos command execution
    if len(execute):
        # ejecutamos el comando
        output = run_command(execute)

        client_socket.send(output)

    # entramos en otro loop si se solicito una command shell
    if command:

        while True:
            # mostramos un prompt simple
            client_socket.send("<BHP:#> ".encode('utf-8'))

            # recibimos hasta que recibamos un enter
            cmd_buffer = b''
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # tenemos un comando valido, asi que lo ejecutamos y enviamos los resultados
            response = run_command(cmd_buffer)

            # enviamos la respuesta de regreso
            client_socket.send(response)


# esta funcion es para las conexiones que recibimos
def server_loop():
    global target
    global port

    # si no se define ningun target, escuchamos en todas las interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # iniciamos un thread para recibir a nuestro cliente
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()

# si no estamos oyendo, entonces nosotros somos el cliente
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # nos conectamos al host objetivo
        client.connect((target, port))

        # si detectamos input de stdin, lo enviamos
        # si no, esperaremos a que el usuario envie alguno
        if len(buffer):
            client.send(buffer.encode('utf-8'))

        while True:
            # ahora esperamos a recibir informacion de regreso
            recv_len = 1
            response = b''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode('utf-8'), end=' ')

            # esperamos por mas inputs
            buffer = input("")
            buffer += "\n"

            # los enviamos
            client.send(buffer.encode('utf-8'))

    except socket.error as exc:
        # detectamos errores genericos
        print("[*] Excepcion! Saliendo.")
        print(f"[*] Excepcion socket.error: {exc}")

        # cerramos la conexion
        client.close()

# funcion que define como se usa el programa
def usage():
    print("Reemplazo de Netcat")
    print()
    print("Uso: bhpnet.py -t target_host -p port")
    print(
        "-l --listen                - listen on [host]:[port] for incoming "
        "connections")
    print(
        "-e --execute=file_to_run   - execute the given file upon receiving "
        "a connection")
    print("-c --command               - initialize a command shell")
    print(
        "-u --upload=destination    - upon receiving connection upload a file "
        "and write to [destination]")
    print()
    print()
    print("Ejemplos: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # leemos las command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target",
                                    "port", "command", "upload"])
        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
            elif o in ("-l", "--listen"):
                listen = True
            elif o in ("-e", "--execute"):
                execute = a
            elif o in ("-c", "--commandshell"):
                command = True
            elif o in ("-u", "--upload"):
                upload_destination = a
            elif o in ("-t", "--target"):
                target = a
            elif o in ("-p", "--port"):
                port = int(a)
            else:
                assert False, "Unhandled Option"

    except getopt.GetoptError as err:
        print(str(err))
        usage()

    # estamos simplemente oyendo, o enviaremos informacion desde STDIN?
    if not listen and len(target) and port > 0:

        # leemos el buffer (string) desde la commandline
        # esto hace que se bloquee, asi que debemos enviar CTRL-D si no se envia el input a stdin
        buffer = sys.stdin.read()

        # enviamos la informacion
        client_sender(buffer)

    # estaremos oyendo y potencialmente enviando cosas, ejecutando comandos y regresando shells
    # dependiendo de las opciones arriba
    if listen:
        server_loop()


main()
