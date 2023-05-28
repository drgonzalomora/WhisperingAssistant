import os
import pyaudio
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()


def load_os_display_env():
    os.environ["DISPLAY"] = ":1"
    os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"


# Directory
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# OS
load_os_display_env()

# Audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK_SECONDS = 0.1
CHUNK = int(RATE * CHUNK_SECONDS)
RECORD_SECONDS = 28
MIC_INPUT_GAIN = 0.5
SILENCE_THRESHOLD = (MIC_INPUT_GAIN * 100 * -1) - 2
CONSECUTIVE_SILENCE_CHUNKS = 1

# Server
PORT = "6969"
OUTPUT_FILE_NAME = "output.wav"

# Whisper
WhisperModel_DEVICE = "cuda"
WhisperModel_WORKERS = 5

# WhisperModel_PATH = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/ml/whisper-large-v2-ct2"
# tiny, tiny.en, tiny
# base, base.en, base
# small, small.en, small
# medium, medium.en, medium
# large, N/A, large

WhisperModel_PATH = "large-v2"
WhisperModel_tiny_PATH = "small"

# compute_type="int8"
# compute_type="int8_float16"
# compute_type="float16"
WhisperModel_COMPUTE = "int8_float16"

# Embeddings
Instructor_MODEL = 'hkunlp/instructor-base'
Instructor_DEVICE = "cpu"

# Hot Word
hot_word_keywords = ['hey victoria']
hot_word_sensitivities = [0.7]
hot_word_keyword_paths = [os.environ.get("hot_word_keyword_paths")]
hot_word_INTERVAL = 0.5

# Secrets
hot_word_api_key = os.environ.get("hot_word_api_key")
toggl_api_key = os.environ.get("toggl_api_key")
toggl_workspace_id = os.environ.get("toggl_workspace_id")
openai_key = os.environ.get("openai_key")

# Training Data
AUDIO_FILES_DIR = "training_data"

# Knowledge Files
AUTOJUMP_FILE = os.path.expanduser("~/.local/share/autojump/autojump.txt")
AUTOJUMP_JSON_FILE = "../assets/docs/autojump_stats.json"
