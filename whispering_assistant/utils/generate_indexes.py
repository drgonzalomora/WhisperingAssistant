import os

from whispering_assistant.utils.command_intent_detection import faiss_index_file_name, default_intent_index, \
    generate_index_for_intent_detection
from whispering_assistant.utils.embeddings_cache import query_embeddings_cache_db_name, create_embedding_database
from whispering_assistant.utils.gpt_prompt_injections import faiss_index_file_name_gpt_prompt_templates, \
    default_csv_prompts_gpt_prompt_templates

# List of files to delete if they exist
files_to_delete = [query_embeddings_cache_db_name,
                   faiss_index_file_name,
                   faiss_index_file_name_gpt_prompt_templates,
                   default_csv_prompts_gpt_prompt_templates,
                   default_intent_index]

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

create_embedding_database()

import whispering_assistant.commands
generate_index_for_intent_detection()
