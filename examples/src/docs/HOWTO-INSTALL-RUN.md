# HOWTO: Install, Configure and Run - Dunes Be One Basketball CMS

This HOWTO documents step-by-step instructions to install, configure, and run the Dunes Be One Basketball CMS on a Linux host (tested workflow uses Docker and Docker Compose). Sections cover a quick install path (Docker), an optional local development run (no Docker), database initialization, creating an administrative account, backups, troubleshooting, and production hardening.

**Last updated:** 8 December 2025

---

**Quick summary (3 steps)**

- Clone repository
- Configure `.env` (set secure secrets)
- Run `docker-compose up -d`

Access the app at: http://localhost

API health check: http://localhost:5000/health

---

## Prerequisites

- A Linux machine (instructions include Debian/Ubuntu commands)
- Docker Engine (latest stable) and Docker Compose v1.29+ or Compose V2
- Git
- Ports required open: `80` (frontend), `5000` (backend - used internally by nginx proxy), `3306` (MySQL). If you run behind a firewall, open these ports as required.
- Minimum resources: 4 GB RAM (8 GB recommended), 10 GB disk space

If you prefer to run without Docker (developer workflow), you need Python 3.9+, pip, and MySQL client/server.

---

## 1. Install Docker & Docker Compose (Debian/Ubuntu)

1. Update packages and install prerequisites:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```

2. Add Docker’s official GPG key and repository:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
```

3. Install Docker Engine and Compose plugin:

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

4. Verify Docker is installed and running:

```bash
sudo systemctl enable --now docker
docker --version
docker compose version
```

5. Add your user to the `docker` group (optional, allows running docker without `sudo`):

```bash
sudo usermod -aG docker $USER
# Log out and back in for the group change to apply
```

If you are using a different distribution, follow Docker's official install guide for your OS: https://docs.docker.com/engine/install/

---

## 2. Clone the repository

Choose a directory for the project and clone the repo:

```bash
cd ~/projects
git clone <repository-url> dunes-cms
cd dunes-cms/src
ls -la
```

You should see directories: `backend/`, `frontend/`, `database/`, `docker/`, `docs/`.

---

## 3. Configure environment variables

The application uses an environment file (`.env`) in the `backend/` folder and docker-compose reads environment variables from the `docker/` folder. Copy the example if present and edit values.

Create or edit the `.env` file at `backend/.env` (the repo may include `.env.example`). Example fields:

```text
FLASK_ENV=production
SECRET_KEY=replace-with-secure-random-string
JWT_SECRET_KEY=replace-with-secure-random-string
DB_HOST=dunes-mysql
DB_PORT=3306
DB_NAME=dunes_cms
DB_USER=dunes_user
DB_PASS=ChangeMeStrongPassword
```

Recommended secrets generation (Linux):

```bash
python3 - <<'PY'
import secrets
print('SECRET_KEY=' + secrets.token_urlsafe(48))
print('JWT_SECRET_KEY=' + secrets.token_urlsafe(48))
PY
```

Place these generated values into `backend/.env` (or the docker `environment:` variables in `docker/docker-compose.yml`).

Important security notes:

- Never commit `.env` to source control.
- Use a secrets manager for production (HashiCorp Vault, AWS Secrets Manager, etc.).

---

## 4. Deploy with Docker Compose (recommended)

Change into the `docker/` folder and start services. The `docker-compose.yml` in `docker/` orchestrates MySQL, the Flask backend, and the Nginx frontend.

```bash
cd docker
docker compose up -d --build
```

Wait for containers to start. Check status:

```bash
docker compose ps
docker compose logs -f
```

Important operations:

- To rebuild backend after code changes:

```bash
docker compose up -d --build backend
```

- To stop and remove containers:

```bash
docker compose down
```

If ports are already in use (common on dev hosts), either stop those services or edit `docker/docker-compose.yml` to use alternative ports (remember to update proxy/nginx config if you change ports).

---

## 5. Initialize the database schema and load sample data

The database schema is provided in `database/schema.sql`.

Import schema into the MySQL container (replace `dunes-mysql` with your service name if different):

```bash
# Copy schema to container and import
docker cp ../database/schema.sql dunes-mysql:/tmp/schema.sql
docker exec -i dunes-mysql sh -c 'mysql -u root -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE} < /tmp/schema.sql'
```

Alternatively, run the import through the host MySQL client (if you have MySQL client installed):

```bash
mysql -h 127.0.0.1 -P 3306 -u dunes_user -p dunes_cms < database/schema.sql
```

Verify tables exist by connecting to the MySQL container:

```bash
docker exec -it dunes-mysql mysql -u dunes_user -p dunes_cms
SHOW TABLES;
SELECT COUNT(*) FROM users;
EXIT;
```

If the compose file creates the database and user automatically, the import should succeed. If the DB user lacks permissions, use `root` or grant appropriate privileges first.

---

## 6. Create an administrative (manager) account

Preferred method: use the API register endpoint to create a manager account. Replace values as needed.

```bash
curl -s -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@example.com","password":"StrongPass123!","first_name":"Admin","last_name":"User","role":"manager"}'
```

Expected result: JSON response with success message and (optionally) user data. If registration endpoint is disabled for public use in production, seed the database directly using SQL.

Direct SQL insertion (if required):

1. Generate a bcrypt password hash (on host) using Python:

```bash
python3 - <<'PY'
import bcrypt
pw = b"StrongPass123!"
print(bcrypt.hashpw(pw, bcrypt.gensalt()).decode())
PY
```

