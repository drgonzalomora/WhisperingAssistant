from datetime import datetime
import time

import pyaudio
from pydub import AudioSegment
from pydub.silence import detect_silence

from whispering_assistant.commands import execute_plugin_by_keyword
from whispering_assistant.commands.command_base_template import command_types
from whispering_assistant.configs.config import AUDIO_FILES_DIR, CHANNELS, RATE, CHUNK, FORMAT, RECORD_SECONDS, \
    SILENCE_THRESHOLD, CONSECUTIVE_SILENCE_CHUNKS
from whispering_assistant.states_manager import global_var_state
from whispering_assistant.states_manager.window_manager_messages import message_queue
from whispering_assistant.utils.performance import print_time_profile
from whispering_assistant.utils.prompt import get_prompt_cache
from whispering_assistant.utils.volumes import get_volume, set_volume
from whispering_assistant.utils.window_dialogs import activate_window, get_active_window_id


def model_transcribe_cache_init(model, filepath, beam_size=1, best_of=1):
    segments, info = model.transcribe(filepath, beam_size=beam_size, best_of=best_of, temperature=0, language="en",
                                      without_timestamps=True, word_timestamps=False)
    segments = list(segments)
    print("segments", segments)
    return segments


def save_transcription(transcription, timestamp):
    with open(f"../{AUDIO_FILES_DIR}/transcription_{timestamp}.txt", "w") as f:
        f.write(transcription)


def save_file_then_transcribe(frames, model, audio, context_prompt, transcription_args=None):
    if transcription_args is None:
        transcription_args = {}
    start_time = time.time()
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    audio_file_name = "audio"
    audio_file_extension = "wav"
    audio_file_with_timestamp = f"../{AUDIO_FILES_DIR}/{audio_file_name}_{timestamp}.{audio_file_extension}"

    mic_stream = AudioSegment(b''.join(frames), sample_width=audio.get_sample_size(FORMAT), channels=CHANNELS,
                              frame_rate=RATE)
    mic_stream.export(audio_file_with_timestamp, format="wav")
    print_time_profile(start_time, "export audio")
    processed_audio_file_name = audio_file_with_timestamp

    print("💡Transcribing audio...")

    start_time = time.time()
    segments, info = model.transcribe(processed_audio_file_name, beam_size=5, best_of=1, temperature=0.1, language="en",
                                      initial_prompt=context_prompt, without_timestamps=True, word_timestamps=False,
                                      vad_filter=False, vad_parameters=dict(min_silence_duration_ms=1000),
                                      **transcription_args, )
    print_time_profile(start_time, "generators")

    start_time = time.time()
    result_text = ""
    segment_end = 0
    for segment in segments:
        result_text = result_text + segment.text
        segment_end = segment.end
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    print_time_profile(start_time, "transcription")

    print("Showing transcribed text...")
    print("⏳️ result", result_text)
    print("segment_end", segment_end)
    save_transcription(result_text, timestamp)

    return result_text


def check_transcript_for_short_commands(stream, model, audio):
    print("Showing transcribing window...")
    max_time_check_short_command = 4
    frames = []
    max_it = int(RATE / CHUNK * max_time_check_short_command)

    message_queue.put(('create_avatar', 'set_content', "✅ Recording", "✅ Recording..."))

    for i in range(0, max_it):
        data = stream.read(CHUNK)
        frames.append(data)

    # 📌 TODO: Replace this with a function
    context_prompt = "lock screen"
    result_text = save_file_then_transcribe(frames=frames, model=model, audio=audio, context_prompt=context_prompt)
    plugin_used = execute_plugin_by_keyword(result_text, run_command=False)

    command_chainable = False
    skip_next_transcription = False

    if 'cancel' in result_text.lower():
        skip_next_transcription = True

    if getattr(plugin_used, 'command_type', None) == command_types['ONE_SHOT']:
        execute_plugin_by_keyword(result_text, run_command=True, skip_fallback=True)
        skip_next_transcription = True

    # 📌 TODO: Change wait time based on command type

    return frames, command_chainable, skip_next_transcription


