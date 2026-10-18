"""
Automated Integration and Unit Tests for Smart Parking Management System Web APIs
Tests the Flask REST API endpoints and their integration with underlying DSA structures.
"""

import os
import sys
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, parking_lot
from src.parking_system import ParkingLot


class TestWebAPI(unittest.TestCase):
    """Test suite for Flask Web endpoints and DSA integration."""

    def setUp(self):
        """Configure test client and initialize fresh ParkingLot instance."""
        self.app = app
        self.client = self.app.test_client()
        # Reset global parking lot for each test to 3 slots, rate Rs. 20.0
        import app as app_module
        app_module.parking_lot = ParkingLot(capacity=3, hourly_rate=20.0)

    def test_index_route(self):
        """Verify the main web dashboard page renders with HTTP 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Parking Management System", response.data)
        self.assertIn(b"Visual Parking Lot Layout", response.data)

    def test_status_endpoint(self):
        """Verify /api/status returns accurate initial state."""
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["summary"]["capacity"], 3)
        self.assertEqual(data["summary"]["occupied_slots"], 0)
        self.assertEqual(data["summary"]["available_slots"], 3)
        self.assertEqual(len(data["slots"]), 3)

    def test_park_vehicle_endpoint_success_and_duplicate(self):
        """Verify /api/park handles normal entry and prevents duplicates."""
        # 1. Normal Entry
        res = self.client.post("/api/park", json={"vehicle_number": "KA01AB1234"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["slot_id"], 1)
        self.assertEqual(data["summary"]["occupied_slots"], 1)

        # 2. Duplicate Entry Attempt
        dup_res = self.client.post("/api/park", json={"vehicle_number": "KA01AB1234"})
        self.assertEqual(dup_res.status_code, 400)
        dup_data = json.loads(dup_res.data)
        self.assertFalse(dup_data["success"])
        self.assertIn("Duplicate Entry", dup_data["message"])

        # 3. Blank Plate Entry Attempt
        blank_res = self.client.post("/api/park", json={"vehicle_number": "   "})
        self.assertEqual(blank_res.status_code, 400)

    def test_full_lot_overflow_to_waiting_queue(self):
        """Verify vehicles overflow to FIFO Waiting Queue when lot is full."""
        # Fill 3 slots
        self.client.post("/api/park", json={"vehicle_number": "CAR1"})
        self.client.post("/api/park", json={"vehicle_number": "CAR2"})
        self.client.post("/api/park", json={"vehicle_number": "CAR3"})

        # 4th vehicle joins waiting queue
        q_res = self.client.post("/api/park", json={"vehicle_number": "WAIT1"})
        self.assertEqual(q_res.status_code, 200)
        q_data = json.loads(q_res.data)
        self.assertTrue(q_data["success"])
        self.assertIn("added to waiting queue", q_data["message"])
        self.assertEqual(q_data["summary"]["waiting_count"], 1)
        self.assertIn("WAIT1", q_data["summary"]["waiting_vehicles"])

    def test_exit_vehicle_and_auto_queue_handover(self):
        """Verify exit computes fee and hands freed slot to waiting car."""
        # Park 3 cars + 1 waiting car
        self.client.post("/api/park", json={"vehicle_number": "CAR1"})
        self.client.post("/api/park", json={"vehicle_number": "CAR2"})
        self.client.post("/api/park", json={"vehicle_number": "CAR3"})
        self.client.post("/api/park", json={"vehicle_number": "WAIT1"})

        # Exit CAR1 with simulated 2.5 hours
        exit_res = self.client.post("/api/exit", json={
            "vehicle_number": "CAR1",
            "simulated_duration_hours": 2.5
        })
        self.assertEqual(exit_res.status_code, 200)
        exit_data = json.loads(exit_res.data)
        self.assertTrue(exit_data["success"])
        # 2.5 hours ceil -> 3 hours * Rs. 20 = Rs. 60.00
        self.assertEqual(exit_data["receipt"]["fee"], 60.0)
        self.assertEqual(exit_data["receipt"]["assigned_waiting_vehicle"], "WAIT1")
        # Slot 1 should now be occupied by WAIT1
        self.assertEqual(exit_data["summary"]["occupied_slots"], 3)
        self.assertEqual(exit_data["summary"]["waiting_count"], 0)

    def test_search_vehicle_endpoint(self):
        """Verify /api/search finds vehicles in active, queue, and history."""
        self.client.post("/api/park", json={"vehicle_number": "SEARCH1"})
        
        # Search active
        res = self.client.get("/api/search?q=SEARCH1")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["data"]["found"])
        self.assertIsNotNone(data["data"]["active_status"])

        # Search non-existent
        res_non = self.client.get("/api/search?q=UNKNOWN99")
        self.assertEqual(res_non.status_code, 200)
        data_non = json.loads(res_non.data)
        self.assertFalse(data_non["data"]["found"])

    def test_sort_history_endpoint(self):
        """Verify /api/history applies custom Insertion Sort correctly."""
        # Park and exit 2 vehicles with different simulated fees
        self.client.post("/api/park", json={"vehicle_number": "C1"})
        self.client.exit_vehicle = self.client.post("/api/exit", json={"vehicle_number": "C1", "simulated_duration_hours": 1.0}) # Rs. 20

        self.client.post("/api/park", json={"vehicle_number": "C2"})
        self.client.post("/api/exit", json={"vehicle_number": "C2", "simulated_duration_hours": 4.0}) # Rs. 80

        # Sort descending by fee
        res_desc = self.client.get("/api/history?sort_by=fee&reverse=true")
        self.assertEqual(res_desc.status_code, 200)
        data_desc = json.loads(res_desc.data)
        self.assertEqual(len(data_desc["history"]), 2)
        self.assertEqual(data_desc["history"][0]["vehicle_number"], "C2") # higher fee first
        self.assertEqual(data_desc["history"][1]["vehicle_number"], "C1")

        # Sort ascending by fee
        res_asc = self.client.get("/api/history?sort_by=fee&reverse=false")
        data_asc = json.loads(res_asc.data)
        self.assertEqual(data_asc["history"][0]["vehicle_number"], "C1") # lower fee first

    def test_undo_endpoint(self):
        """Verify /api/undo rolls back last entry."""
        self.client.post("/api/park", json={"vehicle_number": "UNDO1"})
        undo_res = self.client.post("/api/undo")
        self.assertEqual(undo_res.status_code, 200)
        undo_data = json.loads(undo_res.data)
        self.assertTrue(undo_data["success"])
        self.assertIn("rolled back", undo_data["message"])
        self.assertEqual(undo_data["summary"]["occupied_slots"], 0)

    def test_reset_endpoint(self):
        """Verify /api/reset updates lot capacity and hourly rate."""
        reset_res = self.client.post("/api/reset", json={"capacity": 5, "hourly_rate": 25.0})
        self.assertEqual(reset_res.status_code, 200)
        reset_data = json.loads(reset_res.data)
        self.assertEqual(reset_data["summary"]["capacity"], 5)
        self.assertEqual(reset_data["summary"]["hourly_rate"], 25.0)

    def test_dsa_info_endpoint(self):
        """Verify /api/dsa-info returns mapping of concepts."""
        info_res = self.client.get("/api/dsa-info")
        self.assertEqual(info_res.status_code, 200)
        info_data = json.loads(info_res.data)
        self.assertGreaterEqual(len(info_data["concepts"]), 6)


if __name__ == "__main__":
    unittest.main()
