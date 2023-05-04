from whispering_assistant.states_manager.window_manager_messages import message_queue
import yaml

initial_prompt_cache = None


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

        # Split each keyword into individual words
        split_keywords = [word.lower() for keyword in keywords for word in keyword.split()]

        # Check if any word from the split_keywords is present in the input_string
        if any(word in input_string.lower() for word in split_keywords):
            related_keywords.extend(keywords)

    return related_keywords, ignored_categories


def generate_related_keywords_prompt(input_string):
    print("input_string", input_string)

    keywords_data = load_keywords_from_keyword_yml_file()
    related_keywords, ignored_categories = find_related_keywords_from_category_list(input_string, keywords_data,
                                                                                    ignore_categories=[
                                                                                        'frequent_misspelled'])

    print("related_keywords", related_keywords)
    frequent_misspelled = ignored_categories['frequent_misspelled']

    final_string = None

    if related_keywords:
        final_string = f"topics about {', '.join(frequent_misspelled + related_keywords)}."
        print("final_string", final_string)

    return final_string


def generate_frequent_misspelled_prompt():
    global initial_prompt_cache

    keywords_data = load_keywords_from_keyword_yml_file()
    frequent_misspelled_items = keywords_data.get('frequent_misspelled', [])

    print("frequent_misspelled_items", frequent_misspelled_items)
    final_string = f"topics about {', '.join(frequent_misspelled_items)}."
    print("frequent_misspelled_items", final_string)
    initial_prompt_cache = final_string

    return final_string


# print(generate_related_keywords_prompt("its so hot"))
