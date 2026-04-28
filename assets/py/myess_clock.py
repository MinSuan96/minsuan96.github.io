#!/usr/bin/env python3
"""
MyESS Clock In/Out Script
Automates clock-in and clock-out for MyESS (iSoftStone Malaysia).

Usage:
    python myess_clock.py              # Interactive mode
    python myess_clock.py --action in  # Clock in directly
    python myess_clock.py --action out # Clock out directly
"""

import argparse
import base64
import json
import sys
from datetime import datetime

import requests

# =============================================================================
# Configuration
# =============================================================================
API_BASE = "https://api.myess.isoftstone.com.my/api/index.php"

# Default location for clock-in/out. Change to your preferred location.
# Available locations: "MENARA 1", "Client", "Home", "11A", "11E", etc.
DEFAULT_LOCATION = "MENARA 1"

# Default coordinates (MENARA 1 office). Update if using a different location.
DEFAULT_LAT = 3.1336711
DEFAULT_LNG = 101.6863413

# Common headers required by the API (mimics the web app's requests).
COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://myess.isoftstone.com.my/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
}


# =============================================================================
# API Functions
# =============================================================================
def login(username: str, password: str) -> dict:
    """
    Authenticate with MyESS and return session info.

    The API expects the password to be base64-encoded (matching the web app's
    behavior of encoding via TextEncoder + btoa).
    """
    encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

    resp = requests.post(
        f"{API_BASE}/login/login",
        json={"username": username, "password": encoded_password},
        headers=COMMON_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("statusCode") != 200 or data.get("status") != "OK":
        return {"success": False, "message": data.get("result", "Login failed")}

    result = data["result"]
    return {
        "success": True,
        "app_token": result["appToken"],
        "staff_id": result["StaffId"],
        "staff_name": result["StaffName"],
    }


def get_last_timecard(app_token: str) -> dict | None:
    """Get the last timecard entry to determine current clock state."""
    resp = requests.get(
        f"{API_BASE}/timecard/last",
        headers={**COMMON_HEADERS, "apptoken": app_token},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("statusCode") == 200 and data.get("result"):
        entry = data["result"][0]
        return {
            "type": int(entry["Type"]),  # 1 = clock-in, 2 = clock-out
            "date": entry["Date"],
            "time": entry["Time"],
            "hours": entry.get("Hours", "0"),
            "remarks": entry.get("Remarks", ""),
        }
    return None


def get_office_list(app_token: str) -> list[dict]:
    """Get the list of available office locations."""
    resp = requests.get(
        f"{API_BASE}/staff/officeList",
        headers={**COMMON_HEADERS, "apptoken": app_token},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", [])


def clock_action(
    app_token: str,
    action_type: int,
    location: str = DEFAULT_LOCATION,
    lat: float = DEFAULT_LAT,
    lng: float = DEFAULT_LNG,
    hours: float = 0,
    remarks: str = "",
) -> dict:
    """
    Perform a clock-in or clock-out action.

    Args:
        app_token:   The authentication token from login.
        action_type: 1 for clock-in, 2 for clock-out.
        location:    Office location name (e.g. "MENARA 1", "Home", "Client").
        lat:         GPS latitude.
        lng:         GPS longitude.
        hours:       Hours worked (required for clock-out, ignored for clock-in).
        remarks:     Optional remarks/notes.

    Returns:
        dict with 'success' bool and 'message' str.
    """
    now = datetime.now()
    payload = {
        "ClockType": "",
        "Remarks": remarks,
        "MITI_Location": location,
        "Type": action_type,
        "lat": lat,
        "lng": lng,
        "LastClockInRemarks": "",
        "authToken": None,
        "DateTime": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Clock-out requires Hours and OriginalDate
    if action_type == 2:
        payload["Hours"] = hours
        payload["OriginalDate"] = now.strftime("%Y-%m-%d")

    resp = requests.post(
        f"{API_BASE}/timecard/newTimeCard",
        json=payload,
        headers={**COMMON_HEADERS, "apptoken": app_token},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("statusCode") == 200 and data.get("status") == "OK":
        action_name = "Clock-In" if action_type == 1 else "Clock-Out"
        return {"success": True, "message": f"{action_name} successful!"}

    return {"success": False, "message": data.get("result", "Action failed")}


# =============================================================================
# Helper Functions
# =============================================================================
def calculate_hours_worked(last_clock_in_time: str, last_clock_in_date: str) -> float:
    """Calculate hours worked since last clock-in."""
    clock_in_dt = datetime.strptime(
        f"{last_clock_in_date} {last_clock_in_time}", "%Y-%m-%d %H:%M:%S"
    )
    now = datetime.now()
    diff = now - clock_in_dt
    hours = diff.total_seconds() / 3600
    return round(hours, 2)


def print_status(last_entry: dict | None):
    """Print current clock status."""
    if last_entry is None:
        print("  Status: No timecard entries found. You can clock in.")
        return

    type_name = "Clocked IN" if last_entry["type"] == 1 else "Clocked OUT"
    print(f"  Last action : {type_name}")
    print(f"  Date        : {last_entry['date']}")
    print(f"  Time        : {last_entry['time']}")

    if last_entry["type"] == 1:
        hours = calculate_hours_worked(last_entry["time"], last_entry["date"])
        print(f"  Hours so far: {hours:.2f}")


def interactive_mode(app_token: str, staff_name: str):
    """Run in interactive mode, letting the user choose actions."""
    print(f"\nWelcome, {staff_name}!")
    print("-" * 40)

    # Get current status
    last_entry = get_last_timecard(app_token)
    print("\nCurrent Status:")
    print_status(last_entry)

    # Determine available actions
    if last_entry is None or last_entry["type"] == 2:
        can_clock_in = True
        can_clock_out = False
    else:
        can_clock_in = False
        can_clock_out = True

    print("\nAvailable Actions:")
    if can_clock_in:
        print("  [1] Clock In")
    if can_clock_out:
        print("  [2] Clock Out")
    print("  [3] Check Status")
    print("  [4] List Locations")
    print("  [0] Exit")

    choice = input("\nSelect action: ").strip()

    if choice == "1" and can_clock_in:
        do_clock_in(app_token)
    elif choice == "2" and can_clock_out:
        do_clock_out(app_token, last_entry)
    elif choice == "3":
        print("\nRefreshed status:")
        last_entry = get_last_timecard(app_token)
        print_status(last_entry)
    elif choice == "4":
        offices = get_office_list(app_token)
        print("\nAvailable Locations:")
        for office in offices:
            print(f"  - {office['item']}")
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice or action not available.")


def prompt_location(app_token: str) -> str:
    """Prompt the user to select a location."""
    offices = get_office_list(app_token)
    print("\nSelect Location:")
    for i, office in enumerate(offices, 1):
        print(f"  [{i}] {office['item']}")
    print(f"  [0] Use default ({DEFAULT_LOCATION})")

    choice = input("\nLocation: ").strip()
    if choice == "0" or choice == "":
        return DEFAULT_LOCATION

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(offices):
            return offices[idx]["item"]
    except ValueError:
        pass

    print(f"Invalid choice, using default: {DEFAULT_LOCATION}")
    return DEFAULT_LOCATION


def do_clock_in(app_token: str, location: str = None, remarks: str = None):
    """Perform clock-in with optional prompts."""
    if location is None:
        location = prompt_location(app_token)

    if remarks is None:
        remarks = input("Remarks (optional, press Enter to skip): ").strip()

    print(f"\nClocking in at {location}...")
    result = clock_action(app_token, action_type=1, location=location, remarks=remarks)

    if result["success"]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {result['message']}")
        print(f"  Location : {location}")
        print(f"  Date/Time: {now}")
    else:
        print(f"  FAILED: {result['message']}")


def do_clock_out(app_token: str, last_entry: dict = None, location: str = None, remarks: str = None):
    """Perform clock-out with optional prompts."""
    if location is None:
        location = prompt_location(app_token)

    if remarks is None:
        remarks = input("Remarks (optional, press Enter to skip): ").strip()

    # Calculate hours worked
    if last_entry and last_entry["type"] == 1:
        hours = calculate_hours_worked(last_entry["time"], last_entry["date"])
    else:
        hours = float(input("Enter hours worked: ").strip() or "0")
    hours = min(8, hours)

    print(f"\nClocking out at {location} with {hours:.2f} hours...")
    result = clock_action(
        app_token, action_type=2, location=location, hours=hours, remarks=remarks
    )

    if result["success"]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {result['message']}")
        print(f"  Location : {location}")
        print(f"  Hours    : {hours:.2f}")
        print(f"  Date/Time: {now}")
    else:
        print(f"  FAILED: {result['message']}")


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="MyESS Clock In/Out Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python myess_clock.py                          # Interactive mode
  python myess_clock.py --action in              # Clock in (prompts for credentials)
  python myess_clock.py --action out             # Clock out
  python myess_clock.py --action in --location Home
  python myess_clock.py --action status          # Check current status
  python myess_clock.py -u ISS280 -p mypass --action in
        """,
    )
    parser.add_argument("-u", "--username", help="Staff ID (e.g. ISS280)")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument(
        "--action",
        choices=["in", "out", "status"],
        help="Action to perform: in (clock-in), out (clock-out), status (check status)",
    )
    parser.add_argument(
        "--location", default=DEFAULT_LOCATION, help=f"Location (default: {DEFAULT_LOCATION})"
    )
    parser.add_argument("--remarks", default="", help="Optional remarks")

    args = parser.parse_args()

    # Get credentials (CLI args override defaults)
    username = args.username or "ISS280"
    password = args.password or "VRF^G^Vlh!5Mst"

    if not username:
        username = input("Staff ID (e.g. ISS280): ").strip()
    if not password:
        import getpass
        password = getpass.getpass("Password: ")

    # Login
    print("\nLogging in...")
    login_result = login(username, password)
    if not login_result["success"]:
        print(f"Login failed: {login_result['message']}")
        sys.exit(1)

    app_token = login_result["app_token"]
    staff_name = login_result["staff_name"]
    print(f"Logged in as {staff_name}")

    # Execute action
    if args.action is None:
        # Interactive mode
        while True:
            try:
                interactive_mode(app_token, staff_name)
                print()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
    elif args.action == "status":
        last_entry = get_last_timecard(app_token)
        print("\nCurrent Status:")
        print_status(last_entry)
    elif args.action == "in":
        last_entry = get_last_timecard(app_token)
        if last_entry and last_entry["type"] == 1:
            print("\nYou are already clocked in!")
            print_status(last_entry)
            confirm = input("Clock in again anyway? (y/N): ").strip().lower()
            if confirm != "y":
                sys.exit(0)
        do_clock_in(app_token, location=args.location, remarks=args.remarks)
    elif args.action == "out":
        last_entry = get_last_timecard(app_token)
        if last_entry and last_entry["type"] == 2:
            print("\nYou are already clocked out!")
            print_status(last_entry)
            sys.exit(0)
        do_clock_out(app_token, last_entry, location=args.location, remarks=args.remarks)


if __name__ == "__main__":
    main()
