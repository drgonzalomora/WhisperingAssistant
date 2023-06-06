import subprocess
import time

import requests

from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.states_manager import global_var_state


class ContinuousConversation(BaseCommand):
    trigger = "continuous_conversation"
    command_type = command_types['ONE_SHOT']
    keywords = {"action": ["continuous"], "subject": ["conversation"]}
    description = [
        "use the following tool to activate continuous conversation. usually activates like 'activate continuous conversation'"
    ]

    def run(self, text_parameter, raw_text, *args, **kwargs):
        global_var_state.continuous_conversation_mode = True
        command = "sleep 0.5; curl http://127.0.0.1:6969"
        subprocess.Popen(command, shell=True)
