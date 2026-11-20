import json
from pathlib import Path

import chromadb

from app.chunking import load_and_chunk_documents
from app.embed import generate_embeddings

# Project paths
base_path = Path(__file__).resolve().parent.parent

eval_path = base_path / "eval" / "eval_set.json"

results_path = (
    base_path / "eval" / "evaluation_results.json"
)


# Load evaluation questions
with open(eval_path, "r", encoding="utf-8") as file:
    questions = json.load(file)


# Two configurations
configurations = [
    {
        "name": "Config 1",
        "chunk_size": 400,
        "top_k": 3
    },
    {
        "name": "Config 2",
        "chunk_size": 600,
        "top_k": 5
    }
]


# Function to evaluate one configuration
def evaluate_config(config):

    print("\nRunning:", config["name"])

   # Create a separate collection for each configuration
    client = chromadb.Client()

    collection_name = (
        f"evaluation_{config['chunk_size']}_{config['top_k']}"
    )

    collection = client.get_or_create_collection(
        name=collection_name
    )

    # Remove old records if the evaluation is run again
    if collection.count() > 0:
        collection.delete(
            ids=collection.get()["ids"]
        )

    # Load documents with selected chunk size
    documents = load_and_chunk_documents(
        chunk_size=config["chunk_size"]
    )
    # Load documents with selected chunk size
    documents = load_and_chunk_documents(
        chunk_size=config["chunk_size"]
    )

    texts = [doc["text"] for doc in documents]

    # Generate embeddings
    embeddings = generate_embeddings(texts)

    ids = [
        f"chunk_{i}"
        for i in range(len(documents))
    ]

    metadatas = [
        {
            "source": doc["source"],
            "title": doc["title"],
            "page": -1
        }
        for doc in documents
    ]

    # Add documents to ChromaDB
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Chunks indexed:", collection.count())

    relevant_answers = 0
    citation_available = 0

    question_results = []

    # Test all evaluation questions
    for item in questions:

        question = item["question"]

        expected_keywords = item["expected_keywords"]

        print("\nTesting:", question)

        # Generate query embedding
        query_embedding = generate_embeddings([question])

        # Retrieve relevant chunks
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(
                config["top_k"],
                collection.count()
            )
        )

        retrieved_docs = results["documents"][0]

        retrieved_metadata = results["metadatas"][0]

        # Combine retrieved text
        retrieved_text = " ".join(
            retrieved_docs
        ).lower()

        # Match expected keywords
        matched_keywords = [
            keyword
            for keyword in expected_keywords
            if keyword.lower() in retrieved_text
        ]

        # Evaluate answerable questions
        if item["answerable"]:

            retrieval_relevant = (
                len(matched_keywords) > 0
            )

            if retrieval_relevant:
                relevant_answers += 1

        else:

            # Q6 is expected to be unanswerable.
            # Record it separately for manual verification.
            retrieval_relevant = None

        # Check source metadata availability
        has_citation = (
            len(retrieved_metadata) > 0
        )

        if has_citation:
            citation_available += 1

        # Save individual question result
        question_results.append({

            "id": item["id"],

            "question": question,

            "answerable": item["answerable"],

            "expected_keywords": expected_keywords,

            "matched_keywords": matched_keywords,

            "retrieval_relevant": retrieval_relevant,

            "citation_available": has_citation,

            "retrieved_sources": [
                metadata["source"]
                for metadata in retrieved_metadata
            ]
        })

        print("Matched keywords:", matched_keywords)

        print("Retrieval relevant:", retrieval_relevant)

        print("Citation available:", has_citation)

    # Calculate metrics
    total_questions = len(questions)

    answerable_count = sum(
        1 for item in questions
        if item["answerable"]
    )

    retrieval_accuracy = round(
        relevant_answers / answerable_count * 100,
        2
    )

    citation_rate = round(
        citation_available / total_questions * 100,
        2
    )

    # Configuration summary
    summary = {

        "name": config["name"],

        "chunk_size": config["chunk_size"],

        "top_k": config["top_k"],

        "total_chunks": len(documents),

        "total_questions": total_questions,

        "answerable_questions": answerable_count,

        "relevant_answers": relevant_answers,

        "retrieval_accuracy": retrieval_accuracy,

        "citation_available": citation_available,

        "citation_rate": citation_rate,

        "question_results": question_results
    }

    return summary


# Run both configurations
all_results = []

for config in configurations:

    result = evaluate_config(config)

    all_results.append(result)

    print("\nCompleted:", config["name"])

    print(
        "Retrieval accuracy:",
        result["retrieval_accuracy"],
        "%"
    )

    print(
        "Citation rate:",
        result["citation_rate"],
        "%"
    )


# Save evaluation results
with open(
    results_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_results,
        file,
        indent=4,
        ensure_ascii=False
    )


print("\nEvaluation completed!")

print(
    "Results saved to:",
    results_path
)