import os
import time
from openai.embeddings_utils import cosine_similarity
import pandas as pd
from gptcache.embedding import Onnx
import numpy as np

from whispering_assistant.utils.performance import print_time_profile

os.environ["TOKENIZERS_PARALLELISM"] = "true"

onnx = Onnx()
max_tokens = 512
default_csv_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/text_with_embeddings_v1.csv"


# 📌 TODO: gptcache.embedding Once we have more time, we can try out other embedding models from this library.
def get_embedding(input_text):
    input_text_embedding = onnx.to_embeddings(input_text)
    # I do manual conversion because for some reason the saved data being saved is in string format and scientific
    # notation.
    formatted_input_text_embedding = [float('{:.8f}'.format(value)) for value in input_text_embedding]
    return formatted_input_text_embedding


def generate_index_csv(input_text=None, id_text=None, file_name=default_csv_name):
    processed_data = []

    input_text_embedding = get_embedding(input_text)

    processed_data.append({
        'id_text': id_text,
        'input_text': input_text,
        'embedding': input_text_embedding
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


def search_index_csv(search_text, n=3, pprint=True, file_name=default_csv_name):
    start_time = time.time()
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        df["embedding"] = df.embedding.apply(eval).apply(np.array)
    else:
        print(f"🛑 The file '{file_name}' does not exist. Generate an index first")
        return
    print_time_profile(start_time, "File Loading")

    start_time = time.time()
    search_text_embedding = get_embedding(search_text)

    df["similarity"] = df.embedding.apply(
        lambda x: cosine_similarity(x, search_text_embedding))
    print_time_profile(start_time, "Get Embedding")

    start_time = time.time()
    results_df = (
                     df.sort_values("similarity", ascending=False)
                     .head(n)
                 ).iloc[::-1].reset_index(drop=True)

    print_time_profile(start_time, "Cosine")

    top_result = None

    if pprint:
        for idx, row in results_df.iterrows():
            top_result = {column: row[column] for column in results_df.columns}
            print(f"Intent: {row['input_text'][:200]}")
            print(f"Cosine Similarity: {row['similarity']}\n")

    return top_result, results_df