2. Insert user into `users` table with role `manager` using the generated password hash:

```sql
INSERT INTO users (email, password_hash, first_name, last_name, role) 
VALUES ('manager@example.com','<bcrypt-hash>','Admin','User','manager');
```

Perform the SQL via `docker exec -it dunes-mysql mysql ...` or any MySQL client with privileges.

---

## 7. Verify the application

- Frontend: open `http://localhost` in your browser; log in with the manager credentials or one of the sample test users.
- Backend health: `curl http://localhost:5000/health` should return HTTP 200 with JSON status.
- API endpoints: try `GET http://localhost:5000/api/v1/` to list API version root.

Check logs if something fails:

```bash
docker compose logs backend --tail 200
docker compose logs dunes-mysql --tail 200
docker compose logs nginx --tail 200
```

Common issues:

- `Error: Access denied` -> verify DB credentials in `backend/.env` and `docker-compose.yml`.
- `Port already in use` -> identify conflicting service (`lsof -i :80`) and stop it, or change mapping in compose.
- `Backend not reachable` -> check CORS, network in compose, or Nginx config.

---

## 8. Backups and restores

Backup the MySQL database with `mysqldump`:

```bash
docker exec dunes-mysql sh -c 'exec mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}' > dunes_cms_backup.sql
```

Restore from a backup file:

```bash
cat dunes_cms_backup.sql | docker exec -i dunes-mysql sh -c 'mysql -u root -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}'
```

Set up automated backups using a cron job or dedicated backup container that runs `mysqldump` daily and pushes the file to remote storage (S3, SCP, etc.).

---

## 9. Run the app locally without Docker (developer mode)

This is useful for debugging and active development.

1. Create Python virtual environment and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure `backend/.env` with local DB settings (or run a local MySQL instance).

3. Run Flask app (development server):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

4. Serve frontend locally (simple Python HTTP server from `frontend/`):

```bash
cd ../frontend
python3 -m http.server 8000
# Open http://localhost:8000
```

Note: In local dev mode you need to set up CORS or point the frontend to the backend base URL.

---

## 10. Troubleshooting guide (common problems)

- Docker compose hangs on startup:
  - Run `docker compose logs` to see failing service.
  - If MySQL is initializing, it may take a while to be ready; watch logs for `ready for connections`.

- `ERROR 1045 (28000): Access denied for user`:
  - Confirm `DB_USER` and `DB_PASS` values and that user exists with correct privileges.

- Backend returns 500 on requests:
  - Check backend logs (`docker compose logs backend`) for Python exception traceback.

- Assets 404 on frontend:
  - Confirm `nginx` container mapping points to correct `frontend` build directory. Rebuild frontend Dockerfile if necessary.

- Cannot register a new user (endpoint rejects):
  - Validate JSON payload and required fields. Check backend logs for validation errors.

If stuck, capture logs and share them (or attach them to an issue) with timestamps and container names.

---

## 11. Production hardening and recommendations

- Use HTTPS (TLS) in production. Obtain certificates from Let's Encrypt and configure Nginx with the certs. Example: use Certbot on the host.
- Replace all default or weak passwords with secure random values and rotate JWT secrets periodically.
- Do not expose the MySQL admin port to the public internet; keep it on an internal network or use VPC.
- Use a managed MySQL service if available for production (RDS, Cloud SQL) and update `DB_HOST` accordingly.
- Use a secrets manager for `SECRET_KEY`, `JWT_SECRET_KEY`, and DB credentials.
- Add monitoring and alerting: Prometheus + Grafana or Datadog; monitor container health, CPU, memory, and DB replication lag.
- Configure log aggregation (ELK/EFK) or use a cloud logging service.
- Use automatic backups with point-in-time recovery and test restores regularly.

Scaling notes:

- Backend: run multiple backend replicas behind a load balancer (nginx or cloud LB).
- Database: scale vertically, or set up read replicas and a managed primary for write-heavy workloads.

CI/CD suggestions:

- Use GitHub Actions / GitLab CI to build and push images to a container registry (Docker Hub, ECR, GCR).
- Run automated tests during CI: linting, unit tests, integration tests against a test DB.
- Deploy via a controlled pipeline (staging -> production) and use rolling deployments.

---

## 12. Useful commands (summary)

```bash
# Start services
cd docker
docker compose up -d --build

# Show logs
docker compose logs -f

# Connect to backend container
docker compose exec backend /bin/sh

# Enter MySQL container
docker exec -it dunes-mysql mysql -u dunes_user -p dunes_cms

# Backup DB
docker exec dunes-mysql sh -c 'exec mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}' > dunes_cms_backup.sql

# Restore DB
cat dunes_cms_backup.sql | docker exec -i dunes-mysql sh -c 'mysql -u root -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}'
```

---

## 13. Next steps & optional enhancements

- Configure HTTPS with Let's Encrypt and automate renewal
- Add automated scheduled DB backups to remote storage
- Add a Runbook for common operational tasks and on-call procedures
- Build additional health endpoints and readiness/liveness probes

---

If you want, I can:

- Run `docker compose up -d` in your environment (I can show commands for you to paste).
- Generate a secure `.env` with strong secrets and optionally write it to `backend/.env` (you must confirm before I write secrets into your workspace).
- Create a small helper script to create an admin user using the app API.

Tell me which of the optional actions you'd like me to do next.
