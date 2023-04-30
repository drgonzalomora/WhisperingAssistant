from Xlib import X, display


def get_active_window_id():
    d = display.Display()
    root = d.screen().root
    window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
    return window_id


def get_active_window_name():
    d = display.Display()
    root = d.screen().root
    window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
    window = d.create_resource_object('window', window_id)

    try:
        window_name = window.get_full_property(d.intern_atom('_NET_WM_NAME'), X.AnyPropertyType).value.decode("utf-8")
    except AttributeError:
        window_name = window.get_wm_name()

    return window_name


def activate_window(window_id):
    d = display.Display()
    window = d.create_resource_object('window', window_id)
    screen = d.screen()
    window.configure(stack_mode=X.Above)
    window.set_input_focus(X.RevertToParent, X.CurrentTime)
    d.sync()
