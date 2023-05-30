# Example of an OpenAI ChatCompletion request with stream=True
# https://platform.openai.com/docs/guides/chat
import os
import re
import threading
import time
import openai
from dotenv import load_dotenv
import queue
import requests
from duckduckgo_search import DDGS

from whispering_assistant.states_manager import global_var_state
from whispering_assistant.utils.tts_test import tts_queue, SENTINEL, audio_queue
import json
from datetime import datetime

load_dotenv()
openai.api_key = os.environ.get("openai_key")

global history_list

# 📌 TODO:
# - Save History to a file on every response
# - I need to filter out the history list to make sure that it won't go over the maximum number of tokens.
# - Clean up the locally created transcriptions so that it don't get large over time.

# This is too strict not saving anything
# https://github.com/hwchase17/langchain/blob/99a1e3f3a309852da989af080ba47288dcb9a348/langchain/agents/conversational/prompt.py#L35
# Currently the best system role prompt based on my tests
role_instruction = """
Assistant is a large language model trained by OpenAI.
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

---

TOOLS:
- SEARCH: use this to search for current events or latest news from the internet

---

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of the tools: [SEARCH]
Action Input: the input to the action
Observation: the result of the action

---

When you have an observation, or you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No
Final Answer: [your response here, you make sure to reply with brief, to-the-point answers with no elaboration]
"""

history_list = [{"role": "system",
                 "content": role_instruction}, {"role": "user",
                                                "content": "Begin!"}]


# This also removes the \n from the history. The problem for that is readability of the promopt
def clean_text(text):
    # Regular expression pattern to match any characters that are not alphanumeric and also not in the approved list of special characters
    pattern = re.compile(r'[^a-zA-Z0-9 _\-:,.|]')
    # Substitute matching characters with an empty string
    cleaned_text = pattern.sub('', text)
    return cleaned_text


def encode_decode_text(text, encoding='utf-8'):
    # Encodes and decodes the text using the provided encoding (default is UTF-8)
    try:
        text = text.encode(encoding, 'ignore').decode(encoding)
    except UnicodeDecodeError:
        print("The text could not be encoded/decoded as {}.".format(encoding))
        return None
    return text


def clear_history_list():
    global history_list
    history_list = [{"role": "system",
                     "content": role_instruction}, {"role": "user",
                                                    "content": "Begin!"}]


def append_and_remove_spaces_history_list(item):
    global history_list
    history_list.append(item)

    for message in history_list:
        cleaned_text = encode_decode_text(message['content'].strip())
        cleaned_text = clean_text(cleaned_text)
        message['content'] = cleaned_text


def get_filename():
    # Get the current time
    now = datetime.now()

    # Use floor division to get the minute part to change every two minutes
    minute = now.minute // 2 * 2

    # Create the formatted datetime string without seconds
    formatted_date_time = now.strftime(f"%Y_%m_%d-%H_{minute:02d}")

    # Create filename
    return f'history_list_{formatted_date_time}.json'


observation_sent = False
open_ai_req_counter = 0


# 📌 Remove Extra spaces on the inputs
# Only add observation not results
# Make sure that the response from Final answer completion does not contain the stop word
# Check Top P if same on open ai playground
# See history_list_2023_05_30-16_32.json
# Only Cut by words, don't cut mid way.

