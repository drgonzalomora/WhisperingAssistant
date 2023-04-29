import time

import pandas as pd
import tiktoken
import openai
from openai.embeddings_utils import get_embedding
import os
import json
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import yaml
import pandas as pd
import json
from gptcache.embedding import OpenAI as OpenAIE, Onnx
import numpy as np

onnx = Onnx()

from whispering_assistant.configs.config import openai_key
from whispering_assistant.utils.performance import print_time_profile

print("openai_key", openai_key)

os.environ["OPENAI_API_KEY"] = openai_key
openai.api_key = openai_key

# embedding model parameters
embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191

# df = pd.read_csv('intents_with_embeddings_v3.csv')
# df["embedding"] = df.embedding.apply(eval).apply(np.array)


def parse_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def generate_index_csv(input_text, file_name="intents_with_embeddings_v3.csv"):
    processed_data = []

    # intent_embedding = get_embedding(input_text, engine=embedding_model)
    intent_embedding = onnx.to_embeddings(input_text)
    formatted_list = [float('{:.8f}'.format(value)) for value in intent_embedding]

    print("intent_embedding", intent_embedding)
    # print("formatted_list", formatted_list)

    processed_data.append({
        'input_text': input_text,
        'embedding': formatted_list
    })

    # Convert the list of processed data to a DataFrame
    new_data_df = pd.DataFrame(processed_data)

    try:
        # If the CSV file exists, read it and append the new data to it
        existing_data_df = pd.read_csv(file_name, index_col=0)
        updated_data_df = existing_data_df.append(new_data_df, ignore_index=True)
    except FileNotFoundError:
        # If the CSV file does not exist, use the new data as the updated data
        updated_data_df = new_data_df

    # Save the resulting DataFrame to a CSV file
    updated_data_df.to_csv(file_name)


def search_index_csv(product_description, n=3, pprint=True):
    df = pd.read_csv('intents_with_embeddings_v3.csv')
    df["embedding"] = df.embedding.apply(eval).apply(np.array)

    start_time = time.time()
    # product_embedding = get_embedding(
    #     product_description,
    #     engine="text-embedding-ada-002"
    # )
    product_embedding = onnx.to_embeddings(product_description)

    df["similarity"] = df.embedding.apply(
        lambda x: cosine_similarity(x, product_embedding))
    print_time_profile(start_time, "Get Emb")

    start_time = time.time()
    results_df = (
        df.sort_values("similarity", ascending=False)
        .head(n)
    )
    print_time_profile(start_time, "Cosine")

    if pprint:
        for idx, row in results_df.iterrows():
            print(f"Intent: {row['input_text'][:200]}")
            print(f"Cosine Similarity: {row['similarity']}\n")

    return results_df


start_time = time.time()
generate_index_csv("I've changed the volume to 5%")
# search_index_csv("war cannot be predicted")
# search_index_csv("decrease the volume to 5%")
print_time_profile(start_time, "Final")
