from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from . import models, auth


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str):
    hashed = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_target(db: Session, user_id: int, target_text: str, start_date: date, duration_in_days: int):
    end_date = start_date + timedelta(days=duration_in_days - 1)
    target = models.Target(
        user_id=user_id,
        target_text=target_text,
        start_date=start_date,
        end_date=end_date,
        duration_in_days=duration_in_days,
        status=models.TargetStatus.ACTIVE,
        locked=True,
    )
    db.add(target)
    db.commit()
    db.refresh(target)

    # initialize streak row
    streak = models.Streak(target_id=target.id, current_streak=0, last_completed_date=None)
    db.add(streak)
    db.commit()
    return target


def get_active_targets(db: Session, user_id: int):
    return db.query(models.Target).filter(models.Target.user_id == user_id, models.Target.status == models.TargetStatus.ACTIVE).all()


def get_target_history(db: Session, user_id: int):
    return db.query(models.Target).filter(models.Target.user_id == user_id, models.Target.status != models.TargetStatus.ACTIVE).order_by(models.Target.created_at.desc()).all()


def get_target(db: Session, target_id: int):
    return db.query(models.Target).filter(models.Target.id == target_id).first()


def get_checkin_for_date(db: Session, target_id: int, d: date):
    return db.query(models.DailyCheckin).filter(models.DailyCheckin.target_id == target_id, models.DailyCheckin.date == d).first()


def create_checkin(db: Session, target: models.Target, d: date):
    checkin = models.DailyCheckin(target_id=target.id, date=d, completed=True)
    db.add(checkin)
    # update streak
    streak = db.query(models.Streak).filter(models.Streak.target_id == target.id).first()
    yesterday = d - timedelta(days=1)
    if streak and streak.last_completed_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.last_completed_date = d
    db.add(streak)

    # Check for success
    total_completed = db.query(models.DailyCheckin).filter(models.DailyCheckin.target_id == target.id).count() + 1
    if total_completed >= target.duration_in_days:
        target.status = models.TargetStatus.SUCCESS

    db.commit()
    return checkin


def fail_target(db: Session, target: models.Target):
    target.status = models.TargetStatus.FAILED
    # reset streak
    streak = db.query(models.Streak).filter(models.Streak.target_id == target.id).first()
    if streak:
        streak.current_streak = 0
        streak.last_completed_date = None
        db.add(streak)
    db.add(target)
    db.commit()
    return target


def get_streak(db: Session, target_id: int):
    return db.query(models.Streak).filter(models.Streak.target_id == target_id).first()


def check_and_fail_missed_targets(db: Session, user_id: int):
    """Check all active targets and fail any that have missed days."""
    today = datetime.utcnow().date()
    active_targets = db.query(models.Target).filter(
        models.Target.user_id == user_id,
        models.Target.status == models.TargetStatus.ACTIVE
    ).all()
    
    for target in active_targets:
        # Skip if target hasn't started yet
        if today < target.start_date:
            continue
        
        # Check each day from start_date to yesterday
        check_until = min(today - timedelta(days=1), target.end_date)
        current_date = target.start_date
        
        while current_date <= check_until:
            checkin = get_checkin_for_date(db, target.id, current_date)
            if not checkin:
                # Missed a day - fail the target
                fail_target(db, target)
                break
            current_date += timedelta(days=1)


def is_today_checked_in(db: Session, target_id: int) -> bool:
    """Check if today has already been checked in for a target."""
    today = datetime.utcnow().date()
    checkin = get_checkin_for_date(db, target_id, today)
    return checkin is not None


def get_completed_days_count(db: Session, target_id: int) -> int:
    """Get count of completed check-ins for a target."""
    return db.query(models.DailyCheckin).filter(models.DailyCheckin.target_id == target_id).count()
