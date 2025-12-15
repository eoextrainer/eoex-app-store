# DEVELOPMENT: Step-by-Step Implementation Guide

## PART 1: ENVIRONMENT SETUP & DEPENDENCIES

### Step 1.1: System Requirements

Ensure your development machine has:
- Python 3.9 or higher
- Git 2.30 or higher
- Docker & Docker Compose
- Node.js 16+ (optional, for frontend build tools)
- MySQL 8.0 (can use Docker)
- A text editor or IDE (VS Code recommended)

### Step 1.2: Install Python Dependencies

Create a virtual environment and install all required packages:

```bash
# Create project directory
mkdir -p ~/dunes-cms
cd ~/dunes-cms

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install --upgrade pip
pip install Flask==2.3.0
pip install Flask-CORS==4.0.0
pip install mysql-connector-python==8.0.33
pip install python-dotenv==1.0.0
pip install bcrypt==4.0.1
pip install PyJWT==2.8.0
pip install requests==2.31.0
pip install python-dateutil==2.8.2
pip install click==8.1.3

# Create requirements.txt for future deployments
pip freeze > requirements.txt
```

### Step 1.3: Verify Python Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Verify key packages
python -c "import flask; import mysql.connector; import bcrypt; print('All dependencies installed successfully')"
```

### Step 1.4: Git Configuration

```bash
# Configure Git user
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --global --list
```

---

## PART 2: GIT REPOSITORY SETUP & BRANCHING STRATEGY

### Step 2.1: Initialize Git Repository

```bash
cd ~/dunes-cms

# Initialize local repository
git init

# Create initial commit
git add .gitignore
git commit -m "init: Initial project setup with gitignore"

# Verify initial commit
git log --oneline
```

### Step 2.2: Create Local Branch Structure

```bash
# Create and switch to main branch (new standard instead of master)
git checkout -b main

# Create develop branch
git checkout -b develop

# Create supporting branches
git checkout -b feature/skeleton  # Temporary for initial setup
git checkout -b test
git checkout -b ready
git checkout -b archive

# Return to main for tracking
git checkout main

# Verify branches exist
git branch -a
```

### Step 2.3: Set Up Remote Repository

On GitHub/GitLab, create a new repository named "dunes-cms" (do NOT initialize with README)

```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/dunes-cms.git

# Create remote branches (follow from local)
git push -u origin main
git push -u origin develop
git push -u origin feature/skeleton
git push -u origin test
git push -u origin ready
git push -u origin archive

# Set main as default branch on GitHub (in Settings)

