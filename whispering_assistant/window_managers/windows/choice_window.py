import queue
import time

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from whispering_assistant.window_managers.windows.base_window_template import BaseWindowTemplate


class ChoiceWindow(BaseWindowTemplate):
    def __init__(self, parent=None, choices=[], process_cb=None):
        super().__init__(parent, choices=choices, process_cb=process_cb)

    def initUI(self, choices, process_cb):
        self.setWindowTitle("Select the desired link")
        self.setGeometry(1000, 500, 1600, 200)
        self.selected_index = None
        self.choices = choices
        self.process_cb = process_cb

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.list_widget = QListWidget(central_widget)
        for choice in choices:
            display_text = choice['display_text']
            list_item = QListWidgetItem(display_text)
            self.list_widget.addItem(list_item)

        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.list_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.show()

    def on_item_double_clicked(self, item):
        self.selected_index = self.list_widget.row(item)
        print("self.selected_index", self.selected_index, self.choices[self.selected_index])
        selected_item = self.choices[self.selected_index]
        if self.process_cb:
            self.process_cb(selected_item)
        self.close()
