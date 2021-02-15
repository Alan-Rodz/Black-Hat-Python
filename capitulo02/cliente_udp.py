import socket

host = "127.0.0.1"
puerto_objetivo = 80

# creamos objeto de tipo socket
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# enviamos informacion
cliente.sendto(b"AAABBBCCC", (host, puerto_objetivo))

# recibimos informacion
informacion, direccion = cliente.recvfrom(4096)

# cerramos la conexion
cliente.close()

print(informacion)
