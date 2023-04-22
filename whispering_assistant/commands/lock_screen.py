import os
import subprocess

from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class LockScreen(BaseCommand):
    # Set the trigger for the 'Shutdown' command plugin
    trigger = "lock_screen"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["lock", "lock screen"],
        "subject": ["laptop", "computer"]
    }

    def run(self, *args, **kwargs):
        subprocess.run(['xdotool', 'key', 'Super+Escape'])