def askGpt(input_text, role="user"):
    global observation_sent, open_ai_req_counter
    # record the time before the request is sent
    start_time = time.time()

    if 'user' in role:
        input_text_edited = "Answer as best you can. Question: " + input_text
    else:
        input_text_edited = input_text

    # send a ChatCompletion request to count to 100

    append_and_remove_spaces_history_list({'role': role, 'content': input_text_edited})

    open_ai_req_counter = open_ai_req_counter + 1
    print("✅ open_ai_req_counter", open_ai_req_counter)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=history_list,
        temperature=0,
        stop=['Observation:'],
        stream=True  # again, we set stream=True
    )

    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []
    collected_parsed_messages = []
    # iterate through the stream of events

    buffer = ""

    def buffer_clear():
        global buffer
        buffer = ""

    # 📌 TODO: Skip if the model is thinking

    # 📌 TODO: Watch out from the stream about the [SEARCH] action

    for chunk in response:
        print('⏭️chunk', chunk)
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message

        if 'content' in chunk_message:
            collected_parsed_messages.append(chunk_message['content'])
            buffer += chunk_message['content']

            # Check if the buffer ends with a stop character.
            if re.search(r'[.,!:?]\s*$', buffer):
                print("🗣️", buffer)  # print all messages in the buffer
                # Add the buffer to the TTS queue
                tts_queue.put((buffer, buffer_clear))
                buffer = ""  # reset the buffer

    # Check for any remaining items in the buffer after the loop
    if buffer:
        result_buffer = "".join(buffer)
        # Add the buffer to the TTS queue
        print("🗣️", result_buffer)
        tts_queue.put((result_buffer, buffer_clear))

    print("collected_parsed_messages", collected_parsed_messages)

    collected_parsed_messages_str = "".join(collected_parsed_messages)

    print("collected_parsed_messages", collected_parsed_messages_str)

    append_and_remove_spaces_history_list({'role': 'assistant', 'content': collected_parsed_messages_str})

    filename = get_filename()

    # Save history_list in json format
    with open(filename, 'w') as f:
        json.dump(history_list, f, indent=4)

    if 'Action Input:' in collected_parsed_messages_str and not observation_sent:
        print('🔎 Need to perform a search')
        # API call
        match = re.search(r'Action Input: ?"?(.*?)"?$', collected_parsed_messages_str, re.MULTILINE)
        if match:
            action_input = match.group(1).strip()  # Use strip() to remove leading/trailing whitespaces
            print(f'Action Input: {action_input}')
            ddgs_text_gen = DDGS().text(action_input, backend="api")
            snippets = [result["body"] for result in ddgs_text_gen]
            first_10_res_str = " -- ".join(snippets)[:768]

            result_str = f"""
            Observation: {first_10_res_str}
            """

            print(result_str.lstrip())

            time.sleep(0.1)
            askGpt(result_str.lstrip(), role='assistant')
            observation_sent = True
        else:
            print('No match found.')

    # Wait for the worker threads to finish processing all the items in the queues
    print("1")
    tts_queue.join()
    print("2")
    audio_queue.put(SENTINEL)
    print("3")
    audio_queue.join()
    print("4")

    print("response", response)
    print("collected_messages", collected_parsed_messages)

    print("history_list", history_list)

    observation_sent = False
    return collected_parsed_messages


global input_thread


def should_end_conversation(input_string_lower):
    print("should_end_conversation", input_string_lower)

    end_word_patterns = [r'\bend\b', r'\bconversation\b', r'\bthanks\b', r'\bbye\b']
    return any(re.search(pattern, input_string_lower, re.IGNORECASE) for pattern in end_word_patterns)


def process_input(input_queue_local):
    while True:
        end_conversation = False
        input_string = input_queue_local.get()
        input_string_lower = input_string.lower()

        # Your processing code here
        print(f'Processing input: {input_string}')

        if should_end_conversation(input_string_lower):
            end_conversation = True

        if input_string and not end_conversation:
            askGpt(input_string)

        # Indicate that a formerly enqueued task is complete
        input_queue.task_done()
        print(f'✅ Task Done: {input_string}')

        if not end_conversation:
            requests.get("http://127.0.0.1:6969")

        if end_conversation:
            clear_history_list()
            global_var_state.continuous_conversation_mode = False

        # Let's not hog the CPU
        time.sleep(0.1)


# Create a queue to communicate between the threads
input_queue = queue.Queue()

# Start the thread that processes input
input_thread = threading.Thread(target=process_input, args=(input_queue,), daemon=True)
print("starting input thread")
input_thread.start()

# Wait for both threads to complete
# input_thread.join()
