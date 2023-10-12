import json

import socket

class SightViewTCPServer():
    def __init__(self, ip,port):
        self.ip = ip
        self.port = int(port)
        
    def send_data(self,dictsite):
        sock = socket.socket(socket.AF_INET)
        sock.connect((self.ip, self.port))
        
        json_data = json.dumps(dictsite).encode('utf-8')
        sock.send(json_data)
        print("send view data")

        rcv_data = sock.recv(128)            
        rcv_data = rcv_data.decode('utf-8')
        rcvdict = json.loads(rcv_data)
        print("result: " + rcvdict['Return'])