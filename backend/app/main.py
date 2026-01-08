import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List

from . import models, schemas, crud, auth
from .database import engine
from .deps import get_db, get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="IronStreak")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_seed_users():
    # create two predefined users if none exist
    db = next(get_db())
    ucount = db.query(models.User).count()
    if ucount == 0:
        u1 = os.getenv("USER1_EMAIL", "Tarungangwar@gmail.com")
        p1 = os.getenv("USER1_PASSWORD", "password")
        u2 = os.getenv("USER2_EMAIL", "brother@example.com")
        p2 = os.getenv("USER2_PASSWORD", "password")
        crud.create_user(db, u1, p1)
        crud.create_user(db, u2, p2)


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/target/create", response_model=schemas.TargetOut)
def create_target(payload: schemas.TargetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # start_date must be UTC date
    t = crud.create_target(db, current_user.id, payload.target_text, payload.start_date, payload.duration_in_days)
    return t


@app.get("/target/active", response_model=List[schemas.TargetOut])
def active_targets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # First, check and fail any targets that have missed days
    crud.check_and_fail_missed_targets(db, current_user.id)
    return crud.get_active_targets(db, current_user.id)


@app.get("/target/history", response_model=List[schemas.TargetOut])
def target_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_target_history(db, current_user.id)


@app.post("/checkin/today", response_model=schemas.CheckinResult)
def checkin_today(target_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    t = crud.get_target(db, target_id)
    if not t or t.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Target not found")
    if t.status != models.TargetStatus.ACTIVE:
        return {"success": False, "message": "Target is not active"}

    today = datetime.utcnow().date()
    # Only allow check-in for today
    if not (t.start_date <= today <= t.end_date):
        return {"success": False, "message": "Today is outside the target active range"}

    # If there's already a checkin for today, reject
    existing = crud.get_checkin_for_date(db, t.id, today)
    if existing:
        return {"success": False, "message": "Already checked in for today"}

    # If today is not the start date, ensure yesterday was completed; otherwise fail target
    if today > t.start_date:
        yesterday = today - timedelta(days=1)
        yesterday_check = crud.get_checkin_for_date(db, t.id, yesterday)
        if not yesterday_check:
            crud.fail_target(db, t)
            return {"success": False, "message": "Missed yesterday — target failed"}

    # create checkin and update streak; business logic enforced server-side
    crud.create_checkin(db, t, today)
    return {"success": True, "message": "Checked in for today"}


@app.get("/streak/{target_id}")
def get_streak(target_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    t = crud.get_target(db, target_id)
    if not t or t.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Target not found")
    s = crud.get_streak(db, target_id)
    today_done = crud.is_today_checked_in(db, target_id)
    completed_days = crud.get_completed_days_count(db, target_id)
    return {
        "target_id": target_id, 
        "current_streak": s.current_streak if s else 0, 
        "last_completed_date": s.last_completed_date if s else None,
        "today_done": today_done,
        "completed_days": completed_days
    }
