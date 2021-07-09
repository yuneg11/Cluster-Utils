import argparse
import subprocess
import re


TOTAL_MEM = 11019


class Colors:
    # HEADER = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    end = '\033[0m'
    # UNDERLINE = '\033[4m'


def mem_color(mem, total_mem=TOTAL_MEM):
    if mem == 0:
        return Colors.green
    elif mem / total_mem <= .5:
        return Colors.yellow
    else:
        return Colors.red


def util_color(util):
    if util == 0:
        return Colors.green
    elif util < 50:
        return Colors.yellow
    else:
        return Colors.red


def printc(message, color, end=""):
    print(color, end="")
    print(message, end="")
    print(Colors.end, end=end)


help = """
GSAI SIML GPU Monitor

usage: gpus [-h] {all, mem, util}

all:  Print memory and utilization of GPU
mem:  Print memory of GPU
util: Print utilization of GPU
""".strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="", add_help=False)
    parser.add_argument("resource", nargs="?", default="mem",
                        choices=["util", "mem", "all"], help=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(help)
        exit()

    for i in [1, 2, 3, 4, 5, 6, 7, 8]:
        if i == 3:
            printc(f"siml{i:02d}:", Colors.bold)
            print(" Failed due to ssh issue")
            continue

        command = ["ssh", f"siml{i:02d}", "-o", "LogLevel=QUIET", "-t", "nvidia-smi"]
        output = subprocess.check_output(command).decode("utf-8")

        mems = map(int, re.findall(r"([0-9]+)MiB / [0-9]+MiB", output))
        utils = map(int, re.findall(r"([0-9]+)% +Default", output))

        printc(f"siml{i:02d}:", Colors.bold)

        if args.resource == "mem":
            for mem in mems:
                printc(f" {mem:5d} MiB", mem_color(mem))

        elif args.resource == "util":
            for util in utils:
                printc(f" {util:3d} %", util_color(util))

        elif args.resource == "all":
            for mem, util in zip(mems, utils):
                printc(f" {mem:5d}M", mem_color(mem))
                print("(", end="")
                printc(f"{util:3d}%", util_color(util))
                print(")", end="")

        print()
