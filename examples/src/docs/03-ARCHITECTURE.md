# ARCHITECTURE: Dunes Be One Basketball CMS Platform

## C4 ARCHITECTURE MODEL

### Context Level (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Internet Users                       │
│  (Athletes, Coaches, Club Managers, General Managers)           │
└────────────┬──────────────────────────────────────────────────┘
             │ HTTPS/Web Browser
             ▼
┌─────────────────────────────────────────────────────────────────┐
│        Dunes Be One Basketball CMS Platform System              │
│                                                                   │
│  - Player Management (Training, Health, Performance)            │
│  - Game Management (Schedules, Results, Statistics)             │
│  - Performance Analytics (Dashboards, Reports)                  │
│  - News Management (Basketball News, Announcements)            │
│  - Authentication (Role-based Access Control)                   │
│  - Data Export (CSV Archival)                                  │
└─────────────────────────────────────────────────────────────────┘
             ▲
             │ CSV Export (Scheduled)
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              External Archival Storage (CSV Files)               │
└─────────────────────────────────────────────────────────────────┘
```

### Container Level (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Dunes Be One CMS Platform                           │
│                                                                            │
│  ┌───────────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Web Browser (SPA)   │  │   Mobile Browser │  │  CSV Export Tool │  │
│  │  (HTML/CSS/JS)        │  │  (HTML/CSS/JS)   │  │   (Command Line) │  │
│  └───────────┬───────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│              │ HTTPS REST API        │                      │             │
│              └──────────────┬────────┘                      │             │
│                             ▼                               │             │
│              ┌──────────────────────────┐                  │             │
│              │   Flask Web API Server   │                  │             │
│              │  (Python + Extensions)   │                  │             │
│              │  - Authentication        │                  │             │
│              │  - API Endpoints         │                  │             │
│              │  - Business Logic        │                  │             │
│              │  - Role-based Access     │                  │             │
│              │  - CSV Export Controller │◄─────────────────┘             │
│              └───────────┬──────────────┘                                │
│                          │ SQL Queries
│                          ▼
│              ┌──────────────────────────┐
│              │   MySQL Database         │
│              │  (8.0+)                  │
│              │  - Athletes Table        │
│              │  - Coaches Table         │
│              │  - Clubs Table           │
│              │  - Games Table           │
│              │  - Training Table        │
│              │  - Statistics Table      │
│              │  - Users Table           │
│              │  - News Table            │
│              │  - Stored Procedures     │
│              │  - Triggers              │
│              └──────────────────────────┘
│
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Level (C4 Level 3 - Backend)

```
┌──────────────────────────────────────────────────────────────────┐
│                     Flask Application                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          Authentication & Authorization Module         │    │
│  │  - User login/logout                                   │    │
│  │  - Role validation (Athlete, Coach, Club, Manager)    │    │
│  │  - Session management                                 │    │
│  │  - Password hashing/verification                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────┬───────────┴────────────┬─────────────────────┐  │
│  ▼            ▼                        ▼                     ▼  │
│                                                               │  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │   Athlete    │  │   Coach      │  │   Club/Manager   │   │  │
│  │   Routes    │  │   Routes    │  │   Routes         │   │  │
│  │ & Handlers   │  │ & Handlers   │  │  & Handlers      │   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │  │
│                                                               │  │
│  ┌──────────────────────────────────────────────────────┐    │  │
│  │        Business Logic & Service Layer               │    │  │
│  │  - Player Management Service                        │    │  │
│  │  - Game Management Service                          │    │  │
│  │  - Statistics Calculation Service                   │    │  │
│  │  - Performance Analytics Service                    │    │  │
│  │  - News Management Service                          │    │  │
│  │  - CSV Export Service                               │    │  │
│  └──────────────────────────────────────────────────────┘    │  │
│                           │                                   │  │
│  ┌────────────┬───────────┴────────────┬────────────────┐    │  │
│  ▼            ▼                        ▼                ▼    │  │
│                                                               │  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │   Database   │  │   Database   │  │  Database CSV    │   │  │
│  │  Service     │  │   Query      │  │  Export Service  │   │  │
│  │  (Models)    │  │  Builder     │  │                  │   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │  │
│         │                  │                   │              │  │
│         └──────────────────┴───────────────────┘              │  │
│                            │                                   │  │
│                            ▼                                   │  │
│         ┌──────────────────────────────────┐                 │  │
│         │  MySQL Database Connector        │                 │  │
│         │  (mysql-connector-python)        │                 │  │
│         └──────────────────────────────────┘                 │  │
│                                                               │  │
└──────────────────────────────────────────────────────────────┘  │
```

## ENTITY RELATIONSHIP DIAGRAM (ERD)

```
┌──────────────────┐
│     USERS        │
├──────────────────┤
│ user_id (PK)     │
│ email            │
│ password_hash    │
│ first_name       │
│ last_name        │
│ role             │
│ created_at       │
└────────┬─────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    │         │            │          │
    ▼         ▼            ▼          ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ATHLETES │ │ COACHES  │ │ CLUBS    │ │MANAGERS  │
