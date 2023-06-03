import os
import re
import threading
from queue import Queue

import inflect
import time

from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
from datasets import load_dataset

from pydub import AudioSegment
from pydub.playback import play

# https://github.com/microsoft/SpeechT5/issues/8 more fine-tuned model
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7533]["xvector"]).unsqueeze(0)

def reword_to_make_it_easier_to_pronounce(s):
    p = inflect.engine()
    words = s.split()
    new_words = []

    def number_to_word(num_str):
        parts = num_str.split('.')
        whole_word = p.number_to_words(parts[0])
        decimal_word = ' point '.join([p.number_to_words(i) for i in parts[1:]]) if len(parts) > 1 else ''
        return f"{whole_word}{decimal_word}"

    for word in words:
        clean_word = word.replace('.', '')
        if clean_word.isdigit():  # Check if the word is a number
            if word.endswith('.'):  # Handle ordinal numbers
                ordinal_word = p.number_to_words(clean_word, ordinal=True)
                new_words.append(ordinal_word)
            else:
                new_words.append(number_to_word(word))
        elif re.match('^[0-9]+[A-Za-z]+$', clean_word):  # Handle labels with digits and letters
            label_word = ' '.join([p.number_to_words(i) if i.isdigit() else i for i in clean_word])
            new_words.append(label_word)
        elif re.match('^[A-Za-z][0-9\.]+$', clean_word):  # Handle words starting with a letter followed by a number
            new_words.append(f"{word[0]} {number_to_word(word[1:])}")
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


def contains_only_special_characters(string):
    pattern = r"^[^\w\s]*$"  # \w matches any word character (equal to [a-zA-Z0-9_]), \s matches any whitespace character (spaces, tabs, line breaks)
    match = re.match(pattern, string)
    return match is not None


# TODO: We should convert numbers to word numbers since model cannot pronounce

def tts_chunk_by_chunk(input_text, callback=None, word_limit=7):
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

        # Output file is based on chunk_ingest
        # Remove special characters and replace spaces with underscores and Create the output file name
        safe_filename = re.sub(r'\W+', '', chunk_ingest.replace(' ', '_'))
        chunk_ingest_output_filename = safe_filename + '.wav'  # or whatever file extension you want

        print(f'Processing chunk {i + 1} of {len(chunks)}')
        print("chunk_ingest", chunk_ingest)
        print("chunk_ingest_output_filename", chunk_ingest_output_filename)

        if os.path.isfile(chunk_ingest_output_filename):
            print("🙌🙌 chunk_ingest_output_filename", chunk_ingest_output_filename)
            audio_queue.put(chunk_ingest_output_filename)
        elif chunk_ingest and not contains_only_special_characters(chunk_ingest):
            # Generate the speech audio for this chunk
            start_time = time.time()
            inputs = processor(text=chunk_ingest, return_tensors="pt")
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
            end_time = time.time()

            print(f'Text-to-speech generation for chunk {i + 1} took {end_time - start_time} seconds')

            sf.write(chunk_ingest_output_filename, speech.numpy(), samplerate=16000)
            # sf.write(output_file, wav, rate)

            # Add the filename to the audio queue
            audio_queue.put(chunk_ingest_output_filename)

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
        print('🎯 text for TTS', text)

        # Process the text
        tts_chunk_by_chunk(text, callback=callback)

        # Mark the task as done
        tts_queue.task_done()

        # Let's not hog the CPU
        time.sleep(0.1)


def audio_worker():
    while True:
        # Wait for a filename to be added to the queue
        output_file = audio_queue.get()

        if output_file:
            audio = AudioSegment.from_file(output_file)

            # Speed up the audio
            fast_audio = audio.speedup(playback_speed=1.15)

            # Play the audio file
            play(fast_audio)

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
