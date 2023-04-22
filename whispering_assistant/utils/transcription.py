import time

from whispering_assistant.configs.config import AUDIO_FILES_DIR


def model_transcribe_cache_init(model,filepath, beam_size=1, best_of=1):
    segments, info = model.transcribe(filepath, beam_size=beam_size,
                                      best_of=best_of,
                                      temperature=0,
                                      language="en",
                                      without_timestamps=True,
                                      word_timestamps=False)
    result_text = ""

    for segment in segments:
        result_text = result_text + segment.text
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    print("Showing transcribed text...")
    print("result", result_text)
    return result_text

def model_transcribe(model,filepath, context_prompt, beam_size=20, best_of=2):
    start_time = time.time()

    # We should skip model transcription to the audio file that will be inputted as large number of silences.
    segments, info = model.transcribe(filepath, beam_size=20,
                                      best_of=2,
                                      temperature=0,
                                      language="en", initial_prompt=context_prompt, without_timestamps=True,
                                      word_timestamps=False)

    end_time = time.time()

    execution_time = end_time - start_time

    print(f"The execution time is {execution_time} seconds.")

    result_text = ""
    for segment in segments:
        result_text = result_text + segment.text
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    print("Showing transcribed text...")
    print("result", result_text)

    end_time = time.time()

    execution_time = end_time - start_time

    print(f"The execution time for result cat is {execution_time} seconds.")

    return result_text

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


def check_transcript_for_short_commands(stream):
    start_time = time.time()
    # Show transcribing window
    print("Showing transcribing window...")
    max_time_check_short_command = 4
    frames = []
    silence_counter = 0
    max_it = int(RATE / CHUNK * max_time_check_short_command)
    offset_delay = 0
    progress_pct = 0

    message_queue.put(('create_avatar', 'set_content', "✅ Recording", "✅ Recording..."))
    for i in range(0, max_it):
        data = stream.read(CHUNK)
        frames.append(data)

    start_time = time.time()
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    audio_file_name = "audio"
    audio_file_extension = "wav"
    audio_file_with_timestamp = f"./{AUDIO_FILES_DIR}/{audio_file_name}_{timestamp}.{audio_file_extension}"

    mic_stream = AudioSegment(b''.join(frames), sample_width=audio.get_sample_size(FORMAT), channels=CHANNELS,
                              frame_rate=RATE)
    mic_stream.export(audio_file_with_timestamp, format="wav")
    print_time_profile(start_time, "export audio")
    processed_audio_file_name = audio_file_with_timestamp

    print("💡💡💡Transcribing audio...")

    start_time = time.time()
    context_prompt = get_prompt_short_commands()

    start_time = time.time()
    segments, info = model.transcribe(processed_audio_file_name, beam_size=1,
                                      best_of=1,
                                      temperature=0.1,
                                      language="en",
                                      initial_prompt=context_prompt,
                                      without_timestamps=True,
                                      word_timestamps=False,
                                      vad_filter=False, vad_parameters=dict(min_silence_duration_ms=1000))
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
    print("⏳⏳⏳️ result", result_text)
    print("segment_end", segment_end)
    save_transcription(result_text, timestamp)

    command_chainable = False
    skip_next_transcription = False
    run_short_command = False

    # Check if result_text contains keyword that can affect the next part of transcription
    if check_if_chainable_commands(result_text):
        print("One of the keywords was found in the result text.")
        command_chainable = True

    if 'cancel' in result_text.lower() or not result_text or check_if_quick_action_commands(result_text):
        skip_next_transcription = True
        run_short_command = True

    if (run_short_command):
        commands(result_text)

    # 📌 TODO: for one-shot commands or short commands, I think we can already execute it on the first transcription and automatically skip the next transcription

    return frames, command_chainable, skip_next_transcription