# Create remote integration (int) branch
git checkout -b int
git push -u origin int
```

### Step 2.4: Branching Strategy Reference

**Local Branches:**
- `main` - Stable production code, synced with remote `main`
- `develop` - Development integration, synced with remote `develop`
- `feature/*` - Feature branches, temporary
- `test` - Testing branch
- `ready` - Ready for production
- `archive` - Historical versions

**Remote Branches:**
- `main` - Production releases
- `prod` - Production deployment
- `qa` - Quality assurance testing
- `int` - Integration testing (synced with local `ready`)

---

## PART 3: DATABASE SETUP

### Step 3.1: MySQL Installation & Setup

Using Docker for consistency:

```bash
# Pull MySQL image
docker pull mysql:8.0

# Create MySQL container for development
docker run --name dunes-mysql \
  -e MYSQL_ROOT_PASSWORD=dunes_root_pass_123 \
  -e MYSQL_DATABASE=dunes_cms \
  -e MYSQL_USER=dunes_user \
  -e MYSQL_PASSWORD=dunes_user_pass_123 \
  -p 3306:3306 \
  -v dunes_data:/var/lib/mysql \
  -d mysql:8.0

# Verify MySQL is running
docker ps | grep dunes-mysql
```

### Step 3.2: Create Database Schema

Create `database/schema.sql`:

```sql
-- Dunes Be One Basketball CMS - Database Schema

CREATE DATABASE IF NOT EXISTS dunes_cms;
USE dunes_cms;

-- USERS Table
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  role ENUM('athlete', 'coach', 'club', 'manager') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ATHLETES Table
CREATE TABLE athletes (
  athlete_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  position VARCHAR(50),
  height DECIMAL(3,2),
  weight INT,
  birthdate DATE,
  jersey_number INT,
  club_id INT,
  bio TEXT,
  medical_notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_club_id (club_id),
  INDEX idx_position (position)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- COACHES Table
CREATE TABLE coaches (
  coach_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  specialization VARCHAR(100),
  certification_level VARCHAR(50),
  years_experience INT,
  club_id INT,
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  INDEX idx_club_id (club_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CLUBS Table
CREATE TABLE clubs (
  club_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  location VARCHAR(200),
  founded_year YEAR,
  contact_email VARCHAR(255),
  contact_phone VARCHAR(20),
  website VARCHAR(255),
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- GAMES Table
CREATE TABLE games (
  game_id INT AUTO_INCREMENT PRIMARY KEY,
  home_club_id INT,
  away_club_id INT,
  game_date DATETIME NOT NULL,
  location VARCHAR(255),
  status ENUM('scheduled', 'ongoing', 'completed', 'cancelled') DEFAULT 'scheduled',
  home_team_score INT,
  away_team_score INT,
  tournament_name VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (home_club_id) REFERENCES clubs(club_id),
  FOREIGN KEY (away_club_id) REFERENCES clubs(club_id),
  INDEX idx_game_date (game_date),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TRAINING Table
CREATE TABLE training (
  training_id INT AUTO_INCREMENT PRIMARY KEY,
  athlete_id INT NOT NULL,
  coach_id INT,
  training_date DATE NOT NULL,
  session_time TIME,
  duration_minutes INT,
  training_type VARCHAR(100),
  focus_area VARCHAR(100),
  intensity_level ENUM('low', 'medium', 'high'),
  attendance BOOLEAN DEFAULT TRUE,
  notes TEXT,
  performance_rating INT CHECK (performance_rating >= 1 AND performance_rating <= 10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
  FOREIGN KEY (coach_id) REFERENCES coaches(coach_id),
  INDEX idx_athlete_id (athlete_id),
  INDEX idx_training_date (training_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- STATISTICS Table
CREATE TABLE statistics (
  statistic_id INT AUTO_INCREMENT PRIMARY KEY,
  athlete_id INT NOT NULL,
  game_id INT NOT NULL,
  points INT DEFAULT 0,
  rebounds INT DEFAULT 0,
  assists INT DEFAULT 0,
  steals INT DEFAULT 0,
  blocks INT DEFAULT 0,
  turnovers INT DEFAULT 0,
  fouls INT DEFAULT 0,
  field_goals_made INT DEFAULT 0,
  field_goals_attempted INT DEFAULT 0,
  three_pointers_made INT DEFAULT 0,
  three_pointers_attempted INT DEFAULT 0,
  free_throws_made INT DEFAULT 0,
  free_throws_attempted INT DEFAULT 0,
  minutes_played DECIMAL(4,2),
  recording_method ENUM('manual', 'automated') DEFAULT 'manual',
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
  FOREIGN KEY (game_id) REFERENCES games(game_id),
  INDEX idx_athlete_id (athlete_id),
  INDEX idx_game_id (game_id),
  UNIQUE KEY unique_athlete_game (athlete_id, game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- NEWS Table
CREATE TABLE news (
  news_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(300) NOT NULL,
  content TEXT,
  category ENUM('tournament', 'player', 'coach', 'club', 'industry') NOT NULL,
  featured_image_url VARCHAR(500),
  created_by_user_id INT,
  related_club_id INT,
  is_published BOOLEAN DEFAULT TRUE,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by_user_id) REFERENCES users(user_id),
  FOREIGN KEY (related_club_id) REFERENCES clubs(club_id),
  INDEX idx_category (category),
  INDEX idx_is_published (is_published)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ATHLETE_COACH Junction Table
CREATE TABLE athlete_coach (
  athlete_id INT NOT NULL,
  coach_id INT NOT NULL,
  assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  role_in_coaching VARCHAR(100),
  PRIMARY KEY (athlete_id, coach_id),
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
  FOREIGN KEY (coach_id) REFERENCES coaches(coach_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add foreign key constraints for club_id in athletes and coaches
ALTER TABLE athletes ADD CONSTRAINT fk_athletes_club 
  FOREIGN KEY (club_id) REFERENCES clubs(club_id);

ALTER TABLE coaches ADD CONSTRAINT fk_coaches_club 
  FOREIGN KEY (club_id) REFERENCES clubs(club_id);

-- Create Stored Procedure for CSV Export
DELIMITER //

CREATE PROCEDURE sp_ExportAthletes()
BEGIN
  SELECT a.athlete_id, u.first_name, u.last_name, u.email, a.position,
         a.height, a.weight, a.birthdate, a.jersey_number, c.name as club_name
  FROM athletes a
  JOIN users u ON a.user_id = u.user_id
  LEFT JOIN clubs c ON a.club_id = c.club_id
  ORDER BY u.last_name, u.first_name;
END //

CREATE PROCEDURE sp_ExportGameStatistics()
BEGIN
  SELECT s.statistic_id, u.first_name, u.last_name, g.game_date,
         s.points, s.rebounds, s.assists, s.steals, s.blocks,
         s.field_goals_made, s.field_goals_attempted,
         s.three_pointers_made, s.three_pointers_attempted,
         s.free_throws_made, s.free_throws_attempted,
         s.minutes_played
  FROM statistics s
  JOIN athletes a ON s.athlete_id = a.athlete_id
  JOIN users u ON a.user_id = u.user_id
  JOIN games g ON s.game_id = g.game_id
  ORDER BY g.game_date DESC;
END //

DELIMITER ;
```

### Step 3.3: Load Schema into Database

```bash
# Connect to MySQL container and execute schema
docker exec -i dunes-mysql mysql -uroot -pdunes_root_pass_123 < database/schema.sql

# Verify tables were created
docker exec dunes-mysql mysql -uroot -pdunes_root_pass_123 -e "USE dunes_cms; SHOW TABLES;"
```

### Step 3.4: Create Database Connection Module

Create `backend/db_connection.py`:

```python
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'dunes_user')
        self.password = os.getenv('DB_PASSWORD', 'dunes_user_pass_123')
        self.database = os.getenv('DB_NAME', 'dunes_cms')
        self.port = os.getenv('DB_PORT', 3306)
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database: {self.database}")
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def get_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    def execute_query(self, query, params=None):
        try:
            cursor = self.get_connection().cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Error as e:
            print(f"Query execution error: {e}")
            return None

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return None

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()
```

---

## PART 4: BACKEND FLASK APPLICATION

### Step 4.1: Create Flask Application Structure

```bash
# Create backend directory structure
cd backend
mkdir routes services models utils
touch app.py config.py requirements.txt
```

### Step 4.2: Create Environment Configuration

Create `backend/.env`:

```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_change_in_production_12345
DB_HOST=localhost
DB_USER=dunes_user
DB_PASSWORD=dunes_user_pass_123
DB_NAME=dunes_cms
DB_PORT=3306
JWT_SECRET_KEY=your_jwt_secret_change_in_production
```

### Step 4.3: Create Main Flask App

Create `backend/app.py`:

```python
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Dunes CMS API'}), 200

# API Version endpoint
@app.route('/api/v1', methods=['GET'])
def api_version():
    return jsonify({
        'service': 'Dunes Be One Basketball CMS',
        'version': '1.0.0',
        'status': 'operational'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Step 4.4: Create Authentication Module

Create `backend/services/auth_service.py`:

```python
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from db_connection import DatabaseConnection

class AuthService:
    def __init__(self):
        self.db = DatabaseConnection()

    def hash_password(self, password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def create_user(self, email, password, first_name, last_name, role):
        """Create a new user account"""
        query = """
        INSERT INTO users (email, password_hash, first_name, last_name, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        password_hash = self.hash_password(password)
        try:
            cursor = self.db.execute_query(query, 
                (email, password_hash, first_name, last_name, role))
            self.db.commit()
            return True, cursor.lastrowid
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def authenticate_user(self, email, password):
        """Authenticate user and return user object"""
        query = "SELECT user_id, email, password_hash, first_name, last_name, role FROM users WHERE email = %s"
        user = self.db.fetch_one(query, (email,))
        
        if user and self.verify_password(password, user[2]):
            return {
                'user_id': user[0],
                'email': user[1],
                'first_name': user[3],
                'last_name': user[4],
                'role': user[5]
            }
        return None

    def generate_token(self, user_id, email, role):
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

    def verify_token(self, token):
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### Step 4.5: Create API Routes

Create `backend/routes/auth_routes.py`:

```python
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_service = AuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = auth_service.authenticate_user(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = auth_service.generate_token(user['user_id'], user['email'], user['role'])
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role']
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    role = data.get('role', 'athlete')
    
    if not all([email, password, first_name, last_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success, result = auth_service.create_user(email, password, first_name, last_name, role)
    
    if success:
        return jsonify({'success': True, 'user_id': result}), 201
    else:
        return jsonify({'error': result}), 400

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    payload = auth_service.verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({
        'user_id': payload['user_id'],
        'email': payload['email'],
        'role': payload['role']
    }), 200
```

Now update `backend/app.py` to register the auth blueprint:

```python
from routes.auth_routes import auth_bp

app.register_blueprint(auth_bp)
```

---

## PART 5: FRONTEND DEVELOPMENT

### Step 5.1: Create Frontend Structure

```bash
cd frontend
mkdir css js
touch index.html main.js style.css
```

### Step 5.2: Create Main HTML File

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dunes Be One - Basketball CMS</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <!-- Navigation -->
        <header class="navbar">
            <div class="navbar-container">
                <div class="navbar-brand">
                    <h1>Dunes Be One</h1>
                </div>
                <nav class="navbar-menu">
                    <a href="#home" class="nav-link active">HOME</a>
                    <a href="#dashboard" class="nav-link">DASHBOARD</a>
                </nav>
                <div class="navbar-user">
                    <button id="loginBtn" class="btn btn-primary">LOGIN</button>
                    <div id="userMenu" class="user-menu hidden">
                        <span id="userName"></span>
                        <button id="logoutBtn" class="btn btn-secondary">LOGOUT</button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Home Page -->
            <section id="homePage" class="page">
                <div class="hero">
                    <h2>Welcome to Dunes Be One Basketball Platform</h2>
                    <p>Manage Athletes • Track Performance • Develop Champions</p>
                    <div class="hero-buttons">
                        <button class="btn btn-primary" onclick="navigateTo('dashboard')">Get Started</button>
                        <button class="btn btn-secondary" onclick="showModal('aboutModal')">Learn More</button>
                    </div>
                </div>

                <div class="grid grid-4">
                    <div class="tile">
                        <div class="tile-icon">👥</div>
                        <h3>ATHLETES</h3>
                        <p class="tile-stat" id="athleteCount">245</p>
                        <p>Athletes</p>
                        <button class="btn btn-outline" onclick="navigateTo('athletes')">VIEW</button>
                    </div>

                    <div class="tile">
                        <div class="tile-icon">🏀</div>
                        <h3>GAMES</h3>
                        <p class="tile-stat" id="gameCount">1,250</p>
                        <p>Games</p>
                        <button class="btn btn-outline" onclick="navigateTo('games')">VIEW</button>
                    </div>

                    <div class="tile">
                        <div class="tile-icon">📊</div>
                        <h3>STATISTICS</h3>
                        <p class="tile-stat" id="statCount">3,450</p>
                        <p>Statistics</p>
                        <button class="btn btn-outline" onclick="navigateTo('statistics')">VIEW</button>
                    </div>

                    <div class="tile">
                        <div class="tile-icon">📈</div>
                        <h3>PERFORMANCE</h3>
                        <p class="tile-stat" id="perfCount">485</p>
                        <p>Benchmarks</p>
                        <button class="btn btn-outline" onclick="navigateTo('performance')">VIEW</button>
                    </div>
                </div>

                <div class="activity-card">
                    <h3>RECENT ACTIVITY</h3>
                    <ul id="recentActivity">
                        <li>Game Completed: Hawks vs Falcons - Hawks won 78-65</li>
                        <li>Player Achievement: Marcus Johnson scored 25 points</li>
                        <li>Training Update: Squad A completed conditioning session</li>
                        <li>News: Coach Sarah Williams joins Elite Academy</li>
                    </ul>
                </div>
            </section>

            <!-- Dashboard Page -->
            <section id="dashboardPage" class="page hidden">
                <h2>Dashboard</h2>
                <p>Dashboard content will load here based on user role</p>
            </section>
        </main>

        <!-- Login Modal -->
        <div id="loginModal" class="modal hidden">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Sign In to Your Account</h3>
                    <button class="close-btn" onclick="closeModal('loginModal')">&times;</button>
                </div>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary full-width">SIGN IN</button>
                </form>
            </div>
        </div>

        <!-- About Modal -->
        <div id="aboutModal" class="modal hidden">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>About Dunes Be One</h3>
                    <button class="close-btn" onclick="closeModal('aboutModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Dunes Be One Basketball CMS Platform is a comprehensive system for managing basketball player development, performance tracking, and talent scouting.</p>
                    <p>With our platform, you can:</p>
                    <ul>
                        <li>Track athlete training and performance</li>
                        <li>Manage game schedules and statistics</li>
                        <li>View real-time performance analytics</li>
                        <li>Identify and develop basketball talent</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 Dunes Be One Basketball Organization. All rights reserved.</p>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>
```

### Step 5.3: Create CSS Stylesheet

Create `frontend/css/style.css`:

```css
/* === DUNES BE ONE BASKETBALL CMS - STYLESHEET === */

