# Software Requirement Specification (SRS)

## Project Title
AI-Based Secure Login System Using Behavioral Biometrics

## Student
[[FILL: YOUR FULL NAME]] — [[FILL: STUDENT ID]]

## 1. Purpose
Design and develop an academic prototype that supplements password authentication with behavioral biometric signals collected during login.

## 2. Scope
The system captures keystroke and mouse behavior, creates a user-specific behavioral model, calculates a trust score during login, and requests fallback PIN verification when behavior is anomalous.

## 3. Functional Requirements
- FR1: User can register with name, email, password, and fallback PIN.
- FR2: Password and PIN must be stored as hashes.
- FR3: System must capture login behavioral features.
- FR4: System must save legitimate baseline samples.
- FR5: System must train a Logistic Regression model per user after enough samples.
- FR6: System must calculate a trust score on later login attempts.
- FR7: System must request PIN fallback when trust score is below threshold.
- FR8: System must log login decisions and anomaly results.
- FR9: Authenticated user can view recent login history.

## 4. Non-Functional Requirements
- NFR1: Runs locally for demonstration.
- NFR2: Input validation must reject unreasonable values.
- NFR3: Secrets are hashed using bcrypt.
- NFR4: UI should work on desktop and mobile browsers.
- NFR5: Code should be modular enough for academic explanation.

## 5. Constraints
- Small academic dataset.
- Synthetic negative/impostor samples are used for demonstration.
- Not intended for production identity verification.
- Model performance depends on consistency and amount of behavioral data.

## 6. Technology Stack
- Python + FastAPI
- SQLite
- scikit-learn Logistic Regression
- HTML/CSS/JavaScript
- bcrypt

## 7. Acceptance Criteria
- Registration works.
- Five or more baseline logins can be stored.
- Model can train successfully.
- Later login produces a trust score.
- Low-trust attempt triggers fallback PIN.
- Login history is visible.