def start_mic_to_transcription(cutoff_padding=0, model=None):
    start_time = time.time()
    message_queue.put(('create_avatar', 'show'))
    message_queue.put(('create_avatar', 'set_content', "❌ Starting", "❌ Starting..."))
    elapsed_time = time.time() - start_time
    print(f"Time taken for opening transcribing window: {elapsed_time:.5f} seconds")

    start_time = time.time()
    global_var_state.is_transcribing = "GO"
    global_var_state.recently_transcribed = True
    elapsed_time = time.time() - start_time
    print(f"Time taken for setting global variables: {elapsed_time:.5f} seconds")

    start_time = time.time()
    window_id = get_active_window_id()
    elapsed_time = time.time() - start_time
    print(f"Time taken for getting the current window: {elapsed_time:.5f} seconds")

    start_time = time.time()
    prev_volume = get_volume()
    elapsed_time = time.time() - start_time
    print(f"VolumeL {prev_volume}")
    print(f"Time taken for getting current volume level: {elapsed_time:.5f} seconds")

    start_time = time.time()
    # Record audio from microphone
    set_volume(5)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    elapsed_time = time.time() - start_time
    print(f"Time taken for recording audio: {elapsed_time:.5f} seconds")

    frames, chainable_commands, skip_next_transcription = check_transcript_for_short_commands(stream, audio=audio,
                                                                                              model=model)

    silence_counter = 0
    silence_reset_counter = 0
    silence_reset_counter_threshold = 0.5
    max_it = int(RATE / CHUNK * RECORD_SECONDS)
    progress_pct = 0

    # Define variables for the static values
    LOWER_BOUND = 3 / (RECORD_SECONDS - 4)
    UPPER_BOUND = 0.9
    MIN_SCALING = 1
    MAX_SCALING = 2

    SCALING_FACTOR_SHORT_COMMANDS = 1 if chainable_commands else 1.5

    if not skip_next_transcription:
        for i in range(0, max_it):
            # Add an offset since there was a first transcription done for 3 seconds
            data = stream.read(CHUNK * 2)
            frames.append(data)

            if global_var_state.is_transcribing == "STOP":
                break

            # Calculate progress percentage
            progress_pct = i / max_it

            # Calculate scaling factor based on progress percentage
            if progress_pct >= 0.9:
                scaling_factor = 2
            elif progress_pct <= LOWER_BOUND:
                scaling_factor = 1 + cutoff_padding
            else:
                scaling_factor = SCALING_FACTOR_SHORT_COMMANDS + (progress_pct - LOWER_BOUND) * (
                        MAX_SCALING - MIN_SCALING) / (UPPER_BOUND - LOWER_BOUND)

            # Auto cutoff on silence with dynamic CONSECUTIVE_SILENCE_CHUNKS
            current_audio = b''.join([data])
            audio_segment = AudioSegment(data=current_audio, sample_width=audio.get_sample_size(FORMAT),
                                         frame_rate=RATE, channels=CHANNELS)
            is_silent = detect_silence(audio_segment, min_silence_len=180, silence_thresh=SILENCE_THRESHOLD)
            print("is_silent", is_silent)
            print("📍 silence_counter", silence_counter, silence_reset_counter)

            if is_silent:
                silence_counter += 0.1
                silence_reset_counter = 0
            elif silence_reset_counter > silence_reset_counter_threshold:
                silence_counter = 0
            else:
                silence_reset_counter += 0.1

            # Check for consecutive silence
            print('scaling_factor', CONSECUTIVE_SILENCE_CHUNKS * scaling_factor)
            if silence_counter >= CONSECUTIVE_SILENCE_CHUNKS * scaling_factor:
                print("Stopped recording due to seconds of consecutive silence.")
                break

    print("Terminate audio...")
    start_time = time.time()
    set_volume(prev_volume)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print_time_profile(start_time, "setting vol")

    print("Closing transcribing window...")
    global_var_state.is_transcribing = "STOP"
    message_queue.put(('create_avatar', 'hide'))
    print("Processing audio...")

    if not skip_next_transcription:
        context_prompt = get_prompt_cache()
        result_text = save_file_then_transcribe(frames=frames, model=model, audio=audio, context_prompt=context_prompt)

        print("Activate prev window...")
        start_time = time.time()
        activate_window(window_id)
        print_time_profile(start_time, "activate window")

        print("Analyzing transcription what command to run")
        start_time = time.time()
        execute_plugin_by_keyword(result_text)
        print_time_profile(start_time, "run command")

    global_var_state.recently_transcribed = False
    return


def stop_record():
    global_var_state.is_transcribing = "STOP"
    return
