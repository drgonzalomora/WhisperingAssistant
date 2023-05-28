from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface
import soundfile as sf
from playsound import playsound
import time

models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
    "facebook/fastspeech2-en-ljspeech",
    arg_overrides={"vocoder": "none", "fp16": False, "cpu": True}
)

model = models[0]
TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
generator = task.build_generator([model], cfg)

print('generator', generator)

text = "Hello, this is a test run."

sample = TTSHubInterface.get_model_input(task, text)

print('sample', sample)

start_time = time.time()
wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)
end_time = time.time()
print(f'Text-to-speech generation took {end_time - start_time} seconds')

print('wav', wav)

# Save the output wav file
output_file = 'tts_output.wav'
sf.write(output_file, wav, rate)

# Play the output file
playsound(output_file)
