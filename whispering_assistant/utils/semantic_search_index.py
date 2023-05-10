import os
import time
import pandas as pd
import numpy as np
from whispering_assistant.configs.config import Instructor_DEVICE, Instructor_MODEL
from whispering_assistant.utils.embeddings_cache import query_embeddings_cache_db_name
from whispering_assistant.utils.performance import print_time_profile
from InstructorEmbedding import INSTRUCTOR
import sqlite3

from whispering_assistant.utils.vector_embeddings_storage import save_faiss_index, init_faiss_index

model = INSTRUCTOR(Instructor_MODEL, device=Instructor_DEVICE)

os.environ["TOKENIZERS_PARALLELISM"] = "true"

max_tokens = 512
default_csv_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/text_with_embeddings_v1.csv"

# 📌 TODO: Make the instructions dynamic based on the embeddings that will be processed.
query_instruction = 'Represent the prompt name for retrieving supporting documents: '
storing_instruction = 'Represent the prompt description document for retrieval: '

faiss_index = init_faiss_index()


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


def is_duplicate(existing_data_df, id_text):
    return id_text in existing_data_df['id_text'].values


def generate_index_csv(input_text=None, id_text=None, file_name=default_csv_name):
    # Get the embedding of the input text
    input_text_embedding = get_embedding(input_text, embedding_instruction=storing_instruction)

    # Add the embedding to the Faiss index
    faiss_index.add(np.array(input_text_embedding).astype('float32').reshape(1, -1))

    # Add the input text and id_text to a CSV file
    processed_data = [{'id_text': id_text, 'input_text': input_text}]

    new_data_df = pd.DataFrame(processed_data)

    try:
        existing_data_df = pd.read_csv(file_name, index_col=0)
        if not is_duplicate(existing_data_df, id_text):
            updated_data_df = pd.concat([existing_data_df, new_data_df], ignore_index=True)
        else:
            print("The given data is already present in the CSV")
            updated_data_df = existing_data_df
    except FileNotFoundError:
        updated_data_df = new_data_df

    save_faiss_index(faiss_index, file_name)
    updated_data_df.to_csv(file_name)

    csv_row_count = len(updated_data_df)

    print("index count faiss", faiss_index.ntotal)
    print("index count csv", csv_row_count)
    print("index count should match!", faiss_index.ntotal == csv_row_count)


def search_index_csv(search_text, n=3, pprint=True, file_name=default_csv_name, similarity_threshold=0.85):
    start_time = time.time()
    if os.path.exists(file_name):
        metadata_df = pd.read_csv(file_name)
    else:
        print(f"🛑 The file '{file_name}' does not exist. Generate an index first")
        return

    print_time_profile(start_time, "File Loading")

    start_time = time.time()
    search_text_embedding = get_embedding(search_text)
    search_text_embedding = np.array(search_text_embedding).astype('float32').reshape(1,
                                                                                      -1)  # Convert to 2D NumPy array
    print_time_profile(start_time, "Get Embedding")

    # Search the Faiss index for the top n most similar embeddings
    start_time = time.time()
    distances, indices = faiss_index.search(search_text_embedding, n)
    # Get the corresponding metadata from the CSV file
    results_df = metadata_df.iloc[indices[0]].copy()
    results_df['similarity'] = 1 - distances[0] / 2  # Convert Euclidean distance to cosine similarity

    # reversed the order so we will just add the last item as the top result
    reversed_df = results_df.iloc[::-1]
    print_time_profile(start_time, "Search Faiss")

    top_result = None

    if pprint:
        for idx, row in reversed_df.iterrows():
            if row['similarity'] > similarity_threshold:
                top_result = {column: row[column] for column in results_df.columns}
            print(f"Intent: {row['input_text'][:200]}")
            print(f"Cosine Similarity: {row['similarity']}\n")

    return top_result, results_df
