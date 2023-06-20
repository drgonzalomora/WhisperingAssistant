import time
import pyclip
from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.clipboard_manager import typingViaClipBoardHandler
from whispering_assistant.utils.gpt_prompt_injections import parse_markdown
import difflib

GPT3_ALIAS = 'ruby'
GPT4_ALIAS = 'nora'
chatgpt_link_gpt3 = "https://chat.openai.com/chat?model=text-davinci-002-render-sha"
chatgpt_link_gpt4 = "https://chat.openai.com/chat?model=gpt-4"
root_dir = "../assets/images"

# Define the region to search in
x1, y1, width1, height1 = 0, 0, 3840, 130
region1 = (x1, y1, width1, height1)
image1_chat_logo = f'{root_dir}/CHAT_LOGO.png'

x2, y2, width2, height2 = 630, 0, 3840, 1200
region2 = (x2, y2, width2, height2)
image2_chat_box = f'{root_dir}/CHAT_BOX.png'

x3, y3, width3, height3 = 0, 0, 3840, 500
region3 = (x1, y1, width1, height1)
image3_gpt4_url = f'{root_dir}/CHAT_GPT4_URL.png'

x4, y4, width4, height4 = 630, 0, 3840, 1800
region4 = (x4, y4, width4, height4)
image4_chat_down_arrow = f'{root_dir}/CHAT_DOWN_ARROW.png'


def generate_examples_of_prompt_injections():
    def get_all_descriptions(parsed_markdown):
        return [section.get('desc', '') for section in parsed_markdown]

    list_md = parse_markdown()
    # print(list_md)
    all_sample_commands = get_all_descriptions(list_md)

    # print(all_sample_commands)

    def append_names_to_commands(commands, names=None):
        if names is None:
            names = [GPT3_ALIAS, GPT4_ALIAS]
        return [command.replace("{assistant_name}", name) for name in names for command in commands]

    updated_commands = append_names_to_commands(all_sample_commands)
    # print(updated_commands)

    return updated_commands


def send_question_to_gpt(query, new_conversation=False, gpt_type='GPT3', check_gpt_type=False):
    import pyautogui
    new_conversation_2 = new_conversation
    chatgpt_link = chatgpt_link_gpt4 if 'GPT4' in gpt_type else chatgpt_link_gpt3

    # Press CTRL-ALT-SHIFT-Q to activate chrome with GPT
    pyautogui.hotkey('ctrl', 'alt', 'shift', 'q')
    print("CTRL-ALT-SHIFT-Q pressed.")
    time.sleep(1)

    if check_gpt_type:
        image3_location = pyautogui.locateOnScreen(image3_gpt4_url,  confidence=0.90)
        print("image3_location", image3_location)
        if image3_location is None:
            print("❌ CHAT GPT 4 not found on the screen.")
            new_conversation_2 = True

    if new_conversation_2:
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.3)
        typingViaClipBoardHandler.run_thread(chatgpt_link, 'enter')
        time.sleep(2)

    # Check if image1_chat_logo exists on the screen
    image1_location = pyautogui.locateOnScreen(image1_chat_logo,  confidence=0.8)

    if image1_location is not None:
        print(f"Image 1 found at {image1_location}")

        # Look for image2_chat_box on the screen
        image2_location = pyautogui.locateOnScreen(image2_chat_box,  confidence=0.5)

        if image2_location is not None:
            print(f"Image 2 found at {image2_location}")

            # Click in the center of image2_chat_box
            image2_center = pyautogui.center(image2_location)
            pyautogui.click(image2_center)

            # Type the string
            old_clipboard = pyclip.paste()
            pyclip.copy(query.lstrip())
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
            pyclip.copy(old_clipboard)
            time.sleep(0.5)

            # Press the enter key
            pyautogui.press('enter')
            print("Typing and pressing enter done.")

            time.sleep(0.5)
            image4_location = pyautogui.locateOnScreen(image4_chat_down_arrow,  confidence=0.80)

            if image4_location is not None:
                image4_center = pyautogui.center(image4_location)
                pyautogui.click(image4_center)
            else:
                print("Image 4 not found on the screen.")

        else:
            print("Image 2 not found on the screen.")
            send_question_to_gpt(query, new_conversation=True, gpt_type=gpt_type, check_gpt_type=check_gpt_type)
    else:
        print("❌ Image 1 logo not found on the screen.")


def get_best_match(query, items):
    """
    Helper function to get the best match for a query from a list of items.
    """
    sample_commands = [item['desc'] for item in items]
    match = difflib.get_close_matches(query, sample_commands, n=1, cutoff=0.85)

    print("match", match)

    # If there is a match
    if match:
        match_command = match[0]
        for item in items:
            if match_command in item['desc']:
                return item
    else:
        return None


class TalkGPTWithClipboardContext(BaseCommand):
    sub_commands_for_prompt_injection = generate_examples_of_prompt_injections()
    list_md = parse_markdown()
    trigger = "talk_gpt_with_clipboard_context"
    command_type = command_types['CHAINABLE_LONG']
    keywords = {
        "action": ["relation", "clipboard", "context", "question"],
        "subject": ["nora", "ruby"]
    }
    keyword_match = 'send relation nora'
    description = [
        "use the following tool for asking requests to nora with context or relation. command usually starts with 'send relation to nora' or 'send context to nora'"
    ]
    description_sub_commands = sub_commands_for_prompt_injection
    required_keywords = ['ruby', 'nora']
    examples = [
        'ask question to nora',
        'send relation to nora',
        'give context to nora',
        'talk to nora',
        'ask question to ruby',
        'send relation to ruby',
        'give context to ruby',
        'talk to ruby',
    ]

    def run(self, text_parameter, raw_text, command_intent=None, *args, **kwargs):
        modified_text = text_parameter
        raw_text_for_ingestion = raw_text

        chatgpt_type = 'GPT4' if GPT4_ALIAS in raw_text.lower() else 'GPT3'
        resume_keywords = ['continue', 'resume']
        clipBoard_keywords = ['clipboard', 'context', 'relation']

        only_resume_conversation = any(keyword in raw_text.lower() for keyword in resume_keywords)
        check_gpt_type = True if not only_resume_conversation else False
        curr_clipboard = None

        prompt_template = None

        if command_intent:
            print("💖 command_intent", command_intent)
            print("💖 input_text", command_intent['input_text'])

            best_match = get_best_match(query=command_intent['input_text'], items=self.list_md)
            print("best_match", best_match)

            if best_match and 'prompt' in best_match:
                prompt_template = best_match['prompt']

        # TODO: If the prompt requires the context, we just add the keyword context so we execute the same code as before.
        # Right now we're just assuming that all prompt injections requires a copy of the clipboard.
        if prompt_template:
            raw_text_for_ingestion = raw_text_for_ingestion + "(use the context)"

        clipboard_needed = any(keyword in raw_text_for_ingestion.lower() for keyword in clipBoard_keywords)

        # Handle Clipboard injection
        if clipboard_needed:
            curr_clipboard = pyclip.paste()
            modified_text = curr_clipboard
            print("curr_clipboard", curr_clipboard)
            curr_clipboard = "Context:\n" + "```\n" + curr_clipboard.decode('utf-8') + "\n```\n"

            if text_parameter:
                modified_text = curr_clipboard + text_parameter

        if prompt_template:
            modified_text = prompt_template.replace('[PROMPT]', text_parameter)

            if curr_clipboard:
                modified_text = modified_text + '\n\n' + curr_clipboard

        send_question_to_gpt(modified_text, gpt_type=chatgpt_type, check_gpt_type=check_gpt_type)
