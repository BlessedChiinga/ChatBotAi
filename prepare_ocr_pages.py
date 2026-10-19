import json
from pathlib import Path

import fitz

BOOKS_FOLDER = Path("data/books")
REPORT_FILE = Path("data/processed/page_visual_report.json")
OUTPUT_FOLDER = Path("data/processed/ocr_candidates")


def main():
    if not REPORT_FILE.exists():
        print("ERROR: page_visual_report.json was not found.")
        return

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        results = json.load(file)

    candidates = [
        item for item in results
        if item["status"] == "VISIBLE CONTENT - OCR CANDIDATE"
    ]

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    print("OCR candidate pages:", len(candidates))

    saved = 0

    for item in candidates:
        pdf_path = BOOKS_FOLDER / item["book"]
        page_number = item["page"]

        try:
            with fitz.open(pdf_path) as pdf:
                page = pdf[page_number - 1]

                # Render at a higher resolution for easier reading.
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    colorspace=fitz.csRGB,
                    alpha=False
                )

                # Use a unique filename for each page.
                safe_name = pdf_path.stem.replace(" ", "_")
                image_name = f"{safe_name}_page_{page_number}.png"
                image_path = OUTPUT_FOLDER / image_name

                pix.save(str(image_path))
                saved += 1

                print("Saved:", image_path)

        except Exception as error:
            print(
                f"ERROR: {item['book']} page {page_number}: {error}"
            )

    print("\n========== SUMMARY ==========")
    print("Images successfully saved:", saved)
    print("Output folder:", OUTPUT_FOLDER)


if __name__ == "__main__":
    main()