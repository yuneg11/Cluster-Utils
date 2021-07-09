import os
import argparse

from blessed import Terminal

from utils import (
    remote,
    gpu_stat,
    misc,
)


def print_stat(cluster, term=None, eol_char=os.linesep, debug=False, **kwargs):
    if term is None:
        term = Terminal()

    outputs = cluster.query("nvidia-smi")

    maxlen = max([len(n) for n in outputs.keys()])

    for name, (connection_type, output) in outputs.items():
        if isinstance(output, Exception):
            if debug:
                stat = term.blue(str(output))  # For detailed error message
            else:
                stat = term.blue("Connection error")
        else:
            stat = gpu_stat.get_status(term=term, output=output, **kwargs)

        name_style = misc.connection_style(term, connection_type)
        print(f"[{name_style(name.ljust(maxlen))}] {stat}", end=eol_char)

    if "ssh" in [t for t, _ in outputs.values()]:
        print(
            "\n" + term.yellow("Some server monitor(s) are running in fallback mode.") + term.clear_eol + \
            "\n" + term.yellow("Please contact to admin.") + term.clear_eol,
            end=eol_char
        )

    if None in [t for t, _ in outputs.values()]:
        print(
            "\n" + term.red("Cannot connect to some server monitor(s).") + term.clear_eol + \
            "\n" + term.red("Please contact to admin.") + term.clear_eol,
            end=eol_char
        )



HELP = """
Remote GPU Monitor

usage: gpus [-h] {all, mem, util} [-i [INTERVAL]] [-t <TARGET ...>]

arguments:
  all:  Print memory and utilization of GPU
  mem:  Print memory of GPU
  util: Print utilization of GPU

optional arguments:
  -h, --help                       Print this help screen
  -t, --target-hosts <TARGET...>   Specify target host names to monitor
  -i, --interval [INTERVAL]        Use watch mode if given; seconds update interval
  -f, --hosts-file                 Path to the 'hosts.json' file
  -d, --debug                      Show information for debugging
""".strip()


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("resource", nargs="?", default="mem", choices=["all", "mem", "util"])
    parser.add_argument("-f", "--hosts-file", type=str, default="~/.bin/hosts.json")
    parser.add_argument("-t", "--target-hosts", nargs="+")
    parser.add_argument("-i", "--interval", nargs="?", type=float, default=0)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(HELP)
        exit()

    print_memory = (args.resource in ["mem", "all"])
    print_utilization = (args.resource in ["util", "all"])

    # Load hosts
    try:
        hosts = misc.load_json(os.path.expanduser(args.hosts_file))

        if args.target_hosts:
            try:
                hosts = {name: hosts[name] for name in args.target_hosts}
            except KeyError as e:
                print(f"Invalid host name {e}")
                exit(-1)

        # temporary remote extraction
        hosts = {name: host for name, host in hosts.items()}
    except ValueError as e:
        print(e)
        exit(-1)

    # Prepare sockets
    cluster = remote.Cluster(hosts)

    if args.interval is None:
        args.interval = 2
    if args.interval > 0:
        args.interval = max(0.5, args.interval)
        misc.loop_update(
            print_stat,
            cluster=cluster,
            print_memory=print_memory,
            print_utilization=print_utilization,
            interval=args.interval,
            debug=args.debug,
        )
    else:
        print_stat(
            cluster=cluster,
            print_memory=print_memory,
            print_utilization=print_utilization,
            debug=args.debug,
        )
