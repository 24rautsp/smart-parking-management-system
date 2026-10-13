"""
Smart Parking Management System - Main Interactive CLI Application
Provides a menu-driven console interface with robust input validation,
clear tabular displays, and demonstration options for DSA college vivas.
"""

import os
import sys
import time
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.parking_system import ParkingLot
except ModuleNotFoundError:
    from parking_system import ParkingLot


def print_banner() -> None:
    """Displays application banner."""
    print("=" * 65)
    print("        SMART PARKING MANAGEMENT SYSTEM (DSA PROJECT)")
    print("=" * 65)


def print_menu() -> None:
    """Displays the main operations menu."""
    print("\n" + "-" * 40)
    print("             MAIN MENU")
    print("-" * 40)
    print(" 1. View All Parking Slots")
    print(" 2. Park a Vehicle (Auto-Assign Slot)")
    print(" 3. Exit a Vehicle & Calculate Fee")
    print(" 4. Search Vehicle (Active, Queue, History)")
    print(" 5. View Waiting Queue (FIFO)")
    print(" 6. View Completed Parking History")
    print(" 7. Sort Completed History (Custom Insertion Sort)")
    print(" 8. Undo Last Entry (LIFO Stack)")
    print(" 9. View System Statistics & Revenue")
    print(" 0. Exit System")
    print("-" * 40)


def format_timestamp(ts: Optional[float]) -> str:
    """Formats epoch float timestamp into human-readable string."""
    if not ts:
        return "N/A"
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def handle_view_slots(lot: ParkingLot) -> None:
    """Renders formatted table of all parking bays."""
    slots_data = lot.get_slot_status()
    print("\n" + "=" * 60)
    print(f"{'Slot #':<8}{'Status':<14}{'Vehicle No.':<18}{'Entry Time':<20}")
    print("=" * 60)
    for s in slots_data:
        status_str = "Occupied" if s["is_occupied"] else "Available"
        veh_str = s["vehicle_number"] if s["vehicle_number"] else "-"
        time_str = format_timestamp(s["entry_time"]) if s["is_occupied"] else "-"
        print(f"{s['slot_id']:<8}{status_str:<14}{veh_str:<18}{time_str:<20}")
    print("=" * 60)


def handle_park_vehicle(lot: ParkingLot) -> None:
    """Handles parking a vehicle with input validation."""
    print("\n--- Park a Vehicle ---")
    plate = input("Enter vehicle registration number (e.g. KA01AB1234): ").strip()
    if not plate:
        print("[!] Error: Registration number cannot be empty.")
        return

    success, message, slot_id = lot.park_vehicle(plate)
    if success:
        print(f"[+] Success: {message}")
    else:
        print(f"[-] Operation Failed: {message}")


def handle_exit_vehicle(lot: ParkingLot) -> None:
    """Handles vehicle exit, billing calculation, and queue handover."""
    print("\n--- Exit a Vehicle ---")
    plate = input("Enter vehicle registration number to exit: ").strip()
    if not plate:
        print("[!] Error: Registration number cannot be empty.")
        return

    print("Choose duration calculation mode:")
    print("  1. Real-Time Elapsed Duration (System Clock)")
    print("  2. Custom Simulated Duration (Ideal for Viva Demonstration)")
    mode = input("Select mode (1 or 2, default 2): ").strip()

    simulated_hours = None
    if mode != "1":
        dur_input = input("Enter simulated duration in hours (e.g., 2.5): ").strip()
        try:
            simulated_hours = float(dur_input)
            if simulated_hours < 0:
                print("[!] Duration cannot be negative. Using default 1.0 hour.")
                simulated_hours = 1.0
        except ValueError:
            print("[!] Invalid number. Using default 1.0 hour.")
            simulated_hours = 1.0

    success, message, receipt = lot.exit_vehicle(
        vehicle_number=plate,
        simulated_duration_hours=simulated_hours
    )

    if success and receipt:
        print("\n" + "=" * 45)
        print("           PARKING CHECKOUT RECEIPT")
        print("=" * 45)
        print(f" Vehicle Plate : {receipt['vehicle_number']}")
        print(f" Slot Released : #{receipt['slot_id']}")
        print(f" Entry Time    : {format_timestamp(receipt['entry_time'])}")
        print(f" Exit Time     : {format_timestamp(receipt['exit_time'])}")
        print(f" Duration      : {receipt['duration_hours']} hour(s)")
        print(f" Hourly Rate   : Rs. {lot.hourly_rate:.2f}")
        print(f" Total Fee     : Rs. {receipt['fee']:.2f}")
        if receipt.get("assigned_waiting_vehicle"):
            print(f" [*] Auto-Handover: Waiting car {receipt['assigned_waiting_vehicle']} assigned to this slot!")
        print("=" * 45)
    else:
        print(f"[-] Exit Failed: {message}")


