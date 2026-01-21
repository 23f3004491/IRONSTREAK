# IronStreak

A full-stack discipline tracking app with **strict, irreversible streak rules**.

## Core Features

- **Multiple targets**: Create unlimited fixed-duration goals
- **Daily check-ins**: Mark each day complete (or fail permanently)
- **Strict rules**: Miss any day → target fails immediately
- **Independent streaks**: Each target has its own streak counter
- **Locked targets**: No edits allowed once started
- **2 users only**: Private app for you and one other person

## Tech Stack

**Backend**
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- JWT authentication
- Python 3.9+

**Frontend**
- Next.js 13 (App Router)
- TypeScript
- Tailwind CSS
- React

## Project Structure

```
IRONSTREAK/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app & endpoints
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Business logic
│   │   ├── auth.py          # JWT & password hashing
│   │   ├── deps.py          # Dependencies
│   │   └── database.py      # DB config
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main dashboard
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   └── README.md
└── README.md
```

## Quick Start

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (copy `.env.example` to `.env`):
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/ironstreak
JWT_SECRET=your-secret-key-here
FRONTEND_ORIGIN=http://localhost:3000
USER1_EMAIL=me@example.com
USER1_PASSWORD=password
USER2_EMAIL=brother@example.com
USER2_PASSWORD=password
```

4. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set backend URL (optional, defaults to `http://localhost:8000`):
```bash
# Create .env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Run the frontend:
```bash
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Database Schema

**Users**
- id, email, hashed_password, created_at

**Targets**
- id, user_id, target_text, start_date, end_date, duration_in_days, status (ACTIVE/FAILED/SUCCESS), locked

**DailyCheckin**
- id, target_id, date, completed, completed_at

**Streak**
- target_id, current_streak, last_completed_date

## Authentication

Default credentials (development):
- User 1: `me@example.com` / `password`
- User 2: `brother@example.com` / `password`

Change these in `.env` before deployment!

## API Endpoints

### Auth
- `POST /auth/login` - Get JWT token
- `GET /me` - Get current user

### Targets
- `POST /target/create` - Create new target
- `GET /target/active` - List active targets
- `GET /target/history` - List completed/failed targets

### Check-ins
- `POST /checkin/today?target_id=X` - Mark today complete

### Streaks
- `GET /streak/{target_id}` - Get streak info

## Business Rules (Backend Enforced)

1. **One check-in per day per target** (UTC timezone)
2. **Must check in consecutively**: Missing any day → target fails
3. **Check-in only for today**: Cannot mark past/future dates
4. **Targets are immutable**: Cannot edit after creation
5. **Success = complete all days**: Auto-marked when duration reached
6. **Failed = permanent**: No recovery, must create new target