/* Root Variables */
:root {
    --primary-orange: #FF6B35;
    --primary-black: #1A1A1A;
    --primary-white: #FFFFFF;
    --secondary-light-gray: #F5F5F5;
    --secondary-dark-gray: #333333;
    --accent-orange: #FFA500;
    --success-green: #4CAF50;
    --warning-amber: #FFC107;
    --error-red: #F44336;
    --info-blue: #2196F3;
    
    --spacing-8: 8px;
    --spacing-16: 16px;
    --spacing-24: 24px;
    --spacing-32: 32px;
    --spacing-48: 48px;
    
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* === GLOBAL STYLES === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    font-family: var(--font-family);
    background-color: var(--primary-white);
    color: var(--secondary-dark-gray);
    line-height: 1.6;
}

/* === TYPOGRAPHY === */
h1 {
    font-size: 32px;
    font-weight: 700;
    line-height: 1.3;
    color: var(--primary-black);
}

h2 {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--primary-black);
    margin-bottom: var(--spacing-24);
}

h3 {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--primary-black);
}

p {
    font-size: 14px;
    font-weight: 400;
    line-height: 1.6;
}

a {
    color: var(--primary-orange);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* === NAVBAR === */
.navbar {
    background-color: var(--primary-black);
    color: var(--primary-white);
    padding: var(--spacing-16) 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.navbar-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 var(--spacing-24);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand h1 {
    font-size: 24px;
    color: var(--primary-white);
}

.navbar-menu {
    display: flex;
    gap: var(--spacing-32);
}

.nav-link {
    color: var(--primary-white);
    font-size: 14px;
    font-weight: 600;
    transition: color 0.3s ease;
    padding-bottom: var(--spacing-8);
    border-bottom: 2px solid transparent;
}

.nav-link:hover,
.nav-link.active {
    color: var(--primary-orange);
    border-bottom-color: var(--primary-orange);
}

.navbar-user {
    display: flex;
    align-items: center;
    gap: var(--spacing-16);
}

.user-menu {
    display: flex;
    align-items: center;
    gap: var(--spacing-16);
}

.user-menu.hidden {
    display: none;
}

/* === BUTTONS === */
.btn {
    padding: var(--spacing-8) var(--spacing-16);
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    line-height: 1.5;
}

.btn-primary {
    background-color: var(--primary-orange);
    color: var(--primary-white);
}

.btn-primary:hover {
    background-color: #E55A2B;
}

.btn-primary:active {
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
}

.btn-secondary {
    background-color: var(--primary-black);
    color: var(--primary-white);
}

.btn-secondary:hover {
    background-color: var(--secondary-dark-gray);
}

.btn-outline {
    background-color: transparent;
    color: var(--primary-orange);
    border: 2px solid var(--primary-orange);
}

.btn-outline:hover {
    background-color: var(--primary-orange);
    color: var(--primary-white);
}

.btn.full-width {
    width: 100%;
    display: block;
}

.btn:disabled {
    background-color: #CCCCCC;
    color: #999999;
    cursor: not-allowed;
}

/* === MAIN CONTENT === */
.main-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-32) var(--spacing-24);
    min-height: calc(100vh - 200px);
}

