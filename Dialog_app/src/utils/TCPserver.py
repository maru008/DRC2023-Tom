import socket

class SocketConnection:
    def __init__(self, host='localhost', port=12345):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def send_data(self, data):
        encoded_data = data.encode('utf-8', errors='ignore')
        self.s.sendall(encoded_data)
        # print(f"Sent data: {data}")