├─────────┤ ├──────────┤ ├──────────┤ ├──────────┤
│athlete_ │ │coach_id  │ │club_id   │ │manager   │
│id (PK)  │ │(PK)(FK)  │ │(PK)(FK)  │ │_id(PK)(FK)
│user_id  │ │club_id   │ │name      │ │club_id   │
│(FK)     │ │(FK)      │ │location  │ │(FK)      │
│position │ │          │ │founded   │ │          │
│height   │ │          │ │         │ │          │
│weight   │ │          │ │         │ │          │
│birthdate│ │          │ │         │ │          │
└────┬────┘ └────┬─────┘ └──────────┘ └──────────┘
     │           │
     │      ┌────▼──────────┐
     │      │ ATHLETE_COACH  │
     │      ├────────────────┤
     │      │ athlete_id(FK) │
     │      │ coach_id (FK)  │
     │      │ assigned_date  │
     │      └────────────────┘
     │
     └──────────┬─────────────────┬──────────┐
                │                 │          │
                ▼                 ▼          ▼
          ┌──────────────┐  ┌──────────┐ ┌────────────┐
          │   TRAINING   │  │  GAMES   │ │ STATISTICS │
          ├──────────────┤  ├──────────┤ ├────────────┤
          │training_id   │  │game_id   │ │statistic   │
          │(PK)          │  │(PK)      │ │_id(PK)     │
          │athlete_id    │  │date      │ │athlete_id  │
          │(FK)          │  │home_team │ │(FK)        │
          │coach_id(FK)  │  │away_team │ │game_id(FK) │
          │date          │  │location  │ │points      │
          │duration      │  │status    │ │rebounds    │
          │type          │  │result    │ │assists     │
          │notes         │  │home_score│ │steals      │
          └──────────────┘  │away_score│ │blocks      │
                            └──────────┘ │field_goals │
                                        │recorded_at │
                                        └────────────┘

          ┌──────────────┐
          │     NEWS     │
          ├──────────────┤
          │ news_id (PK) │
          │ title        │
          │ content      │
          │ category     │
          │ published_at │
          │ created_by   │
          │ (FK to Users)│
          └──────────────┘
