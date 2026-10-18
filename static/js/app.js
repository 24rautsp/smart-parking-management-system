/**
 * Smart Parking Management System - Frontend JavaScript
 * Connects browser UI directly to the Python Flask & DSA backend.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let currentSlots = [];
    let currentSummary = {};

    // Elements - Stats
    const elCapacity = document.getElementById("statCapacity");
    const elOccupied = document.getElementById("statOccupied");
    const elAvailable = document.getElementById("statAvailable");
    const elWaiting = document.getElementById("statWaiting");
    const elHistoryCount = document.getElementById("statHistoryCount");
    const elRevenue = document.getElementById("statRevenue");
    const elRate = document.getElementById("statRate");

    // Elements - Containers
    const slotsContainer = document.getElementById("slotsContainer");
    const queueContainer = document.getElementById("queueContainer");
    const historyTableBody = document.getElementById("historyTableBody");
    const searchResults = document.getElementById("searchResults");
    const toastContainer = document.getElementById("toastContainer");

    // Elements - Forms
    const formPark = document.getElementById("formPark");
    const formExit = document.getElementById("formExit");
    const formSearch = document.getElementById("formSearch");
    const btnClearSearch = document.getElementById("btnClearSearch");
    const btnUndo = document.getElementById("btnUndo");
    const sortKeySelect = document.getElementById("sortKey");

    // Elements - Modals
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

    // -------------------------------------------------------------
    // 1. Toast Notifications
    // -------------------------------------------------------------
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

    // -------------------------------------------------------------
    // 2. Fetch & Render System Status
    // -------------------------------------------------------------
    async function loadStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            if (data.success) {
                currentSummary = data.summary;
                currentSlots = data.slots;
                updateStats(data.summary);
                renderSlots(data.slots);
                renderQueue(data.summary.waiting_vehicles);
            }
        } catch (err) {
            console.error("Failed to load status:", err);
            showToast("Failed to connect to backend server.", "error");
        }
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

    // -------------------------------------------------------------
    // 3. Completed Parking History & Custom Insertion Sort
    // -------------------------------------------------------------
    async function loadHistory() {
        const sortVal = sortKeySelect.value;
        let sort_by = "fee";
        let reverse = "true";

        if (sortVal === "fee-desc") { sort_by = "fee"; reverse = "true"; }
        else if (sortVal === "fee-asc") { sort_by = "fee"; reverse = "false"; }
        else if (sortVal === "duration-desc") { sort_by = "duration_hours"; reverse = "true"; }
        else if (sortVal === "duration-asc") { sort_by = "duration_hours"; reverse = "false"; }
        else if (sortVal === "vehicle-asc") { sort_by = "vehicle_number"; reverse = "false"; }

        try {
            const res = await fetch(`/api/history?sort_by=${sort_by}&reverse=${reverse}`);
            const data = await res.json();
            if (data.success) {
                renderHistoryTable(data.history);
            }
        } catch (err) {
            console.error("Failed to load history:", err);
        }
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

    sortKeySelect.addEventListener("change", loadHistory);

    // -------------------------------------------------------------
    // 4. Form Actions: Park, Exit, Undo
    // -------------------------------------------------------------
    formPark.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("parkVehicleNumber");
        const vehicleNumber = input.value.trim().toUpperCase();
        if (!vehicleNumber) return;

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
                updateStats(data.summary);
                renderSlots(data.slots);
                renderQueue(data.summary.waiting_vehicles);
            } else {
                showToast(data.message, "error");
            }
        } catch (err) {
            showToast("Server communication error.", "error");
        }
    });

    formExit.addEventListener("submit", async (e) => {
        e.preventDefault();
        const inputPlate = document.getElementById("exitVehicleNumber");
        const inputHours = document.getElementById("exitSimulatedHours");
        const vehicleNumber = inputPlate.value.trim().toUpperCase();
        const simulatedHours = inputHours.value.trim();

        if (!vehicleNumber) return;

        try {
            const payload = { vehicle_number: vehicleNumber };
            if (simulatedHours !== "") {
                payload.simulated_duration_hours = parseFloat(simulatedHours);
            }

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
                updateStats(data.summary);
                renderSlots(data.slots);
                renderQueue(data.summary.waiting_vehicles);
                loadHistory();

                // Open Receipt Modal
                if (data.receipt) {
                    showReceiptModal(data.receipt);
                }
            } else {
                showToast(data.message, "error");
            }
        } catch (err) {
            showToast("Server communication error.", "error");
        }
    });

    btnUndo.addEventListener("submit", (e) => e.preventDefault());
    btnUndo.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/undo", { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, "warning");
                updateStats(data.summary);
                renderSlots(data.slots);
                renderQueue(data.summary.waiting_vehicles);
            } else {
                showToast(data.message, "error");
            }
        } catch (err) {
            showToast("Failed to perform undo operation.", "error");
        }
    });

    // -------------------------------------------------------------
    // 5. Multi-Tier Search
    // -------------------------------------------------------------
    formSearch.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("searchQuery");
        const query = input.value.trim().toUpperCase();
        if (!query) return;

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            if (data.success) {
                renderSearchResults(data.data);
            } else {
                showToast(data.message, "error");
            }
        } catch (err) {
            showToast("Search failed.", "error");
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
            searchResults.innerHTML += `<div class="text-muted">No records found for vehicle <strong>${result.vehicle_number}</strong> across active slots, waiting queue, or past history.</div>`;
            return;
        }

        // 1. Active status
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

        // 2. Queue status
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

        // 3. Past History
        if (result.past_sessions && result.past_sessions.length > 0) {
            let historyHtml = `
                <div style="margin-top: 0.75rem;">
                    <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem;">
                        <span class="dsa-tag tag-list">Past Sessions (${result.past_sessions.length})</span>
                    </div>
                    <ul style="padding-left: 1.25rem; font-size: 0.82rem; color: var(--text-secondary);">
            `;
            result.past_sessions.forEach((s) => {
                historyHtml += `
                    <li style="margin-bottom: 0.35rem;">
                        Slot #${s.slot_id} | Duration: <strong>${s.duration_hours}h</strong> | Total Paid: <strong style="color: var(--success);">Rs. ${Number(s.fee).toFixed(2)}</strong> (Exited: ${s.exit_time_formatted})
                    </li>
                `;
            });
            historyHtml += `</ul></div>`;
            searchResults.innerHTML += historyHtml;
        }
    }

    // -------------------------------------------------------------
    // 6. Modal Handlers
    // -------------------------------------------------------------
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
                updateStats(data.summary);
                renderSlots(data.slots);
                renderQueue(data.summary.waiting_vehicles);
                loadHistory();
            } else {
                showToast(data.message, "error");
            }
        } catch (err) {
            showToast("Failed to reconfigure parking lot.", "error");
        }
    });

    // DSA Concepts Modal
    btnDsaModal.addEventListener("click", async () => {
        dsaModal.classList.add("active");
        try {
            const res = await fetch("/api/dsa-info");
            const data = await res.json();
            if (data.concepts) {
                dsaTableBody.innerHTML = "";
                data.concepts.forEach(c => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${c.concept}</strong><br><small class="text-muted">${c.description}</small></td>
                        <td>${c.component}</td>
                        <td><code style="color: var(--accent);">${c.time_complexity}</code></td>
                        <td><code style="color: #c084fc;">${c.space_complexity}</code></td>
                    `;
                    dsaTableBody.appendChild(tr);
                });
            }
        } catch (err) {
            console.error(err);
        }
    });

    [btnCloseDsa, btnCloseDsaBtn].forEach(b => b.addEventListener("click", () => dsaModal.classList.remove("active")));

    // Global helper functions
    window.quickExit = function(vehiclePlate) {
        document.getElementById("exitVehicleNumber").value = vehiclePlate;
        document.getElementById("exitSimulatedHours").focus();
        showToast(`Vehicle <strong>${vehiclePlate}</strong> selected for exit. Enter simulated hours or submit for real-time.`, "info");
    };

    window.focusParkInput = function() {
        document.getElementById("parkVehicleNumber").focus();
    };

    // Initial load
    loadStatus();
    loadHistory();
});
