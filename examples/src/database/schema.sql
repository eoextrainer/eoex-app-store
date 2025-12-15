-- Dunes Be One Basketball CMS - Database Schema

CREATE DATABASE IF NOT EXISTS dunes_cms;
USE dunes_cms;

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
  FOREIGN KEY (club_id) REFERENCES clubs(club_id),
  INDEX idx_club_id (club_id),
  INDEX idx_position (position)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  FOREIGN KEY (club_id) REFERENCES clubs(club_id),
  INDEX idx_club_id (club_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
  FOREIGN KEY (coach_id) REFERENCES coaches(coach_id),
  INDEX idx_athlete_id (athlete_id),
  INDEX idx_training_date (training_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
  FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
  INDEX idx_athlete_id (athlete_id),
  INDEX idx_game_id (game_id),
  UNIQUE KEY unique_athlete_game (athlete_id, game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

CREATE TABLE athlete_coach (
  athlete_id INT NOT NULL,
  coach_id INT NOT NULL,
  assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  role_in_coaching VARCHAR(100),
  PRIMARY KEY (athlete_id, coach_id),
  FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
  FOREIGN KEY (coach_id) REFERENCES coaches(coach_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Stored Procedures
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

DELIMITER ;

-- Insert test data
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES
('athlete@test.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'John', 'Athlete', 'athlete'),
('coach@test.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'James', 'Coach', 'coach'),
('club@test.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Sarah', 'Manager', 'club'),
('manager@test.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Mike', 'Director', 'manager');
