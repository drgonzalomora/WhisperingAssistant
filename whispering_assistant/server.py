# Needed due to dependency on an installed lib
import pyaudio
import subprocess
from flask import Flask
from faster_whisper import WhisperModel
import threading
from whispering_assistant.states_manager import global_var_state
from whispering_assistant.configs.config import WhisperModel_PATH, WhisperModel_DEVICE, WhisperModel_COMPUTE, \
    WhisperModel_WORKERS, PORT
from whispering_assistant.utils.audio import record_on_mic_input
from whispering_assistant.utils.prompt import generate_initial_prompt
from whispering_assistant.utils.start_up_required_libs import start_up_required_libs
from whispering_assistant.utils.transcription import model_transcribe, model_transcribe_cache_init, \
    start_mic_to_transcription, stop_record
from whispering_assistant.commands import execute_plugin_by_keyword

# Set up Flask app
app = Flask(__name__)

start_up_required_libs()


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
