import socket

host = "0.0.0.0"
puerto_objetivo = 9999

# creamos un objeto de tipo socket
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# conectamos con el cliente
cliente.connect((host, puerto_objetivo))

# enviamos informacion
cliente.send("ABCD")

# recibimos informacion
respuesta = cliente.recv(4096)

# cerramos la conexion
cliente.close()

print(respuesta)
