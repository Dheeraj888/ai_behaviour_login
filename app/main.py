from __future__ import annotations
import json
import secrets
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import init_db, get_conn
from .ml import train_user_model, trust_score, has_model, model_info

app = FastAPI(title="Behavioral Biometric Login Demo")
STATIC_DIR = Path(__file__).parent / "static"
# Bearer tokens (no cookies) are used, so any origin (e.g. Live Server) may call the API.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TRUST_THRESHOLD = 70.0
MIN_TRAIN_SAMPLES = 5

class Behavior(BaseModel):
    typing_duration: float = Field(ge=0, le=120000)
    avg_key_interval: float = Field(ge=0, le=10000)
    backspace_count: int = Field(ge=0, le=500)
    mouse_distance: float = Field(ge=0, le=500000)
    avg_mouse_speed: float = Field(ge=0, le=100000)
    login_hour: float = Field(ge=0, lt=24)

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    pin: str = Field(pattern=r"^\d{4,8}$")

class LoginRequest(BaseModel):
    email: str
    password: str
    behavior: Behavior

class VerifyPinRequest(BaseModel):
    challenge_token: str
    pin: str = Field(pattern=r"^\d{4,8}$")

@app.exception_handler(RequestValidationError)
async def _validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors() and [
        {"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]})

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Server error: {exc}"})

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/index.html", include_in_schema=False)
def index_html():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/dashboard.html", include_in_schema=False)
@app.get("/dashboard")
def dashboard():
    return FileResponse(STATIC_DIR / "dashboard.html")


def _hash(secret: str) -> bytes:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt())

def _verify(secret: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(secret.encode(), hashed)

def _new_session(user_id: int) -> str:
    token=secrets.token_urlsafe(32)
    with get_conn() as conn:
        conn.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)", (token,user_id))
    return token

def _auth(authorization: Optional[str]) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing session token")
    token=authorization[7:]
    with get_conn() as conn:
        row=conn.execute("SELECT user_id FROM sessions WHERE token=?", (token,)).fetchone()
    if not row:
        raise HTTPException(401, "Invalid session token")
    return int(row["user_id"])

def _save_sample(user_id: int, sample: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO behavior_samples
            (user_id,typing_duration,avg_key_interval,backspace_count,mouse_distance,avg_mouse_speed,login_hour)
            VALUES(?,?,?,?,?,?,?)""",
            (user_id,sample["typing_duration"],sample["avg_key_interval"],sample["backspace_count"],
             sample["mouse_distance"],sample["avg_mouse_speed"],sample["login_hour"])
        )

def _log(user_id, email, trust, prediction, status, reason=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO login_attempts(user_id,email,trust_score,prediction,status,reason) VALUES(?,?,?,?,?,?)",
            (user_id,email,trust,prediction,status,reason)
        )

@app.post("/api/register")
def register(req: RegisterRequest):
    email=req.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(400, "Enter a valid email address")
    with get_conn() as conn:
        exists=conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
        if exists:
            raise HTTPException(409, "Email already registered")
        cur=conn.execute(
            "INSERT INTO users(name,email,password_hash,pin_hash) VALUES(?,?,?,?)",
            (req.name.strip(), email, _hash(req.password), _hash(req.pin))
        )
        uid=cur.lastrowid
    token=_new_session(uid)
    return {"ok": True, "token": token, "message": "Registered. Perform at least 5 normal logins to collect baseline behavior."}

@app.post("/api/login")
def login(req: LoginRequest):
    email=req.email.strip().lower()
    with get_conn() as conn:
        user=conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not _verify(req.password, user["password_hash"]):
        _log(None, email, None, "password_failed", "rejected", "Invalid email or password")
        raise HTTPException(401, "Invalid email or password")

    uid=int(user["id"])
    sample=req.behavior.model_dump()

    if not has_model(uid):
        _save_sample(uid, sample)
        with get_conn() as conn:
            count=conn.execute("SELECT COUNT(*) c FROM behavior_samples WHERE user_id=?", (uid,)).fetchone()["c"]
        _log(uid, email, None, "baseline_collection", "accepted", f"Baseline sample {count}")
        return {"ok": True, "requires_pin": False, "token": _new_session(uid), "trust_score": None,
                "message": f"Baseline sample saved ({count}/{MIN_TRAIN_SAMPLES} minimum)."}

    try:
        score=trust_score(uid, sample)
    except Exception:
        score=0.0  # unusable model -> fail safe to PIN verification
    if score >= TRUST_THRESHOLD:
        _save_sample(uid, sample)  # adaptive baseline after accepted login
        _log(uid, email, score, "legitimate", "accepted", "Trust score above threshold")
        return {"ok": True, "requires_pin": False, "token": _new_session(uid), "trust_score": score,
                "message": "Behavior accepted."}

    challenge=secrets.token_urlsafe(24)
    with get_conn() as conn:
        conn.execute("INSERT INTO pending_challenges(challenge_token,user_id,sample_json,trust_score) VALUES(?,?,?,?)",
                     (challenge, uid, json.dumps(sample), score))
    _log(uid, email, score, "anomaly", "challenge", "Trust score below threshold")
    return {"ok": False, "requires_pin": True, "challenge_token": challenge, "trust_score": score,
            "message": "Behavioral anomaly detected. Verify fallback PIN."}

@app.post("/api/verify-pin")
def verify_pin(req: VerifyPinRequest):
    with get_conn() as conn:
        ch=conn.execute("SELECT * FROM pending_challenges WHERE challenge_token=?", (req.challenge_token,)).fetchone()
        if not ch:
            raise HTTPException(404, "Challenge not found")
        user=conn.execute("SELECT * FROM users WHERE id=?", (ch["user_id"],)).fetchone()
    if not _verify(req.pin, user["pin_hash"]):
        _log(user["id"], user["email"], ch["trust_score"], "anomaly", "rejected", "Fallback PIN failed")
        raise HTTPException(401, "Incorrect PIN")
    with get_conn() as conn:
        conn.execute("DELETE FROM pending_challenges WHERE challenge_token=?", (req.challenge_token,))
    _log(user["id"], user["email"], ch["trust_score"], "anomaly", "accepted_after_pin", "Fallback PIN succeeded")
    return {"ok": True, "token": _new_session(int(user["id"])), "message": "PIN verified."}

@app.post("/api/behavior/sample")
def add_sample(behavior: Behavior, authorization: Optional[str] = Header(default=None)):
    uid=_auth(authorization)
    _save_sample(uid, behavior.model_dump())
    with get_conn() as conn:
        count=conn.execute("SELECT COUNT(*) c FROM behavior_samples WHERE user_id=?", (uid,)).fetchone()["c"]
        email=conn.execute("SELECT email FROM users WHERE id=?", (uid,)).fetchone()["email"]
    _log(uid, email, None, "manual_sample", "accepted", f"Sample {count} added from dashboard")
    return {"ok": True, "sample_count": count, "min_samples": MIN_TRAIN_SAMPLES,
            "message": f"Behavioral sample recorded ({count}/{MIN_TRAIN_SAMPLES} minimum)."}

@app.post("/api/train")
def train(authorization: Optional[str] = Header(default=None)):
    uid=_auth(authorization)
    with get_conn() as conn:
        rows=conn.execute("SELECT * FROM behavior_samples WHERE user_id=? ORDER BY id", (uid,)).fetchall()
    samples=[dict(r) for r in rows]
    if len(samples) < MIN_TRAIN_SAMPLES:
        raise HTTPException(400, f"Need at least {MIN_TRAIN_SAMPLES} samples; currently {len(samples)}")
    try:
        result=train_user_model(uid, samples)
    except Exception as exc:
        raise HTTPException(500, f"Training failed: {exc}")
    return {"ok": True, **result}

@app.post("/api/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    _auth(authorization)
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (authorization[7:],))
    return {"ok": True}

@app.get("/api/me")
def me(authorization: Optional[str] = Header(default=None)):
    uid=_auth(authorization)
    with get_conn() as conn:
        user=conn.execute("SELECT id,name,email,created_at FROM users WHERE id=?", (uid,)).fetchone()
        count=conn.execute("SELECT COUNT(*) c FROM behavior_samples WHERE user_id=?", (uid,)).fetchone()["c"]
    return {"user": dict(user), "sample_count": count, "model_trained": has_model(uid), "model": model_info(uid), "threshold": TRUST_THRESHOLD}

@app.get("/api/logs")
def logs(authorization: Optional[str] = Header(default=None)):
    uid=_auth(authorization)
    with get_conn() as conn:
        rows=conn.execute("SELECT * FROM login_attempts WHERE user_id=? ORDER BY id DESC LIMIT 50", (uid,)).fetchall()
    return {"logs": [dict(r) for r in rows]}
