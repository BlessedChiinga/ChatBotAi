import json
from pathlib import Path

import fitz
import numpy as np

BOOKS_FOLDER = Path("data/books")
MISSING_FILE = Path("data/processed/missing_pages.json")
REPORT_FILE = Path("data/processed/page_visual_report.json")


def main():
    if not MISSING_FILE.exists():
        print("ERROR: missing_pages.json was not found.")
        return

    with MISSING_FILE.open("r", encoding="utf-8") as file:
        missing_pages = json.load(file)

    results = []

    for item in missing_pages:
        pdf_path = BOOKS_FOLDER / item["book"]
        page_number = item["page"]

        try:
            with fitz.open(pdf_path) as pdf:
                page = pdf[page_number - 1]

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(1, 1),
                    colorspace=fitz.csGRAY,
                    alpha=False
                )

                pixels = np.frombuffer(
                    pix.samples, dtype=np.uint8
                )

                pixels = pixels.reshape(pix.height, pix.width)

                # Count pixels noticeably darker than white.
                dark_percent = float(
                    np.mean(pixels < 220) * 100
                )

                if dark_percent < 0.05:
                    status = "LIKELY BLANK"
                elif dark_percent < 0.5:
                    status = "LOW CONTENT - REVIEW"
                else:
                    status = "VISIBLE CONTENT - OCR CANDIDATE"

                results.append({
                    "book": item["book"],
                    "page": page_number,
                    "dark_pixel_percent": round(dark_percent, 3),
                    "status": status
                })

                print(
                    f'{item["book"]} | Page {page_number} | '
                    f'Dark pixels: {dark_percent:.3f}% | {status}'
                )

        except Exception as error:
            print(
                f'ERROR | {item["book"]} | Page {page_number} | '
                f'{error}'
            )

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n========== SUMMARY ==========")
    print("Pages inspected:", len(results))
    print(
        "Likely blank:",
        sum(r["status"] == "LIKELY BLANK" for r in results)
    )
    print(
        "Low content:",
        sum(r["status"] == "LOW CONTENT - REVIEW" for r in results)
    )
    print(
        "OCR candidates:",
        sum(r["status"] == "VISIBLE CONTENT - OCR CANDIDATE"
            for r in results)
    )
    print("Report saved to:", REPORT_FILE)


if __name__ == "__main__":
    main()