```

## DATABASE SCHEMA STRUCTURE

### Core Tables with Attributes

**USERS Table**
- Primary Key: user_id (INT AUTO_INCREMENT)
- Foreign Keys: None
- Attributes: email (VARCHAR 255 UNIQUE), password_hash (VARCHAR 255), first_name (VARCHAR 100), last_name (VARCHAR 100), role (ENUM: athlete, coach, club, manager), created_at (TIMESTAMP), updated_at (TIMESTAMP)
- Indexes: email (UNIQUE), role, created_at

**ATHLETES Table**
- Primary Key: athlete_id (INT AUTO_INCREMENT)
- Foreign Keys: user_id (FK → USERS.user_id) NOT NULL
- Attributes: position (VARCHAR 50), height (DECIMAL 3,2), weight (INT), birthdate (DATE), jersey_number (INT), club_id (INT FK), bio (TEXT), medical_notes (TEXT), created_at (TIMESTAMP)
- Indexes: user_id (UNIQUE), club_id, position, birthdate

**COACHES Table**
- Primary Key: coach_id (INT AUTO_INCREMENT)
- Foreign Keys: user_id (FK → USERS.user_id) NOT NULL, club_id (FK → CLUBS.club_id)
- Attributes: specialization (VARCHAR 100), certification_level (VARCHAR 50), years_experience (INT), bio (TEXT), created_at (TIMESTAMP)
- Indexes: user_id (UNIQUE), club_id

**CLUBS Table**
- Primary Key: club_id (INT AUTO_INCREMENT)
- Foreign Keys: None
- Attributes: name (VARCHAR 200), location (VARCHAR 200), founded_year (YEAR), contact_email (VARCHAR 255), contact_phone (VARCHAR 20), website (VARCHAR 255), bio (TEXT), created_at (TIMESTAMP)
- Indexes: name, location, founded_year

**GAMES Table**
- Primary Key: game_id (INT AUTO_INCREMENT)
- Foreign Keys: home_club_id (FK → CLUBS.club_id), away_club_id (FK → CLUBS.club_id)
- Attributes: game_date (DATETIME), location (VARCHAR 255), status (ENUM: scheduled, ongoing, completed, cancelled), home_team_score (INT), away_team_score (INT), tournament_name (VARCHAR 100), notes (TEXT), created_at (TIMESTAMP)
- Indexes: game_date, status, home_club_id, away_club_id

**TRAINING Table**
- Primary Key: training_id (INT AUTO_INCREMENT)
- Foreign Keys: athlete_id (FK → ATHLETES.athlete_id), coach_id (FK → COACHES.coach_id)
- Attributes: training_date (DATE), session_time (TIME), duration_minutes (INT), training_type (VARCHAR 100), focus_area (VARCHAR 100), intensity_level (ENUM: low, medium, high), attendance (BOOLEAN), notes (TEXT), performance_rating (INT 1-10), created_at (TIMESTAMP)
- Indexes: athlete_id, coach_id, training_date, training_type

**STATISTICS Table**
- Primary Key: statistic_id (INT AUTO_INCREMENT)
- Foreign Keys: athlete_id (FK → ATHLETES.athlete_id), game_id (FK → GAMES.game_id)
- Attributes: points (INT), rebounds (INT), assists (INT), steals (INT), blocks (INT), turnovers (INT), fouls (INT), field_goals_made (INT), field_goals_attempted (INT), three_pointers_made (INT), three_pointers_attempted (INT), free_throws_made (INT), free_throws_attempted (INT), minutes_played (DECIMAL 4,2), recording_method (ENUM: manual, automated), recorded_at (TIMESTAMP)
- Indexes: athlete_id, game_id, recorded_at, points

**NEWS Table**
- Primary Key: news_id (INT AUTO_INCREMENT)
- Foreign Keys: created_by_user_id (FK → USERS.user_id), related_club_id (FK → CLUBS.club_id) NULLABLE
- Attributes: title (VARCHAR 300), content (TEXT), category (ENUM: tournament, player, coach, club, industry), featured_image_url (VARCHAR 500), is_published (BOOLEAN), published_at (TIMESTAMP) NULLABLE, created_at (TIMESTAMP), updated_at (TIMESTAMP)
- Indexes: category, is_published, published_at, created_at

**ATHLETE_COACH Table** (Many-to-Many)
- Primary Keys: athlete_id (INT FK → ATHLETES.athlete_id), coach_id (INT FK → COACHES.coach_id)
- Attributes: assigned_date (TIMESTAMP), role_in_coaching (VARCHAR 100), created_at (TIMESTAMP)
- Indexes: athlete_id, coach_id

## DATABASE STORED PROCEDURES & TRIGGERS

### Critical Stored Procedures

**PROCEDURE: sp_GetAthletePerformanceSummary**
- Purpose: Calculate current performance metrics for an athlete
- Parameters: p_athlete_id INT
- Output: Performance summary (total points, rebounds, assists, games played, season avg)

**PROCEDURE: sp_UpdateAthleteRankings**
- Purpose: Recalculate athlete performance rankings based on recent statistics
- Parameters: None
- Logic: Calculates percentiles for each position, updates ranking tables

**PROCEDURE: sp_GenerateCoachReport**
- Purpose: Generate comprehensive coaching report for a coach's assigned athletes
- Parameters: p_coach_id INT, p_start_date DATE, p_end_date DATE
- Output: Report with athlete progress, training attendance, game performance

**PROCEDURE: sp_ExportTableToCSV**
- Purpose: Export any table data to CSV format for archival
- Parameters: p_table_name VARCHAR, p_file_path VARCHAR
- Logic: Selects all data from specified table, formats as CSV

### Critical Triggers

**TRIGGER: trg_athlete_stats_update**
- Event: AFTER INSERT on STATISTICS
- Action: Recalculate athlete's performance metrics and rankings

**TRIGGER: trg_game_result_notification**
- Event: AFTER UPDATE on GAMES (when status changes to 'completed')
- Action: Mark statistics entry as finalized, trigger calculation procedures

**TRIGGER: trg_enforce_referential_integrity**
- Event: BEFORE DELETE on ATHLETES
- Action: Prevent deletion if athlete has non-archived training records (soft delete instead)

## DATA FLOW DIAGRAMS

### Athlete Training Data Flow

```
Athlete Creates Training → JSON API Request → Flask Route Handler
          ↓
