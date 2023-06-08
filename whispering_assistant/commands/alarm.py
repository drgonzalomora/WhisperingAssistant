import subprocess

from word2number import w2n
import re

from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.tts_test import tts_queue


def extract_first_alarm_minutes(text):
    # pattern to match hours, minutes, and seconds
    patterns = [
        (r'(\w+)\s*(minutes|min)', 1),
        (r'(\w+)\s*(hours|hour|hrs|hr)', 60),
        (r'(\w+)\s*(seconds|second|secs|sec)', 1 / 60)
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            match_group = match.group(1).lower()
            try:
                # Try to convert word number to numeric number
                numeric_val = w2n.word_to_num(match_group)
            except ValueError:
                # If ValueError is raised, the match is not a word number, so we check if it's a numeric number
                if match_group.isnumeric():
                    numeric_val = int(match_group)
                else:
                    continue  # if it's neither, we move on to the next pattern
            return numeric_val * multiplier

    return None


class Alarm(BaseCommand):
    trigger = "alarm"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["set"],
        "subject": ["alarm", "timer"]
    }
    keyword_match = 'set timer'
    description = [
        "use the following tool for setting and stopping alarms and timers. similar commands: set timer for 2 minutes; set alarm for 5 minutes"
    ]

    def parameter_checker(self, raw_text, *args, **kwargs):
        alarm_input = extract_first_alarm_minutes(raw_text)

        if 'stop' in raw_text:
            return 'stop'

        if alarm_input:
            return alarm_input

        return None

    def run(self, text_parameter, raw_text, *args, **kwargs):
        raw_text = raw_text.lower()
        alarm_minutes = extract_first_alarm_minutes(raw_text)
        script_directory = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/commands/shell_script/alarm-clock.sh"

        if 'stop' in raw_text:
            tts_queue.put(("stopping the timer!", None))
            subprocess.Popen([script_directory, "stop"])
        elif alarm_minutes:
            tts_queue.put(("starting the timer!", None))
            subprocess.Popen([script_directory, "start", str(alarm_minutes)])
