import json
import re
from whispering_assistant.states_manager.window_manager_messages import message_queue


def format_variables(variable):
    formatted_variable = ','.join(variable)
    return formatted_variable

def format_variables(variable):
    formatted_variable = ','.join(variable)
    return formatted_variable

def flatten_list(nested_list):
    return [item for sublist in nested_list for item in sublist]

def unique_list_elements(input_list):
    return list(set(input_list))

def unique_words_in_list(items):
    words_list = [item.split() for item in items]
    flattened_words_list = flatten_list(words_list)
    return unique_list_elements(flattened_words_list)


def generate_initial_prompt():
    with open('prompt.json', 'r') as file:
        data = json.load(file)

    people_names_formatted = format_variables(data['people_names'])
    project_names_formatted = format_variables(data['project_names'])
    technical_terms_formatted = format_variables(data['technical_terms'])
    initial_prompt_formatted = data['initial_prompt']

    initial_prompt = """
    {}.
    He has projects like: {}.
    He talks to: {}.
    He uses terms related to: {}.
    """.format(initial_prompt_formatted, project_names_formatted, people_names_formatted, technical_terms_formatted)

    initial_prompt = re.sub('\s+', ' ', ' '.join(initial_prompt.split('\n')).strip())
    print("using the prompt: ", initial_prompt)

    return initial_prompt


def generate_prompt():
    global initial_prompt_cache
    with open('prompt.json', 'r') as file:
        data = json.load(file)

    people_names_formatted = format_variables(unique_words_in_list(data['people_names']))
    project_names_formatted = format_variables(unique_words_in_list(data['project_names']))
    technical_terms_formatted = format_variables(unique_words_in_list(data['technical_terms']))

    initial_prompt = """
    transcript about:
    people: {} --
    projects: {} --
    jargons: {}
    """.format(people_names_formatted, project_names_formatted, technical_terms_formatted)

    initial_prompt = re.sub('\s+', ' ', ' '.join(initial_prompt.split('\n')).strip())
    print("📌 Using the prompt:", initial_prompt)

    words_and_commas = re.findall(r'\w+|,', initial_prompt)
    unique_words_and_commas = list(set(words_and_commas))
    word_count = len(unique_words_and_commas)
    print("word count: ", word_count)

    if word_count > 150:
        print("❌ Please reduce prompt word count.", "Current word count is:", word_count)

    initial_prompt_cache = initial_prompt
    return initial_prompt


def add_new_prompt():
    message_queue.put(('create_input_box',))


def get_prompt_cache():
    global initial_prompt_cache
    return initial_prompt_cache


# 📌 TODO Change the initial prompt based on the context-aware prompt done on the first transcription
def get_context_aware_prompt():
    return 'sample commands: pycharm, dictation mode, open link, short command, continuous mode'

# generate_prompt()
