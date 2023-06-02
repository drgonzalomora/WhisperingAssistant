import re
import threading
from queue import Queue

import inflect
from playsound import playsound
import time

from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
from datasets import load_dataset

# https://github.com/microsoft/SpeechT5/issues/8 more fine-tuned model
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

# Define a special sentinel value
SENTINEL = 'STOP'


def reword_to_make_it_easier_to_pronounce(s):
    p = inflect.engine()
    words = s.split()
    new_words = []
    for word in words:
        if word.replace('.', '').isdigit():  # Check if the word is a number
            if '.' in word:  # Handle decimal number
                whole, decimal = word.split('.')
                whole_word = p.number_to_words(whole)
                decimal_word = ' '.join([p.number_to_words(i) for i in decimal])
                # Handle Number ranges like 20-30
                new_words.append(f"{whole_word} point {decimal_word}")
            else:  # Handle whole number
                new_words.append(p.number_to_words(word))
        elif word.isupper() and len(word) > 1:  # Check if the word is an abbreviation
            new_words.append(' '.join(list(word)) + ' ')
        else:
            new_words.append(word)
    return ' '.join(new_words)


# Define a function to split text into chunks of a certain number of words
def split_into_chunks(text, max_words):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield ' '.join(words[i:i + max_words])


# Define a function to generate speech
def generate_speech(i, chunk, queue):
    # Get the model input for this chunk

    # Generate the speech audio for this chunk
    start_time = time.time()
    # sample = TTSHubInterface.get_model_input(task, chunk)
    # wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)
    inputs = processor(text=chunk, return_tensors="pt")
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    end_time = time.time()

    print(f'✅ Text-to-speech generation for chunk {i + 1} took {end_time - start_time} seconds')

    # Save the output wav file for this chunk
    output_file = f'tts_output_{i + 1}.wav'
    sf.write(output_file, speech.numpy(), samplerate=16000)
    # sf.write(output_file, wav, rate)

    # Put the filename into the queue
    queue.put(output_file)


# Define a function to play audio
def play_audio(queue):
    while True:
        # Wait for a filename to be added to the queue
        output_file = queue.get()

        # Break the loop if the sentinel value is seen
        if output_file == SENTINEL:
            break

        # Play the audio file
        playsound(output_file)


def contains_only_special_characters(string):
    pattern = r"^[^\w\s]*$"  # \w matches any word character (equal to [a-zA-Z0-9_]), \s matches any whitespace character (spaces, tabs, line breaks)
    match = re.match(pattern, string)
    return match is not None


# TODO: We should convert numbers to word numbers since model cannot pronounce

def tts_chunk_by_chunk(input_text, callback=None, prefix="", word_limit=5):
    # Split the input text into words
    words = input_text.split()

    # Buffer for accumulating words
    buffer = []

    # List to hold chunks
    chunks = []

    for word in words:
        # Add word to buffer
        buffer.append(word)

        # this should make sure not to make number figures harder to read
        # If a stop character is found or the word limit is reached, create a chunk
        if re.search(r'[.,!?\n]$', word) or len(buffer) == word_limit:
            chunks.append(" ".join(buffer))
            # Clear the buffer
            buffer = []

    # If there are remaining words in the buffer after processing all words, add them as a chunk
    if buffer:
        chunks.append(" ".join(buffer))

    # Process each chunk
    for i, chunk in enumerate(chunks):
        chunk_ingest = reword_to_make_it_easier_to_pronounce(chunk.strip())
        print(f'Processing chunk {i + 1} of {len(chunks)}')

        print("chunk_ingest", chunk_ingest)

        if chunk_ingest and not contains_only_special_characters(chunk_ingest):
            # Get the model input for this chunk
            # sample = TTSHubInterface.get_model_input(task, chunk_ingest)

            # Generate the speech audio for this chunk
            start_time = time.time()
            inputs = processor(text=chunk_ingest, return_tensors="pt")
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
            end_time = time.time()

            print(f'Text-to-speech generation for chunk {i + 1} took {end_time - start_time} seconds')

            # Save the output wav file for this chunk
            output_file = f'tts_output_{prefix}_{i + 1}.wav'
            sf.write(output_file, speech.numpy(), samplerate=16000)
            # sf.write(output_file, wav, rate)

            # Add the filename to the audio queue
            audio_queue.put(output_file)

    # Call the callback function if it was provided
    if callback is not None:
        callback()


# 🚥🚥🚥

# Create two queues: one for text-to-speech conversion and another for playing audio files
tts_queue = Queue()
audio_queue = Queue()


def tts_worker():
    while True:
        # Wait for a chunk of text to be added to the queue
        text, callback = tts_queue.get()
        prefix = str(time.time())
        print('🎯 text for TTS', text)

        # Process the text
        tts_chunk_by_chunk(text, callback=callback, prefix=prefix)

        # Mark the task as done
        tts_queue.task_done()

        # Let's not hog the CPU
        time.sleep(0.1)


def audio_worker():
    while True:
        # Wait for a filename to be added to the queue
        output_file = audio_queue.get()

        if output_file:
            playsound(output_file)

        # Mark the task as done
        audio_queue.task_done()

        # Let's not hog the CPU
        time.sleep(0.1)


# Start the worker threads
print("starting tts worker")
tts_worker_thread = threading.Thread(target=tts_worker, daemon=True)
tts_worker_thread.start()

print("starting audio worker")
audio_worker_thread = threading.Thread(target=audio_worker, daemon=True)
audio_worker_thread.start()
