import queue

from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel

from whispering_assistant.states_manager.window_manager_messages import message_queue
from whispering_assistant.window_managers.windows.add_context_window import TextInputProcessingApp
from whispering_assistant.window_managers.windows.avater_window import InfoWindow
from whispering_assistant.window_managers.windows.choice_window import ChoiceWindow

create_avatar_window = None


class SubWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sub Window')

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class MyPtQtApp(QMainWindow):
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue
        self.initUI()

    def initUI(self):
        label = QLabel('PyQt5 App Main Window!', self)
        label.move(50, 50)
        self.setWindowTitle('My PyQt5 App Main Window. This Window Should be Hidden')
        self.setGeometry(300, 300, 400, 200)
        new_window = self.create_new_window()
        new_window.hide()

    def create_new_window(self):
        # Create a new window
        new_window = SubWindow(self)
        new_window.setGeometry(350, 350, 300, 150)
        new_window.show()
        return new_window

    def create_input_box(self):
        # Create a new window
        new_window = TextInputProcessingApp(self)
        print("creating window", new_window)
        new_window.setGeometry(350, 350, 300, 150)
        new_window.show()
        return new_window

    def create_avatar(self):
        global create_avatar_window
        if create_avatar_window is None:
            new_window = InfoWindow(self)
            new_window.setGeometry(0, 0, 300, 300)

            # Position the window in the top-right corner
            screen_geometry = QDesktopWidget().availableGeometry()
            window_geometry = new_window.frameGeometry()
            top_right_point = screen_geometry.topRight() - window_geometry.topRight()
            new_window.move(top_right_point)
            new_window.set_content("❌ Starting", "❌ Starting...")

            # Set the window to stay on top
            new_window.setWindowFlags(new_window.windowFlags() | Qt.X11BypassWindowManagerHint)
            new_window.show()
            create_avatar_window = new_window
            return new_window
        else:
            create_avatar_window.show()

    def create_list_box(self, choices, process_cb):
        print("process_cb", process_cb)
        new_window = ChoiceWindow(self, choices=choices, process_cb=process_cb)
        new_window.show()
        return new_window

    def check_queue(self):
        global create_avatar_window
        try:
            action, *content = message_queue.get_nowait()
            print("📌📌📌📌 action", action)
            if action == 'create_window':
                self.create_new_window()
            elif action == 'create_avatar':
                print("content", content)
                self.create_avatar()

                if (content[0]) == "hide":
                    create_avatar_window.hide_stop()
                elif (content[0]) == "set_content":
                    create_avatar_window.set_content(*(content[:2]))

            elif action == 'create_input_box':
                self.create_input_box()

            elif action == 'create_list_box':
                print("contentcontent", content[0])
                self.create_list_box(choices=content[0], process_cb=content[1])
        except queue.Empty:
            pass
        finally:
            # Check the queue again after a delay
            QTimer.singleShot(100, self.check_queue)


def run_blocking_window_manager():
    app_qt = QApplication([])
    ex = MyPtQtApp(message_queue)
    ex.hide()

    from PyQt5.QtCore import QTimer
    QTimer.singleShot(100, ex.check_queue)

    app_qt.exec_()
