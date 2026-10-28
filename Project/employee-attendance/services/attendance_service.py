"""
attendance_service.py
----------------------
Stands in for the "Attendance Service" from the target architecture.
Handles check-in / check-out / history purely in memory.
"""

from datetime import datetime
from data import demo_data


def _today_str():
    return datetime.now().strftime("%Y-%m-%d")


def _now_str():
    return datetime.now().strftime("%I:%M %p")


def get_today_record(user_id):
    today = _today_str()
    for record in demo_data.attendance:
        if record["user_id"] == user_id and record["date"] == today:
            return record
    return None


def check_in(user_id):
    existing = get_today_record(user_id)
    if existing and existing["check_in"]:
        return {"error": "Already checked in today."}, existing

    if existing:
        existing["check_in"] = _now_str()
        existing["status"] = "Present"
        return None, existing

    record = {
        "id": demo_data.next_attendance_id(),
        "user_id": user_id,
        "date": _today_str(),
        "check_in": _now_str(),
        "check_out": None,
        "status": "Present",
    }
    demo_data.attendance.append(record)
    return None, record


def check_out(user_id):
    record = get_today_record(user_id)
    if not record or not record["check_in"]:
        return {"error": "You must check in before checking out."}, None
    if record["check_out"]:
        return {"error": "Already checked out today."}, record

    record["check_out"] = _now_str()
    return None, record


def history(user_id, limit=10):
    records = [r for r in demo_data.attendance if r["user_id"] == user_id]
    records.sort(key=lambda r: r["date"], reverse=True)
    return records[:limit]


def summary_for_manager():
    """Very small demo metrics for the manager dashboard."""
    today = _today_str()
    todays_records = [r for r in demo_data.attendance if r["date"] == today]
    present_today = len([r for r in todays_records if r["status"] == "Present"])
    return {
        "total_employees": len([u for u in demo_data.users if u["role"] == "employee"]),
        "present_today": present_today,
    }
