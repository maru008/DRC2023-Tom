import socket

class SocketConnection:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def send_data(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        encoded_data = data.encode('utf-8', errors='ignore')
        s.sendall(encoded_data)
        # response = s.recv(1024).decode('utf-8')
        s.close() # 送信後にソケットを閉じる
        # return response 
