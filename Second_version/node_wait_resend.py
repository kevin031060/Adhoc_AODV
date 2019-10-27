from socket import *
import time
import threading
import json
import pickle
BUFSIZ = 1024

class node:

    def __init__(self, idx):

        # mtable=[
        #     [1, 1, 1, 0],
        #     [1, 1, 1, 0],
        #     [1, 1, 1, 1],
        #     [0, 0, 1, 1],
        # ]
        pkl_file = open('data.pkl', 'rb')
        mtable = pickle.load(pkl_file)
        pkl_file.close()
        # 设置端口
        self.port_basis = 9000
        self.to_port_list = list()
        self.my_port = self.port_basis+idx
        node_num = len(mtable)
        # 根据端口数目设置所有端口
        self.allport = []
        for i in range(node_num):
            port_temp = i + 1 + self.port_basis
            self.allport.append(port_temp)

        for i in range(0,node_num):
            if mtable[idx-1][i]:
                port_temp = i+1+self.port_basis
                if port_temp!=self.my_port:
                    self.to_port_list.append(port_temp)

        # 存储已经收到的报文，src——address
        self.received_src = []
        # 记录id，第几次路由
        self.idx=0

        recv_socket = socket(AF_INET, SOCK_DGRAM)
        recv_socket.bind(('127.0.0.1', self.my_port))
        self.recv_socket = recv_socket

        re = threading.Thread(target=self.recv, args=())
        re.start()

    def send(self, msg, to_port):
        self.recv_socket.sendto(msg.encode('utf-8'), ('127.0.0.1', to_port))
        print("---Send:","----Port:",str(to_port), msg)

    def wait_send(self):
        try:
            while True:
                msg = input('Please input the destination if you want to send something>>:')
                if msg.isdigit():
                    des_address = int(msg)
                    if des_address in self.allport:
                        des_address = int(msg)
                        src_address = self.my_port
                        route_list = [self.my_port]
                        sender_port = self.my_port
                        print("start route")
                        c.broadcast(des_address, src_address, route_list, sender_port, 'REQ', self.idx)
                        self.idx = self.idx + 1
        except KeyboardInterrupt:
            self.recv_socket.close()





    def broadcast(self, des_address, src_address, route_list, sender_port, flag, idx):
        json_str = write_json(des_address, src_address, route_list, flag, idx)
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
                des_address, src_address, route_list, flag, idx = parse_json(data.decode('utf-8'))
                # 判断是否到达目的节点
                # 到达目的节点，那么传回REPLY报文（按路由传回），令flag为REP
                if (self.my_port == des_address) and (flag=='REQ'):
                    print("Destination!!!!!!!!! Route back the REPLY")
                    route_list.append(self.my_port)
                    # 令flag为REP,发送REPLY报文
                    json_str = write_json(des_address, src_address, route_list, 'REP', idx)
                    # 直接往回发
                    self.send(json_str, sender_port)

                # 重复请求包的检测(丢弃) 1：如果中间节点收到的请求包中路由记录已经包含本节点 2：如果中间节点收到了来自同一个源(A)请求id相同的请求包;
                elif (flag=='REQ') and (self.my_port not in route_list) and ((src_address,idx) not in self.received_src):

                    # 将本节点加入路由列表，并广播，广播时不往回广播（sender_port排除掉）
                    route_list.append(self.my_port)
                    self.received_src.append( (src_address, idx) )
                    self.broadcast(des_address, src_address, route_list, sender_port, 'REQ', idx)

                # 中间节点收到REPLY报文则按路由转发，到达源节点则cache路由列表
                if (flag=='REP') and (self.my_port!=src_address):
                    # 找到本节点在路由表中的位置，该位置的前序位置即为前一个节点，向该节点传REP报文
                    route_next = route_list[route_list.index(self.my_port)-1]
                    json_str = write_json(des_address, src_address, route_list, 'REP', idx)
                    self.send(json_str, route_next)
                    print("Route back the REPLY to:",str(route_next))

                if (flag=='REP') and (self.my_port==src_address):
                    print("Route List:",route_list)

            except timeout as e:
                # print('no receive data')
                pass


def write_json(des_address, src_address, route_list, flag, idx):
    python2json = {}
    # route_list = [1, 2, 3]
    python2json["route_list"] = route_list
    python2json["src_address"] = src_address
    python2json["des_address"] = des_address
    python2json["flag"] = flag
    python2json["idx"] = idx
    json_str = json.dumps(python2json)
    return json_str

def parse_json(json_str):
    json2python = json.loads(json_str)
    return json2python['des_address'], json2python['src_address'], json2python['route_list'], json2python['flag'], json2python['idx']

c = node(7)
c.wait_send()