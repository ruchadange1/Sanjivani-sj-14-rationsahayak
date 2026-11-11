from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Function to search records using TF-IDF
def smart_search(records, query):

    documents = []

    # Combining record information into text
    for record in records:

        text = (
            record["topic"] + " " +
            record["rule"] + " " +
            record["card_type"] + " " +
            record["quantity_or_limit"] + " " +
            record["authority"]
        )

        documents.append(text)

    # Converting text into numerical values
    vectorizer = TfidfVectorizer()

    record_vectors = vectorizer.fit_transform(documents)

    # Converting user query into numerical values
    query_vector = vectorizer.transform([query])

    # Calculating similarity
    similarity = cosine_similarity(query_vector, record_vectors)

    # Sorting records according to similarity score
    scores = similarity[0]

    result = []

    for i in range(len(scores)):

        if scores[i] > 0:

            record = records[i].copy()
            record["id"] = i + 1
            record["score"] = round(float(scores[i]), 3)

            result.append(record)

    # Highest similarity score first
    result.sort(key=lambda x: x["score"], reverse=True)

    return result