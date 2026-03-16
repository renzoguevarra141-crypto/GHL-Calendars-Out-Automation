"""Cron/CI entry point: update days-out for the two target calendars."""

import argparse
import sys

from ghl_update_days_out import resolve_calendar_ids, update_days_out

CALENDAR_NAMES = [
    "Roadmap Call with Renzo",
    "Coaches and Creators Roadmap Call",
]


def main():
    parser = argparse.ArgumentParser(description="Scheduled update of GHL calendar days-out")
    parser.add_argument("--days-out", type=int, required=True, help="Number of days out (booking window)")
    args = parser.parse_args()

    if args.days_out < 1:
        print("Error: --days-out must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    print(f"Updating {len(CALENDAR_NAMES)} calendars to {args.days_out} days out...")
    calendars = resolve_calendar_ids(CALENDAR_NAMES)
    success = update_days_out(calendars, args.days_out)

    if success:
        print("All calendars updated successfully.")
    else:
        print("Some updates failed. See errors above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
