import re
import string

from whispering_assistant.commands.command_base_template import BaseCommand, FALL_BACK_COMMAND
import os
import importlib

COMMAND_PLUGINS = {}

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py" and file != "command_base_template.py":
        module_name = file[:-3]  # Remove the .py extension
        module = importlib.import_module(f"{__package__}.{module_name}")
        for attr_name in dir(module):
            attribute = getattr(module, attr_name)
            if isinstance(attribute, type) and issubclass(attribute, BaseCommand) and attribute is not BaseCommand:
                command_trigger = attribute.trigger.lower()
                COMMAND_PLUGINS[command_trigger] = attribute()


def execute_plugin(trigger, *args, **kwargs):
    plugin = COMMAND_PLUGINS.get(trigger.lower())
    if plugin:
        plugin.run(*args, **kwargs)
    else:
        print(f"No plugin found for trigger: {trigger}")


def remove_special_chars_regex(text):
    """
    Removes any special characters at the beginning and end of a string using a regular expression.
    """
    pattern = r'^[' + re.escape(string.punctuation) + r']+|[' + re.escape(string.punctuation) + r']+$'
    return re.sub(pattern, '', text)


def check_strings(text, keywords, raw_text=""):
    action_index = None
    action_found = False
    subject_index = None
    subject_found = False
    text_parameter = ""
    subject_length = 0
    action_length = 0

    words = text.split()
    limit_to_five_words = " ".join(words[:10]).lower()

    for action in keywords['action']:
        index_with_spaces = limit_to_five_words.find(action)
        index_without_spaces = limit_to_five_words.find(action.replace(" ", ""))

        if index_with_spaces != -1 or index_without_spaces != -1:
            action_found = True
            index = min(i for i in [index_with_spaces, index_without_spaces] if i != -1)
            if action_index is None or index < action_index:
                action_index = index
                action_length = len(action)
            break

    if len(keywords['subject']) == 0:
        subject_found = True
        subject_index = len(raw_text)

    for subject in keywords['subject']:
        index = limit_to_five_words.find(subject)
        if index != -1:
            subject_found = True
            if subject_index is None or index < subject_index:
                print("subject_index", subject_index)
                subject_index = index
                subject_length = len(subject)
            break

    if subject_found and subject_length > 0:
        text_parameter = raw_text[subject_index + subject_length:]
    elif action_found and action_length > 0:
        text_parameter = raw_text[action_index + action_length:]

    # print("action_found", action_found,subject_found,subject_index,action_index, text_parameter)
    return (action_found and subject_found and action_index < subject_index), remove_special_chars_regex(text_parameter)


def execute_plugin_by_keyword(text, *args, **kwargs):
    found = False
    result_text_lower = text.lower().lstrip()
    words_array = [word.strip() for word in re.split(r'[^\w\s]+|(?<=\s)', result_text_lower) if word.strip()]
    words_cleaned = ' '.join(words_array)
    print(result_text_lower, words_array, words_cleaned)

    for plugin in COMMAND_PLUGINS.values():
        if plugin.trigger.lower() != FALL_BACK_COMMAND:
            match, text_parameter = check_strings(words_cleaned, plugin.keywords, raw_text=result_text_lower)
            if match:
                print('running plugin', plugin.trigger.lower())
                plugin.run(*args, text_parameter=text_parameter, raw_text=text, **kwargs)
                found = True
                break

    if not found:
        print(f"No plugin found for text: {text}")
        fallback_plugin = COMMAND_PLUGINS.get(FALL_BACK_COMMAND.lower())
        if fallback_plugin:
            fallback_plugin.run(*args, text_parameter=text, raw_text=text, **kwargs)
        else:
            print("No fallback plugin found.")
