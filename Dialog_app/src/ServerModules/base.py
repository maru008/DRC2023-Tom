import socket

class Base:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("{}:: Connecting to Server...".format(self.__class__.__name__))
        self.sock.connect((ip, port))
        print("{}:: Connected successfully.".format(self.__class__.__name__))

    def _setblocking(self, flag=True):
        self.sock.setblocking(flag)

    def _settimeout(self, interval=None):
        self.sock.settimeout(interval)

    def _send_command(self,command):
        command_ln = command + "\n"
        # print(self.sock.send(command_ln.encode('utf-8')))
        # print(command_ln)
        self.sock.send(command_ln.encode('utf-8'))

    def _receive(self, size):
        return self.sock.recv(1024)

    def _disconnect(self):
        self.sock.close()
        print("{}:: Disconnected.".format(self.__class__.__name__))