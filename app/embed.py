from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Function to generate embeddings
def generate_embeddings(texts):

    embeddings = model.encode(texts)

    return embeddings


# Test embedding generation
if __name__ == "__main__":

    from app.chunking import load_and_chunk_documents

    # Load document chunks
    documents = load_and_chunk_documents()

    # Extract text from chunks
    texts = [doc["text"] for doc in documents]

    # Generate embeddings
    embeddings = generate_embeddings(texts)

    print("Total chunks:", len(texts))
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))
    print("\nFirst embedding:")
    print(embeddings[0][:10])
