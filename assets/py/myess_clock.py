#!/usr/bin/env python3
"""
MyESS Clock In/Out Script
Automates clock-in and clock-out for MyESS (iSoftStone Malaysia).

Usage:
    python myess_clock.py              # Interactive mode
    python myess_clock.py --action in  # Clock in directly
    python myess_clock.py --action out # Clock out directly
    python myess_clock.py --action submit  # Submit timecard for approval
"""

import argparse
import base64
import json
import sys
from datetime import datetime, timedelta

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


def get_timecard_by_week(app_token: str, from_date: str, to_date: str) -> list[dict]:
    """
    Get timecard entries for a specific week.

    Args:
        app_token:  The authentication token from login.
        from_date:  Start of week as YYYY-MM-DD (Sunday).
        to_date:    End of week as YYYY-MM-DD (Saturday).

    Returns:
        List of daily timecard entry dicts (typically 7, one per day).
    """
    resp = requests.get(
        f"{API_BASE}/timecard/timeCardTableByWeek",
        params={"fromDate": from_date, "toDate": to_date, "staffId": ""},
        headers={**COMMON_HEADERS, "apptoken": app_token},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("statusCode") == 200:
        return data.get("result", [])
    return []


def submit_timecard(app_token: str, timecard_entries: list[dict]) -> dict:
    """
    Submit a week's timecard entries for approval.

    The API expects the full array of daily timecard entries (as returned by
    get_timecard_by_week) to be POSTed as the JSON body.

    Args:
        app_token:        The authentication token from login.
        timecard_entries:  List of daily timecard entry dicts for the week.

    Returns:
        dict with 'success' bool and 'message' str.
    """
    resp = requests.post(
        f"{API_BASE}/timecard/staffTimeCardSave",
        params={"staffId": ""},
        json=timecard_entries,
        headers={**COMMON_HEADERS, "apptoken": app_token},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("statusCode") == 200 and data.get("status") == "OK":
        result = data.get("result", {})
        saved = result.get("saved_records", 0)
        total = result.get("total_records", 0)
        return {
            "success": result.get("success", True),
            "message": result.get("message", f"Saved {saved}/{total} records"),
        }

    return {"success": False, "message": data.get("result", "Submit failed")}


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
def get_week_boundaries(date: datetime = None) -> tuple[str, str]:
    """
    Get the Sunday–Saturday week boundaries for a given date.

    MyESS weeks run Sunday to Saturday. Returns the bounding dates as
    YYYY-MM-DD strings.
    """
    if date is None:
        date = datetime.now()
    # weekday(): Monday=0 … Sunday=6.  We want Sunday as start of week.
    days_since_sunday = (date.weekday() + 1) % 7
    sunday = date - timedelta(days=days_since_sunday)
    saturday = sunday + timedelta(days=6)
    return sunday.strftime("%Y-%m-%d"), saturday.strftime("%Y-%m-%d")


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
    print("  [5] Submit Timecard")
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
    elif choice == "5":
        do_submit_timecard(app_token)
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


def do_submit_timecard(app_token: str):
    """
    List recent weekly timecards and let the user submit one.

    Displays the last 5 weeks, defaults to the most recent week with Draft
    entries, shows a detail summary, then submits on confirmation.
    """
    DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    NUM_WEEKS = 5

    # ------------------------------------------------------------------
    # 1. Fetch recent weeks
    # ------------------------------------------------------------------
    today = datetime.now()
    weeks: list[dict] = []

    for i in range(NUM_WEEKS):
        ref_date = today - timedelta(weeks=i)
        from_date, to_date = get_week_boundaries(ref_date)
        entries = get_timecard_by_week(app_token, from_date, to_date)

        total_hours = sum(float(e.get("FinalWorkedHours", 0)) for e in entries)

        # Determine overall week status
        statuses = {e.get("ApprovalStatus", "Draft") for e in entries}
        if "Approved" in statuses and len(statuses) == 1:
            week_status = "Approved"
        elif "Submitted" in statuses and "Draft" not in statuses:
            week_status = "Submitted"
        else:
            week_status = "Draft"

        weeks.append({
            "from_date": from_date,
            "to_date": to_date,
            "entries": entries,
            "total_hours": total_hours,
            "status": week_status,
        })

    # ------------------------------------------------------------------
    # 2. Display week list
    # ------------------------------------------------------------------
    # Find the default (first Draft week)
    default_idx = None
    for idx, w in enumerate(weeks):
        if w["status"] == "Draft":
            default_idx = idx
            break

    print("\nAvailable Timecards:")
    print("-" * 60)
    for idx, w in enumerate(weeks):
        from_dt = datetime.strptime(w["from_date"], "%Y-%m-%d")
        to_dt = datetime.strptime(w["to_date"], "%Y-%m-%d")
        label = f"{from_dt.strftime('%b %d')} - {to_dt.strftime('%b %d, %Y')}"
        marker = "  <-- default" if idx == default_idx else ""
        print(f"  [{idx + 1}] {label}  | {w['total_hours']:5.1f}h | {w['status']}{marker}")

    if default_idx is None:
        print("\n  No Draft timecards found in the last 5 weeks.")
        return

    # ------------------------------------------------------------------
    # 3. User selects a week
    # ------------------------------------------------------------------
    prompt_text = f"\nSelect week to submit [{default_idx + 1}]: "
    choice = input(prompt_text).strip()

    if choice == "":
        selected_idx = default_idx
    else:
        try:
            selected_idx = int(choice) - 1
            if not (0 <= selected_idx < len(weeks)):
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid choice.")
            return

    selected = weeks[selected_idx]

    if selected["status"] != "Draft":
        print(f"\n  This week is already '{selected['status']}'. Nothing to submit.")
        return

    if not selected["entries"]:
        print("\n  No timecard entries found for this week.")
        return

    # ------------------------------------------------------------------
    # 4. Show detail summary
    # ------------------------------------------------------------------
    from_dt = datetime.strptime(selected["from_date"], "%Y-%m-%d")
    to_dt = datetime.strptime(selected["to_date"], "%Y-%m-%d")
    project = selected["entries"][0].get("ProjectName", "N/A") if selected["entries"] else "N/A"

    print(f"\nWeek: {from_dt.strftime('%b %d')} - {to_dt.strftime('%b %d, %Y')}")
    print(f"  Project: {project}")
    print()

    for entry in sorted(selected["entries"], key=lambda e: e["WorkDate"]):
        edate = datetime.strptime(entry["WorkDate"], "%Y-%m-%d")
        day_name = DAY_NAMES[int(edate.strftime("%w"))]  # %w: 0=Sun
        hours = float(entry.get("FinalWorkedHours", 0))
        status = entry.get("ApprovalStatus", "Draft")
        print(f"  {day_name} {edate.strftime('%d')}: {hours:5.1f}h  ({status})")

    print(f"\n  Total: {selected['total_hours']:.1f}h")

    # ------------------------------------------------------------------
    # 5. Confirm and submit
    # ------------------------------------------------------------------
    confirm = input("\nSubmit this timecard? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    print("\nSubmitting timecard...")
    result = submit_timecard(app_token, selected["entries"])

    if result["success"]:
        print(f"  {result['message']}")
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
  python myess_clock.py --action submit          # Submit timecard for approval
  python myess_clock.py -u ISS280 -p mypass --action in
        """,
    )
    parser.add_argument("-u", "--username", help="Staff ID (e.g. ISS280)")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument(
        "--action",
        choices=["in", "out", "status", "submit"],
        help="Action to perform: in, out, status, submit (submit timecard)",
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
    elif args.action == "submit":
        do_submit_timecard(app_token)


if __name__ == "__main__":
    main()
