import time

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