def record(skip_check_short_commands=False, short_commands_prefix="", cutoff_padding=0):
    global audio, model
    transcribing_window = None

    start_time = time.time()
    update_queue.put(('show',))
    message_queue.put(('create_avatar', 'show'))
    message_queue.put(('create_avatar', 'set_content', "❌ Starting", "❌ Starting..."))
    elapsed_time = time.time() - start_time
    print(f"Time taken for opening transcribing window: {elapsed_time:.5f} seconds")

    start_time = time.time()
    # Set global variable and play audio cue
    global_var_state.is_transcribing = "GO"
    global_var_state.recently_transcribed = True
    elapsed_time = time.time() - start_time
    print(f"Time taken for setting global variables: {elapsed_time:.5f} seconds")

    start_time = time.time()
    # Get the current window
    window_id = get_active_window_id()
    elapsed_time = time.time() - start_time
    print(f"Time taken for getting the current window: {elapsed_time:.5f} seconds")

    start_time = time.time()
    # Get current volume level
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

    frames, chainable_commands, skip_next_transcription = check_transcript_for_short_commands(stream)

    start_time = time.time()
    # Show transcribing window
    print("Showing transcribing window...")
    silence_counter = 0
    max_it = int(RATE / CHUNK * RECORD_SECONDS)
    offset_delay = 0
    progress_pct = 0

    # Define variables for the static values
    LOWER_BOUND = 3 / (RECORD_SECONDS - 4)
    UPPER_BOUND = 0.9
    MIN_SCALING = 1
    MAX_SCALING = 2

    SCALING_FACTOR_SHORT_COMMANDS = 1 if chainable_commands else 2

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
                        MAX_SCALING - MIN_SCALING) / (
                                         UPPER_BOUND - LOWER_BOUND)

            # Auto cutoff on silence with dynamic CONSECUTIVE_SILENCE_CHUNKS
            current_audio = b''.join([data])
            audio_segment = AudioSegment(data=current_audio, sample_width=audio.get_sample_size(FORMAT),
                                         frame_rate=RATE,
                                         channels=CHANNELS)
            is_silent = detect_silence(audio_segment, min_silence_len=90, silence_thresh=SILENCE_THRESHOLD)
            print("is_silent", is_silent)

            if is_silent:
                silence_counter += 0.1
            else:
                silence_counter = 0

            # Check for consecutive silence
            print('scaling_factor', CONSECUTIVE_SILENCE_CHUNKS * scaling_factor)
            if silence_counter >= CONSECUTIVE_SILENCE_CHUNKS * scaling_factor:
                print("Stopped recording due to seconds of consecutive silence.")
                break

    start_time = time.time()
    # Stop recording and close audio streams
    set_volume(prev_volume)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print_time_profile(start_time, "setting vol")

    # Close transcribing window
    global_var_state.is_transcribing = "STOP"

    print("Closing transcribing window...")
    message_queue.put(('create_avatar', 'hide'))

    start_time = time.time()
    # Process audio and transcribe using Whisper model
    print("Processing audio...")
    input_audio_duration = 4 + (progress_pct * RECORD_SECONDS)

    silence_pct = 100

    if input_audio_duration:
        silence_pct = (input_audio_duration - silence_counter) / input_audio_duration

    print('silence_counter', silence_counter)
    print('silence_pct', silence_pct)
    print('input_audio_duration', input_audio_duration)

    if not skip_next_transcription and ((silence_pct < 0.98 and silence_pct > 0) or input_audio_duration > 5):
        start_time = time.time()
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        audio_file_name = "audio"
        audio_file_extension = "wav"
        audio_file_with_timestamp = f"./{AUDIO_FILES_DIR}/{audio_file_name}_{timestamp}.{audio_file_extension}"

        mic_stream = AudioSegment(b''.join(frames), sample_width=audio.get_sample_size(FORMAT), channels=CHANNELS,
                                  frame_rate=RATE)
        mic_stream.export(audio_file_with_timestamp, format="wav")
        print_time_profile(start_time, "export audio")

        # Uncomment this one if you need to here the playback
        # pygame.mixer.Sound("/home/joshua/extrafiles/projects/openai-whisper/output.wav").play()

        start_time = time.time()
        print("Remove silences...")
        # start_time = time.time()
        # processed_audio_file_name = slow_down_audio(input_file=audio_file_with_timestamp)
        processed_audio_file_name = audio_file_with_timestamp

        # if input_audio_duration > 5:
        #     processed_audio_file_name = remove_silences(audio_file_with_timestamp)

        print_time_profile(start_time, "remove silences")

        print("Transcribing audio...")

        start_time = time.time()
        context_prompt = get_prompt_cache()

        print_time_profile(start_time, "get prompt")
        print("context_prompt", context_prompt)

        start_time = time.time()
        # We should skip model transcription to the audio file that will be inputted as large number of silences.
        segments, info = model.transcribe(processed_audio_file_name, beam_size=5,
                                          best_of=1,
                                          temperature=0.1,
                                          language="en",
                                          initial_prompt=context_prompt,
                                          without_timestamps=True,
                                          word_timestamps=False,
                                          vad_filter=False, vad_parameters=dict(min_silence_duration_ms=1000))

        print_time_profile(start_time, "generators")

        start_time = time.time()
        result_text = ""
        segment_end = 0
        for segment in segments:
            result_text = result_text + segment.text
            segment_end = segment.end
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        print("Showing transcribed text...")
        print("result", result_text)
        print("segment_end", segment_end)
        save_transcription(result_text, timestamp)

        print_time_profile(start_time, "transcription")

        print("Activate prev window...")
        start_time = time.time()
        activate_window(window_id)
        print_time_profile(start_time, "activate window")

        print("Analyzing transcription what command to run")
        start_time = time.time()

        commands(result_text)
        print_time_profile(start_time, "run command")

    global_var_state.recently_transcribed = False
    return




def save_transcription(transcription, timestamp):
    with open(f"./{AUDIO_FILES_DIR}/transcription_{timestamp}.txt", "w") as f:
        f.write(transcription)