# Sprint 1 — Auth & Profile (Web Video Finder)

This is the **Sprint 1 subset** of the full project scaffold, containing only
the files needed for these three tickets:

- **[S1][FE/BE] User Registration & Login Interface (5 SP)**
- **[S1][BE] Account Authentication using JWT/Session (3 SP)**
- **[S1][FE/BE] User Profile Management Page (3 SP)**

Backend: Python/Flask on EC2. Database: DynamoDB (`Users` table only, for now).
Frontend: HTML/CSS/vanilla JS.

## What's in here

```
backend/
  app.py               Flask app factory — registers ONLY auth + profile blueprints
  wsgi.py              Gunicorn entry point
  config.py            Env-driven config (JWT secret, table names, etc.)
  extensions.py        Shared boto3 DynamoDB resource
  requirements.txt
  models/user.py       DynamoDB reads/writes for the Users table
  routes/auth.py        /api/auth/register, /api/auth/login
  routes/profile.py     /api/profile/me (GET/PUT), /api/profile/me/password (PUT)
  utils/auth_helpers.py JWT issuing + require_auth / optional_auth decorators
  utils/validators.py   Email format + password strength checks
  utils/ids.py          UUID helper

frontend/
  index.html            Placeholder homepage (video grid comes in a later sprint)
  login.html / js/login.js     Login + Register forms
  profile.html / js/profile.js Edit nickname/avatar, change password
  js/api.js              Fetch wrapper + token storage (only auth/profile calls)
  js/auth.js              Shared header nav (shows login link or logged-in user)
  css/style.css

infra/dynamodb/create_users_table.py   Creates just the Users table
```

## Running it locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env    # fill in JWT_SECRET at minimum

# create the Users table (needs AWS credentials configured, e.g. `aws configure`)
cd ../infra/dynamodb
python3 create_users_table.py --region us-east-1 --prefix dev_

cd ../../backend
flask --app app run --debug     # http://localhost:5000
```

```bash
cd frontend
python3 -m http.server 8080     # http://localhost:8080
```

Open `http://localhost:8080/login.html`, register an account, and you'll be
redirected to the profile page.

## Endpoints in this subset

| Method | Path                    | Auth | Body |
|--------|--------------------------|------|------|
| POST   | `/api/auth/register`     | —    | `{email, password, nickname}` |
| POST   | `/api/auth/login`        | —    | `{email, password}` |
| GET    | `/api/profile/me`        | 🔒   | — |
| PUT    | `/api/profile/me`        | 🔒   | `{nickname?, avatar_url?}` |
| PUT    | `/api/profile/me/password` | 🔒 | `{old_password, new_password}` |

## Note

This subset is intentionally scoped to Sprint 1 — it will NOT run the full
video catalog (that needs the `Videos`, `Ratings`, `Comments`, `Favorites`,
`History`, and `Reports` modules from later sprints). See
`docs/Sprint1_Presentation_Script.md` for the walkthrough script used to
present this sprint.
