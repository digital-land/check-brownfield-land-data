import os
import time
from threading import Thread


def delay_remove_file(file_path, time_limit):
    time.sleep(time_limit)
    os.remove(file_path)


def delay_remove_files_thread(files, time_limit):
    for file in files:
        Thread(target=delay_remove_file, args=(file, time_limit), daemon=True).start()

