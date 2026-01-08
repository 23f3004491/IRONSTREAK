# IronStreak Backend

This is a FastAPI backend for the IronStreak app.

## Setup (local)

1. Create a Python virtualenv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\Activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. Configure environment variables (see `.env.example`).

3. Run the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- The app seeds two users on first startup using `USER1_*` and `USER2_*` env vars.
- Business rules (streaks, failures) are enforced server-side in `/checkin/today`.
