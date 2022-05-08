import math
import os

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
        print(f'{level}: {msg}\n')


def print_only_error_warn():
    LoggerPrintCallbacks[0] = only_error_warn_log_callback


def ensure_folder_created(path: str):
    # noinspection PyBroadException
    try:
        os.mkdir(path)
    except:
        pass
