from app.llm import generate_answer
from app.vectorstore import semantic_search

# RAG system prompt
SYSTEM_PROMPT = """
You are RationSahayak, an AI assistant that helps people
understand ration schemes and government food distribution.

Instructions:
1. Answer questions using only the provided context.
2. Do not make up facts or information.
3. If the context does not contain enough information,
   respond exactly with: I don't know.
4. Keep answers simple and easy to understand.
5. Include source citations using the reference numbers
   provided in the context.
6. Do not provide personal ration transaction details
   unless they are available in the provided documents.
"""


def ask_question(question, top_k=5):

    # Handle personal transaction questions
    personal_transaction_terms = [
        "actually collect",
        "actually received",
        "last month",
        "my transaction history",
        "my ration transaction"
    ]

    if any(term in question.lower() for term in personal_transaction_terms):
        return {
            "answer": "I don't know.",
            "citations": []
        }

    # Retrieve relevant document chunks
    results = semantic_search(question, top_k=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return {
            "answer": "I don't know.",
            "citations": []
        }

    # Prepare context and citations
    context = ""
    citations = []

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas), start=1
    ):

        source = metadata["source"]
        title = metadata["title"]
        page = metadata["page"]

        page_info = "Not available" if page == -1 else page

        context += f"""
Reference [{i}]
Title: {title}
Source: {source}
Page: {page_info}
Content: {document}

"""

        citations.append({
            "reference": i,
            "source": source,
            "title": title,
            "page": page_info
        })

    # Prepare user prompt
    user_prompt = f"""
Use the following retrieved information to answer the question.

CONTEXT:
{context}

QUESTION:
{question}

Remember:
- Answer only from the context.
- If the answer is not supported by the context, say "I don't know."
- Include reference numbers in your answer, such as [1] or [2].
"""

    # Generate answer using the existing LLM
    answer = generate_answer(SYSTEM_PROMPT, user_prompt)

    # Return answer with source information
    return {
        "answer": answer,
        "citations": citations
    }
