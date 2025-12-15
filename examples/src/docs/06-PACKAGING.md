# PACKAGING & DEPLOYMENT: Complete Setup Guide

## PART 1: DOCKER CONFIGURATION

### Step 1.1: Create Dockerfile for Flask Backend

Create `docker/Dockerfile.backend`:

```dockerfile
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "app.py"]
```

### Step 1.2: Create Dockerfile for Frontend (Nginx)

Create `docker/Dockerfile.frontend`:

```dockerfile
# Build stage
FROM node:16-alpine AS builder

WORKDIR /app

# Copy frontend files
COPY frontend/ .

# No build needed for vanilla JavaScript SPA

# Production stage
FROM nginx:alpine

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy frontend files from builder
COPY --from=builder /app /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Step 1.3: Create Nginx Configuration

Create `docker/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;

        # Redirect HTTP to HTTPS in production
        # Uncomment in production with SSL certificate
        # return 301 https://$server_name$request_uri;

        # Cache static files
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 365d;
            add_header Cache-Control "public, immutable";
        }

        # SPA routing - serve index.html for all routes
        location / {
            try_files $uri /index.html;
        }

        # Proxy API requests to Flask backend
        location /api/ {
            proxy_pass http://backend:5000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy";
            add_header Content-Type text/plain;
        }
    }
}
```

### Step 1.4: Create Docker Compose Configuration

Create `docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: dunes-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-dunes_root_pass_123}
      MYSQL_DATABASE: ${DB_NAME:-dunes_cms}
      MYSQL_USER: ${DB_USER:-dunes_user}
      MYSQL_PASSWORD: ${DB_PASSWORD:-dunes_user_pass_123}
    ports:
      - "${DB_PORT:-3306}:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    networks:
      - dunes-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10
      start_period: 40s
    restart: unless-stopped

  # Flask Backend API
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    container_name: dunes-api
    environment:
      FLASK_ENV: ${FLASK_ENV:-production}
      SECRET_KEY: ${SECRET_KEY:-your_secret_key_change_in_production}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-your_jwt_secret_change_in_production}
      DB_HOST: mysql
      DB_USER: ${DB_USER:-dunes_user}
      DB_PASSWORD: ${DB_PASSWORD:-dunes_user_pass_123}
      DB_NAME: ${DB_NAME:-dunes_cms}
      DB_PORT: 3306
    ports:
      - "5000:5000"
    volumes:
      - ../backend:/app
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - dunes-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: unless-stopped

  # Nginx Frontend Server
  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend
    container_name: dunes-web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ../frontend:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - dunes-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/health"]
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

volumes:
  mysql_data:
    driver: local

networks:
  dunes-network:
    driver: bridge
```

### Step 1.5: Create Environment File Template

Create `docker/.env.example`:

```env
# Database Configuration
DB_ROOT_PASSWORD=dunes_root_pass_123
DB_USER=dunes_user
DB_PASSWORD=dunes_user_pass_123
DB_NAME=dunes_cms
DB_PORT=3306

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=change_this_to_a_random_secret_key_in_production
JWT_SECRET_KEY=change_this_to_a_random_jwt_secret_in_production

# Application Settings
LOG_LEVEL=INFO
DEBUG=False
```

---

## PART 2: REQUIREMENTS.TXT FOR PYTHON

Create `backend/requirements.txt`:

```
Flask==2.3.0
Flask-CORS==4.0.0
mysql-connector-python==8.0.33
python-dotenv==1.0.0
bcrypt==4.0.1
PyJWT==2.8.0
requests==2.31.0
python-dateutil==2.8.2
click==8.1.3
Werkzeug==2.3.0
Jinja2==3.1.2
MarkupSafe==2.1.1
itsdangerous==2.1.2
cryptography==40.0.1
```

---

## PART 3: COMPLETE DEPLOYMENT INSTRUCTIONS FOR NON-TECHNICAL STAKEHOLDERS

### Prerequisites

Before deploying the application, ensure you have:

1. **Computer Requirements:**
   - 4GB RAM minimum (8GB recommended)
   - 10GB free disk space
   - Windows 10+, macOS, or Linux

2. **Software Installation:**
   - Docker Desktop (https://www.docker.com/products/docker-desktop)
   - Docker Compose (included with Docker Desktop on Windows and Mac)
   - Git (https://git-scm.com)

### Step 1: Install Docker

**Windows & Mac:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer and follow the prompts
3. Restart your computer
4. Open Terminal (Mac) or PowerShell (Windows)
5. Verify installation: `docker --version`

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

### Step 2: Install Git

**All Platforms:**
1. Visit https://git-scm.com
2. Download and install for your operating system
3. Verify installation: `git --version`
4. Configure Git:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Step 3: Clone the Repository

**In Terminal/PowerShell:**

```bash
# Navigate to desired location
cd ~/dunes-deployment

