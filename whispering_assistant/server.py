from flask import Flask
import threading
from whispering_assistant.hotword_detection.hot_word_dectection import watch_audio_for_hotword
from whispering_assistant.states_manager import global_var_state
from whispering_assistant.configs.config import PORT
from whispering_assistant.utils.start_up_required_libs import start_up_required_libs
from whispering_assistant.utils.transcription import start_mic_to_transcription, stop_record


# Set up Flask app
app = Flask(__name__)

start_up_required_libs()


@app.route('/', methods=['GET'])
def activate_transcription():
    if not global_var_state.is_transcribing:
        print("Starting recording...")
        start_mic_to_transcription()
    else:
        print("Stopping recording...")
        stop_record()
    return "200"


def run_app():
    app.run(port=PORT)


def run_hot_word_detection():
    watch_audio_for_hotword()


if __name__ == '__main__':
    # Create threads for each function
    app_thread = threading.Thread(target=run_app)
    run_hot_word_detection_thread = threading.Thread(target=run_hot_word_detection)

    # Start the threads
    app_thread.start()
    run_hot_word_detection_thread.start()

    # Wait for the threads to finish
    app_thread.join()
    run_hot_word_detection_thread.join()
