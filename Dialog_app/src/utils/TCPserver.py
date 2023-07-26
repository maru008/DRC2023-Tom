import socket

def send_data(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8', errors='ignore'))
        # print(f"Sent data: {data}")
# Example usage:
# send_data('nlu_server_app',12345,"aaaaaa")
