import socket

def start_server():
    host = '0.0.0.0'  # Listen on all interfaces
    port = 12345  # Define your port number

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}. Waiting for connections...")
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received data:", data.decode())  # Decoding and printing the received data
                # Here you can add the logic to process the data and interact with the database

if __name__ == "__main__":
    start_server()