from datetime import datetime
import subprocess
import time
import pvporcupine
from pvrecorder import PvRecorder

from whispering_assistant.configs.config import hot_word_keywords, hot_word_sensitivities, hot_word_keyword_paths, \
    hot_word_INTERVAL, hot_word_api_key
from whispering_assistant.states_manager import global_var_state

porcupine = None
recorder = None

devices = PvRecorder.get_audio_devices()
print(devices)

porcupine = pvporcupine.create(
    access_key=hot_word_api_key,
    keywords=hot_word_keywords,
    sensitivities=hot_word_sensitivities,
    keyword_paths=hot_word_keyword_paths
)

prev_pcm = []


def watch_audio_for_hotword():
    global prev_pcm, recorder

    try:
        # -1 means default
        recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
        recorder.start()

        print('Using device: %s' % recorder.selected_device)

        print('Listening {')
        for keyword, sensitivity in zip(hot_word_keywords, hot_word_sensitivities):
            print('  %s (%.2f)' % (keyword, sensitivity))
        print('}')

        while True:
            pcm = recorder.read()
            result1 = -1

            # Checking previous frame increases the accuracy incase pcm was processed midway of speech
            # if prev_pcm:
            #     result1 = porcupine.process(prev_pcm)

            result = porcupine.process(pcm)
            # prev_pcm = pcm
            # print(result, result1, result2)

            if result >= 0 or result1 >= 0:
                print('[%s] Detected %s' % (str(datetime.now()), hot_word_keywords[result]))
                recorder.stop()
                recorder.delete()
                subprocess.run(['bash', '/home/joshua/extrafiles/projects/openai-whisper/run.sh'])
                break

            if global_var_state.recently_transcribed is True or global_var_state.pause_hotword is True:
                recorder.stop()
                recorder.delete()
                break

        while True:
            if global_var_state.recently_transcribed is True or global_var_state.pause_hotword is True:
                time.sleep(hot_word_INTERVAL)
                continue

            if global_var_state.recently_transcribed is False and global_var_state.pause_hotword is False:
                break

        time.sleep(0.3)
        watch_audio_for_hotword()

    except KeyboardInterrupt:
        print('Stopping ...')

    finally:
        if porcupine is not None:
            porcupine.delete()

        if recorder is not None:
            recorder.delete()
