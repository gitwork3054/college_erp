# College ERP — Temporary Web Showcase

This is a separate browser-compatible showcase of the College ERP desktop application. The original PySide6 files are not modified.

## Latest web features

- Complete English/Gujarati interface switching with saved preferences
- Working Remember username option in the browser
- Clickable KPI cards, complaint rows and department cards
- Complaint and inventory creation with optional PDF attachments
- Dean status updates, remarks and record deletion
- Settings for language, display density and delete confirmation
- Premium responsive UI with motion and hover effects
- SQLite-backed demo records and role-based Dean/HOD/PIO access
- Civil and Electrical PIO demand/calendar reports
- Dean-only CSV and letterhead PDF downloads
- In-app notifications with email/SMS preference fields

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
