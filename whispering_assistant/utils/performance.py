import time
import cProfile
import pstats
from io import StringIO
import functools


def print_time_profile(start_time, desc):
    end_time = time.time()
    execution_time = end_time - start_time

    if execution_time > 0.1:
        print(f"⚡⚡⚡ ⏰ The {desc} execution time is {execution_time} seconds.")
    else:
        print(f"⚡⚡⚡ The {desc} execution time is {execution_time} seconds.")


"""
# Usage example
@profile
def execute_plugin_by_keyword(result_text):
    # Your implementation of the function here
    pass


result_text = "some_text"
result = execute_plugin_by_keyword(result_text)
"""


def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()

        s = StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        return result

    return wrapper


class TimerCheck:
    def __init__(self):
        self.start_time = None
        self.logs = []

    def start(self):
        self.start_time = time.time()

    def stop(self, description):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            self.logs.append((description, elapsed_time))
            self.start_time = None
        else:
            print("Timer is not started yet.")

    def output(self):
        for description, elapsed in self.logs:
            if elapsed > 0.1:
                print(f"🎯 {description}: {elapsed} seconds")
            else:
                print(f"{description}: {elapsed} seconds")

        self.logs = []
