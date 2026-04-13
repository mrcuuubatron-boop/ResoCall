#!/usr/bin/env python3
import argparse
import math


def required_workers(calls: int, avg_seconds: float, deadline_hours: float) -> int:
    total_seconds = calls * avg_seconds
    budget_seconds = deadline_hours * 3600
    return max(1, math.ceil(total_seconds / budget_seconds))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scenario 5 capacity calculator for 10000 calls")
    parser.add_argument("--calls", type=int, default=10000)
    parser.add_argument("--avg-seconds", type=float, default=45.0)
    parser.add_argument("--deadline-hours", type=float, default=8.0)
    args = parser.parse_args()

    workers = required_workers(args.calls, args.avg_seconds, args.deadline_hours)
    print(f"calls={args.calls}")
    print(f"avg_seconds={args.avg_seconds}")
    print(f"deadline_hours={args.deadline_hours}")
    print(f"required_workers={workers}")


if __name__ == "__main__":
    main()
