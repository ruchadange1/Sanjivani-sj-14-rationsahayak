# RationSahayak – Interview Preparation

## 1. My 60-Second Project Pitch

Hello, my project is **RationSahayak – an AI-Powered Ration Assistance System for Maharashtra**.

The main problem I wanted to solve is that ration card holders often find it difficult to understand government ration rules, calculate their monthly foodgrain entitlement, and verify whether they have received the correct quantity.

To address this, I developed a web application using **Python, FastAPI, Streamlit, Retrieval-Augmented Generation, ChromaDB, FastEmbed, and Groq**.

The application has an AI assistant that answers ration-related questions using government documents and provides source citations. It also includes a monthly ration calculator for AAY and PHH cards, e-PoS quantity verification, downloadable ration slips, and user feedback.

I also worked on production readiness by implementing response caching, input validation, LLM latency and token monitoring, and prompt-injection safeguards. I added automated tests, Docker support, GitHub Actions CI, and deployed the application on Render.

The main goal of RationSahayak is to make ration-related information easier to understand, accessible, and supported by reliable sources.

---

## 2. Ten Likely Interview Questions and Answers

### Q1. What problem does RationSahayak solve?

RationSahayak helps people understand ration-related government schemes, check their expected monthly foodgrain entitlement, and compare it with the quantity they actually received.

Instead of searching through multiple government documents, users can ask questions in the AI assistant and receive answers with source citations.

### Q2. Why did you choose RAG instead of a normal chatbot?

A normal chatbot may generate answers from its general training knowledge, which can be outdated or inaccurate.

RAG retrieves relevant information from our indexed government documents before generating an answer. This helps ground the response in the available documents and allows us to show source citations.

### Q3. Explain the RAG workflow in your project.

The workflow is:

1. The user submits a question through Streamlit.
2. FastAPI receives the question.
3. FastEmbed converts the question into an embedding.
4. ChromaDB retrieves relevant document chunks.
5. The retrieved context is passed to the Groq LLM.
6. The LLM generates an answer based on the retrieved information.
7. The application returns the answer with source citations.

### Q4. What was the hardest problem you faced?

The hardest problem was handling changing government rules and overlapping Central and Maharashtra State ration policies.

For example, historical issue-price rules included different rates such as ₹3, ₹2, and ₹1 per kg. Later, free foodgrain provisions under PMGKAY introduced another policy period. At the same time, Central categories such as AAY and PHH and Maharashtra-specific categories such as saffron and white ration cards have different eligibility considerations.

A chatbot can easily mix these rules if it retrieves information without considering dates and authority.

My approach is to identify the applicable scheme, authority, and effective date before answering. The system should prioritize the latest applicable notification and clearly state whether the information comes from the Central Government or Maharashtra State Government.

### Q5. How would you handle conflicting government notifications?

I would use a structured approach:

1. Identify the subject and applicable scheme.
2. Identify the issuing authority: Central or Maharashtra State.
3. Check the notification's publication date and effective date.
4. Determine whether the notification is still applicable or has been superseded.
5. Prefer the latest applicable notification within the relevant rule scope.
6. Show the source document and authority in the answer.

If the available documents do not establish which rule applies, the chatbot should clearly communicate that uncertainty rather than inventing an answer.

### Q6. What is the difference between AAY and PHH?

AAY stands for Antyodaya Anna Yojana, while PHH stands for Priority Household.

In the entitlement calculation used by RationSahayak:

- AAY: 35 kg per household per month.
- PHH: 5 kg per person per month.

For example, a PHH household with four members has an expected entitlement of 20 kg per month under this calculation.

### Q7. What is ChromaDB, and why did you use it?

ChromaDB is a vector database used to store and retrieve document embeddings.

In RationSahayak, government documents are divided into smaller chunks and converted into embeddings using FastEmbed. ChromaDB stores these embeddings and retrieves semantically relevant chunks when a user asks a question.

This makes it possible to find relevant information even when the user's wording differs from the wording in the source document.

### Q8. How did you improve the application's performance?

I introduced response caching using Cachetools. Repeated or normalized equivalent questions can reuse a cached response for up to 10 minutes.

I also added LLM monitoring to record request latency, input tokens, output tokens, total tokens, and request status.

For input validation, I added a maximum question length of 1,000 characters. These changes help improve efficiency, observability, and input handling.

### Q9. How did you test and deploy the project?

I used Pytest for automated testing and Ruff for code-quality checks.

The GitHub Actions workflow automatically runs code-quality checks, tests, and a Docker build verification.

I containerized the application using Docker and deployed the frontend and backend as separate services on Render.

The deployed backend also has a health-check endpoint, and I verified that the frontend can communicate with the backend and retrieve AI answers with citations.

### Q10. What are the limitations and future improvements?

Some limitations are that the accuracy of answers depends on the quality, completeness, and freshness of the indexed government documents. The application also provides estimates and verification assistance; it is not an official government entitlement confirmation.

Future improvements include:

- Regularly updating the government notification database.
- Adding structured metadata for authority, publication date, and effective date.
- Improving conflict resolution between Central and State rules.
- Expanding multilingual support.
- Adding more evaluation questions and testing answer correctness.
- Improving deployment persistence, monitoring, and scalability.

---

## 3. Important Technical Concepts to Revise

| Concept | What I should be able to explain |
|---|---|
| RAG | Retrieval followed by context-based answer generation |
| Embeddings | Numerical representation of text meaning |
| FastEmbed | Generates embeddings for semantic search |
| ChromaDB | Stores and retrieves vector embeddings |
| Groq | LLM inference provider used for answer generation |
| FastAPI | Backend API framework |
| Streamlit | Frontend application framework |
| Docker | Packages the application and dependencies |
| GitHub Actions | Automates testing and build checks |
| Pytest | Automated testing framework |
| Cachetools | Provides in-memory response caching |
| Pydantic | Validates API request data |

---

## 4. My Hardest-Problem Story: Short Version

If the interviewer asks, "What was your biggest technical challenge?", I can say:

"The biggest challenge was not just generating answers, but making sure the answers reflected changing government policies. Historical ration issue prices, free-grain provisions, and overlapping Central and Maharashtra State eligibility categories could cause confusion.

I realized that semantic similarity alone is not enough for government-policy questions. The system also needs to consider the issuing authority, notification date, effective date, and applicable scheme.

My design approach is to retrieve the relevant documents, identify their authority and validity, prioritize the latest applicable notification, and show the source level clearly. If the evidence is insufficient, the chatbot should communicate that instead of guessing."

---

## 5. Final Interview Reminders

- Explain the project in your own words rather than memorizing every sentence.
- Be ready to draw the RAG architecture.
- Explain one complete question-answer flow.
- Be able to explain why you chose FastEmbed and ChromaDB.
- Clearly distinguish implemented features from planned improvements.
- Do not claim that every policy conflict is already automatically resolved unless you have tested that functionality.
- Explain that source citations help users verify answers, but do not guarantee that every generated answer is correct.
