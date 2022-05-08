import math
import os
import shutil

from fides.utils.logger import LoggerPrintCallbacks

Click = int
"""Measure of time."""


def argmin(arr, key):
    selected_idx = 0
    curr_min_value = math.inf
    for idx, el in enumerate(arr):
        val = key(el)
        if val < curr_min_value:
            selected_idx, curr_min_value = idx, val
    return arr[selected_idx]


def argmax(arr, key):
    selected_idx = 0
    curr_min_value = -math.inf
    for idx, el in enumerate(arr):
        val = key(el)
        if val > curr_min_value:
            selected_idx, curr_min_value = idx, val
    return arr[selected_idx]


def only_error_warn_log_callback(level: str, msg: str):
    if level in {'ERROR', 'WARN'}:
        print(f'{level}: {msg}', flush=True)


def print_only_error_warn():
    LoggerPrintCallbacks[0] = only_error_warn_log_callback


# noinspection PyBroadException
def ensure_folder_created_and_clean(path: str):
    # clean up
    try:
        shutil.rmtree(path)
    except:
        pass
    # and recreate
    try:
        os.mkdir(path)
    except:
        pass
