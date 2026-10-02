# PROJECT REPORT

## Title Page
**Project Title:** AI-Based Secure Login System Using Behavioral Biometrics  
**Student:** [[FILL: YOUR FULL NAME]]  
**Student ID:** [[FILL: STUDENT ID]]  
**Program:** [[FILL: PROGRAM / SEMESTER]]  
**Institution:** [[FILL: UNIVERSITY NAME]]  
**Guide/Mentor:** [[FILL: APPROVED MENTOR NAME]]  
**Submission Date:** [[FILL: DATE]]

---

## Abstract
This project presents an AI-based secure login prototype that combines traditional password authentication with behavioral biometrics. During login, the system captures typing and mouse interaction features such as total typing duration, average key interval, backspace count, mouse travel distance, mouse speed, and login time. A Logistic Regression model estimates how closely the current behavior matches the legitimate user's baseline. The probability is converted into a trust score. Low-trust attempts trigger a fallback PIN challenge. The prototype is implemented with FastAPI, SQLite, JavaScript, bcrypt, and scikit-learn.

[[FILL: Add 2-4 sentences summarizing your actual evaluation results.]]

## 1. Introduction
### 1.1 Background
Passwords are widely used but can be stolen, guessed, reused, or exposed. Behavioral biometrics adds another signal by examining how a user interacts with the system.

### 1.2 Problem Statement
A correct password alone does not prove that the legitimate user is currently operating the account. The project therefore investigates whether simple behavioral features can provide an additional trust signal during login.

### 1.3 Objectives
- Study limitations of traditional authentication.
- Analyze keystroke and mouse behavioral biometrics.
- Design SRS, architecture, and database schema.
- Implement secure registration with hashing.
- Capture login behavior.
- Train a simple Logistic Regression model.
- Produce a trust score and fallback PIN challenge.
- Record authentication/anomaly logs.
- Evaluate the prototype and test its major functions.

### 1.4 Scope
Local academic demonstration. It is not a production biometric security product.

## 2. Methodology
### 2.1 Development Approach
[[FILL: e.g. iterative prototype development]]

### 2.2 Behavioral Features
1. Typing duration
2. Average key interval
3. Backspace count
4. Mouse movement distance
5. Average mouse speed
6. Login hour

### 2.3 Data Collection
The user's successful logins are recorded as baseline legitimate behavior samples. A minimum of five samples is required by this prototype before training.

### 2.4 Preprocessing
Features are converted to numeric vectors and standardized before Logistic Regression training.

### 2.5 Model
Logistic Regression is used because it is simple, explainable, and appropriate for a BCA-level prototype. The probability of the legitimate class is multiplied by 100 to produce the trust score.

### 2.6 Negative-Class Limitation
For demonstration, perturbed synthetic samples are generated from legitimate samples to represent anomalous/impostor behavior. This is a limitation and must not be presented as equivalent to a real attacker dataset.

### 2.7 System Architecture
[[FILL: Insert screenshot/export of Architecture.md diagram]]

### 2.8 Database Design
[[FILL: Insert ER diagram]]

## 3. Results and Findings
### 3.1 Dataset Summary
- Legitimate baseline samples: [[FILL: NUMBER]]
- Synthetic negative samples: [[FILL: NUMBER]]

### 3.2 Model Result
- Training accuracy: [[FILL: ACTUAL VALUE]]
- Test/evaluation accuracy: [[FILL: ACTUAL VALUE OR state that a separate holdout test was not performed]]

### 3.3 Confusion Matrix
[[FILL: INSERT CONFUSION MATRIX AND VALUES]]

### 3.4 Functional Results
[[FILL: Explain normal login, anomaly login, PIN fallback, logs. Add screenshots.]]

## 4. Discussion and Analysis
### 4.1 Interpretation
[[FILL: What did you observe about consistent vs unusual typing/mouse behavior?]]

### 4.2 Strengths
- Adds a second behavioral signal without extra hardware.
- Explainable model.
- Local demonstration is simple to reproduce.
- Fallback verification prevents automatic rejection on every anomaly.

### 4.3 Weaknesses
- Small dataset.
- Synthetic negative samples.
- Behavior can vary due to stress, device, injury, browser, or environment.
- Threshold requires calibration.

### 4.4 Opportunities
- Larger multi-user dataset
- Continuous authentication after login
- Device/browser context
- Better anomaly models

### 4.5 Threats
- Mimicry attacks
- Sensor/noise variation
- False rejection of legitimate users
- Privacy concerns around behavioral data

## 5. Conclusion and Recommendations
The prototype demonstrates how behavioral signals can supplement password authentication and trigger step-up verification. It should be treated as an academic proof of concept rather than a deployment-ready biometric security system.

### Recommendations
- Collect more real user/impostor data.
- Separate training and test datasets.
- Calibrate threshold using FAR/FRR style metrics.
- Encrypt sensitive biometric feature storage in a production implementation.
- Add continuous authentication as future work.

## 6. References
[[FILL: Add the actual books/papers/websites you consulted. Use one consistent citation style.]]

## 7. Appendices
- Screenshots
- Test cases
- Unit test output
- Selected source-code snippets
- Additional charts/graphs
