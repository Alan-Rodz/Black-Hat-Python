import socket
import os
import struct
from ctypes import *

# host en el que escucharemos 
host = "host"

# estructura de un ip header 
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer

        # mapeamos constantes de protocolos a sus nombres correspondientes
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # direcciones IP legibles por humanos
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # protocolo legible por humanos
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protocol_num)


# creamos un raw socket y lo unimos a la interfaz publica
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# queremos los IP headers incluidos en la captura
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# si estamos en Windows, enviamos ioctl para configurar modo promiscuo
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        # leemos un paquete
        raw_buffer = sniffer.recvfrom(65535)[0]

        # creamos un IP header a partir de los primeros 20 bytes del buffer
        ip_header = IP(raw_buffer[:20])

        print("Protocol: %s %s -> %s" % (
            ip_header.protocol,
            ip_header.src_address,
            ip_header.dst_address)
              )

except KeyboardInterrupt:
    # si estamos en Windows, apagamos el modo promiscuo
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
