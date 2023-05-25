import time
from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class WebSearch(BaseCommand):
    trigger = "search_the_web_via_ui"
    command_type = command_types['CHAINABLE_LONG']
    description = [
        "use the following tool for searching with google. command usually starts with 'search google'"
    ]
    keywords = {
        "action": ["search", "ask", "find"], "subject": ["google", "web"]}
    examples = [
        'search google',
        'find on the web',
        'ask google',
        'search the web',
        'search with bing',
        'user wants to search web for a question',
        'user intends to search with google for a TOPIC',
        'user intends to search with google for a question'
    ]

    def run(self, text_parameter, raw_text, *args, **kwargs):
        import pyautogui
        import pyclip
        pyautogui.hotkey('ctrl', 'alt', 'shift', 'w', interval=0.1)

        # Type the string
        old_clipboard = pyclip.paste()
        pyclip.copy(text_parameter.lstrip())
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        pyclip.copy(old_clipboard)
        time.sleep(0.5)
