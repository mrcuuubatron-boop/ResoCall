# Scenario 5 Load Testing (10000 calls)

Date: 2026-03-29
Owner: SaKuRa5353

## Scope
Capacity estimate for processing 10000 calls within SLA window.

## Method
Used capacity model implemented in `server/tools/scenario5_capacity.py`:

W = ceil((N * t_avg) / T)
- N = 10000 calls
- t_avg = 45 sec per call (baseline processing average)
- T = 8 hours target window

## Result
Command:
`python3 server/tools/scenario5_capacity.py --calls 10000 --avg-seconds 45 --deadline-hours 8`

Output:
- calls=10000
- avg_seconds=45.0
- deadline_hours=8.0
- required_workers=16

## Queue note
Current implementation uses in-process queue via `ThreadPoolExecutor` in `server/app/services/task_manager.py`.
If RabbitMQ is enabled in next iteration, this worker baseline (16) is used as starting point for consumer pool sizing.

## Conclusion
Scenario 5 planning baseline is prepared. Required workers to meet 8h deadline: **16**.
