import os
import pyaudio
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Directory
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# OS
os.environ["DISPLAY"] = ":1"
os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"
os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

# Audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK_SECONDS = 0.25
CHUNK = int(RATE * CHUNK_SECONDS)
RECORD_SECONDS = 28
SILENCE_THRESHOLD = -40
CONSECUTIVE_SILENCE_CHUNKS = 2.5

# Server
PORT = "6969"
OUTPUT_FILE_NAME = "output.wav"

# Whisper
WhisperModel_DEVICE = "cuda"
WhisperModel_WORKERS = 10
WhisperModel_PATH = "tiny"

# compute_type="int8"
# compute_type="int8_float16"
# compute_type="float16"
WhisperModel_COMPUTE = "int8_float16"

# Hot Word
hot_word_keywords = ['victoria']
hot_word_sensitivities = [1.0]
hot_word_keyword_paths = [os.environ.get("hot_word_keyword_paths")]
hot_word_INTERVAL = 0.5

# Secrets
hot_word_api_key = os.environ.get("hot_word_api_key")

# Training Data
AUDIO_FILES_DIR = "training_data"
