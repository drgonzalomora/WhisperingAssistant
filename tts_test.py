import nltk
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


def tts_simple(input_text):
    # sample: As an AI language model, I don't have feelings, but I'm functioning properly and ready to assist you with any questions or tasks you may have. How can I help you today?

    sample = TTSHubInterface.get_model_input(task, input_text)

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


def tts_phrase_by_phrase(input_text):
    # Split the input text into sentences
    sentences = nltk.tokenize.sent_tokenize(input_text)

    for i, sentence in enumerate(sentences):
        print(f'Processing sentence {i + 1} of {len(sentences)}')

        # Get the model input for this sentence
        sample = TTSHubInterface.get_model_input(task, sentence)

        # Generate the speech audio for this sentence
        start_time = time.time()
        wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)
        end_time = time.time()

        print(f'Text-to-speech generation for sentence {i + 1} took {end_time - start_time} seconds')

        # Save the output wav file for this sentence
        output_file = f'tts_output_{i + 1}.wav'
        sf.write(output_file, wav, rate)

        # Play the output file for this sentence
        playsound(output_file)