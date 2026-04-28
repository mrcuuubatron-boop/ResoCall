# Scenario 6 Training Set Schema

Date: 2026-03-29

## Goal
Create a retraining dataset from analyst corrections after call review.

## Input source
Analyst edits are stored as JSONL records with one correction per line.

Required fields:
- `call_id` (string)
- `segment_id` (string)
- `original_text` (string)
- `corrected_text` (string)
- `original_label` (string: positive|neutral|negative)
- `corrected_label` (string: positive|neutral|negative)
- `reason_code` (string)
- `analyst_id` (string)
- `edited_at` (ISO-8601 string)

## Output dataset (CSV)
Columns:
- `sample_id`
- `call_id`
- `segment_id`
- `text`
- `label`
- `source` (analyst_correction)
- `is_augmented` (bool)
- `analyst_id`
- `edited_at`

## Quality gates
- Drop rows with empty `corrected_text`.
- Drop rows with label not in {positive, neutral, negative}.
- Deduplicate by (`call_id`, `segment_id`, `edited_at`).
- Keep latest correction as final target.

## Split strategy
Recommended split with stratification by label:
- train: 70%
- validation: 15%
- test: 15%

## Artifact files
- Raw edits: `server/data/datasets/analyst_edits.jsonl`
- Built dataset: `server/data/datasets/scenario6_training_set.csv`
- Builder script: `server/tools/build_training_set_from_analyst_edits.py`
