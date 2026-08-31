import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-college-erp-showcase")


USERS = {
    "dean": {"password": "1234", "role": "Dean", "department": None, "name": "College Dean"},
    "hod_hospital": {"password": "1234", "role": "HOD", "department": "Hospital", "name": "Hospital HOD"},
    "hod_computer": {"password": "1234", "role": "HOD", "department": "Computer Department", "name": "Computer Department HOD"},
    "hod_mechanical": {"password": "1234", "role": "HOD", "department": "Mechanical Department", "name": "Mechanical Department HOD"},
    "hod_electrical": {"password": "1234", "role": "HOD", "department": "Electrical Department", "name": "Electrical Department HOD"},
    "hod_civil": {"password": "1234", "role": "HOD", "department": "Civil Department", "name": "Civil Department HOD"},
}

DEPARTMENTS = ["Hospital", "Computer Department", "Mechanical Department", "Electrical Department", "Civil Department"]

COMPLAINTS = [
    {"id": "CMP-1001", "department": "Hospital", "category": "Equipment", "subject": "Oxygen cylinder shortage", "priority": "Urgent", "status": "Pending", "date": "20/08/2026", "description": "Additional oxygen cylinders are urgently required.", "remarks": ""},
    {"id": "CMP-1002", "department": "Computer Department", "category": "IT", "subject": "Projector not working", "priority": "Medium", "status": "Under Review", "date": "19/08/2026", "description": "Projector in computer laboratory is not working.", "remarks": "Technical team has been informed."},
    {"id": "CMP-1003", "department": "Hospital", "category": "Maintenance", "subject": "AC servicing required", "priority": "Medium", "status": "Resolved", "date": "18/08/2026", "description": "AC unit in hospital block requires servicing.", "remarks": "Maintenance completed."},
    {"id": "CMP-1004", "department": "Mechanical Department", "category": "Equipment", "subject": "Lathe machine issue", "priority": "High", "status": "Received", "date": "18/08/2026", "description": "Lathe machine requires technical inspection.", "remarks": ""},
    {"id": "CMP-1005", "department": "Civil Department", "category": "Infrastructure", "subject": "Water leakage", "priority": "High", "status": "Under Review", "date": "17/08/2026", "description": "Water leakage near civil laboratory.", "remarks": "Maintenance department notified."},
    {"id": "CMP-1006", "department": "Electrical Department", "category": "Safety", "subject": "Loose electrical wiring", "priority": "Urgent", "status": "Received", "date": "20/08/2026", "description": "Loose wiring found near electrical laboratory.", "remarks": "Immediate inspection requested."},
]

INVENTORY = [
    {"id": "INV-501", "department": "Hospital", "item": "Oxygen Cylinder", "quantity": "10", "priority": "Urgent", "status": "Pending", "reason": "Required for emergency hospital stock.", "remarks": ""},
    {"id": "INV-502", "department": "Computer Department", "item": "HDMI Cable", "quantity": "15", "priority": "Medium", "status": "Approved", "reason": "Required in classrooms.", "remarks": "Approved for purchase."},
    {"id": "INV-503", "department": "Mechanical Department", "item": "Safety Gloves", "quantity": "50", "priority": "High", "status": "Received", "reason": "Required for laboratory practical sessions.", "remarks": ""},
    {"id": "INV-504", "department": "Electrical Department", "item": "Digital Multimeter", "quantity": "8", "priority": "High", "status": "Pending", "reason": "Required for electrical practical sessions.", "remarks": ""},
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/health")
def health():
    return {"status": "ok"}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and user["password"] == password:
            session.clear()
            session.update(username=username, **user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.get("/dashboard")
@login_required
def dashboard():
    department = session.get("department")
    complaints = [c for c in COMPLAINTS if not department or c["department"] == department]
    inventory = [i for i in INVENTORY if not department or i["department"] == department]
    return render_template(
        "dashboard.html",
        complaints=complaints,
        inventory=inventory,
        departments=DEPARTMENTS,
        user=session,
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
