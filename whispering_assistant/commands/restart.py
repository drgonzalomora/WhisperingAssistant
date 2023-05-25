import os

from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class Restart(BaseCommand):
    # Set the trigger for the 'Shutdown' command plugin
    trigger = "restart"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["restart", "reboot"],
        "subject": ["laptop", "computer"]
    }
    required_keywords = ['computer', 'laptop']
    description = [
        "use the following tool for restarting a computer or laptop. example: 'restart the computer'"
    ]
    examples = [
        'restart computer',
        'reboot laptop'
    ]

    def run(self, *args, **kwargs):
        os.system("reboot")

