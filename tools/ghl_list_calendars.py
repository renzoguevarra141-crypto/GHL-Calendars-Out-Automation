"""List GHL calendars and their booking window settings."""

import argparse
import os
import sys

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required (env vars set externally in CI)

API_BASE = "https://services.leadconnectorhq.com"
HEADERS_TEMPLATE = {
    "Version": "2021-04-15",
    "Accept": "application/json",
}


def get_headers():
    api_key = os.environ.get("GHL_API_KEY")
    if not api_key:
        print("Error: GHL_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return {**HEADERS_TEMPLATE, "Authorization": f"Bearer {api_key}"}


def list_calendars(name_filter=None):
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
        print(f"Error: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    calendars = data.get("calendars", [])

    if name_filter:
        name_lower = name_filter.lower()
        calendars = [c for c in calendars if name_lower in c.get("name", "").lower()]

    if not calendars:
        print("No calendars found.")
        return []

    for cal in calendars:
        booking_for = cal.get("allowBookingFor", "N/A")
        booking_unit = cal.get("allowBookingForUnit", "N/A")
        print(f"  ID:   {cal['id']}")
        print(f"  Name: {cal.get('name', 'Unnamed')}")
        print(f"  Days Out: {booking_for} {booking_unit}")
        print(f"  Type: {cal.get('calendarType', 'N/A')}")
        print()

    return calendars


def main():
    parser = argparse.ArgumentParser(description="List GHL calendars")
    parser.add_argument("--name", help="Filter calendars by name (case-insensitive substring match)")
    args = parser.parse_args()
    list_calendars(name_filter=args.name)


if __name__ == "__main__":
    main()
