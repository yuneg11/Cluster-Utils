import socket


SOCK_TIMEOUT = 1
RECV_BUFFER = 4000


class Cluster:
    def __init__(self, hosts):
        self.sockets = {}

        for name, (host, port) in hosts.items():
            try:
                sock = socket.create_connection((host, port), SOCK_TIMEOUT)
                self.sockets[name] = sock
            except socket.error as e:
                self.sockets[name] = e

    def __del__(self):
        for sock in self.sockets.values():
            try:
                if isinstance(sock, socket.socket):
                    sock.close()
            except:
                pass

    def query(self, command):
        outputs = {}

        for name, sock in zip(list(self.sockets.keys()), list(self.sockets.values())):
            if isinstance(sock, socket.socket):
                try:
                    sock.sendall(command)
                    outputs[name] = None
                except socket.error as e:
                    outputs[name] = e
                    self.sockets[name] = e
                    sock.close()
            else:
                outputs[name] = sock  # sock is error actually

        for name, sock in zip(list(self.sockets.keys()), list(self.sockets.values())):
            if isinstance(sock, socket.socket):
                try:
                    data = sock.recv(RECV_BUFFER)
                    outputs[name] = data.decode("utf-8")
                except socket.error as e:
                    outputs[name] = e
                    self.sockets[name] = e
                    sock.close()

        return outputs