.page {
    animation: fadeIn 0.3s ease;
}

.page.hidden {
    display: none;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* === HERO SECTION === */
.hero {
    text-align: center;
    padding: var(--spacing-48) var(--spacing-24);
    background: linear-gradient(135deg, var(--primary-black) 0%, #2A2A2A 100%);
    color: var(--primary-white);
    border-radius: 8px;
    margin-bottom: var(--spacing-48);
}

.hero h2 {
    font-size: 36px;
    margin-bottom: var(--spacing-16);
    color: var(--primary-white);
}

.hero p {
    font-size: 16px;
    margin-bottom: var(--spacing-32);
}

.hero-buttons {
    display: flex;
    gap: var(--spacing-16);
    justify-content: center;
    flex-wrap: wrap;
}

/* === GRID LAYOUT === */
.grid {
    display: grid;
    gap: var(--spacing-24);
    margin-bottom: var(--spacing-48);
}

.grid-4 {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

@media (max-width: 768px) {
    .grid-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 480px) {
    .grid-4 {
        grid-template-columns: 1fr;
    }
}

/* === TILES === */
.tile {
    background-color: var(--primary-white);
    border: 1px solid var(--secondary-light-gray);
    border-radius: 8px;
    padding: var(--spacing-24);
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.tile:hover {
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15);
    transform: translateY(-2px);
}

.tile-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-16);
}

.tile h3 {
    margin-bottom: var(--spacing-8);
    color: var(--primary-orange);
}

.tile-stat {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary-orange);
    margin: var(--spacing-16) 0 var(--spacing-8) 0;
}

