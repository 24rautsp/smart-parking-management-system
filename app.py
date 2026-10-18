"""
Smart Parking Management System - Web Application Server
Flask Backend connected directly to the core DSA implementation:
- Array / List: Physical parking slots
- Hash Map: O(1) active vehicle lookup & duplicate detection
- FIFO Queue: Waiting queue using linked nodes
- LIFO Stack: Action undo feature using linked nodes
- Singly Linked List: Completed parking history
- Insertion Sort: Custom sorting of completed parking sessions
- Linear Search: Finding slots and searching vehicles
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from flask import Flask, render_template, request, jsonify

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.parking_system import ParkingLot

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Application state: Default capacity 6, rate Rs. 20.0/hr
parking_lot = ParkingLot(capacity=6, hourly_rate=20.0)


def format_timestamp(ts: Optional[float]) -> str:
    """Helper to convert epoch timestamp to readable date-time."""
    if not ts:
        return "N/A"
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def enrich_slots(slots_data):
    """Enrich slot data with formatted time string for frontend display."""
    result = []
    for s in slots_data:
        slot_copy = dict(s)
        slot_copy["entry_time_formatted"] = format_timestamp(s.get("entry_time"))
        result.append(slot_copy)
    return result


def enrich_history(records):
    """Enrich history records with formatted time strings."""
    result = []
    for r in records:
        r_copy = dict(r)
        r_copy["entry_time_formatted"] = format_timestamp(r.get("entry_time"))
        r_copy["exit_time_formatted"] = format_timestamp(r.get("exit_time"))
        result.append(r_copy)
    return result


@app.route("/")
def index():
    """Serves the main interactive dashboard."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns the current state of slots, waiting queue, and overall summary."""
    summary = parking_lot.get_summary()
    slots = enrich_slots(parking_lot.get_slot_status())
    return jsonify({
        "success": True,
        "summary": summary,
        "slots": slots
    })


@app.route("/api/park", methods=["POST"])
def park_vehicle():
    """
    Parks a vehicle. Uses:
    - Hash Map O(1) for duplicate check
    - Linear Search O(N) for finding available slot in Array
    - FIFO Queue O(1) enqueue if parking lot is full
    - LIFO Stack O(1) push for undo logging
    """
    data = request.get_json(silent=True) or {}
    vehicle_number = data.get("vehicle_number", "").strip()

    if not vehicle_number:
        return jsonify({
            "success": False,
            "message": "Vehicle registration number cannot be blank."
        }), 400

    success, message, slot_id = parking_lot.park_vehicle(vehicle_number)
    status_code = 200 if success else 400

    return jsonify({
        "success": success,
        "message": message,
        "slot_id": slot_id,
        "summary": parking_lot.get_summary(),
        "slots": enrich_slots(parking_lot.get_slot_status())
    }), status_code


@app.route("/api/exit", methods=["POST"])
def exit_vehicle():
    """
    Exits a vehicle. Uses:
    - Hash Map O(1) lookup
    - Fee Calculation formula
    - Linked List O(1) append for history
    - FIFO Queue O(1) dequeue for auto-handover to next waiting vehicle
    """
    data = request.get_json(silent=True) or {}
    vehicle_number = data.get("vehicle_number", "").strip()
    simulated_hours = data.get("simulated_duration_hours")

    if not vehicle_number:
        return jsonify({
            "success": False,
            "message": "Vehicle registration number cannot be blank."
        }), 400

    # Parse optional simulated duration for viva demonstrations
    sim_hours_float = None
    if simulated_hours is not None and str(simulated_hours).strip() != "":
        try:
            sim_hours_float = float(simulated_hours)
            if sim_hours_float < 0:
                return jsonify({
                    "success": False,
                    "message": "Duration cannot be negative."
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid duration value provided."
            }), 400

    success, message, receipt = parking_lot.exit_vehicle(
        vehicle_number,
        simulated_duration_hours=sim_hours_float
    )

    if not success:
        return jsonify({
            "success": False,
            "message": message
        }), 404

    receipt_enriched = dict(receipt) if receipt else {}
    if receipt:
        receipt_enriched["entry_time_formatted"] = format_timestamp(receipt.get("entry_time"))
        receipt_enriched["exit_time_formatted"] = format_timestamp(receipt.get("exit_time"))

    return jsonify({
        "success": True,
        "message": message,
        "receipt": receipt_enriched,
        "summary": parking_lot.get_summary(),
        "slots": enrich_slots(parking_lot.get_slot_status())
    }), 200


