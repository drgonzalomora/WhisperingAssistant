import time

from datasets import load_dataset, Audio
from transformers import Wav2Vec2ForCTC, AutoProcessor
import torch

from transformers import AutoModelForCausalLM, AutoTokenizer

# English
stream_data = load_dataset("mozilla-foundation/common_voice_13_0", "en", split="test", streaming=True)
stream_data = stream_data.cast_column("audio", Audio(sampling_rate=16000))
en_sample = next(iter(stream_data))["audio"]["array"]

model_id = "facebook/mms-1b-all"

processor = AutoProcessor.from_pretrained(model_id)
model = Wav2Vec2ForCTC.from_pretrained(model_id, device_map="auto")

start_time = time.time()
inputs = processor(en_sample, sampling_rate=16_000, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs).logits

ids = torch.argmax(outputs, dim=-1)[0]
transcription = processor.decode(ids)

end_time = time.time()
print(f'Took {end_time - start_time} seconds')

# CPU @ ~1.7s
print("transcription", transcription)

