import json

from PyQt5.QtWidgets import QTextEdit, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import yaml

from whispering_assistant.utils.prompt import generate_frequent_misspelled_prompt
from whispering_assistant.window_managers.windows.base_window_template import BaseWindowTemplate


def custom_yaml_dump(data, stream=None, **kwds):
    class CustomDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(CustomDumper, self).increase_indent(flow, False)

    return yaml.dump(data, stream, Dumper=CustomDumper, **kwds)


def update_prompt_dict(text):
    print("text", text)
    words = text.lower().split()
    unique_words = list(set(words))

    # Read the YAML file
    with open('/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/prompt.yml',
              'r') as f:
        prompt_dict = yaml.safe_load(f)

    # Append the unique words to the "technical_terms" list
    prompt_dict["frequent_misspelled"].extend(unique_words)

    # Write the updated YAML back to the file
    with open('/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/prompt.yml',
              'w') as f:
        f.write(custom_yaml_dump(prompt_dict, sort_keys=False, default_flow_style=False, allow_unicode=True))

    generate_frequent_misspelled_prompt()
    return unique_words


class TextInputProcessingApp(BaseWindowTemplate):
    text_input = None
    processing_function = None

    def __init__(self, parent=None):
        super().__init__(parent)

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
