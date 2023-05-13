import os
import faiss

# Create a Faiss index
dimension = 768  # The dimension of your embeddings
faiss_index = None


# Load a Faiss index from a file
def load_faiss_index(file_name):
    return faiss.read_index(file_name)


def init_faiss_index(faiss_index_file_name):
    global faiss_index

    faiss_index = faiss.IndexFlatL2(dimension)

    def save_faiss_index(index):
        faiss.write_index(index, faiss_index_file_name)

    if os.path.exists(faiss_index_file_name):
        print("loading from local file faiss")
        faiss_index = load_faiss_index(faiss_index_file_name)
    else:
        save_faiss_index(faiss_index)

    return faiss_index, save_faiss_index
