import socket
import subprocess


HOST = "0.0.0.0"
PORT = 65432


def get_nvidia_smi():
    return subprocess.check_output(["nvidia-smi"])

def get_htop():
    return subprocess.check_output(["echo q | htop -C"], shell=True)


while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            while True:
                conn, addr = s.accept()

                try:
                    with conn:
                        while True:
                            command = conn.recv(1024)

                            if not command:
                                break
                            else:
                                if command == b"nvidia-smi":
                                    conn.sendall(get_nvidia_smi())
                                elif command == b"htop":
                                    conn.sendall(get_htop())
                                else:
                                    conn.sendall(b"invalid command")
                except KeyboardInterrupt:
                    raise KeyboardInterrupt

                except:
                    pass

    except KeyboardInterrupt:
        exit()

    except Exception as e:
        print(e)
        print("Restart loop")
