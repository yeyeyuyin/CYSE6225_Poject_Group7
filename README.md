# Web Video Finder Platform

CYSE6225 Final Project — a video discovery platform. The platform does **not**
host any video files; it indexes public external links (YouTube, Vimeo, etc.)
and lets users search, filter, sort, rate, comment on, and bookmark titles.

## Tech Stack

| Layer      | Technology                                            |
|------------|--------------------------------------------------------|
| Frontend   | HTML / CSS / vanilla JavaScript                        |
| Backend    | Python (Flask) running on an AWS **EC2** instance       |
| Database   | Amazon **DynamoDB** (NoSQL)                             |
| Web server | Gunicorn (WSGI) behind **Nginx** as a reverse proxy      |
| Auth       | JWT (stateless, `Authorization: Bearer <token>`)         |

## Architecture (EC2-based deployment)

```
 Browser (CYSE6225-Final-Project/frontend/) ──HTTPS──▶ Nginx (EC2, port 443/80)
                                   │  reverse proxy
                                   ▼
                              Gunicorn ──▶ Flask app (CYSE6225-Final-Project/backend/)
                                   │
                                   ▼
                              boto3 ──▶ Amazon DynamoDB
```

* Frontend static files can be served directly by Nginx from the same EC2
  instance, or hosted separately on S3 + CloudFront — either works with this
  scaffold, since `CYSE6225-Final-Project/frontend/js/api.js` only needs
  `API_BASE_URL` pointed at wherever the Flask API lives.
* The Flask app talks to DynamoDB using `boto3`. On EC2, give the instance an
  **IAM role** with DynamoDB read/write permissions instead of hardcoding
  AWS keys.

## Repository Layout

```
requirements.txt                  Python dependencies shared by local/dev deploys
CYSE6225-Final-Project/
  backend/                        Flask API (blueprints per feature, DynamoDB models)
  frontend/                       Static HTML/CSS/JS client
  infra/dynamodb/                 Script to create all DynamoDB tables
  infra/ec2/                      EC2 bootstrap script, systemd unit, Nginx config
  docs/                           Architecture / API notes
```

## Getting Started (local development)

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd CYSE6225-Final-Project/backend
cp .env.example .env            # fill in values (see below)
flask --app app run --debug     # http://localhost:5001
```

### 2. Create the DynamoDB tables

Requires AWS credentials configured locally (`aws configure`) with permission
to create DynamoDB tables, or run against a local DynamoDB (see
`CYSE6225-Final-Project/infra/dynamodb/create_tables.py` --endpoint flag).

```bash
cd CYSE6225-Final-Project/infra/dynamodb
python3 create_tables.py --region us-east-1
```

### 3. Frontend

The frontend is static — no build step. Just point it at your backend:

```bash
# edit CYSE6225-Final-Project/frontend/js/api.js -> API_BASE_URL
cd CYSE6225-Final-Project/frontend
python3 -m http.server 8080     # http://localhost:8080
```

## Environment Variables

See `CYSE6225-Final-Project/backend/.env.example`. Key variables:

| Variable         | Description                                   |
|------------------|------------------------------------------------|
| `AWS_REGION`      | Region your DynamoDB tables live in            |
| `JWT_SECRET`      | Secret used to sign JWTs                       |
| `TABLE_PREFIX`    | Prefix for all DynamoDB table names (e.g. dev_)|
| `FLASK_ENV`       | `development` or `production`                  |

## Deploying to EC2 (outline)

1. Launch an EC2 instance (Amazon Linux 2023 or Ubuntu 22.04), attach an IAM
   role with DynamoDB access.
2. SSH in, clone this repo to `/opt/webvideofinder`, then run
   `/opt/webvideofinder/CYSE6225-Final-Project/infra/ec2/setup.sh` (installs
   Python, creates venv, installs deps from the root `requirements.txt`,
   installs Nginx, registers the systemd service).
3. Copy `CYSE6225-Final-Project/infra/ec2/webvideofinder.service` to
   `/etc/systemd/system/` and `CYSE6225-Final-Project/infra/ec2/nginx.conf` to
   `/etc/nginx/sites-available/`, then
   `systemctl enable --now webvideofinder`.
4. Open ports 80/443 (and optionally restrict 22 to your IP) in the
   instance's Security Group.

Full step-by-step notes: `CYSE6225-Final-Project/infra/ec2/README.md`.

## Feature Map (matches the project spec / sprint tickets)

| Module              | Backend blueprint          | Frontend page/JS         |
|----------------------|-----------------------------|---------------------------|
| Auth & Registration  | `routes/auth.py`            | `login.html`, `js/auth.js`|
| Profile Management    | `routes/profile.py`         | `profile.html`, `js/profile.js`|
| Video Listing/Search/Filter/Sort | `routes/videos.py`, `routes/search.py` | `index.html`, `js/videos.js` |
| Video Detail & Playback | `routes/videos.py`        | `detail.html`, `js/detail.js`|
| Ratings (0–5)         | `routes/ratings.py`         | `js/detail.js`            |
| Click Tracking        | `routes/videos.py`          | `js/detail.js`            |
| Comments              | `routes/comments.py`        | `js/detail.js`            |
| Favorites/Watchlist   | `routes/favorites.py`       | `profile.html`, `js/profile.js`|
| Watch History         | `routes/history.py`         | `profile.html`, `js/profile.js`|
| Broken Link Reporting | `routes/reports.py`         | `js/detail.js`            |

## Team Workflow Notes

This is a scaffold, not a finished app — routes mostly implement the
happy-path CRUD described in the spec so the team has a consistent starting
point. Things intentionally left for the team to fill in / harden:

- Input validation edge cases beyond the basics already in `utils/validators.py`
- Pagination on list endpoints (currently returns full scan results — fine
  for a class project's dataset size, but note it in your write-up)
- Password reset flow
- Rate limiting / abuse protection on ratings & reports
- HTTPS/TLS setup on the EC2 Nginx config (currently HTTP only — add
  Let's Encrypt / ACM as a stretch goal)
