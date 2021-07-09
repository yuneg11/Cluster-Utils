import copy
import socket
import subprocess


SOCK_TIMEOUT = 1
SSH_TIMEOUT = 2
RECV_BUFFER = 6000


class Server:
    def __init__(self, host):
        self.type = None
        self.socket = None
        self.ssh = None
        self.error = None

        if "tcp" in host:
            try:
                self.socket = socket.create_connection(host["tcp"], SOCK_TIMEOUT)
                self.type = "tcp"
            except socket.error as e:
                self.socket = e

        if "ssh" in host:
            self.ssh = host["ssh"]
            if isinstance(self.socket, Exception) or self.socket is None:
                self.type = "ssh"

    def __del__(self):
        if isinstance(self.socket, socket.socket):
            self.socket.close()

    def query(self, command):
        if self.type is None:
            if self.error is None:
                self.error = ConnectionError(404, "Host connection failed")
            output = self.error

        elif self.type == "tcp":
            output = self.tcp_query(command)

            if isinstance(output, Exception):
                self.error = output

                if self.ssh is not None:
                    self.type = "ssh"
                else:
                    self.type = None

        if self.type == "ssh":
            output = self.ssh_query(command)

            if isinstance(output, Exception):
                self.error = output
                self.type = None

        return output

    def tcp_query(self, command):
        try:
            self.socket.sendall(command.encode())
            data = self.socket.recv(RECV_BUFFER)
            if data:
                output = data.decode("utf-8")
            else:
                raise socket.error(444, "Data receive failed")
        except socket.error as e:
            output = e
            self.socket.close()
            self.socket = e

        return output

    def ssh_query(self, command):
        hostname, port = self.ssh
        exec = ["ssh", str(hostname), "-p", str(port), "-o", "LogLevel=QUIET", "-t", str(command)]

        try:
            data = subprocess.check_output(exec, timeout=SSH_TIMEOUT)
            output = data.decode("utf-8")
        except Exception as e:
            output = e
            self.ssh = e

        return output


class Cluster:
    def __init__(self, hosts):
        self.servers = {name: Server(host) for name, host in hosts.items()}

    def query(self, command):
        outputs = {}

        for name, server in self.servers.items():
            output = server.query(command)
            outputs[name] = (server.type, output)

        return outputs
