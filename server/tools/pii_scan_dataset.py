#!/usr/bin/env python3
import csv
import re
from pathlib import Path

PHONE_RE = re.compile(r"\b(?:\+?\d[\d\-\s\(\)]{7,}\d)\b")
NAME_RE = re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b")


def scan_csv(path: Path) -> tuple[int, int]:
    rows = 0
    flagged = 0
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            text = str(row.get("text", ""))
            if PHONE_RE.search(text) or NAME_RE.search(text):
                flagged += 1
    return rows, flagged


def main() -> None:
    dataset = Path("server/data/datasets/sentiment_dataset.csv")
    if not dataset.exists():
        print(f"dataset not found: {dataset}")
        return
    rows, flagged = scan_csv(dataset)
    print(f"rows={rows}")
    print(f"flagged={flagged}")


if __name__ == "__main__":
    main()
