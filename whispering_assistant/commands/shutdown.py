import os

from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class Shutdown(BaseCommand):
    # Set the trigger for the 'Shutdown' command plugin
    trigger = "shutdown"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["shutdown", "shut down", "power off", "turn off"],
        "subject": ["laptop", "computer"]
    }
    required_keywords = ['computer', 'laptop']
    examples = [
        'turn off laptop',
        'shutdown'
        'turn off computer',
        'power off laptop'
    ]

    def run(self, *args, **kwargs):
        # Your command execution logic here
        os.system("shutdown now")