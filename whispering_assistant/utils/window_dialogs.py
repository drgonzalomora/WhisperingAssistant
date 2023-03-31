import subprocess
import signal

def generate_info_dialog(text):
    transcribing_window = subprocess.Popen(
        ['zenity', '--info', '--title', text, '--text', text])
    return transcribing_window

def kill_dialog(window_inst):
    return window_inst.send_signal(signal.SIGTERM)
