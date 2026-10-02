# Test Report: AI-Based Secure Login System Using Behavioral Biometrics

**Stack:** FastAPI, SQLite, HTML/CSS/JavaScript, Logistic Regression (scikit-learn), bcrypt
**Test date:** 2 October 2026
**Method:** automated API tests (pytest) and end-to-end browser tests (headless Microsoft Edge, driven with Playwright) against a separate test database.

## 1. Summary

The system works end to end. A user can register, log in with a password, build a behavioral baseline, train a personal model, and then log in with a trust score. Unusual behavior triggers PIN verification. All attempts are written to the database and shown on the dashboard.

- **Automated tests:** 9 passed, 0 failed.
- **Browser workflow:** every button on the login page and dashboard was exercised and worked.
- **JavaScript errors:** none. The only 4xx responses were the deliberate duplicate-register, wrong-password and wrong-PIN cases.

## 2. How the system decides

1. The login page records typing duration, average gap between keys, backspace count, mouse distance, mouse speed and hour of day.
2. Before a user has a trained model, a correct password logs in and the behavior is saved as a baseline sample (minimum 5).
3. After training, each login gets a trust score (0-100%) from that user's own Logistic Regression model.
4. Trust score of 70% or more: login accepted. Below 70%: the user must enter the fallback PIN.
5. A correct PIN logs in. A wrong PIN is rejected. Every attempt is logged.

## 3. Test results

| # | Test | Result |
|---|------|--------|
| A | Register a new user | Pass. User created, password and PIN stored as bcrypt hashes. |
| B | Register the same email again | Pass. "Email already registered". |
| C | Login with wrong password | Pass. Rejected, attempt logged. |
| D | 5 normal logins before training | Pass. Samples saved: 1/5 to 5/5. |
| E | Train model | Pass. Model trained and status shown on dashboard. |
| F | Normal behavioral login after training | Pass. Accepted, trust scores seen: 84%, 86%, 88%. |
| G | Very slow / unusual typing | Pass. Trust score 0%, PIN requested. |
| H | Correct fallback PIN | Pass. Logged in, dashboard opened. |
| I | Wrong PIN | Pass. "Incorrect PIN", login denied. |
| J | Login history | Pass. Time, trust score, prediction and status shown. |
| K | Reload the browser | Pass. Dashboard state restored from the server. |
| L | Logout | Pass. Session cleared, returned to login page. |
| M | Add samples from the dashboard | Pass. 5 samples recorded, count updated, model trained. |
| N | Page opened from Live Server (port 5500) | Pass. API calls work across origins. |
| O | Demo accounts (5 users) | Pass. All 5 log in with the demo password. |

Automated test coverage (`tests/`): registration, duplicate registration, wrong password, baseline collection, training, trust score range 0-100, PIN challenge (right and wrong), login history, logout, training with too few samples, password hashing, readable validation errors, and the dashboard sample endpoint.

## 4. Model results

- Model: Logistic Regression, one model per user, 6 input features.
- Input to the model: how far a login is from the user's own baseline, per feature.
- Training accuracy seen in tests: 91.7% (6 samples) and 100% (5 samples).
- Trust score is always bounded to 0-100%.

## 5. Problems found and fixed

| Problem | Cause | Fix |
|---|---|---|
| Login failed silently after a user waited on the page | Typing time was measured from page load; backend rejects more than 120 s | Timer starts at the first key typed; all values are clamped |
| Buttons gave no feedback | No error handling, no disabled state | Messages shown, buttons disabled during requests |
| Genuine logins scored about 50% | A linear model cannot separate a cluster surrounded by impostor samples | Model now uses deviation from the user's baseline |
| 405 error | Page opened from a static server, not the API | CORS enabled, frontend points to the API address |
| Training result disappeared | Live Server reloaded the page when model files changed | Accuracy shown permanently from the server, data folder ignored by Live Server |

## 6. Limitations

- The impostor class used for training is **synthetic** (generated from the user's own samples), so the accuracy figure is a demonstration number, not a measured real-world accuracy.
- Models are per user and trained on very few samples (minimum 5), so the trust score is sensitive to how the user types.
- PIN attempts are not rate-limited.
- The system was tested on one machine and one browser (Microsoft Edge, headless).

## 7. How to run

```
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Demo accounts: `aarav@example.com`, `priya@example.com`, `rohan@example.com`, `neha@example.com`, `karan@example.com`. Password `Demo@1234`, PIN `1234`.
