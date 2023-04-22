# Needed due to dependency on an installed lib
import pyaudio
import subprocess
from flask import Flask
from faster_whisper import WhisperModel
import threading
from whispering_assistant.states_manager import global_var_state
from whispering_assistant.config import WhisperModel_PATH, WhisperModel_DEVICE, WhisperModel_COMPUTE, \
    WhisperModel_WORKERS, PORT
from whispering_assistant.utils.audio import record_on_mic_input
from whispering_assistant.utils.prompt import generate_initial_prompt
from whispering_assistant.utils.transcription import model_transcribe, model_transcribe_cache_init
from whispering_assistant.commands import execute_plugin_by_keyword

# Set up Flask app
app = Flask(__name__)

# Load Whisper model
print("Loading Whisper model...")
model = WhisperModel(WhisperModel_PATH, device=WhisperModel_DEVICE, compute_type=WhisperModel_COMPUTE, num_workers=WhisperModel_WORKERS)
print("Whisper model loaded successfully.")

print("Loading Audio Driver")
audio = pyaudio.PyAudio()
print("Audio Driver Loaded")

print("Do an initial transcription to load cache")
# TODO: If no output~1.wav then generate one
model_transcribe_cache_init(model, "output~1.wav")
print("Cache loaded")

print("Load context prompt")
context_prompt = generate_initial_prompt()
print("context prompt loaded")


def start_mic_to_transcription():
    global_var_state.should_transcribe = True
    global_var_state.is_transcribing = True

    # Get the current window
    window_id = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW']).split()[-1]

    audio = pyaudio.PyAudio()
    output_file_name = record_on_mic_input(audio)

    result_text = model_transcribe(model, output_file_name, context_prompt)

    print("Activate prev window...")
    subprocess.call(['xdotool', 'windowactivate', window_id])

    print("Analyzing transcription what command to run")
    execute_plugin_by_keyword(result_text)
    global_var_state.is_transcribing = False
    return

def stop_record():
    global_var_state.should_transcribe = False
    return


@app.route('/', methods=['GET'])
def hello():
    if not global_var_state.is_transcribing:
        print("Starting recording...")
        start_mic_to_transcription()
    else:
        print("Stopping recording...")
        stop_record()
    return "200"


def run_app():
    app.run(port=PORT)


# def run_hot_word_detection():
#     global model
#     detect_hot_word(model_param=model)

if __name__ == '__main__':
    # Create threads for each function
    app_thread = threading.Thread(target=run_app)
    # run_hot_word_detection_thread = threading.Thread(target=run_hot_word_detection)

    # Start the threads
    app_thread.start()
    # run_hot_word_detection_thread.start()

    # Wait for the threads to finish
    app_thread.join()
    # run_hot_word_detection_thread.join()
