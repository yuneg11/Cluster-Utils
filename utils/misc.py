import os
import time
import json

from blessed import Terminal


def loop_update(func, *args, interval=1, **kwargs):
    term = Terminal()

    with term.fullscreen():
        print(term.clear, end="")

        while True:
            try:
                query_start = time.time()

                # Move cursor to (0, 0) but do not restore original cursor loc
                print(term.move(0, 0), end="")
                func(
                    *args,
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
                break


def load_json(file_path="hosts.json"):
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
        return data
    except:
        raise ValueError(f"Failed to load file from '{file_path}'")