Validates Input (Auth, Format, Business Rules) → Success?
          ↓ YES
Calls TrainingService.create_training(data)
          ↓
Executes Parameterized SQL INSERT
          ↓
Triggers: trg_athlete_stats_update
          ↓
Recalculates Performance Metrics
          ↓
Returns JSON Response with Status
          ↓
Frontend Updates UI with New Training Entry
          ↓
Athlete Views Updated Dashboard with Latest Performance
```

### Game Statistics Data Flow

```
Coach Enters Game Result → JSON API Request with Stats → Flask Route
          ↓
Validates Data (Game exists? Athletes exist? Values valid?)
          ↓ YES
Calls StatisticsService.record_game_stats(data)
          ↓
Transaction: INSERT into STATISTICS → INSERT into GAMES result
          ↓
Triggers: trg_game_result_notification
          ↓
Calls sp_UpdateAthleteRankings (Stored Procedure)
          ↓
All athlete rankings recalculated atomically
          ↓
Event notification queued for interested coaches/managers
          ↓
Returns updated statistics and rankings
          ↓
Frontend updates game results page and athlete rankings
```

### CSV Export Data Flow

```
Manager Requests Data Export → CSV Export Request API
          ↓
AuthService validates role (Manager only)
          ↓ AUTHORIZED
Specifies tables: ATHLETES, STATISTICS, GAMES, TRAINING
          ↓
Calls CSVExportService.export_tables(table_list)
          ↓
For each table:
  - Calls sp_ExportTableToCSV(table_name)
  - Retrieves all data from MySQL
  - Formats as CSV
  - Writes to /data/exports/archive_YYYYMMDD_HHmmss.zip
          ↓
Returns download link
          ↓
Manager downloads ZIP file
          ↓
File stored in archival location (external storage, cloud, etc.)
```

## FRONTEND DATA MODEL

### Core JavaScript Classes

```javascript
class User {
  userId
  email
  role  // 'athlete', 'coach', 'club', 'manager'
  firstName
  lastName
  createdAt
}

class Athlete extends User {
  athleteId
  position
  height
  weight
  birthdate
  jerseyNumber
  clubId
  medicalNotes
  coaches  // Array of Coach objects
  trainingRecords  // Array of Training objects
  statistics  // Array of Statistic objects
}

class Coach extends User {
  coachId
  specialization
  certificationLevel
  yearsExperience
  clubId
  assignedAthletes  // Array of Athlete objects
}

