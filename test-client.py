import re
import time
import socket


SOCK_TIMEOUT = 1

NAME = "siml03"
HOST = "10.33.0.2"
PORT = 65432

with socket.create_connection((HOST, PORT), SOCK_TIMEOUT) as s:
    while True:
        s.sendall(b"nvidia-smi")
        data = s.recv(4000)

        output = data.decode("utf-8")
        mems = list(map(int, re.findall(r"([0-9]+)MiB / [0-9]+MiB", output)))
        utils = list(map(int, re.findall(r"([0-9]+)% +Default", output)))
        print(f"\r{NAME} {mems} {utils}", end="\033[1K")
        time.sleep(1)
