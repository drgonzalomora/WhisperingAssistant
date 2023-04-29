import pprint
import re


def parse_markdown(markdown="/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/gpt_prompt_templates.md"):
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

# parse_markdown()