# 服务端
from socket import *
from time import strftime
import threading
import sys


def server(sock, access, addr, size=16):
    while True:
        print('go go go!!!')
        data, addr = sock.recvfrom(BUFSIZ)
        time = strftime('%H:%M:%S')
        data = repr(addr[1]) + '  ' + time + '\n    ' + data.decode('ascii')
        print(data)
        sock.sendto(data, access)


HOST = sys.argv.pop() if len(sys.argv) == 2 else '127.0.0.1'
PORT = 12512
BUFSIZ = 16
ADDR = (HOST, PORT)
threads = []
usrs = []

SerSock = socket(AF_INET, SOCK_DGRAM)
SerSock.bind(ADDR)
SerSock.settimeout(1)
while True:
    try:
        print('waiting connect...')
        access, addr = SerSock.recvfrom(BUFSIZ)
        print(("received from %s 's request") % repr(addr))
        sock=socket(AF_INET, SOCK_DGRAM)
        sock.bind((HOST, addr[1]))
        sock.settimeout(1)
        usrs.append((sock, access, addr))
        print(('successfully bound with %s') % repr(addr))
        t = threading.Thread(target=server, args=(sock, access, addr))
        threads.append(t)
        t.start()
        print(repr(addr) + 'have start server')
    except timeout as e:
        print('None')