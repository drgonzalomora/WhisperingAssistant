from datetime import datetime
import time

import pyaudio
from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.silence import detect_silence

from whispering_assistant.commands import execute_plugin_by_keyword, generate_prompts_for_short_commands
from whispering_assistant.commands.command_base_template import command_types
from whispering_assistant.configs.config import AUDIO_FILES_DIR, CHANNELS, RATE, CHUNK, FORMAT, \
    SILENCE_THRESHOLD, CONSECUTIVE_SILENCE_CHUNKS, MIC_INPUT_GAIN, WhisperModel_tiny_PATH
from whispering_assistant.states_manager import global_var_state
from whispering_assistant.states_manager.window_manager_messages import message_queue
from whispering_assistant.utils.audio import play_sound, SoundHandler
from whispering_assistant.utils.performance import print_time_profile, TimerCheck
from whispering_assistant.utils.prompt import get_prompt_cache, generate_related_keywords_prompt
from whispering_assistant.utils.volumes import get_volume, set_volume, set_microphone_volume
from whispering_assistant.utils.window_dialogs import activate_window, get_active_window_id

model_tiny = WhisperModel(WhisperModel_tiny_PATH, device="cuda", compute_type="int8_float16",
                          num_workers=5)

sound_handler = SoundHandler()
sound_handler.load_sound(
    "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/sound/whistle.mp3")


def model_transcribe_cache_init(model, filepath, beam_size=1, best_of=1):
    segments, info = model.transcribe(filepath, beam_size=beam_size, best_of=best_of, temperature=0, language="en",
                                      without_timestamps=True, word_timestamps=False)
    segments = list(segments)
    print("segments", segments)
    return segments


def save_transcription(transcription, timestamp):
    with open(f"../{AUDIO_FILES_DIR}/transcription_{timestamp}.txt", "w") as f:
        f.write(transcription)


