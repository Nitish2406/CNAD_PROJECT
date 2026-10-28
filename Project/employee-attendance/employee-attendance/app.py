
"""
app.py
------
Cloud-Native Employee Attendance & Leave Management System
Review 2 prototype: in-memory data, Docker + Kubernetes.

Run locally:
    pip install -r requirements.txt
    python app.py

Open http://localhost:5000

Demo accounts:
    Employee : employee@demo.com  / 123456
    Employee : employee2@demo.com / 123456
    Manager  : manager@demo.com   / 123456
"""

from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify
)

from data import demo_data
from services import (
    auth_service,
    attendance_service,
    leave_service,
    notification_service,
)

app = Flask(__name__)
app.secret_key = "review2-demo-secret-key"  # Demo only; use a secure secret in production


# ---------------------------------------------------------------------------
# Kubernetes health checks
# ---------------------------------------------------------------------------
@app.route("/healthz", methods=["GET"])
def healthz():
    """Liveness check: confirms the Flask application is responding."""
    return jsonify({
        "status": "healthy"
    }), 200


@app.route("/readyz", methods=["GET"])
def readyz():
    """Readiness check: confirms the application can accept requests."""
    return jsonify({
        "status": "ready"
    }), 200


# ---------------------------------------------------------------------------
# Auth helpers / decorators
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def manager_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "manager":
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    return auth_service.find_user_by_id(session.get("user_id"))


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") == "manager":
        return redirect(url_for("manager_dashboard"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = auth_service.authenticate(email, password)

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "manager":
                return redirect(url_for("manager_dashboard"))
            return redirect(url_for("dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    today_record = attendance_service.get_today_record(user["id"])
    balance = leave_service.balance_for(user["id"])
    unread = notification_service.unread_count(user["id"])

    return render_template(
        "employee_dashboard.html",
        user=user,
        today_record=today_record,
        balance=balance,
        unread=unread,
    )


@app.route("/attendance")
@login_required
def attendance_page():
    user = current_user()
    today_record = attendance_service.get_today_record(user["id"])
    records = attendance_service.history(user["id"], limit=30)

    return render_template(
        "attendance.html",
        user=user,
        today_record=today_record,
        records=records,
    )


@app.route("/leave")
@login_required
def leave_page():
    user = current_user()
    requests_list = leave_service.my_requests(user["id"])
    balance = leave_service.balance_for(user["id"])

    return render_template(
        "leave.html",
        user=user,
        requests_list=requests_list,
        balance=balance,
    )


@app.route("/notifications")
@login_required
def notifications_page():
    user = current_user()
    items = notification_service.list_for_user(user["id"])
    notification_service.mark_all_read(user["id"])

    return render_template(
        "notifications.html",
        user=user,
        items=items,
    )


@app.route("/manager")
@login_required
@manager_required
def manager_dashboard():
    user = current_user()
    metrics = attendance_service.summary_for_manager()
    pending = leave_service.all_requests(status="Pending")
    services_status = demo_data.system_services

    return render_template(
        "manager_dashboard.html",
        user=user,
        metrics=metrics,
        pending=pending,
        pending_count=len(pending),
        services_status=services_status,
    )


@app.route("/employees")
@login_required
@manager_required
def employees_page():
    user = current_user()
    employees = auth_service.list_employees()
    enriched = []

    for emp in employees:
        today_record = attendance_service.get_today_record(emp["id"])
        enriched.append({
            "employee": emp,
            "status": today_record["status"] if today_record else "Absent",
            "check_in": today_record["check_in"] if today_record else "--:--",
        })

    return render_template(
        "employees.html",
        user=user,
        employees=enriched,
    )


# ---------------------------------------------------------------------------
# REST API — Attendance
# ---------------------------------------------------------------------------
@app.route("/api/attendance/check-in", methods=["POST"])
@login_required
def api_check_in():
    error, record = attendance_service.check_in(session["user_id"])

    if error:
        return jsonify({"success": False, **error}), 400

    return jsonify({"success": True, "record": record})


@app.route("/api/attendance/check-out", methods=["POST"])
@login_required
def api_check_out():
    error, record = attendance_service.check_out(session["user_id"])

    if error:
        return jsonify({"success": False, **error}), 400

    return jsonify({"success": True, "record": record})


@app.route("/api/attendance/history")
@login_required
def api_attendance_history():
    records = attendance_service.history(session["user_id"], limit=30)
    return jsonify({"success": True, "records": records})


# ---------------------------------------------------------------------------
# REST API — Leave
# ---------------------------------------------------------------------------
@app.route("/api/leave/apply", methods=["POST"])
@login_required
def api_leave_apply():
    data = request.get_json(silent=True) or request.form
    leave_type = data.get("type")
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    reason = data.get("reason", "")

    if not leave_type or not from_date or not to_date:
        return jsonify({
            "success": False,
            "error": "Leave type, from date and to date are required.",
        }), 400

    user = current_user()
    record = leave_service.apply_leave(
        user["id"],
        user["name"],
        leave_type,
        from_date,
        to_date,
        reason,
    )

    notification_service.notify(
        user["id"],
        f"Your {leave_type} Leave request is pending manager approval.",
    )

    return jsonify({"success": True, "record": record})


@app.route("/api/leave/my-requests")
@login_required
def api_my_requests():
    return jsonify({
        "success": True,
        "records": leave_service.my_requests(session["user_id"]),
    })


@app.route("/api/leave/requests")
@login_required
@manager_required
def api_all_requests():
    status = request.args.get("status")
    return jsonify({
        "success": True,
        "records": leave_service.all_requests(status),
    })


@app.route("/api/leave/<int:leave_id>/approve", methods=["PUT", "POST"])
@login_required
@manager_required
def api_leave_approve(leave_id):
    error, record = leave_service.approve(leave_id)

    if error:
        return jsonify({"success": False, **error}), 400

    return jsonify({"success": True, "record": record})


@app.route("/api/leave/<int:leave_id>/reject", methods=["PUT", "POST"])
@login_required
@manager_required
def api_leave_reject(leave_id):
    error, record = leave_service.reject(leave_id)

    if error:
        return jsonify({"success": False, **error}), 400

    return jsonify({"success": True, "record": record})


# ---------------------------------------------------------------------------
# REST API — Notifications
# ---------------------------------------------------------------------------
@app.route("/api/notifications")
@login_required
def api_notifications():
    return jsonify({
        "success": True,
        "records": notification_service.list_for_user(session["user_id"]),
    })


@app.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def api_notification_read(notification_id):
    record = notification_service.mark_read(
        notification_id,
        session["user_id"],
    )

    if not record:
        return jsonify({
            "success": False,
            "error": "Notification not found.",
        }), 404

    return jsonify({"success": True, "record": record})


# ---------------------------------------------------------------------------
# REST API — System status
# ---------------------------------------------------------------------------
@app.route("/api/system/status")
@login_required
def api_system_status():
    return jsonify({
        "success": True,
        "services": demo_data.system_services,
        "note": (
            "Demo status. Real Kubernetes and Prometheus health "
            "monitoring is not yet connected."
        ),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
