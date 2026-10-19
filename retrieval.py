
import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# Find the project folder
BASE = Path(__file__).resolve().parent
INDEX_DIR = BASE / "data" / "index"

# Use the same model that created the index
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load the existing index and book passages
print("Loading book index...")

index = faiss.read_index(str(INDEX_DIR / "books.faiss"))

passages = []

with (INDEX_DIR / "passages.jsonl").open(
    "r", encoding="utf-8"
) as file:
    for line in file:
        if line.strip():
            passages.append(json.loads(line))

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

print("ChatBotAI retrieval system is ready!")


def search_books(question, limit=5):
    question = question.strip()

    if not question:
        return []

    # Convert the question into a vector
    question_vector = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    # Search for the most relevant passages
    scores, results = index.search(question_vector, limit)

    matches = []

    for score, position in zip(scores[0], results[0]):
        if position < 0:
            continue

        passage = passages[position]

        matches.append({
            "book": passage.get("book", "Unknown"),
            "page": passage.get("page", "Unknown"),
            "text": passage.get("text", ""),
            "score": float(score),
        })

    return matches


# Allow us to test the search directly
if __name__ == "__main__":
    while True:
        question = input("\nAsk a question about your books (or type exit): ")

        if question.lower().strip() == "exit":
            break

        results = search_books(question)

        if not results:
            print("Please enter a question.")
            continue

        for number, result in enumerate(results, start=1):
            print(f"\n--- Result {number} ---")
            print(f"Book: {result['book']}")
            print(f"Page: {result['page']}")
            print(f"Relevance score: {result['score']:.3f}")
            print(f"Text: {result['text']}")