.tile p {
    color: var(--secondary-dark-gray);
    margin-bottom: var(--spacing-16);
}

.tile .btn {
    width: 100%;
}

/* === ACTIVITY CARD === */
.activity-card {
    background-color: var(--primary-white);
    border: 1px solid var(--secondary-light-gray);
    border-radius: 8px;
    padding: var(--spacing-24);
    margin-bottom: var(--spacing-48);
}

.activity-card h3 {
    margin-bottom: var(--spacing-16);
    padding-bottom: var(--spacing-16);
    border-bottom: 2px solid var(--secondary-light-gray);
}

.activity-card ul {
    list-style: none;
}

.activity-card li {
    padding: var(--spacing-12) 0;
    border-bottom: 1px solid var(--secondary-light-gray);
    font-size: 14px;
}

.activity-card li:last-child {
    border-bottom: none;
}

/* === FORMS === */
.form-group {
    margin-bottom: var(--spacing-24);
    text-align: left;
}

.form-group label {
    display: block;
    margin-bottom: var(--spacing-8);
    font-size: 12px;
    font-weight: 600;
    color: var(--secondary-dark-gray);
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: var(--spacing-8) var(--spacing-12);
    border: 1px solid var(--secondary-dark-gray);
    border-radius: 4px;
    font-family: var(--font-family);
    font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--primary-orange);
    box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.form-group input.error,
