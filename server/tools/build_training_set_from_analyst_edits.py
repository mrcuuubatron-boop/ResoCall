#!/usr/bin/env python3
import csv
import json
from pathlib import Path

VALID_LABELS = {"positive", "neutral", "negative"}


def load_edits(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def normalize(rows: list[dict]) -> list[dict]:
    cleaned = []
    seen = set()
    for row in rows:
        text = str(row.get("corrected_text", "")).strip()
        label = str(row.get("corrected_label", "")).strip().lower()
        if not text or label not in VALID_LABELS:
            continue

        call_id = str(row.get("call_id", "")).strip()
        segment_id = str(row.get("segment_id", "")).strip()
        edited_at = str(row.get("edited_at", "")).strip()
        key = (call_id, segment_id, edited_at)
        if key in seen:
            continue
        seen.add(key)

        cleaned.append(
            {
                "sample_id": f"{call_id}:{segment_id}:{edited_at}",
                "call_id": call_id,
                "segment_id": segment_id,
                "text": text,
                "label": label,
                "source": "analyst_correction",
                "is_augmented": "false",
                "analyst_id": str(row.get("analyst_id", "")).strip(),
                "edited_at": edited_at,
            }
        )
    return cleaned


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample_id",
        "call_id",
        "segment_id",
        "text",
        "label",
        "source",
        "is_augmented",
        "analyst_id",
        "edited_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    input_path = Path("server/data/datasets/analyst_edits.jsonl")
    output_path = Path("server/data/datasets/scenario6_training_set.csv")

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    rows = load_edits(input_path)
    rows = normalize(rows)
    write_csv(output_path, rows)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
