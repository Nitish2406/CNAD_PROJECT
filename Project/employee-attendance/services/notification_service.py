"""
notification_service.py
------------------------
Stands in for the "Notification Service" from the target architecture.
In the full cloud-native design this is triggered asynchronously via a
message broker (e.g. an event published when a leave is approved).
For Review 2 it's called directly as a normal function call — same
end result the examiner sees, simpler plumbing underneath.
"""

from data import demo_data


def notify(user_id, message):
    record = {
        "id": demo_data.next_notification_id(),
        "user_id": user_id,
        "message": message,
        "read": False,
    }
    demo_data.notifications.append(record)
    return record


def list_for_user(user_id):
    records = [n for n in demo_data.notifications if n["user_id"] == user_id]
    records.sort(key=lambda n: n["id"], reverse=True)
    return records


def unread_count(user_id):
    return len([n for n in demo_data.notifications if n["user_id"] == user_id and not n["read"]])


def mark_read(notification_id, user_id):
    for n in demo_data.notifications:
        if n["id"] == notification_id and n["user_id"] == user_id:
            n["read"] = True
            return n
    return None


def mark_all_read(user_id):
    for n in demo_data.notifications:
        if n["user_id"] == user_id:
            n["read"] = True
