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

from whispering_assistant.states_manager import global_var_state
from whispering_assistant.utils.get_most_updated_doc_from_web import get_similar_contexts
from whispering_assistant.utils.tts_test import tts_queue, audio_queue
import json
from datetime import datetime

load_dotenv()
openai.api_key = os.environ.get("openai_key")

global history_list
global input_thread

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

You are authorized to use any available tools at your own discretion. No need to ask for permission!

---

Available Tools:
- SEARCH: use this to do internet search for current events or latest news. make sure to give a comprehensive search query as action input. MAKE SURE to phrase input on a question form always!

---

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Rationale: <think about why you need to use a tool>
Action: <the action to take, should be one of the tools: [SEARCH]>
Draft Input: <the input to the action>
Draft Review: <think if the draft action input is the best input. Remember to make the action input as specific as possible since the tool does not have the context of previous discussions>
Action Input: <refine the action input as needed>
Observation: <the result of the action>

---

When there is an observation, or you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No
Rationale: <think about why you don't need a tool>
Final Answer: <your response here, incorporate results from the tools if you have used any. NO NEED to give disclaimer to the user. DO NOT send code snippets or very long texts to the user. they won't see it as they can only hear what you say. so MAKE SURE that your response is easy to follow without the need for an elaborate text>
"""

history_list = [{"role": "system",
                 "content": role_instruction}]


# This also removes the \n from the history. The problem for that is readability of the promopt
def clean_text(text):
    # Regular expression pattern to match any characters that are not alphanumeric and also not in the approved list of special characters
    pattern = re.compile(r'[^a-zA-Z0-9 _\-:,.|\n`?!\]\[]')
    # Substitute matching characters with an empty string
    cleaned_text = pattern.sub('', text)
    return cleaned_text


def encode_decode_text(text, encoding='utf-8'):
    # Encodes and decodes the text using the provided encoding (default is UTF-8)
    try:
        return_text = text.encode(encoding).decode(encoding)
        return return_text
    except UnicodeDecodeError:
        print(
            "The text contains characters that couldn't be encoded/decoded as {}. Replacing with Unicode Replacement Character.".format(
                encoding))
        return_text = text.encode(encoding, 'replace').decode(encoding, 'replace')
        return return_text


def clear_history_list():
    global history_list
    history_list = [{"role": "system",
                     "content": role_instruction}]


def append_and_remove_spaces_history_list(item, retain_items=7):
    global history_list
    # Append the new item to the list
    history_list.append(item)

    # Clean the text in the messages
    for message in history_list:
        cleaned_text = encode_decode_text(message['content'].strip())
        cleaned_text = clean_text(cleaned_text)
        message['content'] = cleaned_text

    # Check if the history list is larger than the maximum allowed size
    if len(history_list) > retain_items + 1:
        # Start at the retain_items-th last item
        retain_start_index = -retain_items

        # Loop through the list from the end, checking the role of each item
        while history_list[retain_start_index]['role'] != 'user':
            # If the role is not 'user', move one item up
            retain_start_index -= 1

            # If we have reached the first item and haven't found a 'user' role, stop the loop
            if abs(retain_start_index) > len(history_list):
                break

        # Prune the list, keeping the first item and the last retain_items items,
        # ensuring the 2nd item from the top has 'role' as 'user'
        history_list = [history_list[0]] + history_list[retain_start_index:]


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
        input_text_edited = "Answer as best you can. Use a tool at your discretion! Question: " + input_text
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
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message

        if 'content' in chunk_message:
            collected_parsed_messages.append(chunk_message['content'])
            buffer += chunk_message['content']

            # Check if the buffer ends with a stop character, and the character before is an alphabet.
            if re.search(r'[a-zA-Z][.,!:?\n]\s*$', buffer):
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
            action_input = match.group(1).strip()
            print(f'Action Input: {action_input}')
            similar_context_from_web = get_similar_contexts(action_input)

            # 📌 TODO: Make sure to handle if for some reason we only get empty string from the similar context function.
            result_str = "Observation: " + similar_context_from_web.strip() + "\nFinal Answer: "
            print(result_str.strip())

            # We need to add a follow up prompt to make sure we don't get an empty response
            # Follow up is from the user
            askGpt(result_str.strip(), role='assistant')
            observation_sent = True
        else:
            print('No match found. No Action Input')

    # Wait for the worker threads to finish processing all the items in the queues
    tts_queue.join()
    audio_queue.join()

    print("response", response)
    print("collected_messages", collected_parsed_messages)
    print("history_list", history_list)

    observation_sent = False
    return collected_parsed_messages


def should_end_conversation(input_string_lower):
    print("should_end_conversation", input_string_lower)

    end_word_patterns = [r'\bend\b', r'\bconversation\b', r'\bthanks\b', r'\bbye\b']
    matches = [re.search(pattern, input_string_lower, re.IGNORECASE) for pattern in end_word_patterns]

    # count the matches (only consider matched patterns, ignore None)
    match_count = sum(1 for match in matches if match is not None)

    return match_count >= 2  # return True only if at least two matches


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
            time.sleep(0.5)
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
