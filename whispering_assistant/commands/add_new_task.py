import time
import urllib

import pyclip
from whispering_assistant.commands.command_base_template import BaseCommand, command_types


def is_url(s):
    try:
        result = urllib.parse.urlparse(s)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class AddTask(BaseCommand):
    trigger = "add_task"
    command_type = command_types['CHAINABLE_LONG']
    keywords = {"action": ["add", "create"], "subject": ["task", "note", "reminder"]}
    description = [
        "use the following tool for creating new tasks, notes or reminders. usually starts with 'create a task'"
    ]
    keyword_match = 'create reminder'
    examples = [
        'create a task',
        'add a task',
        'create a note',
        'user wants to create a task',
        'user wants to create a reminder',
        'user wants to create a note'
    ]

    def run(self, text_parameter, raw_text, *args, **kwargs):
        import pyautogui
        pyautogui.hotkey('ctrl', 'alt', 'shift', 'a', interval=0.1)

        old_clipboard = (pyclip.paste()).decode('utf-8')

        if is_url(old_clipboard):
            context = f"URL: {old_clipboard}"
            text_parameter = text_parameter.lstrip() + " " + context

        pyclip.copy(text_parameter.lstrip())
        time.sleep(0.5)
        import pyautogui
        pyautogui.hotkey('ctrl', 'v')
        pyclip.copy(old_clipboard)
