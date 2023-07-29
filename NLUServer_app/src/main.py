import socket

print("Starting server...")
host = '0.0.0.0'  # Listen on all interfaces
port = 12345  # Define your port number

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()
print(f"Server started on {host}:{port}. Waiting for connections...")
while True:  # This line is added to accept connections continuously
    conn, addr = s.accept()
    with conn:
        print(f'Connected by {addr[0]}:{addr[1]}')

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received data: {data.decode()}", flush=True)