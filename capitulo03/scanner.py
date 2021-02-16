import socket
import os
import struct
import threading
from ipaddress import ip_address, ip_network
from ctypes import *

# host en el que escuchamos 
host = "host"

# subnet del objetivo 
# i.e. si el host es "aaa.bbb.cc.dd" el subnet sera "aaa.bbb.cc.0/24"
tgt_subnet = ""

# lo que checamos que contangan las respuestas ICMP
tgt_message = "PYTHONRULES!"


def udp_sender(sub_net, magic_message):
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in ip_network(sub_net).hosts():
        sender.sendto(magic_message.encode('utf-8'), (str(ip), 65212))


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

        # mapeamos constantes de protocolos a sus nombres
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # direcciones IP legibles
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # protocolos legibles
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        self.socket_buffer = socket_buffer


# creamos un raw socket y lo unimos a la interfaz publica
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# queremos los IP headers incluidos en la captura
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# si estamos en Windows enviamos IOCTL para entrar en modo promiscuo
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# empezamos a enviar paquetes
t = threading.Thread(target=udp_sender, args=(tgt_subnet, tgt_message))
t.start()

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

        # si es ICMP, lo queremos
        if ip_header.protocol == "ICMP":

            # calculamos donde comienza el paquete ICMP
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # creamos nuestra estructura ICMP
            icmp_header = ICMP(buf)

            print("ICMP -> Type: %d Code: %d" % (
                icmp_header.type,
                icmp_header.code)
                  )

            # checamos que sea de TYPE 3 y CODE 3
            # esto significa que "a host is up but no port available to talk to"
            if icmp_header.code == 3 and icmp_header.type == 3:

                # checamos para asegurarnos de recibir la respuesta que cae en nuestra subnet
                if ip_address(ip_header.src_address) in ip_network(tgt_subnet):

                    # buscamos nuestro mensaje
                    if raw_buffer[len(raw_buffer)
                       - len(tgt_message):] == tgt_message:
                        print("Host Up: %s" % ip_header.src_address)

# manejamos CTRL-C
except KeyboardInterrupt:
    # si estamos en windows apagamos el modo promiscuo
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