.form-group textarea.error,
.form-group select.error {
    border-color: var(--error-red);
}

/* === MODALS === */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
}

.modal.hidden {
    display: none;
}

.modal-content {
    background-color: var(--primary-white);
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-24);
    border-bottom: 1px solid var(--secondary-light-gray);
}

.modal-header h3 {
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--secondary-dark-gray);
}

.close-btn:hover {
    color: var(--primary-orange);
}

.modal-body {
    padding: var(--spacing-24);
}

/* === FOOTER === */
footer {
    background-color: var(--secondary-light-gray);
    text-align: center;
    padding: var(--spacing-32) var(--spacing-24);
    margin-top: var(--spacing-48);
    color: var(--secondary-dark-gray);
    font-size: 12px;
}

/* === RESPONSIVE DESIGN === */
@media (max-width: 768px) {
    .navbar-menu {
        display: none;
    }
    
    .main-content {
        padding: var(--spacing-16);
    }
    
    .hero {
        padding: var(--spacing-32) var(--spacing-16);
    }
    
    .hero h2 {
        font-size: 24px;
    }
}

@media (max-width: 480px) {
    h1 {
        font-size: 24px;
    }
    
    h2 {
        font-size: 18px;
    }
    
    .hero-buttons {
        flex-direction: column;
    }
    
    .btn {
        padding: var(--spacing-12) var(--spacing-16);
        font-size: 12px;
    }
}
```

### Step 5.4: Create JavaScript Application Logic

Create `frontend/js/main.js`:

```javascript
// === DUNES BE ONE BASKETBALL CMS - MAIN APPLICATION ===