class Club {
  clubId
  name
  location
  foundedYear
  website
  athletes  // Array of Athlete objects
  coaches  // Array of Coach objects
  games  // Array of Game objects
}

class Game {
  gameId
  homeClubId
  awayClubId
  gameDate
  location
  status
  homeTeamScore
  awayTeamScore
  statistics  // Array of Statistic objects
}

class Training {
  trainingId
  athleteId
  coachId
  trainingDate
  duration
  type
  intensity
  notes
  performanceRating
}

class Statistic {
  statisticId
  athleteId
  gameId
  points
  rebounds
  assists
  steals
  blocks
  fieldGoalsMade
  fieldGoalsAttempted
  threePointersMade
  threePointersAttempted
  freeThrowsMade
  freeThrowsAttempted
  minutesPlayed
}

class News {
  newsId
  title
  content
  category
  publishedAt
  createdBy
}
```

### Frontend State Management Pattern

```javascript
class CMS {
  state = {
    currentUser: null,
    athletes: [],
    coaches: [],
    clubs: [],
    games: [],
    training: [],
    statistics: [],
    news: [],
    ui: {
      currentPage: 'home',
      isLoading: false,
      errorMessage: null
    }
  }

  async initializeApp() {
    await this.loadCurrentUser()
    await this.loadInitialData()
    this.renderUI()
  }

  async loadCurrentUser() {
    // Calls /api/auth/me endpoint
  }

  async loadInitialData() {
    // Based on user role, loads relevant data
  }

  renderUI() {
    // Renders appropriate view based on state
  }

  updateState(newState) {
    // Merges state changes
    // Triggers re-render
  }
}
```

## SYSTEM INTEGRATION POINTS

### API Integration Points

**Frontend ↔ Backend Communication**
- Endpoint: http://localhost:5000/api/v1/
- Method: REST over HTTP/HTTPS
- Format: JSON
- Authentication: Bearer Token (JWT) in Authorization header
- CORS: Configured for development and production

**Authentication Flow**
```
POST /api/v1/auth/login {email, password}
  ↓ Backend validates, returns JWT token
  ↓ Frontend stores token in sessionStorage
  ↓ Frontend includes token in all subsequent requests
GET /api/v1/auth/me
  ↓ Returns current user and role
  ↓ Frontend renders role-specific interface
```

**Data Synchronization**
- Single Page App loads data once on initialization
- Subsequent changes made through API calls
- Frontend updates state immediately (optimistic update)
- Backend processes change asynchronously
- WebSocket (optional future feature) for real-time updates

## DEPLOYMENT ARCHITECTURE

```
┌──────────────────────────────────────────────────────┐
│             Docker Container System                  │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Web Server Container (nginx)                │   │
│  │  - Serves static frontend files              │   │
│  │  - Reverse proxies /api/* to Flask           │   │
│  │  - Handles HTTPS termination                 │   │
│  └──────────────────────────────────────────────┘   │
│                     ▲                                 │
│                     │ Port 5000 (internal)           │
│                     ▼                                 │
│  ┌──────────────────────────────────────────────┐   │
│  │  Flask App Container (Python)                │   │
│  │  - REST API endpoints                        │   │
│  │  - Business logic                            │   │
│  │  - Database operations                       │   │
│  └──────────────────────────────────────────────┘   │
│                     ▲                                 │
│                     │ Port 3306 (internal)           │
│                     ▼                                 │
│  ┌──────────────────────────────────────────────┐   │
│  │  MySQL Container (Database)                  │   │
│  │  - Data persistence                          │   │
│  │  - Backups                                   │   │
│  │  - Stored procedures & triggers              │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
└──────────────────────────────────────────────────────┘
         ▲
         │ Port 80 (HTTP) / 443 (HTTPS)
         │ Browser Access
```

---

**Architecture Summary:** The Dunes Be One CMS Platform uses a three-tier architecture (Presentation/Application/Data) containerized in Docker, enabling simple deployment while maintaining professional separation of concerns and security practices.
