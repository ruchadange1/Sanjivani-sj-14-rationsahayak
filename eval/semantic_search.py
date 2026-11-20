from pathlib import Path

from app.vectorstore import collection, index_documents, semantic_search

# Project folder
base_path = Path(__file__).resolve().parent.parent


# 10 RationSahayak questions
questions = [
    "How much grain does an AAY card get?",
    "Can I use my Beed ration card in Kopargaon?",
    "What is the PHH grain entitlement?",
    "Where can I complain about receiving less ration?",
    "My family has five members and a PHH card. How much grain should we receive every month?",
    "How many kilograms of rice and wheat did my family actually collect from our fair price shop last month?",
    "What documents are required to apply for a new ration card in Maharashtra?",
    "What should I do if biometric authentication fails at the ration shop?",
    "Can I use my Maharashtra ration card in another state under ONORC?",
    "What benefits are available under NFSA for pregnant women and children?"
]


# Check whether documents are indexed
if collection.count() == 0:
    index_documents()


# Store search results
report = []

report.append("# RationSahayak Semantic Search Results\n")
report.append("## Objective\n")
report.append(
    "To test semantic search using 10 real RationSahayak user questions "
    "and retrieve relevant document chunks from ChromaDB.\n"
)

for number, question in enumerate(questions, start=1):

    print("\nTesting:", question)

    # Perform semantic search
    results = semantic_search(question, top_k=3)

    report.append(f"\n## Question {number}: {question}\n")

    for i in range(len(results["documents"][0])):

        text = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        report.append(f"### Result {i + 1}\n")
        report.append(f"- **Source:** {metadata['source']}\n")
        report.append(f"- **Title:** {metadata['title']}\n")

        page = metadata["page"]
        report.append(
            f"- **Page:** {'Not available' if page == -1 else page}\n"
        )

        report.append(f"- **Distance:** {distance:.4f}\n")
        report.append(f"- **Retrieved text:** {text[:350]}...\n")

    print("Results retrieved:", len(results["documents"][0]))


# Save search results
output_file = base_path / "eval" / "search_results.md"

with open(output_file, "w", encoding="utf-8") as file:
    file.writelines(report)

print("\nSemantic search evaluation completed!")
print("Questions tested:", len(questions))
print("Results saved to:", output_file)
