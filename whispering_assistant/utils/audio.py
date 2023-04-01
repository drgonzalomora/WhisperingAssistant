from whispering_assistant import global_var_state
import subprocess
from pydub.silence import split_on_silence
from pydub import AudioSegment
from pydub.silence import detect_silence

from whispering_assistant.config import FORMAT, CHANNELS, RATE, CHUNK, RECORD_SECONDS, SILENCE_THRESHOLD, \
    CONSECUTIVE_SILENCE_CHUNKS, OUTPUT_FILE_NAME
from whispering_assistant.utils.volumes import get_current_volume, set_volume
from whispering_assistant.utils.window_dialogs import generate_info_dialog, kill_dialog


def remove_silences(input_file):
    audio_input = AudioSegment.from_file(input_file, format="wav")
    chunks = split_on_silence(audio_input, min_silence_len=1000, silence_thresh=audio_input.dBFS - 24)

    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk

    postfix = "~1"
    output_file_name, output_file_extension = input_file.rsplit(".", 1)
    output_file_with_postfix = f"{output_file_name}{postfix}.{output_file_extension}"
    combined.export(output_file_with_postfix, format="wav")
    return output_file_with_postfix

# audio = pyaudio.PyAudio()
def record_on_mic_input(audio):
    transcribing_window = None
    transcribing_window = generate_info_dialog("❌ Starting")

    # Set global variable and play audio cue
    global_var_state.is_transcribing = "GO"
    global_var_state.recently_transcribed = True

    # Get the current window
    window_id = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW']).split()[-1]

    # Get current volume level
    prev_volume = get_current_volume()

    # Record audio from microphone
    set_volume("5%")
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Show transcribing window
    print("Showing transcribing window...")

    frames = []
    silence_counter = 0
    max_it = int(RATE / CHUNK * RECORD_SECONDS)
    offset_delay = int(RATE / CHUNK * 0.05)

    for i in range(0, max_it):
        data = stream.read(CHUNK)
        frames.append(data)

        if i == offset_delay:
            kill_dialog(transcribing_window)
            transcribing_window = generate_info_dialog("✅ Recording")

        if not global_var_state.should_transcribe:
            break

        # Auto cutoff on silence
        current_audio = b''.join([data])
        audio_segment = AudioSegment(data=current_audio, sample_width=audio.get_sample_size(FORMAT), frame_rate=RATE,
                                     channels=CHANNELS)

        is_silent = detect_silence(audio_segment, min_silence_len=250, silence_thresh=SILENCE_THRESHOLD)
        print("is_silent", is_silent)

        if is_silent:
            silence_counter += 0.25
        else:
            silence_counter = 0

        if silence_counter >= CONSECUTIVE_SILENCE_CHUNKS:
            print("Stopped recording due to seconds of consecutive silence.")
            break

    # Stop recording and close audio streams
    set_volume(f"{prev_volume}%")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Close transcribing window
    print("Closing transcribing window...")
    kill_dialog(transcribing_window)

    # Process audio and transcribe using Whisper model
    print("Processing audio...")
    mic_stream = AudioSegment(b''.join(frames), sample_width=audio.get_sample_size(FORMAT), channels=CHANNELS,
                              frame_rate=RATE)
    mic_stream.export(OUTPUT_FILE_NAME, format="wav")

    print("Remove silences...")
    output_file_with_minimal_silence = remove_silences(OUTPUT_FILE_NAME)

    return output_file_with_minimal_silence
