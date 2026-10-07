import os
import sqlite3
import csv
from io import BytesIO, StringIO
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "college_erp.db"))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", BASE_DIR / "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-college-erp-showcase")
app.config.update(MAX_CONTENT_LENGTH=10 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax")

USERS = {
    "dean": {"password": "1234", "role": "Dean", "department": None, "name": "College Dean"},
    "hod_anatomy": {"password": "1234", "role": "HOD", "department": "Anatomy", "name": "Anatomy HOD"},
    "hod_physiology": {"password": "1234", "role": "HOD", "department": "Physiology", "name": "Physiology HOD"},
    "hod_biochemistry": {"password": "1234", "role": "HOD", "department": "Biochemistry", "name": "Biochemistry HOD"},
    "hod_pathology": {"password": "1234", "role": "HOD", "department": "Pathology", "name": "Pathology HOD"},
    "hod_microbiology": {"password": "1234", "role": "HOD", "department": "Microbiology", "name": "Microbiology HOD"},
    "hod_pharmacology": {"password": "1234", "role": "HOD", "department": "Pharmacology", "name": "Pharmacology HOD"},
    "pio_civil": {"password": "1234", "role": "PIO", "department": "Civil", "name": "Civil PIO"},
    "pio_electrical": {"password": "1234", "role": "PIO", "department": "Electrical", "name": "Electrical PIO"},
    "manager_it": {"password": "1234", "role": "Management", "department": None, "management_category": "IT", "name": "IT Management"},
    "manager_infrastructure": {"password": "1234", "role": "Management", "department": None, "management_category": "Infrastructure", "name": "Infrastructure Management"},
    "manager_equipment": {"password": "1234", "role": "Management", "department": None, "management_category": "Equipment", "name": "Equipment Management"},
    "manager_maintenance": {"password": "1234", "role": "Management", "department": None, "management_category": "Maintenance", "name": "Maintenance Management"},
    "manager_safety": {"password": "1234", "role": "Management", "department": None, "management_category": "Safety", "name": "Safety Management"},
}
DEPARTMENTS = ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Microbiology", "Pharmacology"]
PIO_DEPARTMENTS = ["Civil", "Electrical"]
PIO_CATEGORIES = {
    "Civil": ["Pipe", "Flooring", "Civil Work"],
    "Electrical": ["Fan", "Plug", "Switchboard"],
}
ALLOWED_STATUS = {"Pending", "Received", "Under Review", "Approved", "Rejected", "Resolved", "Completed"}
ALLOWED_PRIORITY = {"Low", "Medium", "High", "Urgent"}
MANAGEMENT_CATEGORIES = ["Equipment", "IT", "Maintenance", "Infrastructure", "Safety", "Other"]


def db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with db() as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS complaints (
          id TEXT PRIMARY KEY, department TEXT NOT NULL, category TEXT NOT NULL,
          subject TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL,
          date TEXT NOT NULL, description TEXT NOT NULL, remarks TEXT DEFAULT '', attachment TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS inventory (
          id TEXT PRIMARY KEY, department TEXT NOT NULL, item TEXT NOT NULL,
          quantity INTEGER NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL,
          date TEXT NOT NULL, reason TEXT NOT NULL, remarks TEXT DEFAULT '', attachment TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS pio_reports (
          id TEXT PRIMARY KEY, department TEXT NOT NULL, category TEXT NOT NULL,
          report_type TEXT NOT NULL, title TEXT NOT NULL, details TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'Pending', report_date TEXT NOT NULL,
          reminder_date TEXT DEFAULT '', recipient TEXT DEFAULT '', created_by TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notifications (
          id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
          message TEXT NOT NULL, created_at TEXT NOT NULL, is_read INTEGER DEFAULT 0,
          record_type TEXT DEFAULT '', record_id TEXT DEFAULT '', event_type TEXT DEFAULT 'update'
        );
        CREATE TABLE IF NOT EXISTS notification_settings (
          username TEXT PRIMARY KEY, email TEXT DEFAULT '', mobile TEXT DEFAULT '',
          in_app INTEGER DEFAULT 1, email_enabled INTEGER DEFAULT 0, sms_enabled INTEGER DEFAULT 0
        );
        """)
        for table in ("complaints", "inventory", "pio_reports"):
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            if "created_by" not in columns:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN created_by TEXT DEFAULT ''")
            if "archived" not in columns:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN archived INTEGER DEFAULT 0")
            if "archive_reason" not in columns:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN archive_reason TEXT DEFAULT ''")
            if "archived_at" not in columns:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN archived_at TEXT DEFAULT ''")
            if table == "inventory" and "category" not in columns:
                connection.execute("ALTER TABLE inventory ADD COLUMN category TEXT DEFAULT 'Other'")
        notification_columns = {row[1] for row in connection.execute("PRAGMA table_info(notifications)")}
        for column, definition in {
            "record_type": "TEXT DEFAULT ''", "record_id": "TEXT DEFAULT ''", "event_type": "TEXT DEFAULT 'update'"
        }.items():
            if column not in notification_columns:
                connection.execute(f"ALTER TABLE notifications ADD COLUMN {column} {definition}")
        if not connection.execute("SELECT 1 FROM complaints LIMIT 1").fetchone():
            complaints = [
                ("CMP-1001", "Anatomy", "Equipment", "Dissection table maintenance", "Urgent", "Pending", "20/08/2026", "A dissection table requires immediate maintenance.", "", ""),
                ("CMP-1002", "Physiology", "IT", "Laboratory projector not working", "Medium", "Under Review", "19/08/2026", "The projector in the physiology laboratory is not working.", "Technical team has been informed.", ""),
                ("CMP-1003", "Biochemistry", "Maintenance", "Laboratory AC servicing required", "Medium", "Resolved", "18/08/2026", "The laboratory AC unit requires servicing.", "Maintenance completed.", ""),
                ("CMP-1004", "Pathology", "Equipment", "Microscope calibration issue", "High", "Received", "18/08/2026", "Laboratory microscopes require calibration.", "", ""),
                ("CMP-1005", "Microbiology", "Infrastructure", "Water leakage near laboratory", "High", "Under Review", "17/08/2026", "Water leakage was reported near the microbiology laboratory.", "Maintenance department notified.", ""),
                ("CMP-1006", "Pharmacology", "Safety", "Loose electrical wiring", "Urgent", "Received", "20/08/2026", "Loose wiring was found near the pharmacology laboratory.", "Immediate inspection requested.", ""),
            ]
            connection.executemany(
                "INSERT INTO complaints (id,department,category,subject,priority,status,date,description,remarks,attachment) VALUES (?,?,?,?,?,?,?,?,?,?)",
                complaints,
            )
        if not connection.execute("SELECT 1 FROM inventory LIMIT 1").fetchone():
            inventory = [
                ("INV-501", "Anatomy", "Equipment", "Dissection Kit", 10, "Urgent", "Pending", "20/08/2026", "Required for anatomy practical sessions.", "", ""),
                ("INV-502", "Physiology", "Equipment", "Digital Spirometer", 5, "Medium", "Approved", "19/08/2026", "Required for physiology demonstrations.", "Approved for purchase.", ""),
                ("INV-503", "Microbiology", "Safety", "Safety Gloves", 50, "High", "Received", "18/08/2026", "Required for laboratory practical sessions.", "", ""),
                ("INV-504", "Pharmacology", "Equipment", "Drug Display Trays", 8, "High", "Pending", "20/08/2026", "Required for pharmacology demonstrations.", "", ""),
            ]
            connection.executemany(
                "INSERT INTO inventory (id,department,category,item,quantity,priority,status,date,reason,remarks,attachment) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                inventory,
            )
        department_migrations = {
            "Hospital": "Anatomy", "Computer Department": "Physiology",
            "Mechanical Department": "Biochemistry", "Electrical Department": "Pathology",
            "Civil Department": "Microbiology"
        }
        for old_name, new_name in department_migrations.items():
            connection.execute("UPDATE complaints SET department=? WHERE department=?", (new_name, old_name))
            connection.execute("UPDATE inventory SET department=? WHERE department=?", (new_name, old_name))
        if not connection.execute("SELECT 1 FROM pio_reports LIMIT 1").fetchone():
            today = date.today().isoformat()
            connection.executemany(
                "INSERT INTO pio_reports (id,department,category,report_type,title,details,status,report_date,reminder_date,recipient,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                [
                    ("PIO-1001", "Civil", "Pipe", "Demand", "Laboratory water-line pipe requirement", "Replacement pipes are required for the laboratory block.", "Pending", today, "", "College Dean", "pio_civil"),
                    ("PIO-1002", "Electrical", "Switchboard", "Calendar", "Switchboard inspection schedule", "Inspect switchboards across all academic blocks.", "Scheduled", today, "", "College Dean", "pio_electrical"),
                ],
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def may_edit(record):
    return session.get("role") == "Dean" or bool(record["created_by"] and record["created_by"] == session.get("username"))


def record_for_user(row):
    result = dict(row)
    result["can_edit"] = may_edit(row)
    result["can_delete"] = result["can_edit"] and not result.get("archived", 0)
    return result


def visible_rows(table, archived=False):
    department = session.get("department")
    query, params = f"SELECT * FROM {table} WHERE archived = ?", (1 if archived else 0,)
    if session.get("role") == "Management":
        query += " AND category = ?"
        params += (session.get("management_category", ""),)
    elif department:
        query += " AND department = ?"
        params += (department,)
    query += " ORDER BY rowid DESC"
    with db() as connection:
        return [record_for_user(row) for row in connection.execute(query, params)]


def visible_pio_reports(archived=False):
    if session.get("role") not in {"Dean", "PIO"}:
        return []
    query, params = "SELECT * FROM pio_reports WHERE archived=?", (int(archived),)
    if session.get("role") == "PIO":
        query += " AND department=?"
        params += (session.get("department"),)
    query += " ORDER BY report_date DESC, rowid DESC"
    with db() as connection:
        return [record_for_user(row) for row in connection.execute(query, params)]


def visible_notifications():
    username = session.get("username", "")
    with db() as connection:
        return [dict(row) for row in connection.execute(
            "SELECT * FROM notifications WHERE username IN (?, 'all') ORDER BY rowid DESC LIMIT 30",
            (username,),
        )]


def add_notification(connection, username, message, record_type="", record_id="", event_type="update"):
    connection.execute(
        "INSERT INTO notifications (username,message,created_at,record_type,record_id,event_type) VALUES (?,?,?,?,?,?)",
        (username, message, datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d/%m/%Y, %I:%M %p"), record_type, record_id, event_type),
    )


def management_username(category):
    for username, user in USERS.items():
        if user.get("management_category") == category:
            return username
    return ""


def notify_related(connection, department, message, category="", actor="", record_type="", record_id="", event_type="update"):
    """Notify the Dean, affected HOD/PIO and category management, excluding the sender."""
    recipients = {"dean"}
    department_account = department_username(department)
    if department_account:
        recipients.add(department_account)
    management_account = management_username(category)
    if management_account:
        recipients.add(management_account)
    recipients.discard(actor)
    for username in recipients:
        add_notification(connection, username, message, record_type, record_id, event_type)


def department_username(department):
    for username, user in USERS.items():
        if user.get("department") == department:
            return username
    return ""


def save_pdf(file):
    if not file or not file.filename:
        return ""
    if Path(file.filename).suffix.lower() != ".pdf":
        raise ValueError("Only PDF attachments are allowed.")
    filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
    file.save(UPLOAD_DIR / filename)
    return filename


def next_id(connection, table, prefix, start):
    rows = connection.execute(f"SELECT id FROM {table}").fetchall()
    numbers = [int(row[0].split("-")[-1]) for row in rows if row[0].split("-")[-1].isdigit()]
    return f"{prefix}-{max(numbers, default=start) + 1}"


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
    notifications = visible_notifications()
    return render_template("dashboard.html", complaints=visible_rows("complaints"),
                           inventory=visible_rows("inventory"),
                           archived_complaints=visible_rows("complaints", archived=True),
                           archived_inventory=visible_rows("inventory", archived=True),
                           pio_reports=visible_pio_reports(), archived_pio=visible_pio_reports(True), notifications=notifications,
                           unread_notifications=sum(not item["is_read"] for item in notifications),
                           departments=DEPARTMENTS, pio_departments=PIO_DEPARTMENTS,
                           pio_categories=PIO_CATEGORIES, user=session)


def dean_required():
    return session.get("role") == "Dean"


@app.post("/api/pio-reports")
@login_required
def create_pio_report():
    if session.get("role") not in {"Dean", "PIO"}:
        return jsonify(error="You cannot create PIO reports."), 403
    department = session.get("department") if session.get("role") == "PIO" else request.form.get("department", "")
    category = request.form.get("category", "").strip()
    report_type = request.form.get("report_type", "Demand").strip()
    title = request.form.get("title", "").strip()
    details = request.form.get("details", "").strip()
    report_date = request.form.get("report_date") or date.today().isoformat()
    reminder_date = request.form.get("reminder_date", "").strip()
    recipient = request.form.get("recipient", "College Dean").strip()
    if department not in PIO_DEPARTMENTS or category not in PIO_CATEGORIES[department]:
        return jsonify(error="Select a valid PIO department and category."), 400
    if report_type not in {"Demand", "Calendar"} or not title or not details:
        return jsonify(error="Complete all required report fields."), 400
    with db() as connection:
        report_id = next_id(connection, "pio_reports", "PIO", 1000)
        connection.execute(
            "INSERT INTO pio_reports (id,department,category,report_type,title,details,status,report_date,reminder_date,recipient,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (report_id, department, category, report_type, title, details, "Pending" if report_type == "Demand" else "Scheduled", report_date, reminder_date, recipient, session["username"]),
        )
        notify_related(connection, department, f"New {report_type} report {report_id} from {department} PIO", category, session["username"], "pio", report_id, "new")
    return jsonify(ok=True, message="PIO report submitted successfully.")


@app.post("/api/notifications/read")
@login_required
def mark_notifications_read():
    with db() as connection:
        connection.execute("UPDATE notifications SET is_read=1 WHERE username IN (?, 'all')", (session["username"],))
    return jsonify(ok=True, message="Notifications marked as read.")


@app.get("/api/notifications")
@login_required
def notification_feed():
    notifications = visible_notifications()
    return jsonify(
        notifications=notifications,
        unread=sum(not item["is_read"] for item in notifications),
    )


@app.post("/api/notification-settings")
@login_required
def save_notification_settings():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    with db() as connection:
        connection.execute(
            "INSERT INTO notification_settings (username,email,mobile,in_app,email_enabled,sms_enabled) VALUES (?,?,?,?,?,?) "
            "ON CONFLICT(username) DO UPDATE SET email=excluded.email,mobile=excluded.mobile,in_app=excluded.in_app,email_enabled=excluded.email_enabled,sms_enabled=excluded.sms_enabled",
            (session["username"], email, mobile, int(bool(data.get("in_app", True))), int(bool(data.get("email_enabled"))), int(bool(data.get("sms_enabled")))),
        )
    return jsonify(ok=True, message="Notification preferences saved.")


def filtered_pio_reports(args):
    clauses, params = [], []
    department = args.get("department", "").strip()
    report_type = args.get("report_type", "").strip()
    date_from = args.get("date_from", "").strip()
    date_to = args.get("date_to", "").strip()
    period = args.get("period", "").strip()
    if period in {"15", "30", "60"}:
        date_to = date.today().isoformat()
        date_from = (date.today() - timedelta(days=int(period) - 1)).isoformat()
    if department in PIO_DEPARTMENTS:
        clauses.append("department=?")
        params.append(department)
    if report_type in {"Demand", "Calendar"}:
        clauses.append("report_type=?")
        params.append(report_type)
    if date_from:
        clauses.append("report_date>=?")
        params.append(date_from)
    if date_to:
        clauses.append("report_date<=?")
        params.append(date_to)
    query = "SELECT * FROM pio_reports"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY report_date DESC, rowid DESC"
    with db() as connection:
        return [dict(row) for row in connection.execute(query, params)]


def requested_date_range(args):
    period = args.get("period", "").strip()
    today = date.today()
    if period in {"15", "30", "60"}:
        return today - timedelta(days=int(period) - 1), today
    try:
        start = date.fromisoformat(args.get("date_from", "")) if args.get("date_from") else None
        end = date.fromisoformat(args.get("date_to", "")) if args.get("date_to") else None
        return start, end
    except ValueError:
        return None, None


def date_in_range(value, start, end):
    if not start and not end:
        return True
    parsed = None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, fmt).date()
            break
        except (TypeError, ValueError):
            continue
    if not parsed:
        return False
    return (not start or parsed >= start) and (not end or parsed <= end)


@app.get("/reports/pio-letterhead.pdf")
@login_required
def export_pio_pdf():
    if not dean_required():
        return jsonify(error="Only the Dean can download PDF reports."), 403
    records = filtered_pio_reports(request.args)
    department = request.args.get("department") or "All Departments"
    recipient = request.args.get("recipient", "College Dean").strip() or "College Dean"
    reminder = request.args.get("reminder", "").strip()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("Letterhead", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#0f2740"), fontSize=18, leading=22)
    story = [Paragraph("COLLEGE ERP MANAGEMENT SYSTEM", heading), Paragraph(f"{department} PIO REPORT", heading), Spacer(1, 5*mm)]
    story.extend([Paragraph(f"<b>To:</b> {recipient}", styles["BodyText"]), Paragraph(f"<b>Generated:</b> {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d/%m/%Y, %I:%M %p')}", styles["BodyText"])])
    if reminder:
        story.append(Paragraph(f"<b>Reminder:</b> {reminder}", styles["BodyText"]))
    story.append(Spacer(1, 5*mm))
    data = [["ID", "Department", "Type", "Category", "Title", "Date", "Status"]]
    for item in records:
        data.append([item["id"], item["department"], item["report_type"], item["category"], Paragraph(item["title"], styles["BodyText"]), item["report_date"], item["status"]])
    if len(data) == 1:
        data.append(["—", department, "—", "—", "No records found for the selected period.", "—", "—"])
    table = Table(data, repeatRows=1, colWidths=[20*mm, 25*mm, 20*mm, 24*mm, 52*mm, 23*mm, 22*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f2740")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#cbd5e1")), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]), ("PADDING", (0,0), (-1,-1), 5),
    ]))
    story.extend([table, Spacer(1, 10*mm), Paragraph("Authorized by: College Dean", styles["BodyText"])])
    document.build(story)
    filename = f"pio_report_{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y%m%d_%H%M')}.pdf"
    return Response(buffer.getvalue(), mimetype="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-store"})


def csv_safe(value):
    """Prevent spreadsheet formulas from being executed when the CSV is opened."""
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(("=", "+", "-", "@")) else text


@app.get("/reports/export.csv")
@login_required
def export_csv():
    if session.get("role") != "Dean":
        return jsonify(error="Only the Dean can download CSV reports."), 403

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["COLLEGE ERP REPORT"])
    writer.writerow(["Generated On", datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d/%m/%Y, %I:%M %p")])
    writer.writerow([])

    start, end = requested_date_range(request.args)
    with db() as connection:
        complaints = [row for row in connection.execute("SELECT * FROM complaints ORDER BY rowid DESC").fetchall() if date_in_range(row["date"], start, end)]
        inventory = [row for row in connection.execute("SELECT * FROM inventory ORDER BY rowid DESC").fetchall() if date_in_range(row["date"], start, end)]

    writer.writerow(["COMPLAINTS"])
    complaint_fields = ["id", "department", "category", "subject", "priority", "status", "date", "description", "remarks", "archive_reason", "archived_at"]
    writer.writerow(["Complaint ID", "Department", "Category", "Subject", "Priority", "Status", "Date", "Description", "Dean Remarks", "Archive Reason", "Archived On"])
    for row in complaints:
        writer.writerow([csv_safe(row[field]) for field in complaint_fields])

    writer.writerow([])
    writer.writerow(["INVENTORY REQUESTS"])
    inventory_fields = ["id", "department", "item", "quantity", "priority", "status", "date", "reason", "remarks", "archive_reason", "archived_at"]
    writer.writerow(["Request ID", "Department", "Item", "Quantity", "Priority", "Status", "Date", "Reason", "Dean Remarks", "Archive Reason", "Archived On"])
    for row in inventory:
        writer.writerow([csv_safe(row[field]) for field in inventory_fields])

    filename = f"college_erp_report_{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-store"},
    )


@app.get("/reports/download")
@login_required
def download_report():
    if not dean_required():
        return jsonify(error="Only the Dean can download reports."), 403
    dataset = request.args.get("dataset", "complaints")
    output_format = request.args.get("format", "pdf").lower()
    if dataset not in {"complaints", "inventory", "pio"} or output_format not in {"pdf", "csv"}:
        return jsonify(error="Select a valid report and file format."), 400

    if dataset == "pio":
        records = filtered_pio_reports(request.args)
        title = "PIO REPORTS"
        columns = [("id", "Report ID"), ("department", "Department"), ("category", "Category"),
                   ("report_type", "Type"), ("title", "Title"), ("status", "Status"),
                   ("report_date", "Date")]
    else:
        start, end = requested_date_range(request.args)
        with db() as connection:
            records = [dict(row) for row in connection.execute(f"SELECT * FROM {dataset} ORDER BY rowid DESC")]
        records = [row for row in records if date_in_range(row["date"], start, end)]
        if dataset == "complaints":
            title = "COMPLAINT REPORT"
            columns = [("id", "Complaint ID"), ("department", "Department"), ("category", "Category"),
                       ("subject", "Subject"), ("priority", "Priority"), ("status", "Status"), ("date", "Date")]
        else:
            title = "INVENTORY REQUEST REPORT"
            columns = [("id", "Request ID"), ("department", "Department"), ("category", "Category"),
                       ("item", "Item"), ("quantity", "Quantity"), ("priority", "Priority"),
                       ("status", "Status"), ("date", "Date")]

    timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
    base_name = f"{dataset}_report_{timestamp.strftime('%Y%m%d_%H%M')}"
    if output_format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([f"COLLEGE ERP — {title}"])
        writer.writerow(["Generated On", timestamp.strftime("%d/%m/%Y, %I:%M %p")])
        writer.writerow([])
        writer.writerow([label for _, label in columns])
        for row in records:
            writer.writerow([csv_safe(row.get(field, "")) for field, _ in columns])
        return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="{base_name}.csv"', "Cache-Control": "no-store"})

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=12*mm, leftMargin=12*mm, topMargin=14*mm, bottomMargin=14*mm)
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("DownloadHeading", parent=styles["Title"], alignment=TA_CENTER,
                             textColor=colors.HexColor("#0f2740"), fontSize=17, leading=21)
    story = [Paragraph("COLLEGE ERP MANAGEMENT SYSTEM", heading), Paragraph(title, heading), Spacer(1, 4*mm),
             Paragraph(f"Generated: {timestamp.strftime('%d/%m/%Y, %I:%M %p')}", styles["BodyText"]), Spacer(1, 5*mm)]
    table_data = [[label for _, label in columns]]
    for row in records:
        table_data.append([Paragraph(str(row.get(field, "") or "—"), styles["BodyText"]) for field, _ in columns])
    if not records:
        table_data.append([Paragraph("No records found for the selected period.", styles["BodyText"])] + ["—"] * (len(columns) - 1))
    available_width = A4[0] - 24*mm
    table = Table(table_data, repeatRows=1, colWidths=[available_width / len(columns)] * len(columns))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2740")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Spacer(1, 8*mm), Paragraph("Authorized by: College Dean", styles["BodyText"])])
    document.build(story)
    return Response(buffer.getvalue(), mimetype="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{base_name}.pdf"', "Cache-Control": "no-store"})


@app.post("/api/complaints")
@login_required
def create_complaint():
    if session.get("role") not in {"Dean", "HOD"}:
        return jsonify(error="You cannot create complaints."), 403
    try:
        department = session.get("department") or request.form.get("department")
        subject, description = request.form.get("subject", "").strip(), request.form.get("description", "").strip()
        category, priority = request.form.get("category", "Other"), request.form.get("priority", "Medium")
        if department not in DEPARTMENTS or not subject or not description or priority not in ALLOWED_PRIORITY:
            return jsonify(error="Complete all required fields."), 400
        attachment = save_pdf(request.files.get("attachment"))
        with db() as connection:
            item_id = next_id(connection, "complaints", "CMP", 1000)
            connection.execute("INSERT INTO complaints (id,department,category,subject,priority,status,date,description,remarks,attachment,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                               (item_id, department, category, subject, priority, "Pending",
                                datetime.now().strftime("%d/%m/%Y"), description, "", attachment, session["username"]))
            notify_related(connection, department, f"New complaint {item_id} submitted by {department}", category, session["username"], "complaints", item_id, "new")
        return jsonify(ok=True, message="Complaint created successfully.")
    except ValueError as error:
        return jsonify(error=str(error)), 400


@app.post("/api/inventory")
@login_required
def create_inventory():
    if session.get("role") not in {"Dean", "HOD"}:
        return jsonify(error="You cannot create inventory requests."), 403
    try:
        department = session.get("department") or request.form.get("department")
        item, reason = request.form.get("item", "").strip(), request.form.get("reason", "").strip()
        category = request.form.get("category", "Other").strip()
        priority, quantity = request.form.get("priority", "Medium"), int(request.form.get("quantity", "0"))
        if department not in DEPARTMENTS or category not in MANAGEMENT_CATEGORIES or not item or not reason or quantity < 1 or priority not in ALLOWED_PRIORITY:
            return jsonify(error="Complete all required fields."), 400
        attachment = save_pdf(request.files.get("attachment"))
        with db() as connection:
            item_id = next_id(connection, "inventory", "INV", 500)
            connection.execute("INSERT INTO inventory (id,department,category,item,quantity,priority,status,date,reason,remarks,attachment,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                               (item_id, department, category, item, quantity, priority, "Pending",
                                datetime.now().strftime("%d/%m/%Y"), reason, "", attachment, session["username"]))
            notify_related(connection, department, f"New inventory request {item_id} submitted by {department}", category, session["username"], "inventory", item_id, "new")
        return jsonify(ok=True, message="Inventory request created successfully.")
    except (ValueError, TypeError) as error:
        return jsonify(error=str(error) if str(error) else "Invalid form values."), 400


def validated_pio(data, record):
    department = record["department"]
    category = str(data.get("category", record["category"])).strip()
    report_type = data.get("report_type", record["report_type"])
    title = str(data.get("title", record["title"])).strip()
    details = str(data.get("details", record["details"])).strip()
    report_date = str(data.get("report_date", record["report_date"]))
    reminder_date = str(data.get("reminder_date", record["reminder_date"] or "")).strip()
    recipient = str(data.get("recipient", record["recipient"] or "")).strip()
    if category not in PIO_CATEGORIES[department] or report_type not in {"Demand", "Calendar"} or not title or not details:
        raise ValueError("Complete all required PIO fields with a valid category and type.")
    date.fromisoformat(report_date)
    if reminder_date:
        date.fromisoformat(reminder_date)
    return category, report_type, title, details, report_date, reminder_date, recipient


@app.patch("/api/<kind>/<item_id>")
@login_required
def update_record(kind, item_id):
    table = {"complaints": "complaints", "inventory": "inventory", "pio": "pio_reports", "pio-reports": "pio_reports"}.get(kind)
    if not table:
        return jsonify(error="Invalid record type."), 400
    data = request.get_json(silent=True) or {}
    with db() as connection:
        record = connection.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
        if not record:
            return jsonify(error="Record not found."), 404
        if not may_edit(record):
            return jsonify(error="Only the creator of this entry or the Dean can edit it."), 403
        dean = session.get("role") == "Dean"
        try:
            if table == "pio_reports":
                category, report_type, title, details, report_date, reminder_date, recipient = validated_pio(data, record)
                connection.execute("UPDATE pio_reports SET category=?,report_type=?,title=?,details=?,report_date=?,reminder_date=?,recipient=? WHERE id=?", (category, report_type, title, details, report_date, reminder_date, recipient, item_id))
            else:
                category = str(data.get("category", record["category"] or "Other")).strip()
                priority = data.get("priority", record["priority"])
                if category not in MANAGEMENT_CATEGORIES or priority not in ALLOWED_PRIORITY:
                    raise ValueError("Select a valid category and priority.")
                if table == "complaints":
                    subject = str(data.get("subject", record["subject"])).strip()
                    description = str(data.get("description", record["description"])).strip()
                    if not subject or not description:
                        raise ValueError("Subject and description are required.")
                    connection.execute("UPDATE complaints SET subject=?,category=?,priority=?,description=? WHERE id=?", (subject, category, priority, description, item_id))
                else:
                    item = str(data.get("item", record["item"])).strip()
                    reason = str(data.get("reason", record["reason"])).strip()
                    quantity = int(data.get("quantity", record["quantity"]))
                    if not item or not reason or quantity < 1:
                        raise ValueError("Item, quantity and reason are required.")
                    connection.execute("UPDATE inventory SET item=?,category=?,quantity=?,priority=?,reason=? WHERE id=?", (item, category, quantity, priority, reason, item_id))
            status = data.get("status", record["status"]) if dean else record["status"]
            allowed = ALLOWED_STATUS | ({"Scheduled"} if table == "pio_reports" else set())
            if status not in allowed:
                raise ValueError("Invalid status.")
            completed = status in {"Completed", "Resolved"}
            # Editing archived content never silently restores or rewrites its archive history.
            archive = bool(record["archived"]) or completed
            reason = record["archive_reason"] if record["archived"] else ("Completed" if completed else "")
            timestamp = record["archived_at"] if record["archived"] else (datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d/%m/%Y, %I:%M %p") if completed else "")
            if table == "pio_reports":
                connection.execute("UPDATE pio_reports SET status=?,archived=?,archive_reason=?,archived_at=? WHERE id=?", (status, int(archive), reason, timestamp, item_id))
            else:
                remarks = str(data.get("remarks", record["remarks"])).strip() if dean else record["remarks"]
                connection.execute(f"UPDATE {table} SET status=?,remarks=?,archived=?,archive_reason=?,archived_at=? WHERE id=?", (status, remarks, int(archive), reason, timestamp, item_id))
        except (ValueError, TypeError) as error:
            connection.rollback()
            return jsonify(error=str(error)), 400
        event = "completed" if completed and not record["archived"] else ("status" if status != record["status"] else "update")
        notify_related(connection, record["department"], f"{item_id} updated by {session.get('name', session['username'])}", category, session["username"], "pio" if table == "pio_reports" else table, item_id, event)
    return jsonify(ok=True, message="Record updated successfully.")


@app.delete("/api/<kind>/<item_id>")
@login_required
def delete_record(kind, item_id):
    table = {"complaints": "complaints", "inventory": "inventory", "pio": "pio_reports", "pio-reports": "pio_reports"}.get(kind)
    if not table:
        return jsonify(error="Invalid record type."), 400
    with db() as connection:
        record = connection.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
        if not record:
            return jsonify(error="Record not found."), 404
        if not may_edit(record):
            return jsonify(error="Only the creator of this entry or the Dean can delete it."), 403
        if record["archived"]:
            return jsonify(error="This record is already archived."), 409
        archived_at = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d/%m/%Y, %I:%M %p")
        connection.execute(f"UPDATE {table} SET archived=1,archive_reason='Deleted',archived_at=? WHERE id=?", (archived_at, item_id))
        notify_related(connection, record["department"], f"{item_id} moved to Archives by {session.get('name', session['username'])}", record["category"], session["username"], "pio" if table == "pio_reports" else table, item_id, "deleted")
    return jsonify(ok=True, message="Record moved to Archives.")


@app.get("/attachments/<path:filename>")
@login_required
def attachment(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
