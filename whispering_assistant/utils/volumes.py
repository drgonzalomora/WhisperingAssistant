import subprocess
import re

def get_current_volume():
    output = subprocess.check_output(["amixer", "-D", "pulse", "sget", "Master"]).decode("utf-8")
    match = re.search(r"\[(\d+)%\]", output)
    if match:
        curr_volume = int(match.group(1))
        return curr_volume
    return None

def set_volume(volume_percent):
    return subprocess.call(["pactl", "set-sink-volume", "0", volume_percent])
