# Mood Productivity — Next.js Frontend

Minimal Next.js frontend for the mood-based productivity FastAPI backend.

## Setup

```bash
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL to your FastAPI backend URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Pages

| Route        | Description                     |
|--------------|---------------------------------|
| `/`          | Redirects to dashboard or login |
| `/login`     | Email + password login          |
| `/signup`    | New account registration        |
| `/dashboard` | Main app (protected)            |

## Project Structure

```
mood-frontend/
├── pages/
│   ├── _app.js          # Global CSS import
│   ├── index.js         # Redirect logic
│   ├── login.js
│   ├── signup.js
│   └── dashboard.js     # Main view
├── components/
│   ├── MoodSelector.js  # LOW / MEDIUM / HIGH pill buttons
│   ├── StreakDisplay.js # Current streak counter
│   ├── TaskItem.js      # Single task row (complete + delete)
│   ├── TaskList.js      # Full task list + add form
│   └── RecommendedTasks.js
├── lib/
│   └── api.js           # All fetch calls to FastAPI
├── styles/
│   └── globals.css      # Single global stylesheet (CSS variables)
├── .env.local.example
└── package.json
```

## Environment Variables

| Variable               | Default                  | Description          |
|------------------------|--------------------------|----------------------|
| `NEXT_PUBLIC_API_URL`  | `http://localhost:8000`  | FastAPI backend URL  |

## Auth

JWT token is stored in `localStorage` under the key `token`.  
Protected pages redirect to `/login` if the token is missing or invalid.
