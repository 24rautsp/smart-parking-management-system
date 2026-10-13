"""
Smart Parking Management System - Core Parking Lot Module
Integrates:
- Array/List: Physical parking slots
- Queue: FIFO waiting line when lot is full
- Hash Map: O(1) active vehicle lookup and duplicate prevention
- Linked List: Completed parking history records
- Stack: Action logging and undo functionality
"""

import time
import math
import os
import sys
from typing import List, Optional, Tuple, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.queue import WaitingQueue
    from src.stack import ActionStack
    from src.linked_list import HistoryLinkedList
except ModuleNotFoundError:
    from queue import WaitingQueue
    from stack import ActionStack
    from linked_list import HistoryLinkedList


class Slot:
    """
    Represents an individual physical parking slot.
    Array element with direct index access.
    """
    def __init__(self, slot_id: int):
        self.slot_id: int = slot_id
        self.is_occupied: bool = False
        self.vehicle_number: Optional[str] = None
        self.entry_time: Optional[float] = None

    def occupy(self, vehicle_number: str, entry_time: Optional[float] = None) -> None:
        self.is_occupied = True
        self.vehicle_number = vehicle_number.strip().upper()
        self.entry_time = entry_time if entry_time is not None else time.time()

    def vacate(self) -> None:
        self.is_occupied = False
        self.vehicle_number = None
        self.entry_time = None

    def __repr__(self) -> str:
        status = f"Occupied by {self.vehicle_number}" if self.is_occupied else "Available"
        return f"Slot #{self.slot_id}: {status}"


