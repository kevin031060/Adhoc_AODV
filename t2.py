from socket import *

udp_client = socket(AF_INET, SOCK_DGRAM)
udp_client.bind(('127.0.0.1', 1234))
while 1:
    msg = input('>>:')
    udp_client.sendto(msg.encode('utf-8'), ('127.0.0.1', 8080))
    data, server = udp_client.recvfrom(1024)
    print(data.decode('utf-8'),str(server))