def handle_search_vehicle(lot: ParkingLot) -> None:
    """Searches for a vehicle across active slots, queue, and history."""
    print("\n--- Search Vehicle ---")
    plate = input("Enter vehicle registration number to search: ").strip()
    if not plate:
        print("[!] Error: Registration number cannot be empty.")
        return

    result = lot.search_vehicle(plate)
    if not result.get("found"):
        print(f"[-] No active or historical records found for '{plate.upper()}'.")
        return

    print("\n" + "=" * 55)
    print(f" SEARCH RESULTS FOR: {result['vehicle_number']}")
    print("=" * 55)

    if result.get("active_status"):
        act = result["active_status"]
        print(f"[ACTIVE] Currently Parked in Slot #{act['slot_id']}")
        print(f"         Parked At: {format_timestamp(act['entry_time'])}")
    else:
        print("[ACTIVE] Not currently parked in any slot.")

    if result.get("queue_position"):
        print(f"[WAITING QUEUE] Waiting at Position #{result['queue_position']}")
    else:
        print("[WAITING QUEUE] Not in waiting queue.")

    past = result.get("past_sessions", [])
    print(f"[HISTORY] Past Completed Sessions: {len(past)}")
    for i, s in enumerate(past, 1):
        print(f"   {i}. Slot #{s['slot_id']} | {s['duration_hours']}h | Fee: Rs. {s['fee']:.2f}")
    print("=" * 55)


def handle_view_queue(lot: ParkingLot) -> None:
    """Displays the waiting queue."""
    q_list = lot.waiting_queue.to_list()
    print("\n" + "=" * 45)
    print(f" WAITING QUEUE (Total: {len(q_list)})")
    print("=" * 45)
    if not q_list:
        print(" Queue is currently empty.")
    else:
        for idx, plate in enumerate(q_list, 1):
            print(f"  Position #{idx} : {plate}")
    print("=" * 45)


def handle_view_history(lot: ParkingLot) -> None:
    """Displays raw completed history from the Linked List."""
    records = lot.history.to_list()
    print("\n" + "=" * 65)
    print(f"{'#':<4}{'Vehicle No.':<18}{'Slot':<8}{'Duration':<12}{'Fee':<12}")
    print("=" * 65)
    if not records:
        print(" No completed parking records yet.")
    else:
        for idx, r in enumerate(records, 1):
            print(f"{idx:<4}{r['vehicle_number']:<18}#{r['slot_id']:<7}{r['duration_hours']}h{'':<7}Rs. {r['fee']:.2f}")
    print("=" * 65)