// Configuration
const API_URL = 'http://localhost:5000/api/v1';
const STORAGE_KEY = 'dunes_auth_token';
const USER_STORAGE_KEY = 'dunes_user';

// Application State
const app = {
    currentUser: null,
    token: null,
    
    // Initialize application
    init() {
        this.loadAuthToken();
        this.setupEventListeners();
        this.checkAuthStatus();
        console.log('Dunes CMS Application Initialized');
    },
    
    // Load auth token from localStorage
    loadAuthToken() {
        this.token = localStorage.getItem(STORAGE_KEY);
        const userStr = localStorage.getItem(USER_STORAGE_KEY);
        if (userStr) {
            this.currentUser = JSON.parse(userStr);
        }
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Login button
        document.getElementById('loginBtn').addEventListener('click', () => {
            showModal('loginModal');
        });
        
        // Login form submission
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
        
        // Modal close buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                modal.classList.add('hidden');
            });
        });
        
        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });
    },
    
    // Handle login
    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store token and user info
                localStorage.setItem(STORAGE_KEY, data.token);
                localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data.user));
                
                this.token = data.token;
                this.currentUser = data.user;
                
                // Update UI
                this.updateAuthUI();
                
                // Close modal
                closeModal('loginModal');
                
                // Reset form
                document.getElementById('loginForm').reset();
                
                // Navigate to dashboard
                navigateTo('dashboard');
                
                console.log('Login successful:', data.user);
            } else {
                alert('Login failed: ' + data.error);
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login error: ' + error.message);
        }
    },
    
    // Logout
    logout() {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        
        this.token = null;
        this.currentUser = null;
        
        this.updateAuthUI();
        navigateTo('home');
        
        console.log('Logout successful');
    },
    
    // Check authentication status
    checkAuthStatus() {
        if (this.token && this.currentUser) {
            this.updateAuthUI();
        }
    },
    
    // Update UI based on authentication status
    updateAuthUI() {
        const loginBtn = document.getElementById('loginBtn');
        const userMenu = document.getElementById('userMenu');
        const userName = document.getElementById('userName');
        
        if (this.currentUser) {
            loginBtn.classList.add('hidden');
            userMenu.classList.remove('hidden');
            userName.textContent = `${this.currentUser.first_name} (${this.currentUser.role})`;
        } else {
            loginBtn.classList.remove('hidden');
            userMenu.classList.add('hidden');
        }
    }
};

