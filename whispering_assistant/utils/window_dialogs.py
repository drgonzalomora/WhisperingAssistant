import subprocess
import signal
from Xlib import X, display

def generate_info_dialog(text):
    transcribing_window = subprocess.Popen(
        ['zenity', '--info', '--title', text, '--text', text])
    return transcribing_window

def kill_dialog(window_inst):
    return window_inst.send_signal(signal.SIGTERM)

def get_active_window_id():
    d = display.Display()
    root = d.screen().root
    window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
    return window_id

def activate_window(window_id):
    d = display.Display()
    window = d.create_resource_object('window', window_id)
    screen = d.screen()
    window.configure(stack_mode=X.Above)
    window.set_input_focus(X.RevertToParent, X.CurrentTime)
    d.sync()
