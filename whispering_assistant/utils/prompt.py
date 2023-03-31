import json
import re

def format_variables(variable):
    formatted_variable = ','.join(variable)
    return formatted_variable

def generate_initial_prompt():
    with open('prompt.json', 'r') as file:
        data = json.load(file)

    people_names_formatted = format_variables(data['people_names'])
    project_names_formatted = format_variables(data['project_names'])
    technical_terms_formatted = format_variables(data['technical_terms'])
    initial_prompt_formatted = format_variables(data['initial_prompt'])

    initial_prompt = """
    {}.
    He has projects like: {}.
    He talks to: {}.
    He uses terms related to: {}.
    """.format(initial_prompt_formatted, project_names_formatted, people_names_formatted, technical_terms_formatted)

    initial_prompt = re.sub('\s+', ' ', ' '.join(initial_prompt.split('\n')).strip())
    print("using the prompt: ", initial_prompt)

    return initial_prompt
