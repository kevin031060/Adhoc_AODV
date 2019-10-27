from socket import *
import time
import threading
import json
import pickle
import math
import Third_version.change_node as change_node

BUFSIZ = 1024

class node:

    def __init__(self, idx):

        self.port_basis = 9000
        self.my_port = self.port_basis+idx
        # 读取拓扑，获取每个点的坐标
        self.x_list, self.y_list, self.node_num  = self.get_topology()


        # 存储已经收到的报文，src——address
        self.received_src = []
        # 记录id，第几次路由
        self.idx=0

        recv_socket = socket(AF_INET, SOCK_DGRAM)
        recv_socket.bind(('127.0.0.1', self.my_port))
        self.recv_socket = recv_socket

        # 开启一个线程，监听消息
        re = threading.Thread(target=self.recv, args=())
        re.start()

    # 向某个节点发送报文信息
    def send(self, msg, to_port):
        self.recv_socket.sendto(msg.encode('utf-8'), ('127.0.0.1', to_port))
        print("---Send:","----Port:",str(to_port), msg)

    # 等待发起路由
    def wait_send(self):
        try:
            while True:
                msg = input('Please input the destination if you want to send something>>:')
                # 如果本节点要向destination发起路由，msg为目标的address
                if msg.isdigit():
                    des_address = int(msg)
                    if des_address in self.allport:
                        des_address = int(msg)
                        src_address = self.my_port
                        route_list = [self.my_port]
                        sender_port = self.my_port
                        print("start route")
                        # 广播该报文
                        c.broadcast(des_address, src_address, route_list, sender_port, 'REQ', self.idx)
                        self.idx = self.idx + 1
                # 如果拓扑改变
                if msg[0:1]=='c':
                    node_num = msg[1:]
                    change_node.change_node(int(node_num))
                    self.x_list, self.y_list, self.node_num = self.get_topology()
                    print("Node changed! Now there are ",node_num," nodes")

        except KeyboardInterrupt:
            self.recv_socket.close()




    # 广播报文，广播的时候按照拓扑广播，距离N=5以外的收不到报文，因此，首先应发现拓扑
    def broadcast(self, des_address, src_address, route_list, sender_port, flag, idx):
        json_str = write_json(des_address, src_address, route_list, flag, idx)
        # 查看拓扑
        self.x_list, self.y_list, self.node_num = self.get_topology()

        # 本节点的index
        index = self.my_port-self.port_basis-1
        # sender的index
        sender_index = sender_port - self.port_basis - 1

        for i in range(self.node_num):
            if i!=index and i!= sender_index:
                # 广播，距离N=5以内的节点均可以广播到
                if math.sqrt(math.pow((self.x_list[i]-self.x_list[index]),2)+math.pow((self.y_list[i]-self.y_list[index]),2))<5:
                    self.send(json_str, i+self.port_basis+1)



    def get_topology(self):
        # 从文件读取拓扑
        pkl_file = open('ylist.pkl', 'rb')
        y_list = pickle.load(pkl_file)
        pkl_file.close()

        pkl_file = open('xlist.pkl', 'rb')
        x_list = pickle.load(pkl_file)
        pkl_file.close()
        # 端口数目
        node_num = len(x_list)
        # 根据端口数目设置所有端口
        self.allport = []
        for i in range(node_num):
            port_temp = i + 1 + self.port_basis
            self.allport.append(port_temp)
        return x_list, y_list, node_num


    # 不停接听报文的端口，根据报文的flag'REQ'或者'REP'作出相应动作
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

# 打包报文数据，形成json格式报文
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

c = node(5)
c.wait_send()