import time
from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.states_manager import global_var_state


class PauseHotWord(BaseCommand):
    trigger = "pause_hotword_detection"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["stop", "start"],
        "subject": ["hot-word", "listening", "hot word"]
    }

    def run(self, text_parameter, raw_text, *args, **kwargs):
        raw_text = raw_text.lower()

        if 'stop' in raw_text:
            global_var_state.pause_hotword = True

        if 'start' in raw_text:
            global_var_state.pause_hotword = False
