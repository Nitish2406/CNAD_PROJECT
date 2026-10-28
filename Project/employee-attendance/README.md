# Cloud-Native Employee Attendance & Leave Management System
### Review 2 Prototype

A fully functional Flask application demonstrating the complete
employee/manager workflow for attendance and leave management —
**no database**, all data lives in memory while the app runs.

This is intentional: Review 2 focuses on proving out the application
workflow end-to-end. Database-per-service, Kubernetes, a message
broker, and full CI/CD are the next phase (see "Roadmap" below).

---

## Quick start

```bash
# 1. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

### Demo accounts

| Role     | Email                | Password |
|----------|-----------------------|----------|
| Employee | employee@demo.com     | 123456   |
| Employee | employee2@demo.com    | 123456   |
| Manager  | manager@demo.com      | 123456   |

> Restarting the app resets all data back to this starting state —
> that's expected for an in-memory demo store.

---

## Run with Docker

```bash
docker build -t employee-attendance .
docker run -p 5000:5000 employee-attendance
```

Then open **http://localhost:5000**.

---

## Project structure

```
employee-attendance/
│
├── app.py                       # Flask routes + REST API
│
├── services/                    # One module per "microservice" (Review 2: same process)
│   ├── auth_service.py
│   ├── attendance_service.py
│   ├── leave_service.py
│   └── notification_service.py
│
├── data/
│   └── demo_data.py             # In-memory "database" (lists/dicts)
│
├── templates/                   # Jinja2 + Bootstrap pages
│   ├── login.html
│   ├── employee_dashboard.html
│   ├── attendance.html
│   ├── leave.html
│   ├── manager_dashboard.html
│   ├── employees.html
│   └── notifications.html
│
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
│
├── Dockerfile
├── requirements.txt
└── .github/workflows/build.yml  # Minimal CI: install, sanity-check, docker build
```

---

## What's functional right now

- Login / logout (session-based)
- Employee dashboard, check-in / check-out
- Attendance history table + QR check-in demo button
- Apply for leave, view leave balance, view my requests
- Manager dashboard: live metrics, approve/reject pending leave
- Notifications generated automatically on leave submit/approve/reject
- REST API for every action (see `app.py`) — the frontend uses `fetch()` to call it
- Dockerfile + basic GitHub Actions CI build

## Roadmap (planned, not yet built)

- Database-per-service (Employee DB / Attendance DB / Leave DB)
- Kubernetes orchestration
- Message broker for event-driven notifications
- API Gateway in front of split microservices
- Prometheus / Grafana monitoring
- Full CI/CD with automated deployment

---

## API reference (for the demo / viva)

```
POST /api/attendance/check-in
POST /api/attendance/check-out
GET  /api/attendance/history

POST /api/leave/apply
GET  /api/leave/my-requests
GET  /api/leave/requests          (manager)
PUT  /api/leave/<id>/approve      (manager)
PUT  /api/leave/<id>/reject       (manager)

GET  /api/notifications
POST /api/notifications/<id>/read

GET  /api/system/status
```
