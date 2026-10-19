import json
from pathlib import Path
import fitz

BOOKS_FOLDER = Path("data/books")
MISSING_FILE = Path("data/processed/missing_pages.json")

def main():
    if not MISSING_FILE.exists():
        print("ERROR: missing_pages.json was not found.")
        return

    with MISSING_FILE.open("r", encoding="utf-8") as file:
        missing_pages = json.load(file)

    print("Pages to inspect:", len(missing_pages))
    print("\n========== PAGE INSPECTION REPORT ==========")

    for item in missing_pages:
        filename = item["book"]
        page_number = item["page"]
        pdf_path = BOOKS_FOLDER / filename

        try:
            with fitz.open(pdf_path) as pdf:
                page = pdf[page_number - 1]
                text = page.get_text("text").strip()
                images = page.get_images(full=True)

                if text:
                    status = "TEXT FOUND - CHECK PAGE RECORD MATCH"
                elif images:
                    status = "NO TEXT - PAGE CONTAINS IMAGES"
                else:
                    status = "NO TEXT - CHECK IF BLANK OR GRAPHIC"

                print(
                    f"{filename} | Page {page_number} | "
                    f"Characters: {len(text)} | "
                    f"Images: {len(images)} | {status}"
                )

        except Exception as error:
            print(
                f"{filename} | Page {page_number} | "
                f"INSPECTION ERROR: {error}"
            )

if __name__ == "__main__":
    main()