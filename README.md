# College ERP — Temporary Web Showcase

This is a separate browser-compatible showcase of the College ERP desktop application. The original PySide6 files are not modified.

## Latest web features

- Blue and white login with opening logo animation, connecting dots, and light/dark modes
- Compact dashboard with a circular profile menu and dimensional module icons
- Home welcome panel, animated campus network, card lighting and live local clock
- Motion pause control and reduced-motion support
- Font settings scale text only, preserving spacing and sidebar height
- Direct native dialogs for adding and opening complaint, inventory and PIO entries
- Every entry is viewable within existing role visibility; only its creator or the Dean can edit
- Archived content follows the same creator-or-Dean editing rule

- Complete English/Gujarati interface switching with saved preferences
- Working Remember username option in the browser
- Clickable KPI cards, complaint rows and department cards
- Complaint and inventory creation with optional PDF attachments
- Dean status updates, remarks and record deletion
- Settings for language, display density, font size, font weight and delete confirmation
- Premium boxed responsive UI with accessible motion and hover effects
- SQLite-backed demo records and role-based Dean/HOD/PIO access
- Civil and Electrical PIO demand/calendar reports
- Dean-only CSV and letterhead PDF downloads for the last 15, 30, 60 or custom days
- Live in-app notifications routed to the Dean and responsible department account
- Notifications for new entries, edits, status changes, completion and deletion
- Clickable colour-coded notifications that open the affected record
- Sender-excluded routing to the Dean and relevant IT/Infrastructure/other management team
- PDF or CSV format selection for complaint, inventory and PIO downloads

## Demo accounts

- Dean: `dean` / `1234`
- Anatomy HOD: `hod_anatomy` / `1234`
- Physiology HOD: `hod_physiology` / `1234`
- Biochemistry HOD: `hod_biochemistry` / `1234`
- Pathology HOD: `hod_pathology` / `1234`
- Microbiology HOD: `hod_microbiology` / `1234`
- Pharmacology HOD: `hod_pharmacology` / `1234`
- Civil PIO: `pio_civil` / `1234`
- Electrical PIO: `pio_electrical` / `1234`
- IT Management: `manager_it` / `1234`
- Infrastructure Management: `manager_infrastructure` / `1234`
- Equipment Management: `manager_equipment` / `1234`
- Maintenance Management: `manager_maintenance` / `1234`
- Safety Management: `manager_safety` / `1234`

## Test locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Upload to GitHub

Create an empty GitHub repository, then run inside this folder:

```powershell
git init
git add .
git commit -m "College ERP web showcase"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Deploy on Render

1. Sign in to Render and choose **New > Blueprint**.
2. Connect the GitHub repository.
3. Select the repository and click **Apply**.
4. Render reads `render.yaml` and deploys the app.
5. Open the generated `onrender.com` URL.

The free Render service may sleep when inactive and take a short time to open again.

## Showcase limitation

This showcase uses SQLite. Data persists locally, but Render's free filesystem is ephemeral and may reset during redeployment or service replacement. Use Render Postgres or another managed database before production use.

## Blue interface with original workflow

Original backend and permissions retained. Complaint, inventory, PIO, notifications and archive entries open their existing detail views. Every record table includes an Open action. Dashboard supports light and dark appearance in the header and Settings; the circular profile opens account information, preferences and sign-out. Blue sign-in, role autofill, logo intro and connecting dots are retained.

## Creator permissions

New complaints and inventory requests store the authenticated username in created_by; PIO reports already record it. All changes are enforced server-side: only the creator or Dean can edit or archive an entry. Users in the same department gain no edit permission merely from department membership. Legacy records with no recorded creator are Dean-only. Archive content edits preserve archive status and timestamps. The Dean retains status/remarks control. PIO entries support their own native detail/edit dialog and archive table.
