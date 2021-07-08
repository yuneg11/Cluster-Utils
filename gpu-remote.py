import os
import time
import json
import argparse

from blessed import Terminal

from utils import remote, gpu_stat


def load_hosts(hosts_path="hosts.json"):
    try:
        with open(hosts_path) as json_file:
            hosts = json.load(json_file)
        return hosts
    except:
        print("Failed to load hosts from '{hosts_path}'")
        exit(-1)


def print_stat(cluster, no_color=False, term=None, eol_char=os.linesep, **kwargs):
    if term is None:
        if no_color:
            term = Terminal(force_styling=None)
        else:
            term = Terminal()

    outputs = cluster.query(b"nvidia-smi")

    for name, output in outputs.items():
        if isinstance(output, Exception):
            stat = term.blue(str(output))
        else:
            stat = gpu_stat.get_status(
                term=term,
                output=output,
                **kwargs,
            )

        print(f"[{name}] {stat}", end=eol_char)


def loop_stat(cluster, interval, no_color=False, **kwargs):
    if no_color:
        term = Terminal(force_styling=None)
    else:
        term = Terminal()

    with term.fullscreen():
        print(term.clear, end="")
        while True:
            try:
                query_start = time.time()

                # Move cursor to (0, 0) but do not restore original cursor loc
                print(term.move(0, 0), end="")
                print_stat(
                    cluster=cluster,
                    term=term,
                    eol_char=(term.clear_eol + os.linesep),
                    **kwargs,
                )
                print(term.clear_eos, end="")

                query_duration = time.time() - query_start
                sleep_duration = interval - query_duration
                if sleep_duration > 0:
                    time.sleep(sleep_duration)

            except KeyboardInterrupt:
                print("key interrupt")
                break


HELP = """
GSAI SIML GPU Monitor

usage: gpus [-h] {all, mem, util} [-i [INTERVAL]] [--no-color]

arguments:
  all:  Print memory and utilization of GPU
  mem:  Print memory of GPU
  util: Print utilization of GPU

optional arguments:
  -h, --help                   Print this help screen
  -i, --interval [INTERVAL]    Use watch mode if given; seconds to wait between updates
  -C, --no-color               Use a monochrome color scheme
""".strip()


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("resource", nargs="?", default="mem", choices=["util", "mem", "all"])
    parser.add_argument("-i", "--interval", nargs="?", type=float, default=0)
    parser.add_argument("-C", "--no-color", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(HELP)
        exit()

    print_memory = (args.resource in ["mem", "all"])
    print_utilization = (args.resource in ["util", "all"])

    # Load hosts
    hosts = load_hosts("hosts.json")

    # Prepare sockets
    cluster = remote.Cluster(hosts)

    if args.interval is None:
        args.interval = 1.0
    if args.interval > 0:
        args.interval = max(0.3, args.interval)
        loop_stat(
            cluster=cluster,
            print_memory=print_memory,
            print_utilization=print_utilization,
            no_color=args.no_color,
            interval=args.interval,
        )
    else:
        print_stat(
            cluster=cluster,
            print_memory=print_memory,
            print_utilization=print_utilization,
            no_color=args.no_color,
        )
