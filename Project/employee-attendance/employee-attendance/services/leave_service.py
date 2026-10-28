"""
leave_service.py
-----------------
Stands in for the "Leave Service" from the target architecture.
Apply / list / approve / reject, all in memory, plus a simple
leave-balance deduction on approval.
"""

from data import demo_data
from services import notification_service


def apply_leave(user_id, user_name, leave_type, from_date, to_date, reason):
    record = {
        "id": demo_data.next_leave_id(),
        "user_id": user_id,
        "name": user_name,
        "type": leave_type,
        "from_date": from_date,
        "to_date": to_date,
        "reason": reason,
        "status": "Pending",
    }
    demo_data.leave_requests.append(record)
    return record


def my_requests(user_id):
    records = [r for r in demo_data.leave_requests if r["user_id"] == user_id]
    records.sort(key=lambda r: r["id"], reverse=True)
    return records


def all_requests(status=None):
    records = list(demo_data.leave_requests)
    if status:
        records = [r for r in records if r["status"].lower() == status.lower()]
    records.sort(key=lambda r: r["id"], reverse=True)
    return records


def find_request(leave_id):
    for r in demo_data.leave_requests:
        if r["id"] == leave_id:
            return r
    return None


def _days_requested(record):
    from datetime import date
    try:
        d1 = date.fromisoformat(record["from_date"])
        d2 = date.fromisoformat(record["to_date"])
        return max((d2 - d1).days + 1, 1)
    except Exception:
        return 1


def approve(leave_id):
    record = find_request(leave_id)
    if not record:
        return {"error": "Leave request not found."}, None
    if record["status"] != "Pending":
        return {"error": f"Request already {record['status']}."}, record

    record["status"] = "Approved"

    balance = demo_data.leave_balance.get(record["user_id"])
    if balance is not None:
        key = record["type"].lower()
        if key in balance:
            days = _days_requested(record)
            balance[key] = max(balance[key] - days, 0)

    notification_service.notify(
        record["user_id"],
        f"Your {record['type']} Leave request ({record['from_date']} to {record['to_date']}) has been approved.",
    )
    return None, record


def reject(leave_id):
    record = find_request(leave_id)
    if not record:
        return {"error": "Leave request not found."}, None
    if record["status"] != "Pending":
        return {"error": f"Request already {record['status']}."}, record

    record["status"] = "Rejected"
    notification_service.notify(
        record["user_id"],
        f"Your {record['type']} Leave request ({record['from_date']} to {record['to_date']}) was rejected.",
    )
    return None, record


def balance_for(user_id):
    return demo_data.leave_balance.get(user_id, {"casual": 0, "sick": 0})


def pending_count():
    return len([r for r in demo_data.leave_requests if r["status"] == "Pending"])
