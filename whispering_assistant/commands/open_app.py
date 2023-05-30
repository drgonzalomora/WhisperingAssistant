import time
from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.clipboard_manager import typingViaClipBoardHandler


class OpenApp(BaseCommand):
    trigger = "open_app"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["open", "start"],
        "subject": ["applications", "application", "app"]
    }
    description = [
        "use the following tool for opening computer or laptop applications. example commands are: open spotify, open firefox, open gimp"
    ]
    examples = [
        'open firefox',
        'open gimp',
        'open app',
        'open application',
        'open spotify',
        'user wants to open an application',
    ]

    def run(self, text_parameter, *args, **kwargs):
        import pyautogui
        win_key = "winleft"
        pyautogui.keyDown(win_key)
        time.sleep(0.1)
        pyautogui.keyUp(win_key)
        time.sleep(0.5)

        # Type the text parameter
        typingViaClipBoardHandler.run_thread(text_parameter)
        time.sleep(0.45)

        # Press the Enter key
        pyautogui.press("enter")