# Smart Parking Management System (DSA College Project)

A comprehensive, modular **Data Structures and Algorithms (DSA)** college project featuring both an **interactive browser-based Web Application (Flask + HTML/CSS/JS)** and a **menu-driven Command-Line Interface (CLI)**.

Manage parking slots, real-time vehicle entry/exit, fee billing, FIFO overflow queues, multi-tier search, linked history auditing, and stack-based undo operations using core data structures implemented from scratch.

---

## 🌟 Live Links

- **GitHub Repository:** [https://github.com/24rautsp/smart-parking-management-system](https://github.com/24rautsp/smart-parking-management-system)
- **GitHub Pages Interactive Web Dashboard:** [https://24rautsp.github.io/smart-parking-management-system/](https://24rautsp.github.io/smart-parking-management-system/)

---

## 📸 Output Screenshots

Here are the live application outputs from the interactive web interface:

### 1. Dashboard Overview & Active Operations
![Dashboard Overview](output-screenshots/output_screenshot_1.png)

### 2. Visual Parking Lot Layout (Array of Slots)
![Visual Parking Lot Layout](output-screenshots/output_screenshot_2.png)

### 3. FIFO Waiting Queue, Multi-Tier Search & Completed History
![Waiting Queue and History](output-screenshots/output_screenshot_3.png)

### 4. Parking Receipt, Fee Calculation & Automatic Queue Handover
![Parking Receipt and Queue Handover](output-screenshots/output_screenshot_4.png)

---

## ⚠️ Important Note: PowerShell & Python Execution

### Why did you see `"from keyword is not supported in this version of the language"`?
This error occurs in Windows PowerShell when Python source code (like `from src.parking_system import ParkingLot`) is pasted directly into the PowerShell terminal prompt. 
- **PowerShell is a Windows shell**, not a Python interpreter.
- In PowerShell, you execute Python scripts by typing:
  ```powershell
  python app.py
  # OR
  python src/main.py
  ```

### Why did GitHub Pages originally display only the README?
GitHub Pages is a static web hosting service (HTML, CSS, JavaScript). By default, if a repository has no `index.html` file, GitHub Pages uses Jekyll to convert `README.md` into a static webpage. Furthermore, **GitHub Pages cannot execute a Python backend (Flask)**. 
- We have added `index.html` and `static/js/app-standalone.js` so that **GitHub Pages now displays the full interactive visual dashboard**.
- To run the **complete Python Flask backend**, run `python app.py` locally or deploy it to a free Python cloud host such as **Render**.

---

## 1. Problem Statement

Urban parking facilities face recurring challenges:
- Inefficient, manual slot searches leading to traffic congestion.
- Chaotic handling of overflow when the parking lot is full.
- Difficulty in quickly checking whether a vehicle is inside and calculating billing.
- Lack of audit trails and error recovery (e.g., mistyped vehicle entries).

This project demonstrates how fundamental Data Structures and Algorithms provide optimal time and space efficiency to solve these challenges without external framework abstractions.

---

## 2. Key Features

- **Visual Interactive Web Dashboard:** Clean, responsive UI with color-coded slot bays (Green = Available, Red = Occupied), vehicle icons, and live statistics.
- **Automated Slot Allocation (Linear Search):** Scans parking slots sequentially and allots the first available bay.
- **Instant Duplicate Prevention (Hash Map O(1)):** Blocks active vehicles from being parked twice.
- **Dynamic Duration-Based Billing:** Computes parking fees using configurable hourly rates and ceiling-rounded durations (`billable_hours = max(1, math.ceil(duration))`).
- **Simulated & Real-Time Duration Modes:** Allows live testing of multi-hour stays during college viva demonstrations without waiting.
- **FIFO Overflow Waiting Queue:** Places arriving vehicles into an orderly line when the facility is at maximum capacity.
- **Automatic Queue Handover:** As soon as any occupied vehicle exits, the freed slot is immediately assigned to the front vehicle in the waiting line.
- **Multi-Tier Vehicle Search:** Locates vehicles across active bays (Hash Map $O(1)$), waiting queue (Queue $O(M)$), or completed history (Linked List $O(K)$).
- **Custom In-Place Insertion Sort:** Sorts parking session history by fee, duration, or license plate in $O(K^2)$ time and $O(1)$ auxiliary space.
- **LIFO Undo Operation (Stack):** Reverts the most recent vehicle entry using an action stack.
- **Dual Interface:** Run in terminal via interactive CLI (`main.py`) or in Google Chrome via Flask web server (`app.py`).

---

## 3. DSA Concepts & Implementation Mapping

Every core feature is powered by a specific Data Structure or Algorithm:

| DSA Concept | File & Component | Role in the Project | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Array / List** | `src/parking_system.py` (`slots`) | Fixed-capacity parking bay representation with indexed access | Access: $O(1)$ | $O(N)$ |
| **Hash Map / Dict** | `src/parking_system.py` (`active_vehicles`) | Maps license plates to assigned slot IDs for instant duplicate detection and fast lookup | Search: $O(1)$<br>Insert: $O(1)$ | $O(N)$ |
| **Queue (FIFO)** | `src/queue.py` (`WaitingQueue`) | Custom linked queue managing overflow vehicles outside | Enqueue: $O(1)$<br>Dequeue: $O(1)$ | $O(M)$ |
| **Stack (LIFO)** | `src/stack.py` (`ActionStack`) | Custom linked stack tracking entry actions to support an Undo feature | Push: $O(1)$<br>Pop: $O(1)$ | $O(S)$ |
| **Linked List** | `src/linked_list.py` (`HistoryLinkedList`) | Custom singly linked list recording completed parking checkout receipts | Append: $O(1)$<br>Traverse: $O(K)$ | $O(K)$ |
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
├── templates/
│   └── index.html            # Flask HTML template for the web dashboard
│
├── static/
│   ├── css/
│   │   └── style.css         # Modern, responsive dark-mode styling
│   └── js/
│       ├── app.js            # Frontend JavaScript connecting to Flask REST API
│       └── app-standalone.js # Hybrid JS engine for GitHub Pages & Flask
│
├── tests/
│   ├── __init__.py           # Package marker
│   ├── test_parking.py       # Automated unit test suite (10 scenarios)
│   └── test_web_api.py       # Automated Flask REST API integration tests (10 scenarios)
│
├── app.py                    # Flask Web Server entry point
├── index.html                # Root entry point for GitHub Pages
├── requirements.txt          # Python dependencies (Flask, Gunicorn)
├── Procfile                  # Cloud deployment configuration for Render/Railway
├── .gitignore                # Git ignore rules for Python caches
└── README.md                 # Complete documentation & viva reference
```

---

## 5. Beginner-Friendly Windows Setup & Execution

### Step 1: Open the Project in VS Code or Terminal
1. Open PowerShell or Command Prompt on Windows.
2. Navigate to your project folder:
   ```powershell
   cd "c:\Users\USER\Downloads\parking system"
   ```

### Step 2: Verify Python Installation
```powershell
python --version
```
*(Ensure Python 3.8 or higher is installed).*

### Step 3: Install Required Dependencies
Install Flask (required for the web application):
```powershell
pip install -r requirements.txt
```

---

## 6. How to Run the Applications

### Option A: Run the Web Application (Interactive Browser)
Start the Flask web server:
```powershell
python app.py
```
Output:
```
============================================================
   SMART PARKING MANAGEMENT SYSTEM - WEB APPLICATION
   Server running at: http://127.0.0.1:5000
   Open this URL in Google Chrome to view your interactive website!
============================================================
```
Now open **Google Chrome** and visit:
👉 **`http://127.0.0.1:5000`**

From the web browser, you can:
- View live visual parking bays (Green = Available, Red = Occupied).
- Park vehicles with auto-slot assignment.
- Exit vehicles and preview the invoice/receipt (supports custom simulated duration for vivas!).
- Watch vehicles enter the FIFO waiting queue when full and get auto-assigned upon exit.
- Search vehicles across Active slots, Waiting queue, and Completed history.
- Sort completed history using custom Insertion Sort.
- Undo the last parking operation using the LIFO Stack.

---

### Option B: Run the Command-Line Interface (CLI Menu)
If your examiner asks for the console interface:
```powershell
python src/main.py
```
Follow the on-screen menu prompts (Options 0 to 9).

---

## 7. Running Automated Tests

Run the full automated test suite covering all 20 scenarios (10 core DSA tests + 10 web API integration tests):

```powershell
python -m unittest -v tests/test_parking.py tests/test_web_api.py
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
test_dsa_info_endpoint (tests.test_web_api.TestWebAPI.test_dsa_info_endpoint) ... ok
test_exit_vehicle_and_auto_queue_handover (tests.test_web_api.TestWebAPI.test_exit_vehicle_and_auto_queue_handover) ... ok
test_full_lot_overflow_to_waiting_queue (tests.test_web_api.TestWebAPI.test_full_lot_overflow_to_waiting_queue) ... ok
test_index_route (tests.test_web_api.TestWebAPI.test_index_route) ... ok
test_park_vehicle_endpoint_success_and_duplicate (tests.test_web_api.TestWebAPI.test_park_vehicle_endpoint_success_and_duplicate) ... ok
test_reset_endpoint (tests.test_web_api.TestWebAPI.test_reset_endpoint) ... ok
test_search_vehicle_endpoint (tests.test_web_api.TestWebAPI.test_search_vehicle_endpoint) ... ok
test_sort_history_endpoint (tests.test_web_api.TestWebAPI.test_sort_history_endpoint) ... ok
test_status_endpoint (tests.test_web_api.TestWebAPI.test_status_endpoint) ... ok
test_undo_endpoint (tests.test_web_api.TestWebAPI.test_undo_endpoint) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.094s

OK
```

---

## 8. Deploying the Python Backend to the Cloud (Free on Render)

Because GitHub Pages only supports static files, deploying the Python Flask backend to a free cloud service gives you a public URL (e.g., `https://smart-parking-xxx.onrender.com`) to share with your professor.

### Step-by-Step Render Deployment Guide:
1. Push your updated code to GitHub:
   ```powershell
   git add .
   git commit -m "Add interactive web app, Flask backend, and standalone pages"
   git push origin main
   ```
2. Go to **[Render.com](https://render.com)** and sign up / log in with your GitHub account.
3. Click **"New +"** $\rightarrow$ select **"Web Service"**.
4. Choose **"Build and deploy from a Git repository"** and connect your repo:
   `24rautsp/smart-parking-management-system`
5. Configure the settings:
   - **Name:** `smart-parking-management-system`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
6. Click **"Deploy Web Service"**.
7. In ~2 minutes, Render will provide a public HTTPS URL that runs your live Python Flask app!

---

## 9. Viva Examination Cheat Sheet

- **Why did you use a custom Queue instead of Python's `list`?**
  *Python's `list.pop(0)` is $O(N)$ because every remaining element must shift left. Our custom `WaitingQueue` uses linked `QueueNode` objects with `front` and `rear` pointers, achieving true $O(1)$ dequeue.*
- **Why did you use a Hash Map alongside the Array?**
  *Checking if a car is already inside an Array requires scanning every slot ($O(N)$ Linear Search). The Hash Map (`active_vehicles`) stores `license_plate -> slot_id`, providing $O(1)$ average time complexity for duplicate prevention.*
- **Why is Insertion Sort suitable here?**
  *Parking history is often nearly sorted chronologically. Insertion Sort runs in $O(K)$ best-case time for nearly sorted arrays and requires $O(1)$ auxiliary space without memory allocation overhead.*
- **How does the Undo feature work?**
  *Every vehicle entry pushes an action record onto the LIFO `ActionStack`. When Undo is called, `pop()` retrieves the most recent operation in $O(1)$ time, and the system restores the slot state.*

---

## 10. License
Developed for academic purposes under the MIT License.
