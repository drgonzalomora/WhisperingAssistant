import time

import librosa
from pydub.silence import split_on_silence
from pydub import AudioSegment
from playsound import playsound
import threading

from whispering_assistant.utils.volumes import set_volume


def slow_down_audio(input_file, slowdown_factor=0.80):
    # Load the input audio file
    y, sr = librosa.load(input_file, sr=None)

    # Stretch the audio (slow it down)
    y_slow = librosa.effects.time_stretch(y, rate=slowdown_factor)

    # Save the slowed down audio
    # sf.write(input_file, y_slow, sr, subtype='PCM_24')
    return input_file


def remove_silences(input_file):
    audio_input = AudioSegment.from_file(input_file, format="wav")
    chunks = split_on_silence(audio_input, min_silence_len=1500, silence_thresh=audio_input.dBFS - 24)

    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk

    postfix = "~1"
    output_file_name, output_file_extension = input_file.rsplit(".", 1)
    output_file_with_postfix = f"{output_file_name}{postfix}.{output_file_extension}"
    combined.export(output_file_with_postfix, format="wav")
    return output_file_with_postfix


def play_sound(file_path):
    try:
        playsound(file_path)
    except Exception as e:
        print(f"An error occurred while playing the sound: {e}")


class SoundHandler:
    def __init__(self):
        self.sounds = {}

    def load_sound(self, file_path):
        # Here you might load and decode the file to an audio format
        # that your sound library can play. This is dependent on the library you're using.
        # For playsound, we can't preload the file, but in other libraries, this would be possible.
        self.sounds[file_path] = file_path

    def play_sound(self, file_path):
        if file_path not in self.sounds:
            self.load_sound(file_path)
        try:
            def play_and_set_volume():
                time.sleep(0.1)
                set_volume(50)
                playsound(self.sounds[file_path])
                set_volume(5)

            sound_thread = threading.Thread(target=play_and_set_volume)
            sound_thread.start()
        except Exception as e:
            print(f"An error occurred while playing the sound: {e}")
