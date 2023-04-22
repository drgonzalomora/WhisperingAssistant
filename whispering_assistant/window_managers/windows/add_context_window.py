import json

from PyQt5.QtWidgets import QTextEdit, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from whispering_assistant.utils.prompt import generate_prompt
from whispering_assistant.window_managers.windows.base_window_template import BaseWindowTemplate


def update_prompt_dict(text):
    print("text", text)
    words = text.lower().split()
    unique_words = list(set(words))

    # Read the JSON file
    with open('whispering_assistant/assets/docs/prompt.json', 'r') as f:
        prompt_dict = json.load(f)

    # Append the unique words to the "technical_terms" list
    prompt_dict["technical_terms"].extend(unique_words)

    # Write the updated JSON back to the file
    with open('whispering_assistant/assets/docs/prompt.json', 'w') as f:
        json.dump(prompt_dict, f, indent=2)

    generate_prompt()
    return unique_words


class TextInputProcessingApp(BaseWindowTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_input = None
        self.processing_function = None

    def initUI(self):
        self.processing_function = update_prompt_dict

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        label_font = QFont("Arial", 14)
        label = QLabel('Enter your text:', central_widget)
        label.setFont(label_font)
        layout.addWidget(label)

        text_font = QFont("Arial", 14)
        self.text_input = QTextEdit(central_widget)
        self.text_input.setFont(text_font)
        layout.addWidget(self.text_input)

        button_font = QFont("Arial", 14)
        submit_button = QPushButton('Submit', central_widget)
        submit_button.setFont(button_font)
        submit_button.clicked.connect(self.submit_text)
        layout.addWidget(submit_button)

        self.setCentralWidget(central_widget)

    def submit_text(self):
        user_text = self.text_input.toPlainText()
        self.text_processing(user_text)
        self.close()

    def text_processing(self, text):
        # Use the provided processing function
        processed_text = self.processing_function(text)
        print(processed_text)
