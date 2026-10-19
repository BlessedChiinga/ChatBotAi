import json
from pathlib import Path
import fitz

# Folders and files
BOOKS_FOLDER = Path("data/books")
PAGES_FILE = Path("data/processed/pages.jsonl")

def main():
    if not BOOKS_FOLDER.exists():
        print("ERROR: The data/books folder was not found.")
        return

    if not PAGES_FILE.exists():
        print("ERROR: pages.jsonl was not found.")
        return

    # Record every extracted book page
    extracted_pages = set()

    with PAGES_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            book = record.get("book")
            page = record.get("page")

            if book is not None and page is not None:
                extracted_pages.add((book, int(page)))

    total_pdf_pages = 0
    missing_pages = []

    # Compare against every original PDF
    pdf_files = list(BOOKS_FOLDER.glob("*.pdf"))

    print("PDF files found:", len(pdf_files))

    for pdf_path in pdf_files:
        try:
            with fitz.open(pdf_path) as pdf:
                total_pdf_pages += len(pdf)

                # process_books.py uses the PDF filename stem
                # and saves page numbers starting from 1
                book_name = pdf_path.stem

                for page_number in range(1, len(pdf) + 1):
                    if (book_name, page_number) not in extracted_pages:
                        missing_pages.append(
                            (pdf_path.name, page_number)
                        )

        except Exception as error:
            print("Could not read:", pdf_path.name)
            print("Reason:", error)

    print("\n========== MISSING PAGE REPORT ==========")
    print("Total PDF pages:", total_pdf_pages)
    print("Extracted page records:", len(extracted_pages))
    print("Missing page records:", len(missing_pages))

    if missing_pages:
        print("\nFirst 50 missing pages:")

        for book, page in missing_pages[:50]:
            print(f"{book} | Page {page}")

        # Save the complete list for later inspection
        report_path = Path("data/processed/missing_pages.json")

        with report_path.open("w", encoding="utf-8") as file:
            json.dump(
                [
                    {"book": book, "page": page}
                    for book, page in missing_pages
                ],
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\nFull missing-page list saved to:", report_path)

    else:
        print("Every PDF page has a matching extracted record.")

if __name__ == "__main__":
    main()