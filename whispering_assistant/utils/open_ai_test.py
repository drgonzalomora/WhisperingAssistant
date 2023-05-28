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


from whispering_assistant.utils.tts_test import tts_queue, SENTINEL, audio_queue

load_dotenv()
openai.api_key = os.environ.get("openai_key")

global history_list

# 📌 TODO:
# - I need to filter out the history list to make sure that it won't go over the maximum number of tokens.
# - Clean up the locally created transcriptions so that it don't get large over time.
# - Add the ability to search the web using the DuckDuckGo plugin.
# - Connect to whisper


history_list = [{"role": "system",
                 "content": "You are a laconic assistant. You reply with brief, to-the-point answers with no elaboration. BUT have atleast 5 words of a reply to be more fun"}]


def askGpt(input_text):
    # record the time before the request is sent
    start_time = time.time()

    # send a ChatCompletion request to count to 100

    history_list.append({'role': 'user', 'content': input_text})

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=history_list,
        temperature=0,
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

    for chunk in response:
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message

        if 'content' in chunk_message:
            collected_parsed_messages.append(chunk_message['content'])
            buffer += chunk_message['content']

            # Check if the buffer ends with a stop character.
            if re.search(r'[.,!?]\s*$', buffer):
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

    history_list.append({'role': 'assistant', 'content': "".join(collected_parsed_messages)})

    print("history_list", history_list)

    return collected_parsed_messages


global input_thread


def process_input(input_queue_local):
    while True:
        end_conversation = False
        input_string = input_queue_local.get()

        # Your processing code here
        print(f'Processing input: {input_string}')

        if 'end' in input_string and 'conversation' in input_string:
            end_conversation = True

        if input_string and not end_conversation:
            askGpt(input_string)

        # Indicate that a formerly enqueued task is complete
        input_queue.task_done()
        print(f'✅ Task Done: {input_string}')

        # Let's not hog the CPU
        time.sleep(0.1)

        # 📌 TODO: Continue the conversation until otherwise ended
        if not end_conversation:
            requests.get("http://127.0.0.1:6969")


# Create a queue to communicate between the threads
input_queue = queue.Queue()

# Start the thread that processes input
input_thread = threading.Thread(target=process_input, args=(input_queue,), daemon=True)
print("starting input thread")
input_thread.start()

# Wait for both threads to complete
# input_thread.join()
