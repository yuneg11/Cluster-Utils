import re
import time
import socket


NAME = "siml03"
HOST = "10.33.0.2"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        s.sendall(b'nvidia-smi')
        data = s.recv(4000)

        output = data.decode("utf-8")
        mems = list(map(int, re.findall(r"([0-9]+)MiB / [0-9]+MiB", output)))
        utils = list(map(int, re.findall(r"([0-9]+)% +Default", output)))
        print(f"\r{NAME} {mems} {utils}", end="\033[1K")
        time.sleep(1)
