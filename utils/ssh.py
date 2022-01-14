import subprocess


SSH_TIMEOUT = 1


class Cluster:
    def __init__(self, hosts):
        self.hosts = hosts

    def query(self, command):
        outputs = {}

        for name, host in self.hosts.items():
            if isinstance(host, (tuple, list)):
                hostname, port = host
                exec = ["ssh", str(hostname), "-p", str(port), "-o", "LogLevel=QUIET", "-t", str(command)]
                try:
                    data = subprocess.check_output(exec, timeout=SSH_TIMEOUT)
                    outputs[name] = data.decode("utf-8")
                except Exception as e:
                    outputs[name] = e
            else:
                outputs[name] = host  # host is error actually

        return outputs