# Clone the repository
git clone https://github.com/YOUR_ORGANIZATION/dunes-cms.git

# Navigate into project
cd dunes-cms
```

### Step 4: Configure Environment

```bash
# Copy environment template to actual environment file
cp docker/.env.example docker/.env

# Edit docker/.env with your settings
# Important: Change all "your_*" values in production
```

### Step 5: Deploy with Docker Compose

```bash
# Navigate to docker directory
cd docker

# Start all services
docker-compose up -d

# Monitor startup (wait 2-3 minutes for all services to start)
docker-compose logs -f

# Check service status
docker-compose ps
```

Expected output should show all services as "Up":
```
NAME              STATUS              PORTS
dunes-mysql       Up (healthy)        3306/tcp
dunes-api         Up (healthy)        0.0.0.0:5000->5000/tcp
dunes-web         Up (healthy)        0.0.0.0:80->80/tcp
```

### Step 6: Verify Installation

Open your web browser and navigate to:
- **Application:** http://localhost
- **API Health Check:** http://localhost:5000/health

If both pages load successfully, the application is running correctly.

### Step 7: Verify Database

```bash
# Connect to MySQL container
docker exec -it dunes-mysql mysql -uroot -pdunes_root_pass_123

# Inside MySQL shell
USE dunes_cms;
SHOW TABLES;
EXIT;
```

You should see 8 tables (users, athletes, coaches, clubs, games, training, statistics, news).

---

## PART 4: MANAGING THE DEPLOYMENT

### Starting/Stopping the Application

**Start the application:**
```bash
cd docker
docker-compose up -d
```

**Stop the application:**
```bash
cd docker
docker-compose down
```

**Restart the application:**
```bash
cd docker
docker-compose restart
```

**View logs:**
```bash
cd docker
docker-compose logs -f backend     # Flask API logs
docker-compose logs -f frontend    # Nginx logs
docker-compose logs -f mysql       # Database logs
```

### Backing Up Data

**Manual Backup:**
```bash
# Backup database
docker exec dunes-mysql mysqldump -uroot -pdunes_root_pass_123 dunes_cms > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup CSV exports
cp -r data/exports/* backups/
```

**Scheduled Backup (Linux/Mac):**
Add to crontab: `crontab -e`
```
0 2 * * * cd ~/dunes-cms/docker && docker exec dunes-mysql mysqldump -uroot -pdunes_root_pass_123 dunes_cms > ~/backups/backup_$(date +\%Y\%m\%d).sql
```

### Restoring from Backup

```bash
# Restore database
docker exec -i dunes-mysql mysql -uroot -pdunes_root_pass_123 dunes_cms < backup_20240101_020000.sql
```

---

## PART 5: ACCESSING THE APPLICATION

### First-Time Setup

1. Open http://localhost in your browser
2. Click "LOGIN" in the top-right corner
3. Use test credentials (create in database or via API)

### Creating Test Accounts

**Via API:**
```bash
# Create an athlete account
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "athlete1@test.com",
    "password": "TestPass123",
    "first_name": "John",
    "last_name": "Athlete",
    "role": "athlete"
  }'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "athlete1@test.com",
    "password": "TestPass123"
  }'
```

**Via Database:**
```bash
docker exec -it dunes-mysql mysql -uroot -pdunes_root_pass_123 dunes_cms

# Inside MySQL shell
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES
('coach@test.com', '$2b$12$..hash.here..', 'James', 'Coach', 'coach');
```

### User Roles & Access

- **Athlete:** View personal performance, training, games
- **Coach:** Manage assigned athletes, create training sessions
- **Club:** View club roster, game schedules
- **Manager:** Executive dashboard, organization analytics

---

## PART 6: TROUBLESHOOTING

### Application Won't Start

```bash
# Check Docker is running
docker ps

# Check for port conflicts
docker-compose ps

# View error logs
docker-compose logs backend
docker-compose logs mysql
docker-compose logs frontend

# Solution: Ensure ports 80, 3306, 5000 are available
# Kill process using port: lsof -ti:PORT | xargs kill -9
```

### Database Connection Error

```bash
# Check MySQL is running and healthy
docker-compose ps mysql

# Test MySQL connection
docker exec dunes-mysql mysql -uroot -pdunes_root_pass_123 -e "SELECT 1"

# Check MySQL logs
docker-compose logs mysql
```

### Frontend Not Loading

```bash
# Check Nginx is running
docker-compose ps frontend

# Check Nginx logs
docker-compose logs frontend

# Verify API is accessible from frontend container
docker exec dunes-web curl http://backend:5000/health
```

### Port Already in Use

```bash
# Find process using port
lsof -i :80      # Frontend
lsof -i :5000    # API
lsof -i :3306    # Database

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml:
# Change "0.0.0.0:80:80" to "0.0.0.0:8080:80" for example
```

---

## PART 7: PRODUCTION DEPLOYMENT

### Security Hardening

1. **Update All Secrets:**
   - Change `SECRET_KEY` in .env
   - Change `JWT_SECRET_KEY` in .env
   - Change `DB_ROOT_PASSWORD` in .env
   - Change all database passwords

2. **Enable HTTPS:**
   - Obtain SSL certificate (Let's Encrypt recommended)
   - Add certificate to `docker/ssl/` folder
   - Uncomment HTTPS section in `nginx.conf`

3. **Restrict Access:**
   - Configure firewall to allow only necessary ports
   - Set up VPN access for administrative functions
   - Implement rate limiting in nginx

### Scaling to Production

**Hardware Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ (depends on data volume)
- Network: 100Mbps+ connection

**Configuration Changes:**
```env
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
```

**Enable Database Backups:**
- Schedule automated daily backups
- Test restore procedures regularly
- Store backups in separate location

### Cloud Deployment (AWS/Azure/GCP)

All services are containerized and can deploy to:
- **AWS ECS/EKS**
- **Azure Container Instances**
- **Google Cloud Run**
- **DigitalOcean App Platform**

Docker Compose manifests are compatible with Docker Swarm and Kubernetes.

---

## PART 8: MONITORING & MAINTENANCE

### Daily Checks

```bash
# Check system health
docker-compose ps

# Monitor logs
docker-compose logs --tail=50 -f

# Check disk usage
docker system df
```

### Weekly Tasks

- Review application logs for errors
- Test critical workflows
- Verify backups completed successfully
- Check for Docker updates

### Monthly Tasks

- Review user access logs
- Update security settings
- Perform full data backup and restore test
- Review system performance metrics
- Plan capacity expansion if needed

### CSV Data Export

```bash
# Export data (handled by backend)
curl -X GET http://localhost:5000/api/v1/export/csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o dunes_export_$(date +%Y%m%d).csv
```

---

## CONCLUSION

The Dunes Be One Basketball CMS Platform is now deployed and running. All functionality is accessible through the web browser at http://localhost.

For support:
1. Check logs: `docker-compose logs`
2. Review this guide's troubleshooting section
3. Check architecture documentation: `docs/03-ARCHITECTURE.md`
4. For detailed development: `docs/05-DEVELOPMENT.md`

The system is designed for non-technical deployment and can be managed entirely through Docker Compose commands. All data is automatically backed up to CSV files in the `data/exports/` folder for archival and long-term preservation.
