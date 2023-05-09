import os
import time
from openai.embeddings_utils import cosine_similarity
import pandas as pd
import numpy as np
from whispering_assistant.configs.config import Instructor_DEVICE, Instructor_MODEL
from whispering_assistant.utils.performance import print_time_profile
from InstructorEmbedding import INSTRUCTOR
import sqlite3

model = INSTRUCTOR(Instructor_MODEL, device=Instructor_DEVICE)

os.environ["TOKENIZERS_PARALLELISM"] = "true"

max_tokens = 512
default_csv_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/text_with_embeddings_v1.csv"

# 📌 TODO: Make the instructions dynamic based on the embeddings that will be processed.
query_instruction = 'Represent the prompt name for retrieving supporting documents: '
storing_instruction = 'Represent the prompt description document for retrieval: '

query_embeddings_cache_db_name = "query_embeddings_cache.db"


def create_embedding_database():
    conn = sqlite3.connect(query_embeddings_cache_db_name)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS embeddings
    (input_text TEXT PRIMARY KEY,
    embedding BLOB)
    """)
    conn.commit()
    conn.close()


create_embedding_database()


def get_embedding(input_text, embedding_instruction=query_instruction):
    # Check if the input_text already exists in the cache
    with sqlite3.connect(query_embeddings_cache_db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT embedding FROM embeddings WHERE input_text=?", (input_text,))
        cached_embedding = cursor.fetchone()

        if cached_embedding is not None:
            print('returning a cached get_embedding')
            # Load the cached embedding from the database
            return np.frombuffer(cached_embedding[0], dtype=np.float32).tolist()

    # If the input_text is not in the cache, calculate the embedding
    input_text_embedding = model.encode([[embedding_instruction, input_text]])

    # Cache the calculated embedding
    with sqlite3.connect(query_embeddings_cache_db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO embeddings (input_text, embedding) VALUES (?, ?)",
                       (input_text, input_text_embedding.tobytes()))
        conn.commit()

    return np.frombuffer(input_text_embedding.tobytes(), dtype=np.float32).tolist()


# 📌 TODO: Move the storage to a proper vector database instead of storing it in just a csv file.
def generate_index_csv(input_text=None, id_text=None, file_name=default_csv_name):
    processed_data = []

    input_text_embedding = get_embedding(input_text, embedding_instruction=storing_instruction)

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


def search_index_csv(search_text, n=3, pprint=True, file_name=default_csv_name, similarity_threshold=0.85):
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
    print_time_profile(start_time, "Get Embedding")

    start_time = time.time()
    df["similarity"] = df.embedding.apply(
        lambda x: cosine_similarity(x, search_text_embedding))
    results_df = (
                     df.sort_values("similarity", ascending=False)
                     .head(n)
                 ).iloc[::-1].reset_index(drop=True)

    print_time_profile(start_time, "Cosine")

    top_result = None

    if pprint:
        for idx, row in results_df.iterrows():
            if row['similarity'] > similarity_threshold:
                top_result = {column: row[column] for column in results_df.columns}
            print(f"Intent: {row['input_text'][:200]}")
            print(f"Cosine Similarity: {row['similarity']}\n")

    return top_result, results_df
