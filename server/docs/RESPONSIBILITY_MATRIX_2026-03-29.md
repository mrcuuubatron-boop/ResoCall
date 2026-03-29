# Responsibility Matrix (de-facto)

Date: 2026-03-29

## Why there were identical roles in the project plan
The original Gantt plan was prepared at team level without explicit personal ownership by WBS item. This document fixes de-facto ownership and removes role ambiguity.

## De-facto ownership

| Area | Owner | Backup | Evidence |
|---|---|---|---|
| Apache reverse proxy and server deploy | SaKuRa5353 | Osipov | `server/deploy/apache/resocall.conf`, `server/deploy/systemd/resocall.service` |
| Backend API integration and diagnostics | SaKuRa5353 | Osipov | `server/app/main.py`, `server/app/routers/analysis.py` |
| ASR module bridge and fallback | SaKuRa5353 | Zagorodnev | `server/app/services/audio_pipeline.py` |
| Auth persistence (SQLite) | SaKuRa5353 | Osipov | `server/app/services/database.py`, `server/app/security.py` |
| Frontend mock dashboards | Kutyin | SaKuRa5353 | `site/components/*.tsx` |
| ASR quality checker script | Zagorodnev | SaKuRa5353 | `test_data/asr_checker.py`, `test_data/otch.txt` |
| Scenario 5 load testing | SaKuRa5353 | Osipov | `server/tools/scenario5_capacity.py`, `server/reports/SCENARIO5_LOAD_TEST_2026-03-29.md` |
| Scenario 6 training set design | SaKuRa5353 | Zagorodnev | `server/docs/TRAINING_SET_SCHEMA_SCENARIO6.md`, `server/tools/build_training_set_from_analyst_edits.py` |
| External API ban compliance check (ML module) | SaKuRa5353 | Osipov | `server/reports/EXTERNAL_API_AUDIT_2026-03-29.md` |
| PII control in inputs | SaKuRa5353 | Osipov | `server/tools/pii_scan_dataset.py`, `server/reports/PII_CHECK_2026-03-29.md` |

## Approval
This matrix should be referenced from sprint review to evaluate personal contribution against concrete repository artifacts.
