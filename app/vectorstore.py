import chromadb
from pathlib import Path

from app.chunking import load_and_chunk_documents
from app.embed import generate_embeddings


# Project folder
base_path = Path(__file__).resolve().parent.parent

# Create persistent ChromaDB client
client = chromadb.PersistentClient(
    path=str(base_path / "data" / "chroma_db")
)

# Create or access collection
collection = client.get_or_create_collection(
    name="rationsahayak_documents"
)


# Function to index document chunks
def index_documents():
    
        # Remove old records before rebuilding the collection
    if collection.count() > 0:
        collection.delete(
            ids=collection.get()["ids"]
        )
        
    documents = load_and_chunk_documents()

    texts = [doc["text"] for doc in documents]

    embeddings = generate_embeddings(texts)

    ids = [f"chunk_{i}" for i in range(len(documents))]

    metadatas = [
        {
            "source": doc["source"],
            "page": doc["page"] if doc["page"] is not None else -1,
            "title": doc["title"]
        }
        for doc in documents
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Documents indexed:", collection.count())


# Function to perform semantic search
def semantic_search(query, top_k=5):

    query_embedding = generate_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k
    )

    return results


# Test the vector database
if __name__ == "__main__":

    index_documents()

    query = "What is ONORC?"

    results = semantic_search(query)

    print("\nSearch results:")

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        print("\nTitle:", metadata["title"])
        print("Source:", metadata["source"])
        print("Page:", metadata["page"])
        print("Distance:", distance)
        print("Text:", document[:200])
