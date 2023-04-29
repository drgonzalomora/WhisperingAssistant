import os
import time

from gptcache import cache, Config
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
from gptcache.embedding import OpenAI as OpenAIE, Onnx
from gptcache.adapter.langchain_models import LangChainLLMs

from langchain.llms import OpenAI

from whispering_assistant.configs.config import openai_key
from whispering_assistant.utils.performance import print_time_profile

os.environ["TOKENIZERS_PARALLELISM"] = "true"
os.environ["OPENAI_API_KEY"] = openai_key


# get the content(only question) form the prompt to cache
def get_msg_func(data, **_):
    print("datadata", data)
    print("datadata", data.get("prompt"))
    return data.get("prompt")


openaie = OpenAIE()
print(openaie.dimension)
onnx = Onnx()

data_manager = get_data_manager(CacheBase("sqlite"), VectorBase("faiss", dimension=openaie.dimension))
cache.init(
    pre_embedding_func=get_msg_func,
    embedding_func=openaie.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
    config=Config(
        similarity_threshold=1
    ),
)
cache.set_openai_key()

llm = LangChainLLMs(llm=OpenAI(temperature=0))

start_time = time.time()
result = llm("Tell me joke")
print(result)
print_time_profile(start_time, "1st")

start_time = time.time()
result = llm("make me laugh")
print(result)
print_time_profile(start_time, "2nd")
