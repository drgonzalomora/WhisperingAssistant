import os
import re

from whispering_assistant.utils.semantic_search_index import generate_index_csv, search_index_csv
from whispering_assistant.utils.vector_embeddings_storage import init_faiss_index

default_csv_prompts = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/gpt_prompt_templates.csv"
default_md_prompts = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/gpt_prompt_templates.md"
faiss_index_file_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/faiss_index.idx"

query_instruction = 'Represent the prompt name for retrieving supporting documents: '
storing_instruction = 'Represent the prompt description document for retrieval: '

faiss_index, save_faiss_index = init_faiss_index(faiss_index_file_name)
print("faiss_index", faiss_index.ntotal)


def parse_markdown(markdown=default_md_prompts):
    markdown_content = None

    with open(markdown, "r") as f:
        markdown_content = f.read()

    if not markdown_content:
        return None

    sections = re.split(r'\n---\n', markdown_content.strip())
    parsed_sections = []

    for section in sections:
        lines = section.strip().split('\n')
        title = lines[0][2:].strip()
        desc = re.search(r'(?<=\*\*desc:\*\*)\s*(.+)', section).group(1).strip()
        input_required = re.search(r'(?<=\*\*input_required:\*\*)\s*(.+)', section).group(1).strip()
        prompt = re.search(r'(?<=```\n)(.+)(?=\n```)', section, re.DOTALL).group(1).strip()

        parsed_sections.append({
            'title': title,
            'desc': desc,
            'input_required': input_required == 'true',
            'prompt': prompt
        })

    # pp = pprint.PrettyPrinter(indent=4)
    # pprint.pprint(parsed_sections)

    return parsed_sections


prompt_list = parse_markdown()


def generate_index_prompt_for_injection():
    global prompt_list

    prompt_list = parse_markdown()

    for prompt_item in prompt_list:
        generate_index_csv(input_text=prompt_item['desc'], id_text=prompt_item['title'], file_name=default_csv_prompts,
                           faiss_index=faiss_index, save_faiss_index=save_faiss_index,
                           storing_instruction=storing_instruction)


def get_prompt_for_injection(search_text):
    if not search_text:
        return None, None

    if not os.path.exists(default_csv_prompts):
        generate_index_prompt_for_injection()

    print("search_text", search_text)
    top_result, _ = search_index_csv(search_text, n=1, file_name=default_csv_prompts, faiss_index=faiss_index,
                                     query_instruction=query_instruction)

    if not top_result:
        return None, None

    top_result_details = None

    for item in prompt_list:
        if item and top_result and item['title'] == top_result['id_text']:
            top_result_details = item
            break

    print("top_result_prompt", top_result_details['prompt'])

    return top_result_details['prompt'], top_result_details

# parse_markdown()
# generate_index_prompt_for_injection()
# get_prompt_for_injection('create a checklist with the following context')
