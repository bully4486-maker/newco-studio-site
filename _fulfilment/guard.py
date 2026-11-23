#!/usr/bin/env python3
"""Refuse to start a build unless the payment gate and the run limits hold.

Reads a private orders log. The file in this folder is a header template only.
Point --orders at the live log, which stays outside the repository.

payment_cleared must be "cleared" and payment_cleared_by must be "CoS".
Keith confirms the money has arrived. CoS is the only person who sets those two cells.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path

MAX_RUNS_PER_ORDER = 2
MAX_RUNS_PER_DAY = 3
MAX_QA_FAILS = 2
USAGE_STOP_PERCENT = 80
DEFAULT_ORDERS_PATH = Path("/workspace/pivot/orders.csv")
ORDERS_ENV = "NEWCO_ORDERS_CSV"


def default_orders_path() -> Path:
    """Live log path: --orders, else $NEWCO_ORDERS_CSV, else /workspace/pivot/orders.csv."""
    override = (os.environ.get(ORDERS_ENV) or "").strip()
    if override:
        return Path(override)
    return DEFAULT_ORDERS_PATH


def refuse(message: str) -> int:
    print(f"REFUSED: {message}", file=sys.stderr)
    return 2


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"Orders log not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected = {
            "order_id",
            "business_name",
            "payment_cleared",
            "payment_cleared_by",
            "agent_runs",
            "run_dates",
            "qa_fails",
            "status",
            "preview_url",
        }
        fields = set(reader.fieldnames or [])
        missing = expected - fields
        if missing:
            raise SystemExit("Orders log is missing columns: " + ", ".join(sorted(missing)))
        return list(reader)


def as_int(value: str, label: str) -> int:
    text = (value or "").strip()
    if text == "":
        return 0
    try:
        number = int(text)
    except ValueError as exc:
        raise SystemExit(f"{label} must be a whole number, not {value!r}.") from exc
    if number < 0:
        raise SystemExit(f"{label} cannot be negative.")
    return number


def runs_on(rows: list[dict[str, str]], day: date) -> int:
    key = day.isoformat()
    count = 0
    for row in rows:
        for part in (row.get("run_dates") or "").split(";"):
            if part.strip() == key:
                count += 1
    return count


def check(rows: list[dict[str, str]], order_id: str, usage_percent: float, today: date) -> str | None:
    matches = [row for row in rows if (row.get("order_id") or "").strip() == order_id]
    if not matches:
        return f"no order {order_id} in the log. Nothing starts without a logged order."
    if len(matches) > 1:
        return f"order {order_id} appears more than once."
    row = matches[0]
    cleared = (row.get("payment_cleared") or "").strip().casefold()
    marker = (row.get("payment_cleared_by") or "").strip()
    if cleared != "cleared" or marker != "CoS":
        return (
            "payment_cleared is not marked by CoS. "
            "Keith confirms the deposit has cleared, then CoS sets payment_cleared to cleared "
            "and payment_cleared_by to CoS. No build before that."
        )
    runs = as_int(row.get("agent_runs", ""), "agent_runs")
    if runs >= MAX_RUNS_PER_ORDER:
        return f"order {order_id} already has {runs} agent runs. The maximum is {MAX_RUNS_PER_ORDER}."
    fails = as_int(row.get("qa_fails", ""), "qa_fails")
    if fails >= MAX_QA_FAILS:
        return f"order {order_id} has failed QA {fails} times. Stop and escalate to CoS."
    today_runs = runs_on(rows, today)
    if today_runs >= MAX_RUNS_PER_DAY:
        return f"{today_runs} agent runs are already logged for {today.isoformat()}. The daily maximum is {MAX_RUNS_PER_DAY}."
    if usage_percent >= USAGE_STOP_PERCENT:
        return (
            f"Cursor usage is at {usage_percent:g}%, which is at or over {USAGE_STOP_PERCENT}%. "
            "Stop all runs and flag Keith via CoS."
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Payment and limit gate for a website build.")
    parser.add_argument(
        "--orders",
        type=Path,
        default=None,
        help=(
            "Private orders CSV, outside the repository. "
            f"Defaults to ${ORDERS_ENV} or {DEFAULT_ORDERS_PATH}."
        ),
    )
    parser.add_argument("--order-id", default="", help="Order id to start.")
    parser.add_argument("--usage-percent", type=float, default=None, help="Current Cursor usage allowance used, 0 to 100.")
    parser.add_argument("--today", default="", help="Override today's date, YYYY-MM-DD. For tests.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    orders_path = args.orders if args.orders is not None else default_orders_path()
    if not args.order_id or args.usage_percent is None:
        return refuse("pass --order-id and --usage-percent. A missing usage figure is a refusal.")
    today = date.fromisoformat(args.today) if args.today else date.today()
    reason = check(load_rows(orders_path), args.order_id.strip(), args.usage_percent, today)
    if reason:
        return refuse(reason)
    print(f"OK: {args.order_id.strip()} may start one build.")
    return 0


def self_test() -> int:
    import tempfile

    header = (
        "order_id,business_name,payment_cleared,payment_cleared_by,agent_runs,run_dates,qa_fails,status,preview_url\n"
    )
    good = header + "NCS-1,North Lane Flowers,cleared,CoS,1,2026-11-23,0,building,\n"
    blocked = header + "NCS-2,North Lane Flowers,no,,0,,0,quoted,\n"
    twice = header + "NCS-3,North Lane Flowers,cleared,CoS,2,2026-11-22;2026-11-22,0,preview,\n"
    qa = header + "NCS-4,North Lane Flowers,cleared,CoS,1,2026-11-22,2,stopped,\n"
    day = header + (
        "NCS-5,A,cleared,CoS,1,2026-11-23,0,preview,\n"
        "NCS-6,B,cleared,CoS,1,2026-11-23,0,preview,\n"
        "NCS-7,C,cleared,CoS,1,2026-11-23,0,preview,\n"
        "NCS-8,D,cleared,CoS,0,,0,paid,\n"
    )
    today = date(2026, 11, 23)

    def run(text: str, order: str, usage: float) -> str | None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write(text)
            path = Path(handle.name)
        try:
            return check(load_rows(path), order, usage, today)
        finally:
            path.unlink()

    if run(good, "NCS-1", 10) is not None:
        raise SystemExit("self-test: a cleared order should pass")
    if run(blocked, "NCS-2", 10) is None:
        raise SystemExit("self-test: an uncleared order should fail")
    if run(twice, "NCS-3", 10) is None:
        raise SystemExit("self-test: two prior runs should fail")
    if run(qa, "NCS-4", 10) is None:
        raise SystemExit("self-test: two QA fails should fail")
    if run(day, "NCS-8", 10) is None:
        raise SystemExit("self-test: three runs today should fail")
    if run(good, "NCS-1", 80) is None:
        raise SystemExit("self-test: 80% usage should fail")
    if run(good, "NCS-missing", 10) is None:
        raise SystemExit("self-test: unknown order should fail")
    repo_header = Path(__file__).resolve().parent / "orders.csv"
    rows = load_rows(repo_header)
    if rows:
        raise SystemExit("self-test: the repo orders.csv must stay header-only")

    saved = os.environ.get(ORDERS_ENV)
    try:
        if default_orders_path() != DEFAULT_ORDERS_PATH and not saved:
            raise SystemExit("self-test: default path should be /workspace/pivot/orders.csv")
        os.environ[ORDERS_ENV] = "/tmp/example-orders.csv"
        if default_orders_path() != Path("/tmp/example-orders.csv"):
            raise SystemExit("self-test: $NEWCO_ORDERS_CSV should override the default path")
        os.environ.pop(ORDERS_ENV, None)
        if default_orders_path() != DEFAULT_ORDERS_PATH:
            raise SystemExit("self-test: clearing the env var should restore the default path")
        # A missing --order-id or --usage-percent is still a refusal, even with a default path.
        code = main(["--orders", str(repo_header)])
        if code != 2:
            raise SystemExit("self-test: missing --order-id and --usage-percent should refuse")
        # An empty log (header only) refuses any build.
        code = main(["--orders", str(repo_header), "--order-id", "NCS-1", "--usage-percent", "10"])
        if code != 2:
            raise SystemExit("self-test: an empty log should refuse a build")
    finally:
        if saved is None:
            os.environ.pop(ORDERS_ENV, None)
        else:
            os.environ[ORDERS_ENV] = saved

    print("guard.py self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
