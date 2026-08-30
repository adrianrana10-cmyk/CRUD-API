# Task API

A small CRUD API for managing a to-do list, built with FastAPI. Data is stored in memory (resets on restart).

## How to run

```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload --port 8000
```

Server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path            | Description              |
|--------|-----------------|---------------------------|
| GET    | /               | API info                  |
| GET    | /health         | Health check               |
| GET    | /tasks          | List all tasks             |
| GET    | /tasks/{id}     | Get a single task          |
| POST   | /tasks          | Create a task              |
| PUT    | /tasks/{id}     | Update a task              |
| DELETE | /tasks/{id}     | Delete a task               |

## Example request

```
HTTP/1.1 201 Created
date: Fri, 28 Aug 2026 11:01:56 GMT
server: uvicorn
content-length: 40
content-type: application/json
{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

![Swagger screenshot](swagger-screenshot.png)

## Database

This project uses SQLite (`tasks.db`) for storage instead of an in-memory list.

**Why SQLite:** zero setup (no server to install or run), the whole database is a single file, and data survives restarts — ideal for a small project like this.

**Database file:** `tasks.db` is created automatically on first run and is git-ignored, so each fresh clone starts with a clean seeded database.

**Run the project:**
\`\`\`bash
uvicorn main:app --reload --port 8000
\`\`\`

**Sample SQL query (run in DB Browser, Stage 4):**
\`\`\`sql
DELETE FROM tasks WHERE done = 1;
\`\`\`
After marking all tasks done, this deleted all 5 rows, leaving the table empty — confirmed the API reflected the change instantly with no restart needed.

![tasks table in DB Browser](db-screenshot.png)


---

## Update: Containerized Postgres (Week 3)

Storage moved again: in-memory → SQLite → **Postgres, running in Docker**. The API endpoints above are unchanged — only the storage underneath.

### Run everything with one command

```bash
git clone <your-repo-url>
cd todo-api
cp .env.example .env
docker compose up
```

Server runs at `http://localhost:8000` as before.

### Environment variables

Copy `.env.example` to `.env` before running:

| Variable       | Purpose                                  |
|----------------|-------------------------------------------|
| `DATABASE_URL` | Postgres connection string for the app     |

### Architecture

`compose.yaml` defines two services:
- **api** — the FastAPI app, built from the local `Dockerfile`
- **db** — official `postgres:16` image, with a named volume (`taskdata`) so rows survive container restarts

`api` waits for `db`'s healthcheck (`pg_isready`) to pass before starting, avoiding a race condition where the app connects before Postgres finishes initializing.

### Data in Postgres

![Postgres tasks table](postgres-screenshot.png)

### Persistence proof

```bash
docker compose down
docker compose up
curl http://localhost:8000/tasks
```

Tasks created before `down` are still present after `up` — the named volume keeps Postgres's data outside the container lifecycle.

# Task API

A CRUD REST API for managing tasks, built with FastAPI. Originally built with SQLite (Week 2–3), now running on PostgreSQL with Supabase Auth for identity (Week 4).

## Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (via `psycopg`), containerized with Docker
- **Auth:** Supabase (email/password, JWT-based)
- **Docs:** Auto-generated Swagger UI at `/docs`

## Setup

1. Clone the repo:
```powershell
   git clone https://github.com/adrianrana10-cmyk/CRUD-API.git
   cd CRUD-API
```

2. Create a virtual environment and activate it:
```powershell
   python -m venv venv
   venv\Scripts\activate
```

3. Install dependencies:
```powershell
   pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key


5. Start Postgres via Docker (leave the `api` service stopped if running locally):
```powershell
   docker compose up -d db
```

6. Run the server:
```powershell
   uvicorn main:app --reload
```

7. Open `http://localhost:8000/docs` for interactive API docs.

## Auth flow

1. `POST /auth/signup` — create an account (email + password)
2. `POST /auth/login` — returns an `access_token`
3. Click **Authorize** in `/docs` and paste the token to unlock protected routes
4. `POST /auth/logout` — invalidates the session

## Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| GET | `/` | No | API info |
| GET | `/health` | No | Health check |
| GET | `/public/info` | No | Public demo route |
| POST | `/auth/signup` | No | Create account |
| POST | `/auth/login` | No | Log in, get access token |
| POST | `/auth/logout` | Yes | Invalidate session |
| GET | `/protected/profile` | Yes | Get current user info |
| GET | `/protected/dashboard` | Yes | Demo protected route |
| GET | `/tasks` | No | List all tasks |
| POST | `/tasks` | No | Create a task |
| GET | `/tasks/{id}` | No | Get one task |
| PUT | `/tasks/{id}` | No | Update a task |
| DELETE | `/tasks/{id}` | No | Delete a task |

> Note: task endpoints aren't guarded yet — auth currently covers identity only. Per-user data ownership (tenant isolation) is planned for the following week.

## Screenshot

![Swagger docs with Authorize padlock](docs-swagger-screenshot.png)