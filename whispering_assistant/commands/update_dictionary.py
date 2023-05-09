from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.prompt import add_new_prompt


class UpdateDictionary(BaseCommand):
    trigger = "update_dictionary"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["update", "change"], "subject": ["dictionary", "terminology"]}
    examples = [
        'update dictionary',
        'change dictionary'
    ]

    def run(self, text_parameter, raw_text, *args, **kwargs):
        add_new_prompt()
