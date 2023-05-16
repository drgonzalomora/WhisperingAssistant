import os

from whispering_assistant.utils.commands_plugin_state import COMMAND_PLUGINS
from whispering_assistant.utils.semantic_search_index import generate_index_csv, search_index_csv
from whispering_assistant.utils.vector_embeddings_storage import init_faiss_index

default_intent_index = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/plugin_commands_intents.csv"
faiss_index_file_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/faiss_index_intents.idx"

query_instruction = 'Represent the command intent for retrieving similar examples: '
storing_instruction = 'Represent the command intent examples for retrieval: '

faiss_index, save_faiss_index = init_faiss_index(faiss_index_file_name)
generate_index_for_intent_detection_is_running = False

# 📌 TODO: Add a logic to make sure that we need to create the index if it's not yet existing instead of manually running it and assuming that the index is already created.

intent_list = []


def parse_plugin_commands_examples():
    result = []
    for plugin in COMMAND_PLUGINS.values():
        if plugin and hasattr(plugin, 'examples'):
            for example in plugin.examples:
                result.append([plugin.trigger, example])
    return result


def generate_index_for_intent_detection():
    global faiss_index, save_faiss_index
    global intent_list
    global generate_index_for_intent_detection_is_running

    if generate_index_for_intent_detection_is_running:
        return

    generate_index_for_intent_detection_is_running = True

    intent_list = parse_plugin_commands_examples()

    # List of files to delete if they exist
    files_to_delete = [faiss_index_file_name, default_intent_index]

    # Delete files if they exist
    for file in files_to_delete:
        print(f"Attempting to delete: {file}")
        try:
            if os.path.exists(file):
                os.remove(file)
            else:
                print(f"The file {file} does not exist")
        except Exception as e:
            print(f"Error occurred while trying to remove the file {file}: {e}")

    faiss_index, save_faiss_index = init_faiss_index(faiss_index_file_name)

    for idx, intent_item in enumerate(intent_list):
        id_text_with_index = f"{intent_item[0]}_{idx}"
        generate_index_csv(input_text=intent_item[1], id_text=id_text_with_index, file_name=default_intent_index,
                           faiss_index=faiss_index, save_faiss_index=save_faiss_index,
                           storing_instruction=storing_instruction)

    generate_index_for_intent_detection_is_running = False

def get_intent_from_text(command_text):
    global faiss_index, save_faiss_index
    global intent_list
    intent_list = parse_plugin_commands_examples()

    if not command_text:
        return None, None

    if not os.path.exists(default_intent_index):
        generate_index_for_intent_detection()

    top_result, _ = search_index_csv(command_text, n=1, file_name=default_intent_index, faiss_index=faiss_index,
                                     query_instruction=query_instruction)

    print("top_result", top_result)

    if not top_result:
        return None, None

    top_result_details = None

    for item in intent_list:
        if item and top_result and item[0] in top_result['id_text']:
            top_result_details = item
            break

    if not top_result_details:
        return None, None

    print("top_result_prompt", top_result_details)

    return top_result_details[0], top_result_details


# parse_plugin_commands_examples()
# import whispering_assistant.commands
# generate_index_for_intent_detection()
# get_intent_from_text('shutdown')
