import pyaudio

from whispering_assistant.configs.config import WhisperModel_PATH, WhisperModel_DEVICE, WhisperModel_COMPUTE, \
    WhisperModel_WORKERS
from whispering_assistant.utils.prompt import generate_initial_prompt
from whispering_assistant.utils.transcription import model_transcribe_cache_init
from faster_whisper import WhisperModel


def start_up_required_libs():
    # Load Whisper model
    print("Loading Whisper model...")
    model = WhisperModel(WhisperModel_PATH, device=WhisperModel_DEVICE, compute_type=WhisperModel_COMPUTE,
                         num_workers=WhisperModel_WORKERS)
    print("Whisper model loaded successfully.")

    print("Loading Audio Driver")
    audio = pyaudio.PyAudio()
    print("Audio Driver Loaded")

    print("Do an initial transcription to load cache")
    # TODO: If no output~1.wav then generate one
    model_transcribe_cache_init(model, "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/training_data/output~1.wav")
    print("Cache loaded")

    print("Load context prompt")
    context_prompt = generate_initial_prompt()
    print("context prompt loaded")

    return context_prompt, audio, model
