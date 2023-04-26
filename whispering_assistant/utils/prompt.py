import json
import re
from whispering_assistant.states_manager.window_manager_messages import message_queue
import yaml

initial_prompt_cache = None


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
    with open('/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/prompt.json',
              'r') as file:
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
    with open('/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/prompt.json',
              'r') as file:
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


def load_keywords_from_keyword_yml_file(
        file_path='/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/prompt.yml'):
    with open(file_path, 'r') as file:
        keywords_data = yaml.safe_load(file)
    return keywords_data


def find_related_keywords_from_category_list(input_string, keywords_data, ignore_categories=None):
    if ignore_categories is None:
        ignore_categories = []

    related_keywords = []
    ignored_categories = {}

    for category, keywords in keywords_data.items():
        if category in ignore_categories:
            ignored_categories[category] = keywords
            continue

        if any(keyword.lower() in input_string.lower() for keyword in keywords):
            related_keywords.extend(keywords)

    return related_keywords, ignored_categories


def generate_related_keywords_prompt(input_string):
    keywords_data = load_keywords_from_keyword_yml_file()
    related_keywords, ignored_categories = find_related_keywords_from_category_list(input_string, keywords_data,
                                                                                    ignore_categories=[
                                                                                        'frequent_misspelled'])

    print("related_keywords", related_keywords)
    frequent_misspelled = ignored_categories['frequent_misspelled']
    final_string = f"topics about {', '.join(frequent_misspelled + related_keywords)}."
    print("final_string", final_string)

    return final_string

# generate_related_keywords_prompt('testing the new keyword feature')