// Utility Functions
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function navigateTo(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Show target page
    if (pageId === 'home') {
        document.getElementById('homePage').classList.remove('hidden');
    } else if (pageId === 'dashboard') {
        if (!app.currentUser) {
            alert('Please login first');
            showModal('loginModal');
            return;
        }
        document.getElementById('dashboardPage').classList.remove('hidden');
        loadDashboard();
    } else {
        // Navigate to specific section
        alert('Feature coming soon: ' + pageId);
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[href="#${pageId}"]`)?.classList.add('active');
}

function loadDashboard() {
    const dashboardContent = document.querySelector('#dashboardPage');
    
    if (app.currentUser.role === 'athlete') {
        dashboardContent.innerHTML = `
            <div class="athlete-dashboard">
                <h2>Welcome, ${app.currentUser.first_name}!</h2>
                <p>Your athlete dashboard content will be displayed here.</p>
            </div>
        `;
    } else if (app.currentUser.role === 'coach') {
        dashboardContent.innerHTML = `
            <div class="coach-dashboard">
                <h2>Coach Dashboard - ${app.currentUser.first_name}</h2>
                <p>Your coaching dashboard with athlete roster and training schedules.</p>
            </div>
        `;
    } else if (app.currentUser.role === 'manager') {
        dashboardContent.innerHTML = `
            <div class="manager-dashboard">
                <h2>Executive Dashboard</h2>
                <p>Organization-wide analytics and performance metrics.</p>
            </div>
        `;
    } else {
        dashboardContent.innerHTML = '<p>Dashboard content loading...</p>';
    }
}

// API Helper Functions
async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (app.token) {
        headers['Authorization'] = `Bearer ${app.token}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
```

---

## PART 6: COMPLETE DEPLOYMENT STRUCTURE

Your complete file structure should now be:

```
Dunes/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── db_connection.py
│   ├── requirements.txt
│   ├── .env
│   ├── routes/
│   │   └── auth_routes.py
│   └── services/
│       └── auth_service.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── database/
│   └── schema.sql
├── docker/
│   └── docker-compose.yml
├── docs/
│   ├── 01-COVER.md
│   ├── 02-ANALYSIS.md
│   ├── 03-ARCHITECTURE.md
│   └── 04-DESIGN.md
├── data/
│   └── (CSV files for archival)
├── .gitignore
└── README.md
```

---

## GIT WORKFLOW DURING DEVELOPMENT

### Complete Development Workflow Example

```bash
# 1. Make sure you're on main and it's up to date
git checkout main
git pull origin main

# 2. Checkout to develop
git checkout develop
git pull origin develop

# 3. Create feature branch
git checkout -b feature/cms-frontend-login-v1.0.0

# 4. Make changes and test locally
# ... edit files, test thoroughly ...

# 5. Stage changes
git add frontend/
git status  # Review what's staged

# 6. Commit with descriptive message
git commit -m "feat(frontend-login): Add login modal with authentication"

# 7. View commit history
git log --oneline -5

# 8. Checkout to test branch
git checkout test

# 9. Merge from feature (or via pull request)
git merge feature/cms-frontend-login-v1.0.0

# 10. Test thoroughly in test branch
# ... run tests, validate in browser ...

# 11. Checkout to ready
git checkout ready
git merge test

# 12. Push to remote int branch
git push origin ready:int

# 13. Create pull request (if using GitHub/GitLab)
# Monitor build and review process

# 14. Once approved, merge to main
git checkout main
git merge ready
git push origin main

# 15. Clean up feature branch
git branch -d feature/cms-frontend-login-v1.0.0
git push origin --delete feature/cms-frontend-login-v1.0.0
```

---

This concludes the DEVELOPMENT section. Continue to the next documentation file for packaging and deployment instructions.
