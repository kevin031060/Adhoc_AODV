from socket import *

socket_server = socket(AF_INET, SOCK_DGRAM)
socket_server.bind(('127.0.0.1', 8080))

while 1:
    data, client_addr = socket_server.recvfrom(1024)
    print(data.decode('utf-8'),str(client_addr))
    socket_server.sendto(data.upper(), client_addr)

socket_server.close()