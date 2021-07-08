import re


def mem_style(term, mem, total_mem):
    if mem == 0:
        return term.green
    elif mem / total_mem <= .5:
        return term.yellow
    else:
        return term.red


def util_style(term, util):
    if util == 0:
        return term.green
    elif util < 50:
        return term.yellow
    else:
        return term.red


def get_status(term, output, print_memory=True, print_utilization=True):
    if print_memory:
        raw_mems = re.findall(r"([0-9]+)MiB / ([0-9]+)MiB", output)
        mems = [(int(cur_mem), int(total_mem)) for cur_mem, total_mem in raw_mems]

    if print_utilization:
        raw_utils = re.findall(r"([0-9]+)% +Default", output)
        utils = [int(util) for util in raw_utils]

    if print_memory and print_utilization:
        status = [
            mem_style(term, cur_mem, total_mem)(f"{cur_mem:5d}M") \
            + " / " + util_style(term, util)(f"{util:3d}%")
            for (cur_mem, total_mem), util in zip(mems, utils)
        ]
    elif print_memory:
        status = [
            mem_style(term, cur_mem, total_mem)(f"{cur_mem:5d} MB")
            for cur_mem, total_mem in mems
        ]
    elif print_utilization:
        status = [
            util_style(term, util)(f"{util:3d} %")
            for util in utils
        ]
    else:
        raise ValueError("Invalid print options")

    return " | ".join(status)