class ParkingLot:
    """
    Comprehensive Parking Management System Engine.
    """

    def __init__(self, capacity: int = 5, hourly_rate: float = 20.0):
        if capacity <= 0:
            raise ValueError("Parking lot capacity must be at least 1.")
        if hourly_rate < 0:
            raise ValueError("Hourly rate cannot be negative.")

        self.capacity: int = capacity
        self.hourly_rate: float = hourly_rate

        # 1. Array / List for slots
        self.slots: List[Slot] = [Slot(slot_id=i + 1) for i in range(capacity)]

        # 2. Hash Map (Dictionary) for O(1) active vehicle lookup: plate -> slot_id
        self.active_vehicles: Dict[str, int] = {}

        # 3. FIFO Waiting Queue for overflow vehicles
        self.waiting_queue: WaitingQueue = WaitingQueue()

        # 4. LIFO Action Stack for undo support
        self.action_stack: ActionStack = ActionStack()

        # 5. Singly Linked List for completed parking records
        self.history: HistoryLinkedList = HistoryLinkedList()

        # Total revenue collected
        self.total_revenue: float = 0.0

    # -------------------------------------------------------------
    # 1. Slot Allocation & Vehicle Entry
    # -------------------------------------------------------------
    def find_first_available_slot(self) -> Optional[Slot]:
        """DSA Concept: Linear Search - O(N)"""
        for slot in self.slots:
            if not slot.is_occupied:
                return slot
        return None

    def is_full(self) -> bool:
        """Returns True if all slots are occupied."""
        return len(self.active_vehicles) >= self.capacity

    def park_vehicle(
        self,
        vehicle_number: str,
        entry_time: Optional[float] = None,
        auto_queue: bool = True
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Parks a vehicle or places it in the waiting queue if full.
        """
        if not vehicle_number or not vehicle_number.strip():
            return False, "Vehicle registration number cannot be blank.", None

        normalized_plate = vehicle_number.strip().upper()

        # 1. Check if already actively parked (Hash Map O(1))
        if normalized_plate in self.active_vehicles:
            slot_id = self.active_vehicles[normalized_plate]
            return False, f"Duplicate Entry! Vehicle {normalized_plate} is already parked in Slot #{slot_id}.", None

        # 2. Check if already waiting in queue (Queue traversal O(M))
        if self.waiting_queue.contains(normalized_plate):
            return False, f"Vehicle {normalized_plate} is already waiting in the queue.", None

        # 3. Try finding free slot (Linear Search O(N))
        slot = self.find_first_available_slot()
        if slot is None:
            if auto_queue:
                self.waiting_queue.enqueue(normalized_plate)
                return True, f"Parking full! Vehicle {normalized_plate} added to waiting queue (Position #{self.waiting_queue.size()}).", None
            else:
                return False, f"Parking lot is full (Capacity: {self.capacity}).", None

        # 4. Occupy slot and update active hash map
        slot.occupy(normalized_plate, entry_time)
        self.active_vehicles[normalized_plate] = slot.slot_id

        # 5. Push action to Stack (LIFO O(1))
        self.action_stack.push({
            "action_type": "PARK",
            "vehicle_number": normalized_plate,
            "slot_id": slot.slot_id,
            "entry_time": slot.entry_time
        })

        return True, f"Vehicle {normalized_plate} parked successfully in Slot #{slot.slot_id}.", slot.slot_id

    # -------------------------------------------------------------
    # 2. Vehicle Exit & Queue Handover
    # -------------------------------------------------------------
    def calculate_fee(self, entry_time: float, exit_time: float) -> Tuple[float, float]:
        """
        Calculates duration in hours and total fee.
        Formula:
        duration_hours = (exit_time - entry_time) / 3600
        billable_hours = ceil(max(1.0, duration_hours))
        fee = billable_hours * hourly_rate
        """
        elapsed_seconds = max(0.0, exit_time - entry_time)
        duration_hours = elapsed_seconds / 3600.0

        # Minimum 1 hour, rounded up
        billable_hours = max(1, math.ceil(duration_hours)) if duration_hours > 0 else 1
        total_fee = round(billable_hours * self.hourly_rate, 2)
        return round(duration_hours, 2), total_fee

    def exit_vehicle(
        self,
        vehicle_number: str,
        exit_time: Optional[float] = None,
        simulated_duration_hours: Optional[float] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Removes a vehicle from parking, calculates fee, updates history,
        and auto-assigns the freed slot to the next vehicle in the waiting queue.
        """
        if not vehicle_number or not vehicle_number.strip():
            return False, "Vehicle registration number cannot be blank.", None

        normalized_plate = vehicle_number.strip().upper()

        # Step 1: Lookup vehicle in Hash Map O(1)
        if normalized_plate not in self.active_vehicles:
            return False, f"Vehicle {normalized_plate} is not currently parked in the lot.", None

        slot_id = self.active_vehicles[normalized_plate]
        slot = self.slots[slot_id - 1]

        now = time.time() if exit_time is None else exit_time
        entry_time = slot.entry_time or now

        # Compute duration and fee
        if simulated_duration_hours is not None:
            duration_hours = round(simulated_duration_hours, 2)
            billable_hours = max(1, math.ceil(duration_hours))
            fee = round(billable_hours * self.hourly_rate, 2)
        else:
            duration_hours, fee = self.calculate_fee(entry_time, now)

        # Step 2: Vacate slot and remove from active hash map
        slot.vacate()
        del self.active_vehicles[normalized_plate]
        self.total_revenue += fee

        # Step 3: Append to History Linked List O(1)
        receipt = {
            "vehicle_number": normalized_plate,
            "slot_id": slot_id,
            "entry_time": entry_time,
            "exit_time": now,
            "duration_hours": duration_hours,
            "fee": fee
        }
        self.history.append(receipt)

        # Step 4: Check Waiting Queue (FIFO Handover)
        assigned_waiting_vehicle = None
        if not self.waiting_queue.is_empty():
            assigned_waiting_vehicle = self.waiting_queue.dequeue()
            slot.occupy(assigned_waiting_vehicle, now)
            self.active_vehicles[assigned_waiting_vehicle] = slot.slot_id
            
            # Record stack action for queue assignment
            self.action_stack.push({
                "action_type": "PARK_FROM_QUEUE",
                "vehicle_number": assigned_waiting_vehicle,
                "slot_id": slot.slot_id,
                "entry_time": now
            })

        msg = f"Vehicle {normalized_plate} exited Slot #{slot_id}. Duration: {duration_hours}h, Fee: Rs. {fee:.2f}."
        if assigned_waiting_vehicle:
            msg += f" Slot #{slot_id} assigned to waiting vehicle {assigned_waiting_vehicle}!"

        receipt["assigned_waiting_vehicle"] = assigned_waiting_vehicle
        return True, msg, receipt

    # -------------------------------------------------------------
    # 3. Stack-based Undo Feature
    # -------------------------------------------------------------
    def undo_last_parking(self) -> Tuple[bool, str]:
        """
        DSA Concept: Stack LIFO - O(1)
        Reverts the most recent vehicle entry operation.
        """
        if self.action_stack.is_empty():
            return False, "No recent parking actions to undo."

        last_action = self.action_stack.pop()
        action_type = last_action.get("action_type")
        plate = last_action.get("vehicle_number")
        slot_id = last_action.get("slot_id")

        if action_type in ("PARK", "PARK_FROM_QUEUE"):
            # Check if vehicle is still in that slot
            if plate in self.active_vehicles and self.active_vehicles[plate] == slot_id:
                slot = self.slots[slot_id - 1]
                slot.vacate()
                del self.active_vehicles[plate]
                return True, f"Undo Successful: Parking entry for vehicle {plate} in Slot #{slot_id} has been rolled back."
            else:
                return False, f"Cannot undo: Vehicle {plate} is no longer in Slot #{slot_id}."

        return False, f"Unknown action type '{action_type}' cannot be undone."

    # -------------------------------------------------------------
    # 4. Search and Sorting Algorithms (DSA)
    # -------------------------------------------------------------
    @staticmethod
    def insertion_sort(
        records: List[Dict[str, Any]],
        key: str,
        reverse: bool = False
    ) -> List[Dict[str, Any]]:
        """
        DSA Concept: Insertion Sort Algorithm - O(K^2) worst/average, O(K) best
        Iterates through the list, shifting elements to insert each item
        into its correct sorted position.
        
        Parameters:
            records: List of dictionaries to sort.
            key: Dictionary key to sort by (e.g. 'fee', 'duration_hours', 'vehicle_number').
            reverse: If True, sort descending; else ascending.
        """
        arr = [dict(r) for r in records]  # Make a shallow copy to preserve original order
        n = len(arr)

        for i in range(1, n):
            current_item = arr[i]
            val = current_item.get(key, 0)
            j = i - 1

            if not reverse:
                # Ascending order
                while j >= 0 and arr[j].get(key, 0) > val:
                    arr[j + 1] = arr[j]
                    j -= 1
            else:
                # Descending order
                while j >= 0 and arr[j].get(key, 0) < val:
                    arr[j + 1] = arr[j]
                    j -= 1

            arr[j + 1] = current_item

        return arr

    def search_vehicle(self, vehicle_number: str) -> Dict[str, Any]:
        """
        DSA Concept: Multi-Tier Search
        1. Hash Map Lookup O(1): check active parking slots
        2. Queue Linear Search O(M): check waiting line
        3. Linked List Linear Search O(K): check past sessions
        """
        if not vehicle_number or not vehicle_number.strip():
            return {"found": False, "message": "Search query cannot be empty."}

        target = vehicle_number.strip().upper()
        result: Dict[str, Any] = {
            "found": False,
            "vehicle_number": target,
            "active_status": None,
            "queue_position": None,
            "past_sessions": []
        }

        # 1. Check Active Parking Slots (Hash Map O(1))
        if target in self.active_vehicles:
            slot_id = self.active_vehicles[target]
            slot = self.slots[slot_id - 1]
            result["found"] = True
            result["active_status"] = {
                "slot_id": slot_id,
                "entry_time": slot.entry_time
            }

        # 2. Check Waiting Queue (Queue Linear Traversal O(M))
        waiting_list = self.waiting_queue.to_list()
        for idx, waiting_plate in enumerate(waiting_list):
            if waiting_plate == target:
                result["found"] = True
                result["queue_position"] = idx + 1
                break

        # 3. Check History (Linked List Traversal O(K))
        history_records = self.history.search_by_vehicle(target)
        if history_records:
            result["found"] = True
            result["past_sessions"] = history_records

        return result

    def get_sorted_history(self, sort_by: str = "fee", reverse: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieves all completed parking records from the linked list
        and sorts them using custom Insertion Sort.
        """
        all_records = self.history.to_list()
        valid_keys = {"fee", "duration_hours", "vehicle_number", "slot_id"}
        if sort_by not in valid_keys:
            sort_by = "fee"
        return self.insertion_sort(all_records, key=sort_by, reverse=reverse)

    # -------------------------------------------------------------
    # 5. Status & Statistics
    # -------------------------------------------------------------
    def get_slot_status(self) -> List[Dict[str, Any]]:
        """Returns detailed list of all slots."""
        return [
            {
                "slot_id": s.slot_id,
                "is_occupied": s.is_occupied,
                "vehicle_number": s.vehicle_number,
                "entry_time": s.entry_time
            }
            for s in self.slots
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Returns overview statistics of parking lot."""
        occupied = len(self.active_vehicles)
        return {
            "capacity": self.capacity,
            "occupied_slots": occupied,
            "available_slots": self.capacity - occupied,
            "waiting_count": self.waiting_queue.size(),
            "waiting_vehicles": self.waiting_queue.to_list(),
            "total_completed_sessions": self.history.size(),
            "total_revenue": round(self.total_revenue, 2),
            "hourly_rate": self.hourly_rate
        }


if __name__ == "__main__":
    print("=== Testing Stage 5: Integrated Queue, Stack & Linked List ===")
    lot = ParkingLot(capacity=2, hourly_rate=30.0)

    # 1. Park 2 vehicles (Lot becomes full)
    lot.park_vehicle("KA-01-AA-1111")
    lot.park_vehicle("DL-02-BB-2222")
    print("After parking 2 cars:", lot.get_summary())

    # 2. Park 3rd car -> joins Waiting Queue
    success, msg, _ = lot.park_vehicle("MH-03-CC-3333")
    print("Attempt 3rd car:", msg)
    print("Waiting queue status:", lot.waiting_queue)

    # 3. Exit 1st car with simulated 2.5 hours
    success, exit_msg, receipt = lot.exit_vehicle("KA-01-AA-1111", simulated_duration_hours=2.5)
    print("\nExit car 1:", exit_msg)
    print("Receipt:", receipt)

    # 4. Verify 3rd car automatically got Slot #1!
    print("Updated summary after exit & auto-assign:", lot.get_summary())

    # 5. Test Stack Undo
    undo_status, undo_msg = lot.undo_last_parking()
    print("\nUndo test:", undo_msg)
    print("Summary after undo:", lot.get_summary())

    # 6. Verify Linked List History
    print("\nCompleted History in Linked List:", lot.history.to_list())
