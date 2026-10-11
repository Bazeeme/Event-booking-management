# Event Ticket Management Platform

Stack: React + Vite, Python Flask REST API, PostgreSQL, Docker Compose, Jenkins, Recharts.

## Project structure
```text
event-ticket-platform/
├── backend/ (Flask API, JWT auth, PostgreSQL access, Dockerfile)
├── frontend/ (React UI, event list, booking form, admin charts, Dockerfile)
├── db/init.sql (tables + four sample events)
├── docker-compose.yml
├── Jenkinsfile
├── .env.example
└── .gitignore
```

## Step 1 — prerequisites
Install Docker Desktop on Windows and start it. Install Git if you want to push the project to GitHub.

## Step 2 — environment
Copy `.env.example` to `.env`. On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```
The requested database name/password are `eventbooking` / `basi1516`. The compose file creates a database user called `eventapp`. The admin login is `admin@gmail.com` / `admin123` for local development. Change both passwords and the JWT secret before putting this online. Never commit `.env`.

## Step 3 — start the project
Open a terminal in the project root:
```bash
docker compose up --build -d
docker compose ps
```
Open http://localhost:5173. Backend health check: http://localhost:5000/api/health.

## Connect pgAdmin to the project database
The Compose PostgreSQL database is separate from any PostgreSQL server already installed on Windows. It is published on `127.0.0.1:5433` so pgAdmin can connect without replacing or conflicting with a local server on port `5432`. After changing `docker-compose.yml`, apply the port mapping from the project root:
```powershell
docker compose up -d
```
In pgAdmin, register a server and use these **Connection** settings:

| Setting | Value |
| --- | --- |
| Host name/address | `127.0.0.1` |
| Port | `5433` |
| Maintenance database | `eventbooking` |
| Username | `eventapp` |
| Password | `basi1516` |

These are the defaults when no `.env` overrides are set. In pgAdmin, open **Databases → eventbooking → Schemas → public → Tables → bookings**, then use **View/Edit Data → All Rows**. Booking submissions are committed to this database. If the project’s PostgreSQL credentials were changed in `.env`, use those values instead.

## Step 4 — test
1. Register a normal user using a name, email and password (at least 8 characters).
2. Log in using the same email and password.
3. Choose one of the four events and enter attendee name, age, email, phone and slot.
4. Submit and open **My tickets**. The booking is stored in PostgreSQL.
5. Log out and log in as `admin@gmail.com` with `admin123`. The admin dashboard shows booking totals, a bar chart by event, a pie chart by slot, and all booking records.

## Step 5 — useful Docker commands
```bash
docker compose logs -f backend
docker compose logs -f db
docker compose down
```
To delete the database volume and all saved users/bookings (destructive):
```bash
docker compose down -v
```
The SQL init script runs only when the PostgreSQL data volume is first created. If you edit `db/init.sql` after the database has already initialized, use a migration or recreate the volume (which deletes its data).

## Step 6 — Jenkins
The `Jenkinsfile` checks required files, builds Docker images, and runs `docker compose up -d` on branch `main`. Configure a Jenkins Pipeline job connected to this Git repository. The Jenkins agent needs Docker CLI, the Docker Compose plugin, and permission to access the Docker daemon. Do not expose the Docker daemon to untrusted jobs. Set production secrets in Jenkins credentials/environment rather than source control.

## API overview
- `POST /api/register`
- `POST /api/login`
- `GET /api/events`
- `POST /api/bookings` (login required)
- `GET /api/my-bookings` (login required)
- `GET /api/admin/bookings` (admin only)
- `GET /api/admin/stats` (admin only)

## Deployment notes
This is a portfolio/learning starter, not production-hardened software. For a public deployment, use HTTPS, a strong unique admin password and JWT secret, restricted database networking, backups, rate limiting, and proper monitoring. `basi1516` is kept as the requested local database password; do not reuse it for a public service.
