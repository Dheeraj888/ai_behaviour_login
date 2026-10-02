import pytest
from fastapi.testclient import TestClient

from app import db, ml


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(ml, "MODEL_DIR", tmp_path)
    from app.main import app
    with TestClient(app) as c:
        yield c


def beh(interval=120.0, duration=4000.0):
    return {"typing_duration": duration, "avg_key_interval": interval, "backspace_count": 0,
            "mouse_distance": 800.0, "avg_mouse_speed": 400.0, "login_hour": 14.5}


REG = {"name": "Test User", "email": "t@example.com", "password": "password123", "pin": "1234"}


def login(client, behavior, password="password123"):
    return client.post("/api/login", json={"email": REG["email"], "password": password, "behavior": behavior})


def test_full_flow(client):
    assert client.post("/api/register", json=REG).status_code == 200
    assert client.post("/api/register", json=REG).status_code == 409
    assert login(client, beh(), "wrongpass1").status_code == 401

    token = None
    for i in range(6):
        r = login(client, beh(interval=115 + i * 3, duration=3900 + i * 40))
        assert r.status_code == 200 and not r.json()["requires_pin"]
        token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/me", headers=auth).json()["sample_count"] == 6
    t = client.post("/api/train", headers=auth)
    assert t.status_code == 200 and 0 <= t.json()["training_accuracy"] <= 1

    ok = login(client, beh(interval=120, duration=4000))
    assert 0 <= ok.json()["trust_score"] <= 100

    odd = login(client, beh(interval=3000, duration=90000))
    body = odd.json()
    assert body["requires_pin"] and 0 <= body["trust_score"] <= 100

    ch = body["challenge_token"]
    assert client.post("/api/verify-pin", json={"challenge_token": ch, "pin": "9999"}).status_code == 401
    good = client.post("/api/verify-pin", json={"challenge_token": ch, "pin": "1234"})
    assert good.status_code == 200 and good.json()["token"]

    logs = client.get("/api/logs", headers=auth).json()["logs"]
    statuses = {x["status"] for x in logs}
    assert {"accepted", "rejected", "challenge", "accepted_after_pin"} <= statuses
    assert client.post("/api/logout", headers=auth).status_code == 200
    assert client.get("/api/me", headers=auth).status_code == 401


def test_train_needs_samples_and_auth(client):
    assert client.post("/api/train").status_code == 401
    tok = client.post("/api/register", json=REG).json()["token"]
    r = client.post("/api/train", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 400 and "at least" in r.json()["detail"]


def test_passwords_not_stored_plaintext(client):
    client.post("/api/register", json=REG)
    with db.get_conn() as conn:
        row = conn.execute("SELECT password_hash, pin_hash FROM users").fetchone()
    assert b"password123" not in bytes(row["password_hash"]) and b"1234" != bytes(row["pin_hash"])


def test_validation_error_is_readable_json(client):
    r = client.post("/api/register", json={**REG, "pin": "abc"})
    assert r.status_code == 422 and isinstance(r.json()["detail"], list)


def test_dashboard_sample_endpoint(client):
    tok = client.post("/api/register", json=REG).json()["token"]
    auth = {"Authorization": f"Bearer {tok}"}
    assert client.post("/api/behavior/sample", json=beh()).status_code == 401
    for n in range(1, 6):
        r = client.post("/api/behavior/sample", json=beh(interval=100 + n), headers=auth)
        assert r.status_code == 200 and r.json()["sample_count"] == n
    assert client.post("/api/train", headers=auth).status_code == 200
