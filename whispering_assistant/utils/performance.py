import time

def print_time_profile(start_time, desc):
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The {desc} execution time is {execution_time} seconds.")