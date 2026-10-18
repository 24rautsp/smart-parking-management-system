/**
 * Smart Parking Management System - Hybrid Standalone / Connected Engine
 * - If running with Flask backend (e.g. http://127.0.0.1:5000), delegates to Python API.
 * - If running on GitHub Pages (static host), runs the identical DSA data structures
 *   in browser memory to provide a 100% interactive demonstration on GitHub Pages!
 */

(function() {
    // -------------------------------------------------------------
    // Core DSA Implementations (Mirroring Python Classes)
    // -------------------------------------------------------------

    // 1. Queue Node and FIFO Waiting Queue
    class QueueNode {
        constructor(data) {
            this.data = data;
            this.next = null;
        }
    }

    class WaitingQueue {
        constructor() {
            this.front = null;
            this.rear = null;
            this.count = 0;
        }
        isEmpty() { return this.front === null; }
        size() { return this.count; }
        enqueue(plate) {
            const node = new QueueNode(plate.toUpperCase());
            if (this.rear === null) {
                this.front = node;
                this.rear = node;
            } else {
                this.rear.next = node;
                this.rear = node;
            }
            this.count++;
        }
        dequeue() {
            if (this.isEmpty()) return null;
            const plate = this.front.data;
            this.front = this.front.next;
            if (this.front === null) this.rear = null;
            this.count--;
            return plate;
        }
        contains(plate) {
            let curr = this.front;
            const target = plate.toUpperCase();
            while (curr !== null) {
                if (curr.data === target) return true;
                curr = curr.next;
            }
            return false;
        }
        toList() {
            const res = [];
            let curr = this.front;
            while (curr !== null) {
                res.push(curr.data);
                curr = curr.next;
            }
            return res;
        }
    }

    // 2. Stack Node and LIFO Action Stack
    class StackNode {
        constructor(action) {
            this.action = action;
            this.next = null;
        }
    }

    class ActionStack {
        constructor() {
            this.top = null;
            this.count = 0;
        }
        isEmpty() { return this.top === null; }
        push(action) {
            const node = new StackNode(action);
            node.next = this.top;
            this.top = node;
            this.count++;
        }
        pop() {
            if (this.isEmpty()) return null;
            const action = this.top.action;
            this.top = this.top.next;
            this.count--;
            return action;
        }
    }

    // 3. Singly Linked List for Completed Parking History
    class HistoryNode {
        constructor(record) {
            this.record = record;
            this.next = null;
        }
    }

    class HistoryLinkedList {
        constructor() {
            this.head = null;
            this.tail = null;
            this.count = 0;
        }
        append(record) {
            const node = new HistoryNode(record);
            if (this.head === null) {
                this.head = node;
                this.tail = node;
            } else {
                this.tail.next = node;
                this.tail = node;
            }
            this.count++;
        }
        toList() {
            const res = [];
            let curr = this.head;
            while (curr !== null) {
                res.push(curr.record);
                curr = curr.next;
            }
            return res;
        }
        searchByVehicle(plate) {
            const res = [];
            let curr = this.head;
            const target = plate.toUpperCase();
            while (curr !== null) {
                if (curr.record.vehicle_number === target) {
                    res.push(curr.record);
                }
                curr = curr.next;
            }
            return res;
        }
    }

    // 4. In-Memory Parking Lot Simulation (Used on GitHub Pages static host)
    class StandaloneParkingLot {
        constructor(capacity = 6, hourlyRate = 20.0) {
            this.capacity = capacity;
            this.hourlyRate = hourlyRate;
            this.slots = Array.from({ length: capacity }, (_, i) => ({
                slot_id: i + 1,
                is_occupied: false,
                vehicle_number: null,
                entry_time: null,
                entry_time_formatted: null
            }));
            this.activeVehicles = new Map(); // Hash Map O(1)
            this.waitingQueue = new WaitingQueue(); // FIFO Queue O(1)
            this.actionStack = new ActionStack(); // LIFO Stack O(1)
            this.history = new HistoryLinkedList(); // Singly Linked List
            this.totalRevenue = 0.0;
        }

        findFirstAvailableSlot() {
            // Linear search O(N)
            for (let i = 0; i < this.slots.length; i++) {
                if (!this.slots[i].is_occupied) return this.slots[i];
            }
            return null;
        }

        parkVehicle(vehicleNumber) {
            const plate = vehicleNumber.trim().toUpperCase();
            if (!plate) return { success: false, message: "Registration number cannot be blank." };

            // 1. Hash Map Duplicate check O(1)
            if (this.activeVehicles.has(plate)) {
                return { success: false, message: `Duplicate! Vehicle ${plate} is already parked in Slot #${this.activeVehicles.get(plate)}.` };
            }

            // 2. Queue check
            if (this.waitingQueue.contains(plate)) {
                return { success: false, message: `Vehicle ${plate} is already waiting in the queue.` };
            }

            // 3. Find slot (Linear search)
            const slot = this.findFirstAvailableSlot();
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            if (!slot) {
                this.waitingQueue.enqueue(plate);
                return {
                    success: true,
                    message: `Parking is full! Vehicle ${plate} added to WAITING QUEUE at position #${this.waitingQueue.size()}.`,
                    slot_id: null
                };
            }

            slot.is_occupied = true;
            slot.vehicle_number = plate;
            slot.entry_time = Date.now();
            slot.entry_time_formatted = timeStr;
            this.activeVehicles.set(plate, slot.slot_id);

            // Stack Push LIFO
            this.actionStack.push({
                action_type: "PARK",
                vehicle_number: plate,
                slot_id: slot.slot_id
            });

            return {
                success: true,
                message: `Vehicle ${plate} parked successfully in Slot #${slot.slot_id}.`,
                slot_id: slot.slot_id
            };
        }

        exitVehicle(vehicleNumber, simulatedDurationHours = null) {
            const plate = vehicleNumber.trim().toUpperCase();
            if (!this.activeVehicles.has(plate)) {
                return { success: false, message: `Vehicle ${plate} is not currently parked.` };
            }

            const slotId = this.activeVehicles.get(plate);
            const slot = this.slots[slotId - 1];
            const exitTime = Date.now();
            const exitTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            // Calculate duration & fee
            let durationHours = 1.0;
            if (simulatedDurationHours !== null && !isNaN(simulatedDurationHours) && simulatedDurationHours > 0) {
                durationHours = parseFloat(simulatedDurationHours);
            } else if (slot.entry_time) {
                durationHours = Math.max(0.1, (exitTime - slot.entry_time) / 3600000);
            }

            const billableHours = Math.max(1, Math.ceil(durationHours));
            const fee = billableHours * this.hourlyRate;

            this.totalRevenue += fee;
            this.activeVehicles.delete(plate);

            const receipt = {
                vehicle_number: plate,
                slot_id: slotId,
                entry_time_formatted: slot.entry_time_formatted,
                exit_time_formatted: exitTimeStr,
                duration_hours: Number(durationHours.toFixed(1)),
                fee: fee,
                assigned_waiting_vehicle: null
            };

            // Vacate
            slot.is_occupied = false;
            slot.vehicle_number = null;
            slot.entry_time = null;
            slot.entry_time_formatted = null;

            // Add to Linked List History O(1)
            this.history.append(receipt);

            // Check Waiting Queue (FIFO Handover)
            if (!this.waitingQueue.isEmpty()) {
                const nextCar = this.waitingQueue.dequeue();
                slot.is_occupied = true;
                slot.vehicle_number = nextCar;
                slot.entry_time = Date.now();
                slot.entry_time_formatted = exitTimeStr;
                this.activeVehicles.set(nextCar, slot.slot_id);
                receipt.assigned_waiting_vehicle = nextCar;

                this.actionStack.push({
                    action_type: "PARK_FROM_QUEUE",
                    vehicle_number: nextCar,
                    slot_id: slot.slot_id
                });
            }

            return {
                success: true,
                message: `Vehicle ${plate} exited Slot #${slotId}. Fee: Rs. ${fee.toFixed(2)}.`,
                receipt: receipt
            };
        }

        undoLast() {
            if (this.actionStack.isEmpty()) {
                return { success: false, message: "No recent parking actions to undo." };
            }
            const last = this.actionStack.pop();
            const plate = last.vehicle_number;
            const slotId = last.slot_id;

            if (this.activeVehicles.has(plate) && this.activeVehicles.get(plate) === slotId) {
                const slot = this.slots[slotId - 1];
                slot.is_occupied = false;
                slot.vehicle_number = null;
                slot.entry_time = null;
                slot.entry_time_formatted = null;
                this.activeVehicles.delete(plate);
                return { success: true, message: `Undo Successful: Rolled back vehicle ${plate} from Slot #${slotId}.` };
            }
            return { success: false, message: `Cannot undo: Vehicle ${plate} is no longer in Slot #${slotId}.` };
        }

        searchVehicle(query) {
            const target = query.trim().toUpperCase();
            const res = { found: false, vehicle_number: target, active_status: null, queue_position: null, past_sessions: [] };

            // 1. Hash Map O(1)
            if (this.activeVehicles.has(target)) {
                res.found = true;
                const slotId = this.activeVehicles.get(target);
                res.active_status = {
                    slot_id: slotId,
                    entry_time_formatted: this.slots[slotId - 1].entry_time_formatted
                };
            }

            // 2. Queue Traversal O(M)
            const qList = this.waitingQueue.toList();
            for (let i = 0; i < qList.length; i++) {
                if (qList[i] === target) {
                    res.found = true;
                    res.queue_position = i + 1;
                    break;
                }
            }

            // 3. Linked List Traversal O(K)
            const hist = this.history.searchByVehicle(target);
            if (hist.length > 0) {
                res.found = true;
                res.past_sessions = hist;
            }

            return res;
        }

        insertionSort(records, key, reverse = false) {
            // DSA: Custom In-Place Insertion Sort
            const arr = records.map(r => ({ ...r }));
            for (let i = 1; i < arr.length; i++) {
                const current = arr[i];
                const val = current[key];
                let j = i - 1;
                if (!reverse) {
                    while (j >= 0 && arr[j][key] > val) {
                        arr[j + 1] = arr[j];
                        j--;
                    }
                } else {
                    while (j >= 0 && arr[j][key] < val) {
                        arr[j + 1] = arr[j];
                        j--;
                    }
                }
                arr[j + 1] = current;
            }
            return arr;
        }

        getSummary() {
            return {
                capacity: this.capacity,
                occupied_slots: this.activeVehicles.size,
                available_slots: this.capacity - this.activeVehicles.size,
                waiting_count: this.waitingQueue.size(),
                waiting_vehicles: this.waitingQueue.toList(),
                total_completed_sessions: this.history.count,
                total_revenue: this.totalRevenue,
                hourly_rate: this.hourlyRate
            };
        }
    }

    // -------------------------------------------------------------
    // UI Controller
    // -------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", async () => {
        let isBackendMode = false;
        let standaloneLot = null;

        // Detect if Flask backend is responding
        try {
            const check = await fetch("/api/status");
            if (check.ok) {
                const json = await check.json();
                if (json.success) isBackendMode = true;
            }
        } catch (e) {
            isBackendMode = false;
        }

        if (!isBackendMode) {
            console.log("Running in Standalone Client Mode (GitHub Pages environment)");
            standaloneLot = new StandaloneParkingLot(6, 20.0);
        } else {
            console.log("Connected to Python Flask Backend Server!");
        }

        // DOM elements
        const elCapacity = document.getElementById("statCapacity");
        const elOccupied = document.getElementById("statOccupied");
        const elAvailable = document.getElementById("statAvailable");
        const elWaiting = document.getElementById("statWaiting");
        const elHistoryCount = document.getElementById("statHistoryCount");
        const elRevenue = document.getElementById("statRevenue");
        const elRate = document.getElementById("statRate");

        const slotsContainer = document.getElementById("slotsContainer");
        const queueContainer = document.getElementById("queueContainer");
        const historyTableBody = document.getElementById("historyTableBody");
        const searchResults = document.getElementById("searchResults");
        const toastContainer = document.getElementById("toastContainer");

        const formPark = document.getElementById("formPark");
        const formExit = document.getElementById("formExit");
        const formSearch = document.getElementById("formSearch");
        const btnClearSearch = document.getElementById("btnClearSearch");
        const btnUndo = document.getElementById("btnUndo");
        const sortKeySelect = document.getElementById("sortKey");

        const receiptModal = document.getElementById("receiptModal");
        const receiptContent = document.getElementById("receiptContent");
        const btnCloseReceipt = document.getElementById("btnCloseReceipt");
        const btnCloseReceiptBtn = document.getElementById("btnCloseReceiptBtn");

        const resetModal = document.getElementById("resetModal");
        const btnResetModal = document.getElementById("btnResetModal");
        const btnCloseReset = document.getElementById("btnCloseReset");
        const btnCancelReset = document.getElementById("btnCancelReset");
        const formResetLot = document.getElementById("formResetLot");

        const dsaModal = document.getElementById("dsaModal");
        const btnDsaModal = document.getElementById("btnDsaModal");
        const btnCloseDsa = document.getElementById("btnCloseDsa");
        const btnCloseDsaBtn = document.getElementById("btnCloseDsaBtn");
        const dsaTableBody = document.getElementById("dsaTableBody");

        function showToast(message, type = "info") {
            const toast = document.createElement("div");
            toast.className = `toast ${type}`;
            toast.innerHTML = message;
            toastContainer.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = "0";
                toast.style.transform = "translateX(100%)";
                toast.style.transition = "all 0.3s ease";
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }

        function updateStats(summary) {
            elCapacity.textContent = summary.capacity;
            elOccupied.textContent = summary.occupied_slots;
            elAvailable.textContent = summary.available_slots;
            elWaiting.textContent = summary.waiting_count;
            elHistoryCount.textContent = summary.total_completed_sessions;
            elRevenue.textContent = `Rs. ${summary.total_revenue.toFixed(2)}`;
            elRate.textContent = `Rate: Rs. ${summary.hourly_rate.toFixed(2)}/hr`;
        }

        function renderSlots(slots) {
            slotsContainer.innerHTML = "";
            slots.forEach(slot => {
                const card = document.createElement("div");
                card.className = `slot-card ${slot.is_occupied ? "occupied" : "available"}`;
                if (slot.is_occupied) {
                    card.innerHTML = `
                        <div class="slot-number">SLOT #${slot.slot_id}</div>
                        <div class="slot-icon">🚘</div>
                        <div class="slot-plate">${slot.vehicle_number}</div>
                        <div class="slot-time">Entry: ${slot.entry_time_formatted || "Active"}</div>
                        <button class="btn btn-danger slot-action-btn" onclick="quickExit('${slot.vehicle_number}')">
                            Exit Vehicle
                        </button>
                    `;
                } else {
                    card.innerHTML = `
                        <div class="slot-number">SLOT #${slot.slot_id}</div>
                        <div class="slot-icon">🅿️</div>
                        <div class="text-success font-bold" style="font-size: 0.95rem;">AVAILABLE</div>
                        <div class="slot-time text-muted">Ready to park</div>
                        <button class="btn btn-outline slot-action-btn" onclick="focusParkInput()">
                            Allot Here
                        </button>
                    `;
                }
                slotsContainer.appendChild(card);
            });
        }

        function renderQueue(waitingList) {
            queueContainer.innerHTML = "";
            if (!waitingList || waitingList.length === 0) {
                queueContainer.innerHTML = `<span class="queue-empty-msg">No vehicles waiting in line. All incoming cars get instant slots!</span>`;
                return;
            }
            waitingList.forEach((plate, idx) => {
                const item = document.createElement("div");
                item.className = "queue-item";
                const posLabel = idx === 0 ? "1 (Next in Line)" : `#${idx + 1}`;
                item.innerHTML = `
                    <div class="queue-pos">Position: ${posLabel}</div>
                    <div class="queue-plate">${plate}</div>
                `;
                queueContainer.appendChild(item);
            });
        }

        function renderHistoryTable(records) {
            historyTableBody.innerHTML = "";
            if (!records || records.length === 0) {
                historyTableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No completed parking sessions recorded yet.</td></tr>`;
                return;
            }
            records.forEach((r, idx) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${idx + 1}</strong></td>
                    <td><code style="font-family: var(--font-mono); font-weight: 700; color: var(--accent);">${r.vehicle_number}</code></td>
                    <td>Slot #${r.slot_id}</td>
                    <td>${r.duration_hours}h</td>
                    <td style="font-weight: 700; color: var(--success);">Rs. ${Number(r.fee).toFixed(2)}</td>
                    <td class="text-muted" style="font-size: 0.78rem;">${r.entry_time_formatted || "N/A"}</td>
                    <td class="text-muted" style="font-size: 0.78rem;">${r.exit_time_formatted || "N/A"}</td>
                `;
                historyTableBody.appendChild(tr);
            });
        }

        async function refreshState() {
            if (isBackendMode) {
                try {
                    const res = await fetch("/api/status");
                    const data = await res.json();
                    if (data.success) {
                        updateStats(data.summary);
                        renderSlots(data.slots);
                        renderQueue(data.summary.waiting_vehicles);
                    }
                } catch (e) {}
            } else {
                updateStats(standaloneLot.getSummary());
                renderSlots(standaloneLot.slots);
                renderQueue(standaloneLot.waitingQueue.toList());
            }
        }

        async function loadHistory() {
            const sortVal = sortKeySelect.value;
            let sort_by = "fee";
            let reverse = true;

            if (sortVal === "fee-desc") { sort_by = "fee"; reverse = true; }
            else if (sortVal === "fee-asc") { sort_by = "fee"; reverse = false; }
            else if (sortVal === "duration-desc") { sort_by = "duration_hours"; reverse = true; }
            else if (sortVal === "duration-asc") { sort_by = "duration_hours"; reverse = false; }
            else if (sortVal === "vehicle-asc") { sort_by = "vehicle_number"; reverse = false; }

            if (isBackendMode) {
                try {
                    const res = await fetch(`/api/history?sort_by=${sort_by}&reverse=${reverse}`);
                    const data = await res.json();
                    if (data.success) renderHistoryTable(data.history);
                } catch (e) {}
            } else {
                const records = standaloneLot.history.toList();
                const sorted = standaloneLot.insertionSort(records, sort_by, reverse);
                renderHistoryTable(sorted);
            }
        }

        sortKeySelect.addEventListener("change", loadHistory);

        // Forms
        formPark.addEventListener("submit", async (e) => {
            e.preventDefault();
            const input = document.getElementById("parkVehicleNumber");
            const vehicleNumber = input.value.trim().toUpperCase();
            if (!vehicleNumber) return;

            if (isBackendMode) {
                try {
                    const res = await fetch("/api/park", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ vehicle_number: vehicleNumber })
                    });
                    const data = await res.json();
                    if (data.success) {
                        showToast(data.message, "success");
                        input.value = "";
                        refreshState();
                    } else {
                        showToast(data.message, "error");
                    }
                } catch (e) {
                    showToast("Server error.", "error");
                }
            } else {
                const res = standaloneLot.parkVehicle(vehicleNumber);
                if (res.success) {
                    showToast(res.message, "success");
                    input.value = "";
                    refreshState();
                } else {
                    showToast(res.message, "error");
                }
            }
        });

        formExit.addEventListener("submit", async (e) => {
            e.preventDefault();
            const inputPlate = document.getElementById("exitVehicleNumber");
            const inputHours = document.getElementById("exitSimulatedHours");
            const vehicleNumber = inputPlate.value.trim().toUpperCase();
            const simHours = inputHours.value.trim();
            if (!vehicleNumber) return;

            if (isBackendMode) {
                try {
                    const payload = { vehicle_number: vehicleNumber };
                    if (simHours !== "") payload.simulated_duration_hours = parseFloat(simHours);

                    const res = await fetch("/api/exit", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (data.success) {
                        showToast(data.message, "success");
                        inputPlate.value = "";
                        inputHours.value = "";
                        refreshState();
                        loadHistory();
                        if (data.receipt) showReceiptModal(data.receipt);
                    } else {
                        showToast(data.message, "error");
                    }
                } catch (e) {
                    showToast("Server error.", "error");
                }
            } else {
                const hoursVal = simHours !== "" ? parseFloat(simHours) : null;
                const res = standaloneLot.exitVehicle(vehicleNumber, hoursVal);
                if (res.success) {
                    showToast(res.message, "success");
                    inputPlate.value = "";
                    inputHours.value = "";
                    refreshState();
                    loadHistory();
                    if (res.receipt) showReceiptModal(res.receipt);
                } else {
                    showToast(res.message, "error");
                }
            }
        });

        btnUndo.addEventListener("click", async () => {
            if (isBackendMode) {
                try {
                    const res = await fetch("/api/undo", { method: "POST" });
                    const data = await res.json();
                    if (data.success) {
                        showToast(data.message, "warning");
                        refreshState();
                    } else {
                        showToast(data.message, "error");
                    }
                } catch (e) {
                    showToast("Undo failed.", "error");
                }
            } else {
                const res = standaloneLot.undoLast();
                if (res.success) {
                    showToast(res.message, "warning");
                    refreshState();
                } else {
                    showToast(res.message, "error");
                }
            }
        });

        // Search
        formSearch.addEventListener("submit", async (e) => {
            e.preventDefault();
            const input = document.getElementById("searchQuery");
            const query = input.value.trim().toUpperCase();
            if (!query) return;

            if (isBackendMode) {
                try {
                    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    if (data.success) renderSearchResults(data.data);
                } catch (e) {
                    showToast("Search failed.", "error");
                }
            } else {
                const data = standaloneLot.searchVehicle(query);
                renderSearchResults(data);
            }
        });

        btnClearSearch.addEventListener("click", () => {
            document.getElementById("searchQuery").value = "";
            searchResults.style.display = "none";
            searchResults.innerHTML = "";
        });

        function renderSearchResults(result) {
            searchResults.style.display = "block";
            searchResults.innerHTML = `
                <div style="border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">
                    <strong>Search Result for: <span style="color: var(--accent); font-family: var(--font-mono);">${result.vehicle_number}</span></strong>
                </div>
            `;
            if (!result.found) {
                searchResults.innerHTML += `<div class="text-muted">No records found across active slots, waiting queue, or past history.</div>`;
                return;
            }

            if (result.active_status) {
                searchResults.innerHTML += `
                    <div class="search-item">
                        <div>
                            <span class="dsa-tag tag-hash">Active Slot</span>
                            <strong style="margin-left: 0.5rem;">Parked in Slot #${result.active_status.slot_id}</strong>
                        </div>
                        <span class="text-muted" style="font-size: 0.8rem;">Entry: ${result.active_status.entry_time_formatted || "Active"}</span>
                    </div>
                `;
            } else {
                searchResults.innerHTML += `
                    <div class="search-item text-muted">
                        <span><span class="dsa-tag tag-hash">Active Status</span> Not currently parked in any slot.</span>
                    </div>
                `;
            }

            if (result.queue_position !== null) {
                searchResults.innerHTML += `
                    <div class="search-item">
                        <div>
                            <span class="dsa-tag tag-queue">Waiting Queue</span>
                            <strong style="margin-left: 0.5rem; color: var(--warning);">Position #${result.queue_position} in line</strong>
                        </div>
                        <span class="text-muted" style="font-size: 0.8rem;">FIFO Line</span>
                    </div>
                `;
            }

            if (result.past_sessions && result.past_sessions.length > 0) {
                let html = `
                    <div style="margin-top: 0.75rem;">
                        <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem;">
                            <span class="dsa-tag tag-list">Past Sessions (${result.past_sessions.length})</span>
                        </div>
                        <ul style="padding-left: 1.25rem; font-size: 0.82rem; color: var(--text-secondary);">
                `;
                result.past_sessions.forEach(s => {
                    html += `
                        <li style="margin-bottom: 0.35rem;">
                            Slot #${s.slot_id} | Duration: <strong>${s.duration_hours}h</strong> | Total Paid: <strong style="color: var(--success);">Rs. ${Number(s.fee).toFixed(2)}</strong> (Exited: ${s.exit_time_formatted})
                        </li>
                    `;
                });
                html += `</ul></div>`;
                searchResults.innerHTML += html;
            }
        }

        // Receipt Modal
        function showReceiptModal(receipt) {
            receiptContent.innerHTML = `
                <div class="receipt-box">
                    <div class="receipt-title">PARKING INVOICE &amp; RECEIPT</div>
                    <div class="receipt-row">
                        <span class="text-muted">Vehicle Number:</span>
                        <strong style="color: var(--accent);">${receipt.vehicle_number}</strong>
                    </div>
                    <div class="receipt-row">
                        <span class="text-muted">Slot Number:</span>
                        <strong>Slot #${receipt.slot_id}</strong>
                    </div>
                    <div class="receipt-row">
                        <span class="text-muted">Entry Time:</span>
                        <span>${receipt.entry_time_formatted || "N/A"}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="text-muted">Exit Time:</span>
                        <span>${receipt.exit_time_formatted || "N/A"}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="text-muted">Duration:</span>
                        <span>${receipt.duration_hours} hours</span>
                    </div>
                    <div class="receipt-row receipt-total">
                        <span>TOTAL AMOUNT:</span>
                        <span>Rs. ${Number(receipt.fee).toFixed(2)}</span>
                    </div>
                </div>
                ${receipt.assigned_waiting_vehicle ? `
                    <div style="margin-top: 1rem; background: var(--warning-bg); border: 1px solid var(--warning); border-radius: 6px; padding: 0.75rem; font-size: 0.83rem;">
                        <strong>⭐ Auto Queue Handover:</strong> Waiting vehicle <strong>${receipt.assigned_waiting_vehicle}</strong> was automatically allotted this vacated Slot #${receipt.slot_id}!
                    </div>
                ` : ""}
            `;
            receiptModal.classList.add("active");
        }

        [btnCloseReceipt, btnCloseReceiptBtn].forEach(b => b.addEventListener("click", () => receiptModal.classList.remove("active")));

        // Reconfigure Modal
        btnResetModal.addEventListener("click", () => resetModal.classList.add("active"));
        [btnCloseReset, btnCancelReset].forEach(b => b.addEventListener("click", () => resetModal.classList.remove("active")));

        formResetLot.addEventListener("submit", async (e) => {
            e.preventDefault();
            const cap = parseInt(document.getElementById("newCapacity").value, 10);
            const rate = parseFloat(document.getElementById("newHourlyRate").value);

            if (isBackendMode) {
                try {
                    const res = await fetch("/api/reset", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ capacity: cap, hourly_rate: rate })
                    });
                    const data = await res.json();
                    if (data.success) {
                        showToast(data.message, "success");
                        resetModal.classList.remove("active");
                        refreshState();
                        loadHistory();
                    }
                } catch (e) {
                    showToast("Reset failed.", "error");
                }
            } else {
                standaloneLot = new StandaloneParkingLot(cap, rate);
                showToast(`Parking lot reset to ${cap} slots at Rs. ${rate.toFixed(2)}/hour.`, "success");
                resetModal.classList.remove("active");
                refreshState();
                loadHistory();
            }
        });

        // DSA Concepts Mapping Table
        const dsaList = [
            {
                concept: "Array / List",
                component: "Parking Slots",
                time_complexity: "O(1) index access",
                space_complexity: "O(N) fixed capacity",
                description: "Stores physical parking slots with contiguous indices."
            },
            {
                concept: "Hash Map (Dictionary)",
                component: "Active Vehicles Map",
                time_complexity: "O(1) avg lookup/insert/delete",
                space_complexity: "O(N) active vehicles",
                description: "Maps vehicle plate to slot ID for instant duplicate detection and fast lookup."
            },
            {
                concept: "Queue (FIFO)",
                component: "Waiting Queue Line",
                time_complexity: "O(1) enqueue, O(1) dequeue",
                space_complexity: "O(M) waiting vehicles",
                description: "Custom linked nodes with front/rear pointers guaranteeing fair First-In, First-Out allocation."
            },
            {
                concept: "Stack (LIFO)",
                component: "Action Stack & Undo",
                time_complexity: "O(1) push, O(1) pop",
                space_complexity: "O(S) recent operations",
                description: "Custom linked nodes recording recent entries to support instant rollback."
            },
            {
                concept: "Singly Linked List",
                component: "Completed History",
                time_complexity: "O(1) append, O(K) traversal",
                space_complexity: "O(K) completed sessions",
                description: "Dynamic node-based sequence storing session receipts without array resizing."
            },
            {
                concept: "Linear Search",
                component: "Slot & Queue Scan",
                time_complexity: "O(N) slot scan, O(M) queue scan",
                space_complexity: "O(1)",
                description: "Finds the first free parking bay and searches queue nodes sequentially."
            },
            {
                concept: "Insertion Sort",
                component: "Completed History Ordering",
                time_complexity: "O(K^2) worst/avg, O(K) best",
                space_complexity: "O(1) auxiliary",
                description: "Sorts session records by total fee, duration, or vehicle plate in-place."
            }
        ];

        btnDsaModal.addEventListener("click", () => {
            dsaTableBody.innerHTML = "";
            dsaList.forEach(c => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${c.concept}</strong><br><small class="text-muted">${c.description}</small></td>
                    <td>${c.component}</td>
                    <td><code style="color: var(--accent);">${c.time_complexity}</code></td>
                    <td><code style="color: #c084fc;">${c.space_complexity}</code></td>
                `;
                dsaTableBody.appendChild(tr);
            });
            dsaModal.classList.add("active");
        });

        [btnCloseDsa, btnCloseDsaBtn].forEach(b => b.addEventListener("click", () => dsaModal.classList.remove("active")));

        window.quickExit = function(vehiclePlate) {
            document.getElementById("exitVehicleNumber").value = vehiclePlate;
            document.getElementById("exitSimulatedHours").focus();
            showToast(`Vehicle <strong>${vehiclePlate}</strong> selected for exit. Enter simulated hours or submit for real-time.`, "info");
        };

        window.focusParkInput = function() {
            document.getElementById("parkVehicleNumber").focus();
        };

        // Initialize view
        refreshState();
        loadHistory();
    });
})();
