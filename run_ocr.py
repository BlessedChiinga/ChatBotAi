import json
import re
from pathlib import Path

import pytesseract
from PIL import Image

# Project folders
PROJECT_FOLDER = Path(__file__).resolve().parent
PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"
OUTPUT_FILE = PROCESSED_FOLDER / "ocr_pages.jsonl"

# Tesseract executable
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def main():
    # Find prepared page images
    image_files = []

    for folder in (PROCESSED_FOLDER,):
        if folder.exists():
            image_files.extend(folder.rglob("*.png"))
            image_files.extend(folder.rglob("*.jpg"))
            image_files.extend(folder.rglob("*.jpeg"))

    # Remove duplicates and sort filenames
    image_files = sorted(set(image_files))

    if not image_files:
        print("ERROR: No OCR images found.")
        print("Check the image folder and try again.")
        return

    print("OCR images found:", len(image_files))

    processed = 0
    failed = 0

    # Write OCR results to a separate file
    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for index, image_path in enumerate(image_files, start=1):
            try:
                # Extract book name and page number
                match = re.match(
                    r"(.+)_page_(\d+)$",
                    image_path.stem
                )

                if not match:
                    print("Skipping unrecognized filename:", image_path.name)
                    failed += 1
                    continue

                book_name = match.group(1)
                page_number = int(match.group(2))

                # Read image and recognize text
                with Image.open(image_path) as image:
                    image = image.convert("RGB")
                    text = pytesseract.image_to_string(
                        image,
                        lang="eng"
                    )

                record = {
                    "book": book_name,
                    "page": page_number,
                    "source_image": image_path.name,
                    "text": text.strip()
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )
                output.flush()

                processed += 1

                print(
                    f"[{index}/{len(image_files)}] "
                    f"Processed {book_name}, page {page_number} "
                    f"({len(text.strip())} characters)"
                )

            except Exception as error:
                failed += 1
                print("ERROR processing:", image_path.name)
                print("Reason:", error)

    print("\n========== OCR REPORT ==========")
    print("Images found:", len(image_files))
    print("Pages processed:", processed)
    print("Failed or skipped:", failed)
    print("Output saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()