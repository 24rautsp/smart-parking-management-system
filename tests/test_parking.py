"""
Smart Parking Management System - Automated Unit Test Suite
Uses Python's standard `unittest` framework to test all required scenarios and edge cases.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parking_system import ParkingLot
from src.queue import WaitingQueue
from src.stack import ActionStack
from src.linked_list import HistoryLinkedList


class TestParkingSystem(unittest.TestCase):
    """Comprehensive unit test suite for Smart Parking Management System."""

    def setUp(self):
        """Set up a fresh ParkingLot instance before each test."""
        self.capacity = 3
        self.hourly_rate = 20.0
        self.lot = ParkingLot(capacity=self.capacity, hourly_rate=self.hourly_rate)

    # -------------------------------------------------------------
    # Scenario 1: Initial State & Empty Slots
    # -------------------------------------------------------------
    def test_initial_state_empty(self):
        summary = self.lot.get_summary()
        self.assertEqual(summary["capacity"], 3)
        self.assertEqual(summary["occupied_slots"], 0)
        self.assertEqual(summary["available_slots"], 3)
        self.assertEqual(summary["waiting_count"], 0)
        self.assertEqual(summary["total_revenue"], 0.0)

        # Verify all slots in array are marked unoccupied
        for slot in self.lot.slots:
            self.assertFalse(slot.is_occupied)
            self.assertIsNone(slot.vehicle_number)

    # -------------------------------------------------------------
    # Scenario 2: Single Vehicle Entry and Exit
    # -------------------------------------------------------------
    def test_single_vehicle_entry_and_exit(self):
        # Entry
        success, msg, slot_id = self.lot.park_vehicle("KA-01-AB-1234")
        self.assertTrue(success)
        self.assertEqual(slot_id, 1)
        self.assertIn("KA-01-AB-1234", self.lot.active_vehicles)
        self.assertTrue(self.lot.slots[0].is_occupied)

        # Exit with 2.0 hours duration
        exit_success, exit_msg, receipt = self.lot.exit_vehicle(
            "KA-01-AB-1234",
            simulated_duration_hours=2.0
        )
        self.assertTrue(exit_success)
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["fee"], 40.0)  # 2 hours * 20.0
        self.assertNotIn("KA-01-AB-1234", self.lot.active_vehicles)
        self.assertFalse(self.lot.slots[0].is_occupied)
        self.assertEqual(self.lot.history.size(), 1)
        self.assertEqual(self.lot.total_revenue, 40.0)

    # -------------------------------------------------------------
    # Scenario 3: Parking Lot Fills Up & Duplicate Entry Check
    # -------------------------------------------------------------
    def test_fill_lot_and_prevent_duplicates(self):
        # Fill all 3 slots
        self.assertTrue(self.lot.park_vehicle("CAR-1")[0])
        self.assertTrue(self.lot.park_vehicle("CAR-2")[0])
        self.assertTrue(self.lot.park_vehicle("CAR-3")[0])
        self.assertTrue(self.lot.is_full())

        # Attempt duplicate entry
        dup_success, dup_msg, _ = self.lot.park_vehicle("CAR-2")
        self.assertFalse(dup_success)
        self.assertIn("Duplicate Entry", dup_msg)

        # Attempt blank vehicle plate
        blank_success, blank_msg, _ = self.lot.park_vehicle("   ")
        self.assertFalse(blank_success)

    # -------------------------------------------------------------
    # Scenario 4: Waiting Queue FIFO Order
    # -------------------------------------------------------------
    def test_waiting_queue_overflow(self):
        # Fill lot
        self.lot.park_vehicle("CAR-1")
        self.lot.park_vehicle("CAR-2")
        self.lot.park_vehicle("CAR-3")

        # 4th and 5th cars join the waiting queue
        q1_success, q1_msg, _ = self.lot.park_vehicle("WAIT-1")
        q2_success, q2_msg, _ = self.lot.park_vehicle("WAIT-2")

        self.assertTrue(q1_success)
        self.assertTrue(q2_success)
        self.assertEqual(self.lot.waiting_queue.size(), 2)
        self.assertEqual(self.lot.waiting_queue.to_list(), ["WAIT-1", "WAIT-2"])

        # Prevent duplicate waitlist entry
        dup_wait_success, dup_wait_msg, _ = self.lot.park_vehicle("WAIT-1")
        self.assertFalse(dup_wait_success)
        self.assertIn("already waiting", dup_wait_msg)

    # -------------------------------------------------------------
    # Scenario 5: Slot Freed and Auto-Assigned to Waiting Car
    # -------------------------------------------------------------
    def test_queue_handover_on_exit(self):
        self.lot.park_vehicle("CAR-1")
        self.lot.park_vehicle("CAR-2")
        self.lot.park_vehicle("CAR-3")
        self.lot.park_vehicle("WAIT-FIRST")
        self.lot.park_vehicle("WAIT-SECOND")

        # CAR-2 in Slot #2 exits
        exit_success, _, receipt = self.lot.exit_vehicle("CAR-2", simulated_duration_hours=1.0)
        self.assertTrue(exit_success)
        self.assertEqual(receipt["assigned_waiting_vehicle"], "WAIT-FIRST")

        # Verify WAIT-FIRST is now parked in Slot #2
        self.assertEqual(self.lot.active_vehicles["WAIT-FIRST"], 2)
        self.assertTrue(self.lot.slots[1].is_occupied)
        self.assertEqual(self.lot.slots[1].vehicle_number, "WAIT-FIRST")

        # Verify WAIT-SECOND is now the next front in queue
        self.assertEqual(self.lot.waiting_queue.size(), 1)
        self.assertEqual(self.lot.waiting_queue.peek(), "WAIT-SECOND")

    # -------------------------------------------------------------
    # Scenario 6: Unknown Vehicle Exit Rejection
    # -------------------------------------------------------------
    def test_unknown_vehicle_exit(self):
        exit_success, exit_msg, _ = self.lot.exit_vehicle("GHOST-CAR")
        self.assertFalse(exit_success)
        self.assertIn("not currently parked", exit_msg)

    # -------------------------------------------------------------
    # Scenario 7: Fee Calculation Logic (Ceil and Minimum 1 Hour)
    # -------------------------------------------------------------
    def test_fee_calculations(self):
        # 1. Stay for 0.3 hours -> rounded to 1 hour minimum
        _, fee1 = self.lot.calculate_fee(entry_time=0.0, exit_time=0.3 * 3600)
        self.assertEqual(fee1, 20.0)

        # 2. Stay for 2.1 hours -> ceil to 3 hours
        _, fee2 = self.lot.calculate_fee(entry_time=0.0, exit_time=2.1 * 3600)
        self.assertEqual(fee2, 60.0)

        # 3. Stay for exactly 3.0 hours -> 3 hours
        _, fee3 = self.lot.calculate_fee(entry_time=0.0, exit_time=3.0 * 3600)
        self.assertEqual(fee3, 60.0)

    # -------------------------------------------------------------
    # Scenario 8: Stack-Based Undo Operation (LIFO)
    # -------------------------------------------------------------
    def test_undo_last_entry(self):
        # Park vehicle
        self.lot.park_vehicle("CAR-UNDO")
        self.assertIn("CAR-UNDO", self.lot.active_vehicles)
        self.assertEqual(self.lot.action_stack.size(), 1)

        # Undo
        undo_success, undo_msg = self.lot.undo_last_parking()
        self.assertTrue(undo_success)
        self.assertNotIn("CAR-UNDO", self.lot.active_vehicles)
        self.assertFalse(self.lot.slots[0].is_occupied)
        self.assertEqual(self.lot.action_stack.size(), 0)

        # Undo on empty stack
        undo_empty_success, _ = self.lot.undo_last_parking()
        self.assertFalse(undo_empty_success)

    # -------------------------------------------------------------
    # Scenario 9: Multi-Tier Search (Active, Queue, History)
    # -------------------------------------------------------------
    def test_search_functionality(self):
        self.lot.park_vehicle("ACTIVE-1")
        self.lot.park_vehicle("EXITED-1")
        self.lot.park_vehicle("ACTIVE-2")
        self.lot.park_vehicle("WAITING-1")

        # Exit EXITED-1 to create historical record
        self.lot.exit_vehicle("EXITED-1", simulated_duration_hours=1.5)

        # Search Active
        res_active = self.lot.search_vehicle("ACTIVE-1")
        self.assertTrue(res_active["found"])
        self.assertIsNotNone(res_active["active_status"])
        self.assertEqual(res_active["active_status"]["slot_id"], 1)

        # Search Waiting
        # Note: EXITED-1 freed slot 2, which auto-assigned to WAITING-1!
        res_waiting = self.lot.search_vehicle("WAITING-1")
        self.assertTrue(res_waiting["found"])
        self.assertEqual(res_waiting["active_status"]["slot_id"], 2)

        # Search Historical
        res_history = self.lot.search_vehicle("EXITED-1")
        self.assertTrue(res_history["found"])
        self.assertEqual(len(res_history["past_sessions"]), 1)
        self.assertEqual(res_history["past_sessions"][0]["slot_id"], 2)

        # Search Non-existent
        res_none = self.lot.search_vehicle("NONEXISTENT")
        self.assertFalse(res_none["found"])

    # -------------------------------------------------------------
    # Scenario 10: Custom Insertion Sort Algorithm
    # -------------------------------------------------------------
    def test_insertion_sort(self):
        sample_records = [
            {"vehicle_number": "B-CAR", "duration_hours": 3.0, "fee": 60.0},
            {"vehicle_number": "A-CAR", "duration_hours": 1.0, "fee": 20.0},
            {"vehicle_number": "C-CAR", "duration_hours": 5.0, "fee": 100.0},
        ]

        # 1. Sort by fee descending
        sorted_fee_desc = ParkingLot.insertion_sort(sample_records, key="fee", reverse=True)
        fees_desc = [r["fee"] for r in sorted_fee_desc]
        self.assertEqual(fees_desc, [100.0, 60.0, 20.0])

        # 2. Sort by duration ascending
        sorted_dur_asc = ParkingLot.insertion_sort(sample_records, key="duration_hours", reverse=False)
        durs_asc = [r["duration_hours"] for r in sorted_dur_asc]
        self.assertEqual(durs_asc, [1.0, 3.0, 5.0])

        # 3. Sort by vehicle plate alphabetical
        sorted_plates = ParkingLot.insertion_sort(sample_records, key="vehicle_number", reverse=False)
        plates = [r["vehicle_number"] for r in sorted_plates]
        self.assertEqual(plates, ["A-CAR", "B-CAR", "C-CAR"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
