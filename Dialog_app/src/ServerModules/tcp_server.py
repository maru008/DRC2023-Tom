import socket
import json

class ConversationSignalHandler:
    def __init__(self, DIALOG_MODE,host="localhost", port=8001):
        self.host = host
        self.port = int(port)
        self.sock = None
        self.DIALOG_MODE = DIALOG_MODE

    def connect_and_request_rule(self):
        """サーバーに接続し、CONVERSATION_RULEを要求するメソッド"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.sendall("GET_CONVERSATION_RULE\n".encode())
        
    def close(self):
        """接続を閉じるメソッド"""
        if self.sock:
            self.sock.close()

    def check_start_signal(self):
        """CONVERSATION_STARTのシグナルをチェックするメソッド"""
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("Connection closed by the client.")
                    break
                print("data received now")
                decoded_data = data.decode('utf-8')
                
                # JSON形式であるかを確認
                parsed_data = json.loads(decoded_data)
                if parsed_data.get("conversation_rule") == "CONVERSATION_START":
                    return True
            except socket.timeout:
                print("Socket timed out. No data received.")
                break
            except socket.error as e:
                print(f"Socket error: {e}")
                break
            except json.JSONDecodeError:
                continue
    
    def check_end_signal(self):
        """CONVERSATION_ENDのシグナルをチェックするメソッド"""
        while True:
            data = self.sock.recv(1024)
            if not data:
                return False
            
            decoded_data = data.decode('utf-8')
            
            # JSON形式であるかを確認
            try:
                parsed_data = json.loads(decoded_data)
                if parsed_data.get("conversation_rule") == "CONVERSATION_END":
                    return True
            except json.JSONDecodeError:
                continue
