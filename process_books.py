from pathlib import Path
import json
import pymupdf

BOOKS_DIR = Path("data/books")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

all_pages = []

pdf_files = sorted(BOOKS_DIR.glob("*.pdf"))

for pdf_path in pdf_files:
    print(f"Reading: {pdf_path.name}")

    try:
        with pymupdf.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if text:
                    all_pages.append({
                        "book": pdf_path.stem,
                        "page": page_number,
                        "text": text
                    })

    except Exception as error:
        print(f"Could not process {pdf_path.name}: {error}")

output_file = OUTPUT_DIR / "pages.jsonl"

with output_file.open("w", encoding="utf-8") as file:
    for item in all_pages:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"\nPDF files found: {len(pdf_files)}")
print(f"Pages with extracted text: {len(all_pages)}")
print(f"Saved to: {output_file}")