@app.route("/api/search", methods=["GET"])
def search_vehicle():
    """
    Multi-tier search across:
    1. Active Hash Map O(1)
    2. Waiting Queue O(M)
    3. Linked List History O(K)
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({
            "success": False,
            "message": "Search query cannot be empty."
        }), 400

    result = parking_lot.search_vehicle(query)

    # Format timestamps in search result
    if result.get("active_status"):
        result["active_status"]["entry_time_formatted"] = format_timestamp(
            result["active_status"].get("entry_time")
        )
    if result.get("past_sessions"):
        result["past_sessions"] = enrich_history(result["past_sessions"])

    return jsonify({
        "success": True,
        "data": result
    }), 200


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Returns completed parking history sorted using custom Insertion Sort.
    Query parameters:
    - sort_by: 'fee', 'duration_hours', 'vehicle_number', 'slot_id'
    - reverse: 'true' (descending) or 'false' (ascending)
    """
    sort_by = request.args.get("sort_by", "fee")
    reverse_param = request.args.get("reverse", "true").lower() == "true"

    sorted_records = parking_lot.get_sorted_history(sort_by=sort_by, reverse=reverse_param)
    return jsonify({
        "success": True,
        "sort_by": sort_by,
        "reverse": reverse_param,
        "count": len(sorted_records),
        "history": enrich_history(sorted_records)
    })


@app.route("/api/undo", methods=["POST"])
def undo_last():
    """
    DSA Concept: Stack LIFO
    Rolls back the most recent parking action recorded on the ActionStack.
    """
    success, message = parking_lot.undo_last_parking()
    status_code = 200 if success else 400
    return jsonify({
        "success": success,
        "message": message,
        "summary": parking_lot.get_summary(),
        "slots": enrich_slots(parking_lot.get_slot_status())
    }), status_code


@app.route("/api/reset", methods=["POST"])
def reset_system():
    """Resets the parking lot system with custom capacity and rate (for viva demo)."""
    global parking_lot
    data = request.get_json(silent=True) or {}
    capacity = int(data.get("capacity", 6))
    hourly_rate = float(data.get("hourly_rate", 20.0))

    if capacity <= 0 or capacity > 50:
        return jsonify({"success": False, "message": "Capacity must be between 1 and 50."}), 400
    if hourly_rate < 0:
        return jsonify({"success": False, "message": "Hourly rate cannot be negative."}), 400

    parking_lot = ParkingLot(capacity=capacity, hourly_rate=hourly_rate)
    return jsonify({
        "success": True,
        "message": f"Parking lot reset to {capacity} slots at Rs. {hourly_rate:.2f}/hour.",
        "summary": parking_lot.get_summary(),
        "slots": enrich_slots(parking_lot.get_slot_status())
    })


@app.route("/api/dsa-info", methods=["GET"])
def get_dsa_info():
    """Provides DSA concept mapping for educational and viva demonstration."""
    return jsonify({
        "concepts": [
            {
                "concept": "Array / List",
                "component": "Parking Slots",
                "time_complexity": "O(1) index access",
                "space_complexity": "O(N) fixed capacity",
                "description": "Stores individual physical parking bays with contiguous indices."
            },
            {
                "concept": "Hash Map (Dictionary)",
                "component": "Active Vehicles Registry",
                "time_complexity": "O(1) average lookup/insert/delete",
                "space_complexity": "O(N) active vehicles",
                "description": "Maps vehicle registration plate to slot ID for instant duplicate detection and fast lookups."
            },
            {
                "concept": "Queue (FIFO)",
                "component": "Waiting Overflow Line",
                "time_complexity": "O(1) enqueue, O(1) dequeue",
                "space_complexity": "O(M) waiting vehicles",
                "description": "Custom linked nodes with front and rear pointers to guarantee fair First-In, First-Out slot allocation."
            },
            {
                "concept": "Stack (LIFO)",
                "component": "Action Stack & Undo",
                "time_complexity": "O(1) push, O(1) pop",
                "space_complexity": "O(S) recent operations",
                "description": "Custom linked nodes recording recent entries to support instant rollback."
            },
            {
                "concept": "Singly Linked List",
                "component": "Completed Parking History",
                "time_complexity": "O(1) append, O(K) traversal",
                "space_complexity": "O(K) completed sessions",
                "description": "Dynamic node-based sequence storing session receipts without needing contiguous array resizing."
            },
            {
                "concept": "Linear Search",
                "component": "Slot Allocation & Vehicle Search",
                "time_complexity": "O(N) slot scan, O(M) queue scan",
                "space_complexity": "O(1)",
                "description": "Finds the first free parking bay and searches queue nodes sequentially."
            },
            {
                "concept": "Insertion Sort",
                "component": "Completed History Ordering",
                "time_complexity": "O(K^2) worst/average, O(K) best",
                "space_complexity": "O(1) auxiliary",
                "description": "Sorts session records by total fee, duration, or vehicle plate in-place."
            }
        ]
    })


if __name__ == "__main__":
    # Runs local server on port 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"\n" + "=" * 60)
    print("   SMART PARKING MANAGEMENT SYSTEM - WEB APPLICATION")
    print(f"   Server running at: http://127.0.0.1:{port}")
    print("   Open this URL in Google Chrome to view your interactive website!")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=True)
