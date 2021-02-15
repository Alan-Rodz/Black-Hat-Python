import sys
import socket
import threading

# funcion para hacer hexdump tomada de
# http://code.activestate.com/recipes/142812-hex-dumper/

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join([b"%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(
            b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


def receive_from(connection):
    buffer = b''

    # establecemos un time-out de 2 segundos. Dependiendo del objetivo esto puede ser cambiado
    connection.settimeout(2)

    try:

        # continuamos leyendo hacia el buffer hasta que no haya mas informacion u ocurra un time-out
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data

    except TimeoutError:
        pass

    return buffer


# request_handler y response_handler nos permiten modificar los paquetes como queramos, aqui no se modifican

# modificamos cualquier request cuyo destino sea el host remoto
def request_handler(buffer):
    # hacemos las modificaciones del paquete
    return buffer


# modificamos las respuestas cuyo destino sean el localhost
def response_handler(buffer):
    # hacemos las modificaciones del paquete
    return buffer

# cuando recibimos una solicitud de conexion, esta funcion la recibe 
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # conectamos al host remoto
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # recibimos data del lado remoto de ser necesario
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # la enviamos al response_handler
        remote_buffer = response_handler(remote_buffer)

        # si tenemos informacion para enviar a nuestro cliente local, la enviamos
        if len(remote_buffer):
            print("[<==] Enviando %d bytes a localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    # leemos desde local, enviamos a remoto, enviamos a local
    # repetimos
    while True:
        # leemos desde localhost
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] Se recibieron %d bytes de localhost." % len(local_buffer))
            hexdump(local_buffer)

            # lo enviamos a nuestro request_handler
            local_buffer = request_handler(local_buffer)

            # enviamos la informacion al host remoto
            remote_socket.send(local_buffer)
            print("[==>] Enviado a host remoto.")

        # recibimos la respuesta
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Se recibieron %d bytes del host remoto." % len(remote_buffer))
            hexdump(remote_buffer)

            # lo enviamos al response handler
            remote_buffer = response_handler(remote_buffer)

            # enviamos la respuesta al socket local
            client_socket.send(remote_buffer)

            print("[<==] Enviado a localhost.")

        # si no hay mas informacion en ambos lados, cerramos la conexion
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No hay mas informacion. Cerrando conexiones.")
            break


def server_loop(local_host, local_port, remote_host, remote_port,
                receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except socket.error as exc:
        print("[!!] No se puede escuchar en %s:%d" % (local_host,
                                                  local_port))
        print("[!!] Cheque otros sockets que esten escuchando o permisos correctos.")
        print(f"[!!] Excepcion: {exc}")
        sys.exit(0)

    print("[*] Escuchando en %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # imprimimos la informacion de la conexion local
        print("[==>] Se recibio conexion de %s:%d" % (
            addr[0], addr[1]))

        # emepezamos un thread para hablar con el host remoto
        proxy_thread = threading.Thread(target=proxy_handler, args=(
            client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Uso: ./proxy.py [localhost] [localport] [remotehost] "
              "[remoteport] [receive_first]")
        print("Ejemplo: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # configuramos parametros de escucha locales
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # configuramos el objetivo remoto
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # esto le dice al proxy que se conecte y reciba informacion antes de enviarla al host remoto
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # inicializamos el socket que usamos para escuchar
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


main()
