import time

import soundfile
from espnet2.bin.tts_inference import Text2Speech
from playsound import playsound
import soundfile as sf


# text2speech = Text2Speech.from_pretrained("kan-bayashi/ljspeech_vits", device="cuda")
#
# start_time = time.time()
# speech = text2speech("Hello, this is a test run")["wav"]
# end_time = time.time()
# print(f'Text-to-speech generation took {end_time - start_time} seconds')
#
# # Save the output wav file
# output_file = 'out.wav'
# soundfile.write(output_file, speech.numpy(), text2speech.fs, "PCM_16")
#
# # Play the output file
# playsound(output_file)

lang = 'English'
tag = 'kan-bayashi/ljspeech_vits'  # @param ["kan-bayashi/ljspeech_tacotron2", "kan-bayashi/ljspeech_fastspeech", "kan-bayashi/ljspeech_fastspeech2", "kan-bayashi/ljspeech_conformer_fastspeech2", "kan-bayashi/ljspeech_joint_finetune_conformer_fastspeech2_hifigan", "kan-bayashi/ljspeech_joint_train_conformer_fastspeech2_hifigan", "kan-bayashi/ljspeech_vits"] {type:"string"}
vocoder_tag = "parallel_wavegan/ljspeech_hifigan.v1"  # @param ["none", "parallel_wavegan/ljspeech_parallel_wavegan.v1", "parallel_wavegan/ljspeech_full_band_melgan.v2", "parallel_wavegan/ljspeech_multi_band_melgan.v2", "parallel_wavegan/ljspeech_hifigan.v1", "parallel_wavegan/ljspeech_style_melgan.v1"] {type:"string"}

from espnet2.bin.tts_inference import Text2Speech
from espnet2.utils.types import str_or_none

text2speech = Text2Speech.from_pretrained(
    model_tag=str_or_none(tag),
    vocoder_tag=str_or_none(vocoder_tag),
    device="cpu",
    # Only for Tacotron 2 & Transformer
    threshold=0.5,
    # Only for Tacotron 2
    minlenratio=0.0,
    maxlenratio=10.0,
    use_att_constraint=False,
    backward_window=1,
    forward_window=3,
    # Only for FastSpeech & FastSpeech2 & VITS
    speed_control_alpha=1.0,
    # Only for VITS
    noise_scale=0.333,
    noise_scale_dur=0.333,
)

import time
import torch

# Use a static string instead of an input
x = "This is a sample sentence."

# synthesis
start_time = time.time()

with torch.no_grad():
    start = time.time()
    wav = text2speech(x)["wav"]
rtf = (time.time() - start) / (len(wav) / text2speech.fs)
print(f"RTF = {rtf:5f}")

end_time = time.time()
print(f'Text-to-speech generation took {end_time - start_time} seconds')

# Save the generated samples to a WAV file
sf.write('output.wav', wav.view(-1).cpu().numpy(), text2speech.fs)

# Use playsound to play the saved WAV file
playsound('output.wav')
