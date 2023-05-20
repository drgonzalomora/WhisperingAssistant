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


def remove_duplicates(strings):
    seen = set()
    result = []
    for string in strings:
        lowercase_string = string.lower()
        if lowercase_string not in seen:
            result.append(string)
            seen.add(lowercase_string)
    return result


def find_related_keywords_from_category_list(input_string, keywords_data, ignore_categories=None):
    if ignore_categories is None:
        ignore_categories = []

    related_keywords = []
    ignored_categories = {}
    triggering_keywords = []

    for category, keywords in keywords_data.items():
        if category.lower() in (category.lower() for category in ignore_categories):
            ignored_categories[category] = keywords
            continue

        # Split each keyword into individual words
        split_keywords = [word.lower() for keyword in keywords for word in keyword.split()]
        split_keywords = remove_duplicates(split_keywords)

        # Check if any word from the split_keywords is present in the input_string
        for word in split_keywords:
            if word in input_string.lower():
                related_keywords.extend(keywords)
                triggering_keywords.append(word)

    related_keywords = remove_duplicates(related_keywords)

    print("trigger_keywords", triggering_keywords)

    return related_keywords, ignored_categories, triggering_keywords


def generate_related_keywords_prompt(input_string):
    print("input_string", input_string)

    keywords_data = load_keywords_from_keyword_yml_file()
    related_keywords, ignored_categories, _ = find_related_keywords_from_category_list(input_string, keywords_data,
                                                                                       ignore_categories=[
                                                                                           'frequent_misspelled'])

    related_keywords_secondary, ignored_categories, _ = find_related_keywords_from_category_list(
        ' '.join(related_keywords), keywords_data,
        ignore_categories=[
            'frequent_misspelled'])

    print("related_keywords_secondary", related_keywords_secondary)
    print("related_keywords", related_keywords)
    frequent_misspelled = ignored_categories['frequent_misspelled']

    final_string = None

    if related_keywords:
        final_string = f"topics about {', '.join(related_keywords + frequent_misspelled + related_keywords_secondary)}. "
        print("final_string", final_string)

    return final_string


def generate_frequent_misspelled_prompt():
    global initial_prompt_cache

    keywords_data = load_keywords_from_keyword_yml_file()
    frequent_misspelled_items = keywords_data.get('frequent_misspelled', [])

    print("frequent_misspelled_items", frequent_misspelled_items)
    final_string = f"topics about {', '.join(frequent_misspelled_items)}. "
    print("frequent_misspelled_items", final_string)
    initial_prompt_cache = final_string

    return final_string

# print(generate_related_keywords_prompt("its so hot"))
