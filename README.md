# College ERP — Temporary Web Showcase

This is a separate browser-compatible showcase of the College ERP desktop application. The original PySide6 files are not modified.

## Demo accounts

- Dean: `dean` / `1234`
- Hospital HOD: `hod_hospital` / `1234`
- Computer HOD: `hod_computer` / `1234`
- Mechanical HOD: `hod_mechanical` / `1234`
- Electrical HOD: `hod_electrical` / `1234`
- Civil HOD: `hod_civil` / `1234`

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

This temporary version uses in-memory demo data. Changes reset whenever Render restarts. A database should be added for production use.
