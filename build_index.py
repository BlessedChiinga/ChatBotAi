import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data" / "processed" / "pages.jsonl"
INDEX_DIR = BASE / "data" / "index"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
BATCH_SIZE = 32


def split_text(text):
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Book data not found: {DATA_FILE}"
        )

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    passages = []

    print("Reading book records...")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            text = record.get("text", "")

            for chunk in split_text(text):
                passages.append({
                    "book": record.get("book", "Unknown"),
                    "page": record.get("page", "Unknown"),
                    "text": chunk,
                })

    if not passages:
        raise ValueError("No searchable text was found.")

    print("Passages prepared:", len(passages))
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    vectors = model.encode(
        [item["text"] for item in passages],
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    vectors = np.asarray(vectors, dtype=np.float32)

    print("Building FAISS index...")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(
        index,
        str(INDEX_DIR / "books.faiss"),
    )

    with (INDEX_DIR / "passages.jsonl").open(
        "w", encoding="utf-8"
    ) as file:
        for passage in passages:
            file.write(
                json.dumps(passage, ensure_ascii=False) + "\n"
            )

    print("\n========== INDEX REPORT ==========")
    print("Searchable passages:", len(passages))
    print("Embedding dimensions:", vectors.shape[1])
    print("FAISS vectors:", index.ntotal)
    print("Index folder:", INDEX_DIR)


if __name__ == "__main__":
    main()