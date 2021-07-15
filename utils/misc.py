import os
import time
import json

from blessed import Terminal


def loop_update(func, *args, interval=1, debug=False, **kwargs):
    term = Terminal()

    with term.fullscreen():
        print(term.clear, end="")

        while True:
            try:
                query_start = time.time()

                print(term.home, end="")
                func(
                    *args,
                    term=term,
                    debug=debug,
                    **kwargs,
                )
                print(term.clear_eos, end="")

                query_duration = time.time() - query_start
                sleep_duration = interval - query_duration

                if debug:
                    print(f"\nquery time: {query_duration:.3f} s")

                if sleep_duration > 0:
                    time.sleep(sleep_duration)

            except KeyboardInterrupt:
                break


def load_json(file_path="hosts.json"):
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
        return data
    except:
        raise ValueError(f"Failed to load file from '{file_path}'")


def connection_style(term, connection_type):
    if connection_type == "tcp":
        # return term.white
        return lambda msg: msg
    elif connection_type == "ssh":
        return term.yellow
    else:
        return term.red
