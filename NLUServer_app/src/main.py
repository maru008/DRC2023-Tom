from utils.receive_data import Server

server = Server()
server.start_server()

while True:
    received_data = server.accept_connections()
    if received_data is not None:
        # ここで受け取ったデータを使用できます
        received_data_ls = eval(received_data)
        print("ID:",received_data_ls[0], flush=True)
        print("text:",received_data_ls[1], flush=True)
