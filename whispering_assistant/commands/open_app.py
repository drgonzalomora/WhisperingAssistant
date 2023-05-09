import time
from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class OpenApp(BaseCommand):
    trigger = "open_app"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["open", "start"],
        "subject": ["applications", "application", "app"]
    }
    examples = [
        'open firefox',
        'open gimp',
        'open spotify'
    ]
    def run(self, text_parameter, *args, **kwargs):
        import pyautogui
        win_key = "winleft"
        pyautogui.keyDown(win_key)
        time.sleep(0.1)  # Wait for 100 milliseconds
        pyautogui.keyUp(win_key)
        time.sleep(0.5)  # Wait for 300 milliseconds

        # Type the text parameter
        pyautogui.typewrite(text_parameter)

        time.sleep(0.3)  # Wait for 300 milliseconds

        # Press the Enter key
        pyautogui.press("enter")
