from pathlib import Path
from bs4 import BeautifulSoup
import re


# Project folder
base_path = Path(__file__).resolve().parent.parent


# Function to extract text from HTML
def read_html(file_path):

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Get document title
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    else:
        title = file_path.stem.replace("_", " ").title()

    # Remove unnecessary HTML elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)

    return text, title


# Function to extract text from Markdown
def read_markdown(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Get title from first heading
    match = re.search(r"^#\s+(.+)", text, re.MULTILINE)

    if match:
        title = match.group(1).strip()
    else:
        title = file_path.stem.replace("_", " ").title()

    return text, title


# Function to divide text into chunks
def create_chunks(text, chunk_size=400, overlap=50):
    
    words = text.split()
    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# Function to process all documents
def load_and_chunk_documents():

    documents = []

    folders = [
    base_path / "data" / "raw"
]

    for folder in folders:

        for file_path in folder.iterdir():

            if file_path.suffix.lower() == ".html":
                text, title = read_html(file_path)

            elif file_path.suffix.lower() == ".md":
                text, title = read_markdown(file_path)

            else:
                continue

            chunks = create_chunks(text)

            for chunk in chunks:

                documents.append({
                    "text": chunk,
                    "source": file_path.name,
                    "page": None,
                    "title": title
                })

    return documents


# Test the chunking process
if __name__ == "__main__":

    chunks = load_and_chunk_documents()

    print("Total chunks created:", len(chunks))

    for chunk in chunks[:3]:

        print("\nTitle:", chunk["title"])
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("Text:", chunk["text"][:200])