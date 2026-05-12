# Viplov Portfolio App

A Flask-based portfolio website with an admin backend.

## Features
- Public portfolio at `/`
- Admin login at `/admin`
- Upload/replace profile image, resume PDF, resume preview, project screenshots, and project PDFs
- Edit hero copy, stats, learning items, and project text from the admin panel

## Login
- ID: `9810444571`
- Password: `Viplov@123`

## Run locally
```bash
cd viplov_portfolio_app
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open:
- Public site: http://127.0.0.1:5000/
- Admin: http://127.0.0.1:5000/admin

## Important
These credentials are hardcoded because you requested them. Change them before deploying publicly.
