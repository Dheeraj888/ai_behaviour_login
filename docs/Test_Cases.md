# Test Cases

| ID | Scenario | Input / Action | Expected Result | Actual Result |
|---|---|---|---|---|
| TC01 | New registration | Valid name/email/password/PIN | User created | [[FILL]] |
| TC02 | Duplicate email | Same email again | Registration rejected | [[FILL]] |
| TC03 | Wrong password | Invalid password | Login rejected | [[FILL]] |
| TC04 | Baseline collection | Correct login before model | Sample saved | [[FILL]] |
| TC05 | Train too early | <5 samples | Training rejected | [[FILL]] |
| TC06 | Train model | >=5 samples | Model file created | [[FILL]] |
| TC07 | Normal behavior | Similar typing/mouse behavior | Higher trust score | [[FILL]] |
| TC08 | Anomalous behavior | Very different timing/mouse | Low trust -> PIN challenge | [[FILL]] |
| TC09 | Correct fallback PIN | Correct PIN | Login accepted | [[FILL]] |
| TC10 | Wrong fallback PIN | Wrong PIN | Login rejected | [[FILL]] |
| TC11 | Logs | Open dashboard | Attempts visible | [[FILL]] |

## Unit tests
Run:
```powershell
pytest -q
```
Attach a screenshot of the passing test output in the appendix.
