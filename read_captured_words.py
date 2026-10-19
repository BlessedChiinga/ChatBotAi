import json
from pathlib import Path
from collections import Counter

# Location of the extracted book pages
INPUT_FILE = Path("data/processed/pages.jsonl")

# Location for the processed word records
OUTPUT_FILE = Path("data/processed/words.jsonl")

def main():
    if not INPUT_FILE.exists():
        print("ERROR: pages.jsonl was not found.")
        print("Check that you are in the project folder.")
        return

    total_pages = 0
    total_words = 0
    empty_pages = 0
    short_pages = []
    word_counts = Counter()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("r", encoding="utf-8") as source, \
         OUTPUT_FILE.open("w", encoding="utf-8") as output:

        for line in source:
            if not line.strip():
                continue

            page_record = json.loads(line)
            text = page_record.get("text", "").strip()

            total_pages += 1

            if not text:
                empty_pages += 1
                continue

            # Split the extracted text into words in their original order
            words = text.split()
            total_words += len(words)

            if len(text) < 50:
                short_pages.append({
                    "book": page_record.get("book", "Unknown"),
                    "page": page_record.get("page", "Unknown"),
                    "characters": len(text),
                    "words": len(words),
                    "text": text
                })

            # Save each page's words in their original order
            word_record = {
                "book": page_record.get("book", "Unknown"),
                "page": page_record.get("page", "Unknown"),
                "word_count": len(words),
                "words": words
            }

            output.write(
                json.dumps(word_record, ensure_ascii=False) + "\n"
            )

            # Count the words for a basic summary
            word_counts.update(words)

    print("\n========== WORD PROCESSING REPORT ==========")
    print("Pages read:", total_pages)
    print("Total words processed:", total_words)
    print("Empty text records:", empty_pages)
    print("Pages with fewer than 50 characters:", len(short_pages))
    print("Unique words:", len(word_counts))
    print("Saved word records to:", OUTPUT_FILE)

    if short_pages:
        print("\n========== FIRST 30 SHORT PAGES ==========")

        for page in short_pages[:30]:
            print(
                f"{page['book']} | Page {page['page']} | "
                f"{page['words']} words | "
                f"{page['characters']} characters | "
                f"{page['text']!r}"
            )

    print("\nWord processing completed.")


if __name__ == "__main__":
    main()