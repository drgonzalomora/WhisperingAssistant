import os

from whispering_assistant.utils.commands_plugin_state import COMMAND_PLUGINS
from whispering_assistant.utils.semantic_search_index import generate_index_csv, search_index_csv
from whispering_assistant.utils.vector_embeddings_storage import init_faiss_index

default_intent_index = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/plugin_commands_intents.csv"
faiss_index_file_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/faiss_index_intents.idx"

query_instruction = 'Represent question for retrieving relevant tool documents: '
query_template = 'What tool to use for this command: "${command}"'

storing_instruction = 'Represent tool descriptions document for retrieval: '

faiss_index, save_faiss_index = init_faiss_index(faiss_index_file_name)
generate_index_for_intent_detection_is_running = False

# 📌 TODO: Add a logic to make sure that we need to create the index if it's not yet existing instead of manually running it and assuming that the index is already created.

intent_list = []


def parse_plugin_main_commands_desc():
    result = []
    for plugin in COMMAND_PLUGINS.values():
        if plugin and hasattr(plugin, 'description'):
            for desc in plugin.description:
                result.append([plugin.trigger, desc])
    return result


def parse_plugin_sub_commands_desc():
    result = []
    for plugin in COMMAND_PLUGINS.values():
        if plugin and hasattr(plugin, 'description_sub_commands'):
            for desc in plugin.description_sub_commands:
                result.append([plugin.trigger, desc])
    return result


def generate_index_for_intent_detection():
    global faiss_index, save_faiss_index
    global intent_list
    global generate_index_for_intent_detection_is_running

    if generate_index_for_intent_detection_is_running:
        return

    generate_index_for_intent_detection_is_running = True

    intent_list = parse_plugin_main_commands_desc()
    sub_intent_list = parse_plugin_sub_commands_desc()

    faiss_index, save_faiss_index = init_faiss_index(faiss_index_file_name)

    for idx, intent_item in enumerate(intent_list):
        id_text_with_index = f"{intent_item[0]}_{idx}_main"
        generate_index_csv(input_text=intent_item[1], id_text=id_text_with_index, file_name=default_intent_index,
                           faiss_index=faiss_index, save_faiss_index=save_faiss_index,
                           storing_instruction=storing_instruction)

    for idx, intent_item in enumerate(sub_intent_list):
        id_text_with_index = f"{intent_item[0]}_{idx}_sub"
        generate_index_csv(input_text=intent_item[1], id_text=id_text_with_index, file_name=default_intent_index,
                           faiss_index=faiss_index, save_faiss_index=save_faiss_index,
                           storing_instruction=storing_instruction)

    generate_index_for_intent_detection_is_running = False


def get_intent_from_text(command_text):
    global faiss_index, save_faiss_index
    global intent_list
    intent_list = parse_plugin_main_commands_desc()

    if not command_text:
        return None, None

    if not os.path.exists(default_intent_index):
        generate_index_for_intent_detection()

    search_text = query_template.replace("${command}", command_text)
    _, top_3_results = search_index_csv(search_text, n=3, file_name=default_intent_index,
                                        faiss_index=faiss_index,
                                        query_instruction=query_instruction)

    print("top_3_results", top_3_results)

    top_result_filtered = None

    for result in top_3_results:
        if '_main' in result['id_text']:
            if result['similarity'] > 0.899:
                top_result_filtered = result
        elif '_sub' in result['id_text']:
            if result['similarity'] > 0.92:
                top_result_filtered = result

    print("🎯 top_result_filtered", top_result_filtered)

    if not top_result_filtered:
        return None, None

    top_result_details = None

    for item in intent_list:
        if item and top_result_filtered and item[0] in top_result_filtered['id_text']:
            top_result_details = item
            break

    if not top_result_details:
        return None, None

    print("top_result_prompt", top_result_details[0])

    return top_result_details[0], top_result_filtered

# parse_plugin_commands_examples()
# import whispering_assistant.commands
# generate_index_for_intent_detection()
# get_intent_from_text('shutdown')
