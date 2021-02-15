import socket
import threading

ip = "0.0.0.0"
puerto = 9999

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.bind((ip, puerto))

servidor.listen(5)

print("[*] Escuchando en %s:%d" % (ip, puerto))

# este hilo maneja los clientes que recibimos
def manejar_cliente(socket_cliente):
    # imprimimos lo que sea que el cliente mande
    request = socket_cliente.recv(1024)

    print("[*] Recibido: %s" % request)

    # enviamos un paquetee de regreso
    socket_cliente.send(b"ACK!")
    print(socket_cliente.getpeername())
    socket_cliente.close()


while True:
    cliente, direccion = servidor.accept()

    print("[*] Se acepto conexion de: %s:%d" % (direccion[0], direccion[1]))

    # iniciamos el hilo que maneja los clientes para recibir informacion
    client_handler = threading.Thread(target=manejar_cliente, args=(cliente,))
    client_handler.start()
