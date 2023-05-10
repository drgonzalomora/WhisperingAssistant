import os
import faiss

faiss_index_file_name = "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/faiss_index.idx"

# Create a Faiss index
dimension = 768  # The dimension of your embeddings
faiss_index = faiss.IndexFlatL2(dimension)


# Save the Faiss index to a file
def save_faiss_index(index, file_name=faiss_index_file_name):
    faiss.write_index(index, file_name)


# Load a Faiss index from a file
def load_faiss_index(file_name):
    return faiss.read_index(file_name)


def init_faiss_index():
    global faiss_index

    if os.path.exists(faiss_index_file_name):
        print("loading from local file faiss")
        faiss_index = load_faiss_index(faiss_index_file_name)
    else:
        save_faiss_index(faiss_index, faiss_index_file_name)

    return faiss_index
