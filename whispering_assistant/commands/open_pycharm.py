import json
import subprocess
from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.configs.config import AUTOJUMP_FILE, AUTOJUMP_JSON_FILE
from whispering_assistant.utils.fuzzy_json_show_dialog import fuzzy_search_json


def fuzzy_search_autojump(query, process_selected_option_cb):
    autojump_stats = []

    with open(AUTOJUMP_FILE) as f:
        for line in f:
            if line:
                try:
                    weight, directory = line.strip().split('\t')
                    autojump_stats.append({"dir": directory, "weight": float(weight)})
                except ValueError:
                    print(f"Skipping invalid line: {line}")

    # Sort the list by weight
    autojump_stats = sorted(autojump_stats, key=lambda x: x["weight"], reverse=True)

    # Print the list in a pretty format
    # print(json.dumps(autojump_stats, indent=4))

    # Save the list to a JSON file
    with open(AUTOJUMP_JSON_FILE, "w") as f:
        json.dump(autojump_stats, f, indent=4)

    results = fuzzy_search_json(query=query, json_files=[AUTOJUMP_JSON_FILE], return_keys=["dir"], search_keys=["dir"],
                                process_selected_option_cb=process_selected_option_cb, name_keys=["dir"],
                                value_keys=["dir"])
    print(results)
    return results


class OpenPycharm(BaseCommand):
    trigger = "open_pycharm"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["pycharm", "py charm"],
        "subject": []
    }
    description = [
        "use the following tool for opening projects with pycharm for code development. usually start with the phrases: 'open pycharm'"
    ]
    required_keywords = ['pycharm']
    examples = [
        'open py charm for TOPIC',
        'open pycharm TOPIC',
        'open pycharm for TOPIC',
        'pycharm for TOPIC',
        'open TOPIC on py charm',
        'open a project with pycharm',
        'user wants to open pycharm for a project',
        'user intends to open pycharm for a project',
        'user intends to open pycharm for a directory'
    ]

    def run(self, text_parameter, *args, **kwargs):
        def process_cb(dir_path):
            if dir_path is not None:
                cmd = f"terminator --new-tab --command 'zsh -i -c \"cd {dir_path}; pych; exec zsh\"'"
                subprocess.run(cmd, shell=True)

        fuzzy_search_autojump(text_parameter, process_selected_option_cb=process_cb)
