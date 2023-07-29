import socket

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server = None

    def start_server(self):
        print("Starting server...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server started on {self.host}:{self.port}. Waiting for connections...")

    def accept_connections(self):
        conn, addr = self.server.accept()
        with conn:
            print(f'Connected by {addr[0]}:{addr[1]}')
            return self.receive_data(conn)

    def receive_data(self, conn):
        data = conn.recv(1024)
        if data:
            return data.decode()
        return None
