from socket import *
import time
import threading

BUFSIZ = 1024

class chat:

    def __init__(self, my_port, to_port):
        recv_socket = socket(AF_INET, SOCK_DGRAM)
        recv_socket.bind(('127.0.0.1', my_port))
        self.recv_socket = recv_socket
        self.to_port = to_port
        re = threading.Thread(target=recv, args=(recv_socket,))
        re.start()

    def send(self, msg):
        self.recv_socket.sendto(msg.encode('utf-8'), ('127.0.0.1', self.to_port))


def recv(recv_socket):
    print('start recvive data')
    while True:
        try:
            data, address = recv_socket.recvfrom(BUFSIZ)
            print(str(address), data.decode('utf-8'))
        except timeout as e:
            # print('no receive data')
            pass

c = chat(1234, 8000)
c.send(msg="new")