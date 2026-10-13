# Smart Parking Management System (DSA College Project)

A modular, menu-driven Python application designed for **Data Structures and Algorithms (DSA)** coursework. It manages parking slot allocation, real-time vehicle entry/exit, waiting queues, historical session auditing, and stack-based undo operations using core data structures implemented from scratch.

---

## 1. Problem Statement

Urban parking facilities face recurring challenges:
- Inefficient, manual slot searches leading to traffic congestion.
- Chaotic handling of overflow when the parking lot is full.
- Difficulty in quickly checking whether a vehicle is inside and calculating billing.
- Lack of audit trails and error recovery (e.g., mistyped vehicle entries).

This project demonstrates how fundamental Data Structures and Algorithms provide optimal time and space efficiency to solve these challenges without external framework dependencies.

---

## 2. Key Features

- **Automated Slot Allocation:** Scans slots sequentially and assigns the first available bay.
- **Duplicate Entry Prevention:** Instantly blocks active vehicles from being parked twice.
- **Dynamic Duration-Based Billing:** Computes parking fees using configurable hourly rates and ceiling-rounded durations.
- **Simulated & Real-Time Duration Modes:** Allows live testing of multi-hour stays during college viva demonstrations without waiting.
- **FIFO Overflow Waiting Queue:** Places arriving vehicles into an orderly line when the facility is at maximum capacity.
- **Automatic Queue Handover:** As soon as any occupied vehicle exits, the freed slot is immediately assigned to the front vehicle in the waiting line.
- **Multi-Tier Vehicle Search:** Locates vehicles across active bays, the waiting queue, or completed history.
- **Custom In-Place Insertion Sort:** Sorts parking session history by fee, duration, or license plate.
- **LIFO Undo Operation:** Reverts the most recent vehicle entry using an action stack.
- **Input Validation & Crash Resilience:** Handles blank inputs, invalid selections, and negative values cleanly.

---

## 3. DSA Concepts & Implementation Mapping

Every core feature is powered by a specific Data Structure or Algorithm:

| DSA Concept | File & Component | Role in the Project | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Array / List** | `src/parking_system.py` (`slots`) | Fixed-capacity parking bay representation with indexed access | Access: $O(1)$ | $O(N)$ |
| **Queue (FIFO)** | `src/queue.py` (`WaitingQueue`) | Custom linked queue managing overflow vehicles outside | Enqueue: $O(1)$<br>Dequeue: $O(1)$ | $O(M)$ |
| **Hash Map / Dict** | `src/parking_system.py` (`active_vehicles`) | Maps license plates to assigned slot IDs for instant lookup | Search: $O(1)$<br>Insert: $O(1)$ | $O(N)$ |
| **Linked List** | `src/linked_list.py` (`HistoryLinkedList`) | Custom singly linked list recording completed parking checkout receipts | Append: $O(1)$<br>Traverse: $O(K)$ | $O(K)$ |
| **Stack (LIFO)** | `src/stack.py` (`ActionStack`) | Custom linked stack tracking entry actions to support an Undo feature | Push: $O(1)$<br>Pop: $O(1)$ | $O(S)$ |
| **Linear Search** | `find_first_available_slot()`, `search_vehicle()` | Finds first free slot index or searches past visits | Search: $O(N)$ or $O(K)$ | $O(1)$ |
| **Insertion Sort** | `insertion_sort()` | Custom in-place sorting of completed history by fee, duration, or plate | Worst/Avg: $O(K^2)$<br>Best: $O(K)$ | $O(1)$ auxiliary |

*(Legend: $N$ = total parking bays, $M$ = waiting vehicles, $K$ = completed history records, $S$ = action stack depth)*

---

## 4. Project Folder Structure

```
parking-system/
│
├── src/
│   ├── __init__.py           # Package marker
│   ├── queue.py              # Custom FIFO Queue using linked nodes
│   ├── stack.py              # Custom LIFO Stack using linked nodes
│   ├── linked_list.py        # Custom Singly Linked List with head & tail pointers
│   ├── parking_system.py     # Core ParkingLot engine & Insertion Sort
│   └── main.py               # Interactive CLI menu & tabular renderer
│
├── tests/
│   ├── __init__.py           # Package marker
│   └── test_parking.py       # Automated unit test suite (10 scenarios)
│
├── .gitignore                # Git ignore rules for Python caches
└── README.md                 # Complete documentation & viva reference
```

