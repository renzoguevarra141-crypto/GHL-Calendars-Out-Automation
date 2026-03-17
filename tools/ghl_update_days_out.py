"""Update the 'days out' (booking window) setting on GHL calendars."""

import argparse
import os
import sys
from datetime import datetime, timezone

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_BASE = "https://services.leadconnectorhq.com"
HEADERS_TEMPLATE = {
    "Version": "2021-04-15",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_headers():
    api_key = os.environ.get("GHL_API_KEY")
    if not api_key:
        print("Error: GHL_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return {**HEADERS_TEMPLATE, "Authorization": f"Bearer {api_key}"}


def resolve_calendar_ids(names):
    """Look up calendar IDs by name (case-insensitive exact match)."""
    location_id = os.environ.get("GHL_LOCATION_ID")
    if not location_id:
        print("Error: GHL_LOCATION_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    resp = requests.get(
        f"{API_BASE}/calendars/",
        headers=get_headers(),
        params={"locationId": location_id},
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"Error: Failed to list calendars ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    all_calendars = resp.json().get("calendars", [])
    name_to_cal = {c.get("name", "").lower(): c for c in all_calendars}

    resolved = []
    for name in names:
        cal = name_to_cal.get(name.lower())
        if not cal:
            print(f"Error: Calendar '{name}' not found. Available calendars:", file=sys.stderr)
            for c in all_calendars:
                print(f"  - {c.get('name', 'Unnamed')}", file=sys.stderr)
            sys.exit(1)
        resolved.append(cal)

    return resolved


def update_days_out(calendars, days_out, dry_run=False):
    """Update allowBookingFor on each calendar."""
    headers = get_headers()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    success = True

    for cal in calendars:
        cal_id = cal["id"]
        cal_name = cal.get("name", "Unnamed")
        old_value = cal.get("allowBookingFor", "N/A")
        old_unit = cal.get("allowBookingForUnit", "N/A")

        if dry_run:
            print(f"[DRY RUN] [{timestamp}] Would update '{cal_name}': {old_value} {old_unit} -> {days_out} days")
            continue

        payload = cal.copy()
        payload["allowBookingFor"] = days_out
        payload["allowBookingForUnit"] = "days"

        resp = requests.put(
            f"{API_BASE}/calendars/{cal_id}",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 200:
            print(f"[OK] [{timestamp}] Updated '{cal_name}': {old_value} {old_unit} -> {days_out} days")
        else:
            print(f"[FAIL] [{timestamp}] Failed to update '{cal_name}' ({resp.status_code}): {resp.text}", file=sys.stderr)
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="Update GHL calendar days-out setting")
    parser.add_argument("--calendar-name", nargs="+", required=True, help="Calendar name(s) to update")
    parser.add_argument("--days-out", type=int, required=True, help="Number of days out (booking window)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without making changes")
    args = parser.parse_args()

    if args.days_out < 1:
        print("Error: --days-out must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    calendars = resolve_calendar_ids(args.calendar_name)
    success = update_days_out(calendars, args.days_out, dry_run=args.dry_run)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
