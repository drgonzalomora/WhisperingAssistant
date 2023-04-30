import time
import cProfile
import pstats
from io import StringIO
import functools


def print_time_profile(start_time, desc):
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The {desc} execution time is {execution_time} seconds.")


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
