# AI-Based Secure Login Using Behavioral Biometrics

A BCA-level academic prototype that combines password authentication with behavioral biometrics (keystroke dynamics + mouse movement) and a simple Logistic Regression model.

> **Academic prototype only.** This is not a production authentication system.

## Features
- User registration with bcrypt password hashing
- Fallback PIN hashing
- Behavioral capture during login:
  - total typing duration
  - average key interval
  - backspace count
  - mouse distance
  - average mouse speed
  - login hour
- Per-user Logistic Regression model
- Trust score (0-100)
- PIN fallback for low-trust login attempts
- Authentication/anomaly logs
- SQLite database
- Local demo deployment with FastAPI
- Unit tests for feature validation and trust threshold logic

## Quick start (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

## Demo flow
1. Register a user.
2. Login at least **5 times normally**. These become baseline behavioral samples.
3. On the Dashboard click **Train / Retrain Model**.
4. Login again normally and observe the trust score.
5. Try typing very slowly / moving the mouse unusually. If trust is below the threshold, PIN verification is requested.
6. Open Dashboard to show login history and anomaly detection results.

## Academic note about training data
This demo uses the user's captured samples as legitimate behavior and creates perturbed synthetic samples as the negative/impostor class. This is suitable for a classroom demonstration, but a real biometric study should use a larger, independently collected multi-user dataset and stronger evaluation methodology.

## Main files
- `app/main.py` — API and application logic
- `app/db.py` — SQLite schema/helpers
- `app/ml.py` — feature preprocessing, Logistic Regression, trust score
- `app/static/index.html` — registration/login UI
- `app/static/dashboard.html` — model training + logs UI
- `docs/WHAT_TO_FILL.md` — exactly what you need to customize before submission
- `docs/Final_Report_Template.md` — report structure based on the supplied Qollabb guidance
- `docs/Presentation_Outline.md` — slide-by-slide outline
- `docs/milestones/` — six milestone writeups matching your Qollabb milestone names

## Recommended submission sequence
Do **not** mark every milestone complete immediately. Complete the related document/code evidence first, then mark it complete in Qollabb.
