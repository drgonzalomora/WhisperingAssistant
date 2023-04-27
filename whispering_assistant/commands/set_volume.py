import re

from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.volumes import set_volume


class SetVolume(BaseCommand):
    trigger = "set_volume"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["change", "set", "update"],
        "subject": ["volume"]
    }

    def run(self, text_parameter, raw_text, *args, **kwargs):
        raw_text = raw_text.lower()
        pattern = r'(\d+(\.\d{1,2})?)\s*%'

        # Find percentage value in input string
        match = re.search(pattern, raw_text)
        print(match)

        # Extract percentage value from match object and remove % sign
        if match:
            percentage = match.group(1).replace('%', '')
            print("percentage", float(percentage))
            set_volume(float(percentage))

# SetVolume().run(raw_text="set volume to 50%", text_parameter="110%")
