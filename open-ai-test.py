# Example of an OpenAI ChatCompletion request with stream=True
# https://platform.openai.com/docs/guides/chat
import os
import threading
import time

import openai

from tts_test import tts_chunk_by_chunk, tts_queue, SENTINEL, audio_queue

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

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

    buffer = []
    for chunk in response:
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message
        if 'content' in chunk_message:
            collected_parsed_messages.append(chunk_message['content'])
            buffer.append(chunk_message['content'])

        if len(buffer) >= 20:  # Once there are 3 or more items, print them
            result_buffer = "".join(buffer)
            print("🗣️", result_buffer)  # print all messages in the buffer
            # Add the buffer to the TTS queue
            tts_queue.put((result_buffer, buffer.clear))
            buffer = []  # reset the buffer

    # Check for any remaining items in the buffer after the loop
    if buffer:
        result_buffer = "".join(buffer)
        # Add the buffer to the TTS queue
        print("🗣️", result_buffer)
        tts_queue.put((result_buffer, buffer.clear))

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


def process_input(input_string_inner):
    result = askGpt(input_string_inner)
    return result


global input_thread

# Create a thread to handle user input and start it
input_string = input("Please enter the string to pass to the function: ")
input_thread = threading.Thread(target=process_input, args=(input_string,), daemon=True)
input_thread.start()

# Main loop
while True:
    # If the input thread is not alive (i.e., it has finished processing the last input),
    # ask the user for a new input and start a new input thread
    if not input_thread.is_alive():
        input_string = input("Please enter the string to pass to the function: ")
        input_thread = threading.Thread(target=process_input, args=(input_string,), daemon=True)
        input_thread.start()

    # Let's not hog the CPU
    time.sleep(0.1)
