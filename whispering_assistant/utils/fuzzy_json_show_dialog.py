import json
from fuzzywuzzy import fuzz

from whispering_assistant.states_manager.window_manager_messages import message_queue


def process_selected_option_default_cb(selected_text):
    print("selected_text", selected_text)
    return selected_text


def get_display_text(item, name_keys, val_keys):
    name = "Unknown"
    val = "Unknown"

    for key in name_keys:
        if key in item:
            name = item[key]
            break

    for key in val_keys:
        if key in item:
            val = item[key]
            break

    return f"{name} - {val}"


def get_return_value(selected_result, return_keys):
    return_res = None

    for return_key in return_keys:
        if isinstance(selected_result, dict) and return_key in selected_result:
            return_res = selected_result[return_key]
            break

    return return_res


def generate_start_selected_option_cb(return_keys, process_selected_option_cb):
    def start_selected_option_cb(selected_result, return_keys_inner=return_keys):
        return_val = get_return_value(selected_result, return_keys=return_keys_inner)
        process_selected_option_cb(return_val)

    return start_selected_option_cb


def fuzzy_search_json(query,
                      json_files,
                      value_keys,
                      name_keys,
                      return_keys,
                      search_keys,
                      process_selected_option_cb=process_selected_option_default_cb):
    if isinstance(json_files, str):
        json_files = [json_files]

    if isinstance(return_keys, str):
        return_keys = [return_keys]

    all_data = []
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
            all_data.extend(data)

    # Perform fuzzy search on concatenated values of each item
    results = []
    for item in all_data:
        item_string = ' '.join([item[key].lower() for key in search_keys if key in item and isinstance(item[key], str)])
        score = fuzz.token_set_ratio(query.lower(), item_string.lower())
        if score >= 1:
            results.append((item, score))

    # Sort results by descending score
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

    print("sorted_results", sorted_results[0:5])

    if sorted_results and len(sorted_results) > 0:
        top_score = sorted_results[0][1]
        threshold = 10
        top_results = [result for result in sorted_results if abs(result[1] - top_score) <= threshold]
        top_results = top_results[:5]

        if len(top_results) > 1:
            choices = [result[0] for result in top_results]
            print("choices", choices)

            for choice_idx, choice in enumerate(choices):
                display_text = get_display_text(choice, name_keys, value_keys)
                choices[choice_idx]['display_text'] = display_text
            start_selected_option_cb = generate_start_selected_option_cb(return_keys=return_keys,
                                                                         process_selected_option_cb=process_selected_option_cb)
            print("choices", choices)
            message_queue.put(('create_list_box', choices, start_selected_option_cb))
        else:
            # No need to show UI to user just process the highest score
            print("sorted_results[0]", sorted_results[0])
            print("return_keys", return_keys)
            process_selected_option_cb(get_return_value(sorted_results[0][0], return_keys=return_keys))
