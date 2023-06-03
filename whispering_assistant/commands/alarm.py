import subprocess
import re

from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.tts_test import tts_queue


def extract_first_alarm_minutes(text):
    # pattern to match hours, minutes, and seconds
    patterns = [
        (r'(\d+)\s*(minutes|min)', 1),
        (r'(\d+)\s*(hours|hour|hrs|hr)', 60),
        (r'(\d+)\s*(seconds|second|secs|sec)', 1 / 60),
        (r'one\s*(minute|min)', 1),
        (r'one\s*(hour|hr)', 60),
        (r'one\s*(second|sec)', 1 / 60)
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if isinstance(match.group(1), str) and match.group(1).isnumeric():
                return int(match.group(1)) * multiplier
            else:
                return multiplier

    return None


class Alarm(BaseCommand):
    trigger = "alarm"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["set"],
        "subject": ["alarm", "timer"]
    }
    description = [
        "use the following tool for setting and stopping alarms and timers. similar commands: set timer for 2 minutes; set alarm for 5 minutes"
    ]

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
