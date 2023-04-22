import os
import pyaudio

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

os.environ["DISPLAY"] = ":1"
os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"
os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK_SECONDS = 0.25
CHUNK = int(RATE * CHUNK_SECONDS)
RECORD_SECONDS = 28
SILENCE_THRESHOLD = -40
CONSECUTIVE_SILENCE_CHUNKS = 2.5

PORT = "6969"
OUTPUT_FILE_NAME = "output.wav"

WhisperModel_DEVICE = "cuda"
WhisperModel_WORKERS = 10
WhisperModel_PATH = "tiny"

# compute_type="int8"
# compute_type="int8_float16"
# compute_type="float16"
WhisperModel_COMPUTE = "int8_float16"
