import numpy as np

# Model will initially remain unloaded
model = None


def get_model():
    global model

    if model is None:
        from fastembed import TextEmbedding

        model = TextEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return model


def generate_embeddings(texts):
    embedding_model = get_model()

    embeddings = list(
        embedding_model.embed(
            texts,
            batch_size=8
        )
    )

    return np.array(embeddings)


if __name__ == "__main__":
    from app.chunking import load_and_chunk_documents

    documents = load_and_chunk_documents()
    texts = [doc["text"] for doc in documents]

    embeddings = generate_embeddings(texts)

    print("Total chunks:", len(texts))
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))

    print("\nFirst embedding:")
    print(embeddings[0][:10])