# 客户端
from socket import *
import threading
import sys
ip="127.0.0.1"
my_port=input("set my port:\n")
to_port=input("set the port you want to send:\n")

my_address = (ip, int(my_port))

# visit = sys.argv.pop() if len(sys.argv) == 2 else '192.168.1.102'
# PORT = 12512
BUFSIZ = 1024
ADDR = (ip, int(to_port))
# SerAddr = ('192.168.1.103', PORT)



recv_socket = socket(AF_INET, SOCK_DGRAM)
recv_socket.bind(my_address)

def recv():
    print('start recvive data')
    while True:
        try:
            # print('come on')
            data, address = recv_socket.recvfrom(BUFSIZ)
            print(str(address),data.decode('ascii'))
            # recv_socket.sendto("I have received your msg".encode('utf-8'),address)
        except timeout as e:
            # print('no receive data')
            pass


# CliSock.sendto(visit.encode('ascii'), SerAddr)

re = threading.Thread(target=recv, args=())
re.start()


while True:
    data = input('>')
    recv_socket.sendto(data.encode('ascii'), ADDR)


'''
import socket
import json

address = ('127.0.0.1', 31500)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
json_string = json.dumps(mylist)
s.sendto(json_string, address)
s.shutdown(socket.SHUT_RDWR)
s.close()


# !/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import json

address = ('127.0.0.1', 31500)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)
json_string, addr = s.recvfrom(2048)
mylist = json.loads(json_string)

s.shutdown(socket.SHUT_RDWR)
'''