def handle_sort_history(lot: ParkingLot) -> None:
    """Sorts completed history using custom Insertion Sort."""
    records = lot.history.to_list()
    if not records:
        print("\n[!] No completed parking records available to sort.")
        return

    print("\n--- Sort Completed Parking History ---")
    print("Choose sorting criterion:")
    print("  1. Total Fee Paid (Highest to Lowest)")
    print("  2. Total Fee Paid (Lowest to Highest)")
    print("  3. Parking Duration (Longest to Shortest)")
    print("  4. Vehicle Number (Alphabetical A-Z)")
    choice = input("Enter choice (1-4, default 1): ").strip()

    key_map = {
        "1": ("fee", True),
        "2": ("fee", False),
        "3": ("duration_hours", True),
        "4": ("vehicle_number", False),
    }

    sort_key, reverse = key_map.get(choice, ("fee", True))
    sorted_records = lot.get_sorted_history(sort_by=sort_key, reverse=reverse)

    print("\n" + "=" * 65)
    print(f" SORTED HISTORY (Key: '{sort_key}', Reverse: {reverse})")
    print("=" * 65)
    print(f"{'#':<4}{'Vehicle No.':<18}{'Slot':<8}{'Duration':<12}{'Fee':<12}")
    print("-" * 65)
    for idx, r in enumerate(sorted_records, 1):
        print(f"{idx:<4}{r['vehicle_number']:<18}#{r['slot_id']:<7}{r['duration_hours']}h{'':<7}Rs. {r['fee']:.2f}")
    print("=" * 65)


def handle_undo_last_entry(lot: ParkingLot) -> None:
    """Undoes the most recent vehicle entry via the LIFO Action Stack."""
    print("\n--- Undo Last Operation ---")
    success, msg = lot.undo_last_parking()
    if success:
        print(f"[+] {msg}")
    else:
        print(f"[-] {msg}")


def handle_view_summary(lot: ParkingLot) -> None:
    """Displays overall system statistics."""
    summary = lot.get_summary()
    print("\n" + "=" * 45)
    print("       PARKING SYSTEM OVERVIEW")
    print("=" * 45)
    print(f" Total Capacity       : {summary['capacity']} slots")
    print(f" Occupied Slots       : {summary['occupied_slots']}")
    print(f" Available Slots      : {summary['available_slots']}")
    print(f" Waiting Vehicles     : {summary['waiting_count']}")
    print(f" Completed Sessions   : {summary['total_completed_sessions']}")
    print(f" Total Revenue        : Rs. {summary['total_revenue']:.2f}")
    print(f" Configured Rate      : Rs. {summary['hourly_rate']:.2f} / hour")
    print("=" * 45)


def run_interactive_app() -> None:
    """Main CLI event loop."""
    print_banner()
    try:
        cap_in = input("Enter parking lot capacity (default 4): ").strip()
        capacity = int(cap_in) if cap_in else 4
        if capacity <= 0:
            print("[!] Capacity must be > 0. Defaulting to 4.")
            capacity = 4
    except ValueError:
        print("[!] Invalid input. Defaulting to 4 slots.")
        capacity = 4

    try:
        rate_in = input("Enter hourly parking rate in Rs. (default 20.0): ").strip()
        hourly_rate = float(rate_in) if rate_in else 20.0
        if hourly_rate < 0:
            print("[!] Rate cannot be negative. Defaulting to 20.0.")
            hourly_rate = 20.0
    except ValueError:
        print("[!] Invalid input. Defaulting to Rs. 20.0/hr.")
        hourly_rate = 20.0

    lot = ParkingLot(capacity=capacity, hourly_rate=hourly_rate)
    print(f"\n[+] Parking lot initialized with {capacity} slots at Rs. {hourly_rate:.2f}/hour.")

    while True:
        print_menu()
        choice = input("Enter your choice (0-9): ").strip()

        if choice == "1":
            handle_view_slots(lot)
        elif choice == "2":
            handle_park_vehicle(lot)
        elif choice == "3":
            handle_exit_vehicle(lot)
        elif choice == "4":
            handle_search_vehicle(lot)
        elif choice == "5":
            handle_view_queue(lot)
        elif choice == "6":
            handle_view_history(lot)
        elif choice == "7":
            handle_sort_history(lot)
        elif choice == "8":
            handle_undo_last_entry(lot)
        elif choice == "9":
            handle_view_summary(lot)
        elif choice == "0":
            print("\nThank you for using Smart Parking Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("[!] Invalid option. Please enter a number between 0 and 9.")


if __name__ == "__main__":
    run_interactive_app()
