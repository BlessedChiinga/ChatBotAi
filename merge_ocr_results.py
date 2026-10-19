import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PAGES_FILE = BASE / "data" / "processed" / "pages.jsonl"
OCR_FILE = BASE / "data" / "processed" / "ocr_pages.jsonl"
OUTPUT_FILE = BASE / "data" / "processed" / "pages_with_ocr.jsonl"


def read_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def main():
    ocr_by_page = {}

    for record in read_jsonl(OCR_FILE):
        key = (record.get("book"), record.get("page"))
        text = record.get("text", "").strip()

        if key[0] and key[1] is not None and text:
            ocr_by_page[key] = text

    total = 0
    improved = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for record in read_jsonl(PAGES_FILE):
            total += 1
            key = (record.get("book"), record.get("page"))
            original = record.get("text", "").strip()
            ocr_text = ocr_by_page.get(key, "")

            if ocr_text and len(original) < 100:
                record["text"] = ocr_text
                record["text_source"] = "tesseract_ocr"
                improved += 1

            output.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    print("========== MERGE REPORT ==========")
    print("Original records:", total)
    print("Pages supplemented with OCR:", improved)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()