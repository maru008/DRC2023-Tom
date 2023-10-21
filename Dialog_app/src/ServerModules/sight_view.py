import json

import socket

class SightViewTCPServer():
    def __init__(self, DIALOG_MODE, ip, port):
        self.ip = ip
        self.port = int(port)
        self.DIALOG_MODE = DIALOG_MODE
        
    def send_data(self,dictsite):
        if self.DIALOG_MODE == "console_dialog":
            return None
        sock = socket.socket(socket.AF_INET)
        sock.connect((self.ip, self.port))
        
        json_data = json.dumps(dictsite).encode('utf-8')
        sock.send(json_data)
        print("send view data")

        rcv_data = sock.recv(128)            
        rcv_data = rcv_data.decode('utf-8')
        rcvdict = json.loads(rcv_data)
        print("result: " + rcvdict['Return'])