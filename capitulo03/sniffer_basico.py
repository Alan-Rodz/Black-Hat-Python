import socket
import os

# host en el que escucharemos 
host = "host"

# creamos un raw socket y lo unimos a la interfaz publica
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol) 

sniffer.bind((host, 0))

# queremos incluir los IP headers en la captura
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# si estamos en windows, enviamos un IOCTL para entrar en modo promiscuo
if os.name == "nt": 
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# leemos un paquete
print(sniffer.recvfrom(65535))

# si estamos en Windows, apagamos el modo promiscuo
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
