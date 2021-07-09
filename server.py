import time
import socket
import argparse
import threading
import subprocess

from datetime import datetime as dt


RECV_BUFFER = 1024


NVIDIA_SMI_LAST_TIME = 0
NVIDIA_SMI_LAST_CACHE = None
HTOP_LAST_TIME = 0
HTOP_LAST_CACHE = None


def get_nvidia_smi():
    global NVIDIA_SMI_LAST_TIME
    global NVIDIA_SMI_LAST_CACHE

    if time.time() - NVIDIA_SMI_LAST_TIME >= 1:
        NVIDIA_SMI_LAST_CACHE = subprocess.check_output(["nvidia-smi"])
        NVIDIA_SMI_LAST_TIME = time.time()

    return NVIDIA_SMI_LAST_CACHE


def get_htop():
    global HTOP_LAST_TIME
    global HTOP_LAST_CACHE

    if time.time() - HTOP_LAST_TIME >= 1:
        HTOP_LAST_CACHE = subprocess.check_output(["echo q | htop -C"], shell=True)
        HTOP_LAST_TIME = time.time()

    return HTOP_LAST_CACHE


def exec_query(query):
    """query and returns should be byte-string"""

    if query == b"nvidia-smi":
        return get_nvidia_smi()
    elif query == b"htop":
        return get_htop()
    else:
        return b"invalid command"


class Server:
    def __init__(self, host, port, debug=False):
        self.socket = None
        self.debug = debug

        if debug:
            self.log = lambda msg: print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
        else:
            self.log = lambda msg: None

        self.log("Creating socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log("Socket created")

        self.log(f"Binding server to {host}:{port}...")
        self.socket.bind((host, port))
        self.log(f"Server binded to {host}:{port}")

    def __del__(self):
        try:
            self.log("Shutting down server...")
        except:
            if self.debug:
                print("Shutting down server...")

        self.socket.close()

    def handle_client(self, client_socket, client_address):
        self.log(f"Connection from {client_address} opened")

        try:
            with client_socket:
                query = client_socket.recv(RECV_BUFFER)

                while query:
                    # self.log(f"REQUEST from {client_address}: {query}")
                    output = exec_query(query)
                    client_socket.sendall(output)

                    query = client_socket.recv(RECV_BUFFER)

        except OSError as err:
            self.log(err)

        finally:
            self.log(f"Connection from {client_address} closed")

    def listen(self, max_clients=20):
        try:
            self.log("Listening for incoming connection")
            self.socket.listen(max_clients)

            while True:
                client_socket, client_address = self.socket.accept()
                self.log(f"Accepted connection from {client_address}")

                threading.Thread(
                    target = self.handle_client,
                    args = (client_socket, client_address),
                ).start()

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--host", type=str, default="0.0.0.0")
    parser.add_argument("-p", "--port", type=int, default=65432)
    parser.add_argument("-m", "--max-clients", type=int, default=20)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    server = Server(args.host, args.port, debug=args.debug)
    server.listen(args.max_clients)
