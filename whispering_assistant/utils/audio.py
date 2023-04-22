import librosa
from pydub.silence import split_on_silence
from pydub import AudioSegment


def slow_down_audio(input_file, slowdown_factor=0.80):
    # Load the input audio file
    y, sr = librosa.load(input_file, sr=None)

    # Stretch the audio (slow it down)
    y_slow = librosa.effects.time_stretch(y, rate=slowdown_factor)

    # Save the slowed down audio
    sf.write(input_file, y_slow, sr, subtype='PCM_24')
    return input_file


def remove_silences(input_file):
    audio_input = AudioSegment.from_file(input_file, format="wav")
    chunks = split_on_silence(audio_input, min_silence_len=1500, silence_thresh=audio_input.dBFS - 24)

    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk

    postfix = "~1"
    output_file_name, output_file_extension = input_file.rsplit(".", 1)
    output_file_with_postfix = f"{output_file_name}{postfix}.{output_file_extension}"
    combined.export(output_file_with_postfix, format="wav")
    return output_file_with_postfix