---

## 5. Prerequisites and Setup

- **Python Version:** Python 3.8 or higher.
- **Dependencies:** Built purely on Python standard library modules (`time`, `math`, `sys`, `os`, `unittest`). No external `pip install` required!

### Setup Steps:
1. Clone or download the project into your local folder.
2. Open a terminal (PowerShell, Command Prompt, or bash) in the project root:
   ```powershell
   cd "parking system"
   ```

---

## 6. How to Run the Application

Start the interactive console application:

```powershell
python src/main.py
```

### Main Menu Overview:
```
=================================================================
        SMART PARKING MANAGEMENT SYSTEM (DSA PROJECT)
=================================================================
 1. View All Parking Slots
 2. Park a Vehicle (Auto-Assign Slot)
 3. Exit a Vehicle & Calculate Fee
 4. Search Vehicle (Active, Queue, History)
 5. View Waiting Queue (FIFO)
 6. View Completed Parking History
 7. Sort Completed History (Custom Insertion Sort)
 8. Undo Last Entry (LIFO Stack)
 9. View System Statistics & Revenue
 0. Exit System
```

---

## 7. Sample Demonstration Walkthrough

1. **Initialize:** Set capacity to `3` slots and hourly rate to `Rs. 25.00`.
2. **Park 3 Vehicles:**
   - Park `KA01AB1234` $\rightarrow$ Assigned Slot #1.
   - Park `DL02CD5678` $\rightarrow$ Assigned Slot #2.
   - Park `MH03EF9999` $\rightarrow$ Assigned Slot #3 (Lot is now 100% full).
3. **Trigger Waiting Queue:**
   - Park `UP04GH0001` $\rightarrow$ System notifies lot is full and enqueues the vehicle at Position #1 in the waiting line.
4. **Exit and Auto-Handover:**
   - Select Option 3 to exit `KA01AB1234` with 2.5 hours duration.
   - Total Fee calculated: $3 \times \text{Rs. } 25 = \text{Rs. } 75.00$.
   - Slot #1 is freed and **immediately assigned** to waiting vehicle `UP04GH0001`!
5. **Undo Demonstration:**
   - Select Option 8 (Undo Last Entry). Slot #1 is vacated and returned to available status.
6. **Sort Completed History:**
   - Select Option 7 to sort receipts by Fee Paid in descending order using custom Insertion Sort.

---

## 8. Automated Testing

Run the built-in test suite covering all 10 edge cases and features:

```powershell
python -m unittest -v tests/test_parking.py
```

Expected output:
```
test_fee_calculations (tests.test_parking.TestParkingSystem.test_fee_calculations) ... ok
test_fill_lot_and_prevent_duplicates (tests.test_parking.TestParkingSystem.test_fill_lot_and_prevent_duplicates) ... ok
test_initial_state_empty (tests.test_parking.TestParkingSystem.test_initial_state_empty) ... ok
test_insertion_sort (tests.test_parking.TestParkingSystem.test_insertion_sort) ... ok
test_queue_handover_on_exit (tests.test_parking.TestParkingSystem.test_queue_handover_on_exit) ... ok
test_search_functionality (tests.test_parking.TestParkingSystem.test_search_functionality) ... ok
test_single_vehicle_entry_and_exit (tests.test_parking.TestParkingSystem.test_single_vehicle_entry_and_exit) ... ok
test_undo_last_entry (tests.test_parking.TestParkingSystem.test_undo_last_entry) ... ok
test_unknown_vehicle_exit (tests.test_parking.TestParkingSystem.test_unknown_vehicle_exit) ... ok
test_waiting_queue_overflow (tests.test_parking.TestParkingSystem.test_waiting_queue_overflow) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.003s

OK
```

---

## 9. Future Enhancements

- **Vehicle Categorization:** Support multi-tier pricing based on vehicle type (Two-Wheeler, Sedan, SUV, EV).
- **Persistent Storage:** Integrate SQLite or JSON file persistence across program restarts.
- **Graphical / Web Dashboard:** Build a visual UI with Tkinter or Flask while preserving the same DSA core engine.
- **Priority Queue / Heap:** Allow VIP parking reservations or emergency vehicle preemptions using a Min-Heap.
