"""
auth_service.py
----------------
Stands in for the "Employee/Auth Service" from the target architecture.
For Review 2 this is a plain in-memory credential check — no JWT / OAuth
yet, no database. That upgrade path is: this file -> a real Auth service
with hashed passwords + tokens, sitting behind the API Gateway.
"""

from data import demo_data


def find_user_by_email(email):
    for user in demo_data.users:
        if user["email"].lower() == (email or "").lower():
            return user
    return None


def find_user_by_id(user_id):
    for user in demo_data.users:
        if user["id"] == user_id:
            return user
    return None


def authenticate(email, password):
    """Return the user dict if credentials match, else None."""
    user = find_user_by_email(email)
    if user and user["password"] == password:
        return user
    return None


def list_employees():
    """All users with role 'employee' — used by the manager's Employees page."""
    return [u for u in demo_data.users if u["role"] == "employee"]


def public_user(user):
    """Strip the password before sending a user object to the frontend."""
    if not user:
        return None
    return {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
