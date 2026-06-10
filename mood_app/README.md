# Mood-Based Productivity API

A FastAPI backend for tracking mood, managing tasks by difficulty, and maintaining productivity streaks.

---

## Tech Stack
- **FastAPI** — web framework
- **PostgreSQL** (Supabase-compatible) — database
- **SQLAlchemy** — ORM
- **JWT (python-jose)** — authentication
- **bcrypt (passlib)** — password hashing

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY
```

### 3. Run the server
```bash
uvicorn main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## Project Structure
```
mood_app/
├── main.py              # App entry point, middleware, router registration
├── config.py            # Env vars
├── database.py          # SQLAlchemy engine + session + Base
├── schemas.py           # Pydantic request/response models
├── models/
│   ├── user.py          # User table
│   ├── mood.py          # Mood table + MoodLevel enum
│   ├── task.py          # Task + TaskLog tables + Difficulty enum
│   └── streak.py        # Streak table
├── services/
│   ├── auth.py          # JWT + password hashing + get_current_user dep
│   └── streak.py        # Streak update logic
├── routes/
│   ├── auth.py          # POST /signup, POST /login
│   ├── mood.py          # POST /mood, GET /mood/today
│   ├── tasks.py         # CRUD /tasks + /tasks/{id}/complete + /tasks/recommend
│   └── streak.py        # GET /streak
├── .env.example
└── requirements.txt
```

---

## API Reference

### Auth
| Method | Route     | Auth | Description        |
|--------|-----------|------|--------------------|
| POST   | /signup   | No   | Register new user  |
| POST   | /login    | No   | Login, get JWT     |

### Mood
| Method | Route        | Auth | Description              |
|--------|--------------|------|--------------------------|
| POST   | /mood        | Yes  | Log mood for today       |
| GET    | /mood/today  | Yes  | Get today's latest mood  |

### Tasks
| Method | Route                    | Auth | Description                  |
|--------|--------------------------|------|------------------------------|
| POST   | /tasks                   | Yes  | Create a task                |
| GET    | /tasks                   | Yes  | List all tasks               |
| GET    | /tasks/{id}              | Yes  | Get a single task            |
| PATCH  | /tasks/{id}              | Yes  | Update task title/difficulty |
| DELETE | /tasks/{id}              | Yes  | Delete a task                |
| POST   | /tasks/{id}/complete     | Yes  | Mark task complete           |
| GET    | /tasks/recommend         | Yes  | Get mood-based suggestions   |

### Streak
| Method | Route    | Auth | Description             |
|--------|----------|------|-------------------------|
|  GET   | /streak  | Yes  | Get current streak info |

---

## Recommendation Logic

| Today's Mood | Recommended Difficulty         |
|--------------|-------------------------------|
| LOW          | EASY tasks (or fallback tips) |
| MEDIUM       | MEDIUM tasks                  |
| HIGH         | HARD → MEDIUM tasks           |

- If no mood is logged today, EASY tasks are returned.
- If no matching user tasks exist, 3 built-in fallback wellness tasks are returned.

---

## Streak Logic
- Completing any task updates your streak.
- Completing on consecutive days increments the streak.
- Missing a day resets the streak to 1.

---

## Supabase / Hosted PostgreSQL
Set `DATABASE_URL` to your Supabase connection string:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```
Tables are auto-created on first run via `Base.metadata.create_all()`.
