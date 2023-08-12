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

    def accept_connections(self):
        while True:
            print("="*100)
            conn, addr = self.server.accept()  # 新しい接続を受け入れる
            print(f'Connected by {addr[0]}:{addr[1]}')
            data = self.receive_data(conn)  # データを受け取る
            if data:
                # conn.close()  # 接続を閉じる
                print(f"Connection from {addr[0]}:{addr[1]} closed.")
                return data,conn

    def receive_data(self, conn):
        data = conn.recv(1024)
        if data:
            return data.decode()
        return None
