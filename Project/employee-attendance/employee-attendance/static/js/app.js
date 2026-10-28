/**
 * app.js
 * Small helper layer that talks to the Flask REST API defined in app.py.
 * No frameworks — plain fetch() calls, matching the "keep it simple"
 * approach for the Review 2 prototype.
 */

const AppAPI = (() => {

  function setMsg(elId, text, ok) {
    const el = document.getElementById(elId);
    if (!el) return;
    el.textContent = text;
    el.className = "small mt-2 " + (ok ? "text-success" : "text-danger");
  }

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    return { ok: res.ok, data };
  }

  async function checkIn(onAttendancePage = false, viaQr = false) {
    const { ok, data } = await postJSON("/api/attendance/check-in");
    const msgId = onAttendancePage ? "attendance-msg" : "attendance-msg";
    if (ok) {
      setMsg(msgId, (viaQr ? "✓ QR check-in successful. " : "✓ Attendance marked successfully. ") + "Check-in: " + data.record.check_in, true);
      document.getElementById("check-in-time").textContent = data.record.check_in;
      document.getElementById("btn-check-in").disabled = true;
      document.getElementById("btn-check-out").disabled = false;
    } else {
      setMsg(msgId, data.error || "Something went wrong.", false);
    }
  }

  async function checkOut() {
    const { ok, data } = await postJSON("/api/attendance/check-out");
    if (ok) {
      setMsg("attendance-msg", "✓ Checked out at " + data.record.check_out, true);
      document.getElementById("check-out-time").textContent = data.record.check_out;
      document.getElementById("btn-check-out").disabled = true;
    } else {
      setMsg("attendance-msg", data.error || "Something went wrong.", false);
    }
  }

  async function applyLeave(payload) {
    const { ok, data } = await postJSON("/api/leave/apply", payload);
    if (ok) {
      setMsg("leave-msg", "✓ Leave application submitted. Status: Pending", true);
      setTimeout(() => window.location.reload(), 900);
    } else {
      setMsg("leave-msg", data.error || "Something went wrong.", false);
    }
  }

  async function decideLeave(id, action) {
    const { ok, data } = await postJSON(`/api/leave/${id}/${action}`);
    const msgEl = document.getElementById("leave-action-msg");
    if (ok) {
      if (msgEl) {
        msgEl.className = "small mt-2 text-success";
        msgEl.textContent = action === "approve"
          ? "✓ Leave request approved successfully. Notification sent to employee."
          : "✓ Leave request rejected. Notification sent to employee.";
      }
      const row = document.querySelector(`.pending-row[data-id="${id}"]`);
      if (row) row.remove();
    } else if (msgEl) {
      msgEl.className = "small mt-2 text-danger";
      msgEl.textContent = data.error || "Something went wrong.";
    }
  }

  return { checkIn, checkOut, applyLeave, decideLeave };
})();
