import socket

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server = None
        self.conn = None

    def start_server(self):
        print("Starting server...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server started on {self.host}:{self.port}. Waiting for connections...")
        self.conn, addr = self.server.accept()
        print(f'Connected by {addr[0]}:{addr[1]}')
        
    def stop_server(self):
        if self.conn:
            self.conn.close()
        if self.server:
            self.server.close()
            print("Server stopped.")
    
    def accept_connections(self):
        while True: # このループで同一接続からのデータを受け取り続ける
            data = self.receive_data(self.conn)
            if data:
                return data
            else: # dataがNoneの場合、接続が閉じられたと判断
                break

    def receive_data(self, conn):
        data = conn.recv(1024)
        if data:
            return data.decode()
        return None
