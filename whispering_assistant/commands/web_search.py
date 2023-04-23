import time
import pyperclip
from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class WebSearch(BaseCommand):
    trigger = "search_the_web_via_ui"
    command_type = command_types['CHAINABLE_LONG']
    keywords = {
        "action": ["search", "ask", "find"], "subject": ["google", "web"]}

    def run(self, text_parameter, raw_text, *args, **kwargs):
        import pyautogui
        pyautogui.hotkey('ctrl', 'alt', 'shift', 'w', interval=0.1)

        # Type the string
        old_clipboard = pyperclip.paste()
        pyperclip.copy(text_parameter.lstrip())
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        pyperclip.copy(old_clipboard)
        time.sleep(0.5)