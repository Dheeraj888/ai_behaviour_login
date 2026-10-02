# Milestone 6 — Testing and Deployment

## Deployment
The system is deployed locally with:
```powershell
uvicorn app.main:app --reload
```

## Testing
- Unit tests: `pytest -q`
- Registration/login validation
- Baseline sample collection
- Model training
- Trust-score decision
- PIN fallback
- Authentication log display

## Evidence to Add
[[FILL: Screenshot of pytest result]]
[[FILL: Screenshot of normal login]]
[[FILL: Screenshot of anomaly + PIN fallback]]
[[FILL: Screenshot of login history]]

## Final Status
[[FILL: Mention bugs found/fixed and whether all planned functions worked]]
