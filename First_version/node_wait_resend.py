from socket import *
import time
import threading
import json

BUFSIZ = 1024

class node:

    def __init__(self, idx):
        if idx==1:
            self.my_port, self.to_port_list = 8001, [8002,8003]
        elif idx==2:
            self.my_port, self.to_port_list = 8002, [8001, 8003]
        elif idx==3:
            self.my_port, self.to_port_list = 8003, [8001, 8002, 8004]
        elif idx==4:
            self.my_port, self.to_port_list = 8004, [8003]

        # 存储已经收到的报文，src——address
        self.received_src = []

        recv_socket = socket(AF_INET, SOCK_DGRAM)
        recv_socket.bind(('127.0.0.1', self.my_port))
        self.recv_socket = recv_socket

        re = threading.Thread(target=self.recv, args=())
        re.start()

    def send(self, msg, to_port):
        self.recv_socket.sendto(msg.encode('utf-8'), ('127.0.0.1', to_port))
        print("---Send:","----Port:",str(to_port), msg)

    def wait_send(self):
        while True:
            msg = input('>>:')
            self.send(msg)

    def broadcast(self, des_address, src_address, route_list, sender_port, flag):
        json_str = write_json(des_address, src_address, route_list, flag)
        for item in self.to_port_list:
            # 广播时不往回广播（sender_port排除掉）
            if item != sender_port:
                self.send(json_str, item)

    def recv(self):
        print('Port',self.my_port,':start recvive data')
        while True:
            try:
                data, address = self.recv_socket.recvfrom(BUFSIZ)
                # 提取出发送方的端口，广播时不往回广播
                sender_port = int(str(address)[-5:-1])
                print("---Receive:", str(address), data.decode('utf-8'))
                # 提取出报文内容
                des_address, src_address, route_list, flag = parse_json(data.decode('utf-8'))
                # 判断是否到达目的节点
                # 到达目的节点，那么传回REPLY报文（按路由传回），令flag为REP
                if (self.my_port == des_address) and (flag=='REQ'):
                    print("Destination!!!!!!!!! Route back the REPLY")
                    route_list.append(self.my_port)
                    # 令flag为REP,发送REPLY报文
                    json_str = write_json(des_address, src_address, route_list, 'REP')
                    # 直接往回发
                    self.send(json_str, sender_port)

                # 重复请求包的检测(丢弃) 1：如果中间节点收到的请求包中路由记录已经包含本节点 2：如果中间节点收到了来自同一个源(A)请求id相同的请求包;
                elif (flag=='REQ') and (self.my_port not in route_list) and (src_address not in self.received_src):

                    # 将本节点加入路由列表，并广播，广播时不往回广播（sender_port排除掉）
                    route_list.append(self.my_port)
                    self.received_src.append(src_address)
                    self.broadcast(des_address, src_address, route_list, sender_port, 'REQ')

                # 中间节点收到REPLY报文则按路由转发，到达源节点则cache路由列表
                if (flag=='REP') and (self.my_port!=src_address):
                    # 找到本节点在路由表中的位置，该位置的前序位置即为前一个节点，向该节点传REP报文
                    route_next = route_list[route_list.index(self.my_port)-1]
                    json_str = write_json(des_address, src_address, route_list, 'REP')
                    self.send(json_str, route_next)
                    print("Route back the REPLY to:",str(route_next))

                if (flag=='REP') and (self.my_port==src_address):
                    print("Route List:",route_list)

            except timeout as e:
                # print('no receive data')
                pass


def write_json(des_address, src_address, route_list, flag):
    python2json = {}
    # route_list = [1, 2, 3]
    python2json["route_list"] = route_list
    python2json["src_address"] = src_address
    python2json["des_address"] = des_address
    python2json["flag"] = flag
    json_str = json.dumps(python2json)
    return json_str

def parse_json(json_str):
    json2python = json.loads(json_str)
    return json2python['des_address'], json2python['src_address'], json2python['route_list'], json2python['flag']

c = node(1)