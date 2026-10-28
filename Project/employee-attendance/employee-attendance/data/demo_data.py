"""
demo_data.py
------------
Central in-memory "database" for Review 2.

There is NO real database here on purpose. Everything lives in plain
Python lists/dicts while the Flask process is running. Restarting the
app resets everything back to this initial state — that's expected
and is called out explicitly in the presentation.

In the final version, each of these collections becomes its own
service-owned database (Employee DB, Attendance DB, Leave DB, ...).
"""

from itertools import count

# ---------------------------------------------------------------------------
# Users (would live in the Employee/Auth service's own DB eventually)
# ---------------------------------------------------------------------------
users = [
    {
        "id": 1,
        "name": "Kamalesh",
        "email": "employee@demo.com",
        "password": "123456",
        "role": "employee",
    },
    {
        "id": 2,
        "name": "Ananya",
        "email": "employee2@demo.com",
        "password": "123456",
        "role": "employee",
    },
    {
        "id": 3,
        "name": "Rahul Verma",
        "email": "manager@demo.com",
        "password": "123456",
        "role": "manager",
    },
]

# Leave balances per user id (days remaining)
leave_balance = {
    1: {"casual": 8, "sick": 6},
    2: {"casual": 5, "sick": 4},
}

# ---------------------------------------------------------------------------
# Attendance records — each: id, user_id, date, check_in, check_out, status
# ---------------------------------------------------------------------------
attendance = [
    {"id": 1, "user_id": 1, "date": "2026-09-20", "check_in": "09:05 AM", "check_out": "06:10 PM", "status": "Present"},
    {"id": 2, "user_id": 1, "date": "2026-09-19", "check_in": None, "check_out": None, "status": "Absent"},
    {"id": 3, "user_id": 2, "date": "2026-09-20", "check_in": "09:20 AM", "check_out": "06:00 PM", "status": "Present"},
]

# ---------------------------------------------------------------------------
# Leave requests — each: id, user_id, name, type, from, to, reason, status
# ---------------------------------------------------------------------------
leave_requests = [
    {
        "id": 1,
        "user_id": 1,
        "name": "Kamalesh",
        "type": "Sick",
        "from_date": "2026-09-12",
        "to_date": "2026-09-12",
        "reason": "Fever",
        "status": "Approved",
    },
]

# ---------------------------------------------------------------------------
# Notifications — each: id, user_id, message, read
# ---------------------------------------------------------------------------
notifications = [
    {"id": 1, "user_id": 1, "message": "Your Sick Leave request has been approved.", "read": False},
]

# ---------------------------------------------------------------------------
# Simple auto-incrementing id counters (per collection)
# ---------------------------------------------------------------------------
_attendance_id_counter = count(len(attendance) + 1)
_leave_id_counter = count(len(leave_requests) + 1)
_notification_id_counter = count(len(notifications) + 1)


def next_attendance_id():
    return next(_attendance_id_counter)


def next_leave_id():
    return next(_leave_id_counter)


def next_notification_id():
    return next(_notification_id_counter)


# ---------------------------------------------------------------------------
# "System" metrics for the cloud-native / admin style dashboard panel
# ---------------------------------------------------------------------------
system_services = [
    {"name": "Employee Service", "status": "Healthy"},
    {"name": "Attendance Service", "status": "Healthy"},
    {"name": "Leave Service", "status": "Healthy"},
    {"name": "Notification Service", "status": "Healthy"},
]