def save_file_then_transcribe(frames, model, audio, context_prompt, transcription_args=None, use_model_tiny=False):
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

    if use_model_tiny:
        segments, info = model_tiny.transcribe(processed_audio_file_name, beam_size=10, best_of=1, temperature=0,
                                               language="en",
                                               initial_prompt=context_prompt, without_timestamps=True,
                                               word_timestamps=False,
                                               vad_filter=False, vad_parameters=dict(min_silence_duration_ms=1000),
                                               **transcription_args, )
    else:
        segments, info = model.transcribe(processed_audio_file_name, beam_size=5, best_of=1, temperature=0,
                                          language="en",
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

    if result_text:
        result_text = result_text.lstrip()

    return result_text


# TODO: Based on the findings, what we can improve here is the checking of the command prompts because this is being done twice,
#  first on the short command and next is for the actual transcription.
short_transcription_timer_check = TimerCheck()


def check_transcript_for_short_commands(stream, audio):
    model = model_tiny

    short_transcription_timer_check.start()
    print("Showing transcribing window...")
    max_time_check_short_command = 2.5
    frames = []
    max_it = int(RATE / CHUNK * max_time_check_short_command)
    message_queue.put(('create_avatar', 'set_content', "✅ Recording", "✅ Recording..."))
    short_transcription_timer_check.stop("showing avatar")

    short_transcription_timer_check.start()
    for i in range(0, max_it):
        data = stream.read(CHUNK)
        frames.append(data)
    short_transcription_timer_check.stop("recording")

    # 📌 TODO: Add a checking here to check the number of silences in the input and use that as the basis if we need to skip the transcription altogether.

    short_transcription_timer_check.start()
    context_prompt = generate_prompts_for_short_commands()
    result_text = save_file_then_transcribe(frames=frames + frames, model=model, audio=audio,
                                            context_prompt=context_prompt)
    short_transcription_timer_check.stop("first pass transcript")

    short_transcription_timer_check.start()
    plugin_used = execute_plugin_by_keyword(result_text, run_command=False, skip_fallback=True, intent_sensitivity=0.8)
    short_transcription_timer_check.stop("check command props")

    short_transcription_timer_check.start()
    command_chainable = False
    skip_next_transcription = False
    next_transcription_max_time = 60
    next_transcription_cut_off_factor = 1

    # 📌 TODO: Implement the checking for silences before transcription.

    command_type = getattr(plugin_used, 'command_type', None)
    print("⚡️command_type", command_type)

    if command_type == command_types['ONE_SHOT']:
        execute_plugin_by_keyword(result_text, run_command=True, skip_fallback=True, intent_sensitivity=0.8)
        skip_next_transcription = True
    elif command_type == command_types['CHAINABLE_SHORT']:
        next_transcription_max_time = 1
        next_transcription_cut_off_factor = 0.5
    elif command_type == command_types['CHAINABLE_LONG']:
        next_transcription_max_time = 60
        next_transcription_cut_off_factor = 2

    short_transcription_timer_check.stop("set parameters based on command type")

    short_transcription_timer_check.output()
    return frames, command_chainable, skip_next_transcription, next_transcription_max_time, next_transcription_cut_off_factor


# TODO: Based on the findings, what we can improve here is the second pass for transcription.
#  Maybe we can reduce this one further because we're just using this to get the keywords to pass on the actual transcription.
#  So this can be less accurate, but yeah. And next also, we can further improve the performance of
#  the checking of plug-in to run based on the transcript. Currently it takes around 300 milliseconds.
#  If we can bring that down to 100 milliseconds, then I think that will be the best. That would be like the best.
transcription_timer_check = TimerCheck()


def start_mic_to_transcription(model=None):
    print('🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 Starting Transcription')
    transcription_timer_check.start()
    audio = pyaudio.PyAudio()

    # Iterate over the available input devices and print their information
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        print(f"Device index: {i}, Name: {device_info['name']}")

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    set_microphone_volume('alsa_input', MIC_INPUT_GAIN)  # 50% volume
    transcription_timer_check.stop("open mic stream")

    transcription_timer_check.start()
    message_queue.put(('create_avatar', 'show'))
    message_queue.put(('create_avatar', 'set_content', "❌ Starting", "❌ Starting..."))
    transcription_timer_check.stop("opening transcribing window")

    transcription_timer_check.start()
    global_var_state.is_transcribing = "GO"
    global_var_state.recently_transcribed = True
    transcription_timer_check.stop("set global var")

    transcription_timer_check.start()
    prev_volume = get_volume()
    transcription_timer_check.stop("get volume")

    transcription_timer_check.start()
    sound_handler.play_sound(
        "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/sound/whistle.mp3")
    transcription_timer_check.stop("play sound cue")

    transcription_timer_check.start()

    # 📌 TODO: Instead of using a short initial transcription, let's add a queue that automatically sends chunks to a speech to text and checks the output for any keywords.
    # we can put this inside for-loop
    frames, \
        chainable_commands, \
        skip_next_transcription, \
        next_transcription_max_time, \
        next_transcription_cut_off_factor = check_transcript_for_short_commands(stream, audio=audio)
    transcription_timer_check.stop("first pass short transcription")

    silence_counter = 0
    silence_reset_counter = 0
    silence_reset_counter_threshold = 0.5
    max_it = int(RATE / CHUNK * next_transcription_max_time)

    # Define variables for the static values
    LOWER_BOUND = 2.5 / (next_transcription_max_time - 2.5)
    UPPER_BOUND = 0.9
    MIN_SCALING = 1
    MAX_SCALING = 2

    if not skip_next_transcription:

        transcription_timer_check.start()
        # TODO: We should have a keep condition on this for loop that once it detects certain keywords and detects the prompt to use, it will break.
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
                scaling_factor = next_transcription_cut_off_factor
            else:
                scaling_factor = next_transcription_cut_off_factor + (progress_pct - LOWER_BOUND) * (
                        MAX_SCALING - MIN_SCALING) / (UPPER_BOUND - LOWER_BOUND)

            # Auto cutoff on silence with dynamic CONSECUTIVE_SILENCE_CHUNKS
            current_audio = b''.join([data])
            audio_segment = AudioSegment(data=current_audio, sample_width=audio.get_sample_size(FORMAT),
                                         frame_rate=RATE, channels=CHANNELS)
            is_silent = detect_silence(audio_segment, min_silence_len=180, silence_thresh=SILENCE_THRESHOLD)
            print("is_silent", is_silent)
            print("audio_segment.dBFS", audio_segment.dBFS)
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

        transcription_timer_check.stop("finished recording")

    transcription_timer_check.start()
    print("Terminate audio...")
    start_time = time.time()
    set_volume(prev_volume)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    transcription_timer_check.stop("terminating stream and setting vol")

    transcription_timer_check.start()
    print("Closing transcribing window...")
    global_var_state.is_transcribing = "STOP"
    message_queue.put(('create_avatar', 'hide'))
    print("Processing audio...")
    transcription_timer_check.stop("closing avatar window")

    if not skip_next_transcription:
        transcription_timer_check.start()
        context_prompt = get_prompt_cache()
        frames_for_processing = frames
        transcription_timer_check.stop("get prompt cache")

        print("🎤len(frames)", len(frames))
        if len(frames) < 40:
            frames_for_processing = frames + frames

        transcription_timer_check.start()
        # 📌 TODO: In order to make the transcription service as efficient as possible, we can move this part of the logic to the speech-to-text view. That way we can do both keywords detection as well as prompt detection before actually processing to a larger model.
        prev_result_text = save_file_then_transcribe(frames=frames_for_processing, model=model, audio=audio,
                                                     context_prompt=context_prompt, use_model_tiny=True)
        result_text = prev_result_text
        transcription_timer_check.stop("second pass transcription")

        if len(frames) > 30:
            transcription_timer_check.start()
            context_prompt_related_keywords = generate_related_keywords_prompt(prev_result_text)
            result_text = save_file_then_transcribe(frames=frames, model=model, audio=audio,
                                                    context_prompt=context_prompt_related_keywords)
            transcription_timer_check.stop("third pass transcription")

        transcription_timer_check.start()
        print("💡 result_text comparison")
        print("result_text prev:", prev_result_text)
        print("result_text after:", result_text)
        print("🕵️ Analyzing transcription what command to run")
        execute_plugin_by_keyword(result_text)
        transcription_timer_check.stop("check what plugin to run")

    global_var_state.recently_transcribed = False
    print('🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 Ending Transcription')
    transcription_timer_check.output()
    return


def stop_record():
    global_var_state.is_transcribing = "STOP"
    return
