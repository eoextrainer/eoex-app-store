#!/usr/bin/env python3
"""
Populate demo data for Dunes Be One Basketball CMS
Creates: 4 clubs, 8 managers (2 per club), 16 coaches (4 per club), 40 athletes (10 per club)
Plus statistics, training, games, and news for each
"""

import mysql.connector
from mysql.connector import Error
import bcrypt
import random
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Database config
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'dunes_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dunes_user_pass_123')
DB_NAME = os.getenv('DB_NAME', 'dunes_cms')
DB_PORT = int(os.getenv('DB_PORT', 3306))

# Password for all demo users
DEMO_PASSWORD = 'StrongPass123!'
PASSWORD_HASH = bcrypt.hashpw(DEMO_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Random data generators
FIRST_NAMES = [
    "James", "Michael", "David", "Robert", "William", "Richard", "Joseph", "Thomas",
    "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Edward",
    "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Young", "Allen"
]

CLUB_NAMES = [
    "Phoenix Vipers",
    "Miami Heat Squad",
    "Los Angeles Lakers Elite",
    "Boston Celtics Pride"
]

CLUB_CITIES = [
    "Phoenix, AZ",
    "Miami, FL",
    "Los Angeles, CA",
    "Boston, MA"
]

POSITIONS = ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"]

CERTIFICATIONS = ["Level 1", "Level 2", "Level 3", "National Coach", "FIBA Certified"]

NEWS_TITLES = [
    "Outstanding Performance in Recent Game",
    "New Training Program Launched",
    "Player Achievement Recognition",
    "Team Victory Celebration",
    "Athlete Selected for Regional Tournament",
    "Coach Milestone Celebration",
    "Club Championship Victory",
    "New Recruitment Campaign",
    "Player Development Success",
    "Regional Rankings Update"
]

NEWS_CONTENT = [
    "Fantastic performance by our athletes this week!",
    "New training initiatives show promising results.",
    "Our team continues to excel in regional competitions.",
    "Great news from the coaching staff on player development.",
    "Excited to announce upcoming championship matches.",
    "Club infrastructure improvements completed.",
    "Player stats show significant improvement.",
    "Community engagement events scheduled."
]

def get_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_insert(conn, query, data):
    cursor = conn.cursor()
    try:
        cursor.execute(query, data)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Insert error: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()

def create_user(conn, email, password_hash, first_name, last_name, role):
    query = """
    INSERT INTO users (email, password_hash, first_name, last_name, role)
    VALUES (%s, %s, %s, %s, %s)
    """
    user_id = execute_insert(conn, query, (email, password_hash, first_name, last_name, role))
    return user_id

def create_club(conn, name, location):
    query = """
    INSERT INTO clubs (name, location, founded_year, contact_email, website)
    VALUES (%s, %s, %s, %s, %s)
    """
    website = f"www.{name.lower().replace(' ', '')}.com"
    club_id = execute_insert(conn, query, (name, location, 2020, f"info@{name.lower().replace(' ', '')}.com", website))
    return club_id

def create_athlete(conn, user_id, position, height, weight):
    query = """
    INSERT INTO athletes (user_id, position, height, weight, bio)
    VALUES (%s, %s, %s, %s, %s)
    """
    bio = f"Professional basketball player specializing in {position}."
    athlete_id = execute_insert(conn, query, (user_id, position, height, weight, bio))
    return athlete_id

def create_coach(conn, user_id, specialization, certification_level):
    query = """
    INSERT INTO coaches (user_id, specialization, certification_level, bio)
    VALUES (%s, %s, %s, %s)
    """
    bio = f"Experienced coach with expertise in {specialization}."
    coach_id = execute_insert(conn, query, (user_id, specialization, certification_level, bio))
    return coach_id

def create_game(conn, home_club_id, away_club_id, home_score, away_score):
    query = """
    INSERT INTO games (home_club_id, away_club_id, game_date, status, home_score, away_score)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    game_date = datetime.now() - timedelta(days=random.randint(1, 30))
    game_id = execute_insert(conn, query, (home_club_id, away_club_id, game_date, 'completed', home_score, away_score))
    return game_id

def create_statistics(conn, athlete_id, game_id, points, rebounds, assists, steals, blocks):
    query = """
    INSERT INTO statistics (athlete_id, game_id, points, rebounds, assists, steals, blocks)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    stat_id = execute_insert(conn, query, (athlete_id, game_id, points, rebounds, assists, steals, blocks))
    return stat_id

def create_training(conn, athlete_id, coach_id, training_date, duration, training_type):
    query = """
    INSERT INTO training (athlete_id, coach_id, training_date, duration, type, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    notes = f"Training session for {training_type} development."
    training_id = execute_insert(conn, query, (athlete_id, coach_id, training_date, duration, training_type, notes))
    return training_id

def create_news(conn, title, content, category, created_by_user_id):
    query = """
    INSERT INTO news (title, content, category, created_by_user_id)
    VALUES (%s, %s, %s, %s)
    """
    news_id = execute_insert(conn, query, (title, content, category, created_by_user_id))
    return news_id

def assign_coach_to_athlete(conn, athlete_id, coach_id):
    query = """
    INSERT INTO athlete_coach (athlete_id, coach_id)
    VALUES (%s, %s)
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query, (athlete_id, coach_id))
        conn.commit()
    except Error as e:
        print(f"Assignment error: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    conn = connect_db()
    if not conn:
        return
    
    print("Starting database population...")
    
    # Store all users for reporting
    all_users = []
    
    # Create 4 clubs
    clubs = []
    for i, club_name in enumerate(CLUB_NAMES):
        club_id = create_club(conn, club_name, CLUB_CITIES[i])
        if club_id:
            clubs.append({'id': club_id, 'name': club_name})
            print(f"✓ Created club: {club_name}")
    
    # For each club, create 2 managers, 4 coaches, 10 athletes
    for club in clubs:
        club_id = club['id']
        club_name = club['name']
        
        # Create 2 managers per club
        managers = []
        for m in range(2):
            first_name, last_name = get_random_name().split()
            email = f"manager{m+1}_{club_name.lower().replace(' ', '')}" + str(random.randint(100, 999)) + "@dunes.com"
            user_id = create_user(conn, email, PASSWORD_HASH, first_name, last_name, 'manager')
            if user_id:
                managers.append(user_id)
                all_users.append({
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'role': 'Manager',
                    'club': club_name,
                    'password': DEMO_PASSWORD
                })
                print(f"  ✓ Created manager: {first_name} {last_name} ({email})")
        
        # Create 4 coaches per club
        coaches = []
        for c in range(4):
            first_name, last_name = get_random_name().split()
            email = f"coach{c+1}_{club_name.lower().replace(' ', '')}" + str(random.randint(100, 999)) + "@dunes.com"
            user_id = create_user(conn, email, PASSWORD_HASH, first_name, last_name, 'coach')
            if user_id:
                coaches.append(user_id)
                coach_id = create_coach(conn, user_id, random.choice(POSITIONS), random.choice(CERTIFICATIONS))
                all_users.append({
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'role': 'Coach',
                    'club': club_name,
                    'password': DEMO_PASSWORD
                })
                print(f"  ✓ Created coach: {first_name} {last_name} ({email})")
        
        # Create 10 athletes per club
        athletes = []
        for a in range(10):
            first_name, last_name = get_random_name().split()
            email = f"player{a+1}_{club_name.lower().replace(' ', '')}" + str(random.randint(100, 999)) + "@dunes.com"
            user_id = create_user(conn, email, PASSWORD_HASH, first_name, last_name, 'athlete')
            if user_id:
                height = random.randint(180, 220)
                weight = random.randint(80, 130)
                athlete_id = create_athlete(conn, user_id, random.choice(POSITIONS), height, weight)
                athletes.append({'id': athlete_id, 'user_id': user_id})
                all_users.append({
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'role': 'Athlete',
                    'club': club_name,
                    'password': DEMO_PASSWORD
                })
                print(f"  ✓ Created athlete: {first_name} {last_name} ({email})")
                
                # Assign random coaches to each athlete
                for coach_user_id in random.sample(coaches, min(2, len(coaches))):
                    cursor = conn.cursor()
                    cursor.execute("SELECT coach_id FROM coaches WHERE user_id = %s", (coach_user_id,))
                    result = cursor.fetchone()
                    cursor.close()
                    if result:
                        coach_db_id = result[0]
                        assign_coach_to_athlete(conn, athlete_id, coach_db_id)
        
        # Create games and statistics
        if len(clubs) > 1:
            other_clubs = [c for c in clubs if c['id'] != club_id]
            if other_clubs:
                away_club = random.choice(other_clubs)
                for g in range(3):  # 3 games per club
                    home_score = random.randint(70, 120)
                    away_score = random.randint(70, 120)
                    game_id = create_game(conn, club_id, away_club['id'], home_score, away_score)
                    
                    if game_id and athletes:
                        # Add statistics for random athletes
                        for athlete in random.sample(athletes, min(5, len(athletes))):
                            create_statistics(
                                conn,
                                athlete['id'],
                                game_id,
                                random.randint(5, 35),  # points
                                random.randint(1, 15),  # rebounds
                                random.randint(1, 10),  # assists
                                random.randint(0, 5),   # steals
                                random.randint(0, 5)    # blocks
                            )
                        print(f"  ✓ Created game with statistics")
        
        # Create training sessions
        if coaches and athletes:
            for t in range(5):
                training_date = datetime.now() - timedelta(days=random.randint(1, 60))
                coach_user_id = random.choice(coaches)
                athlete = random.choice(athletes)
                
                cursor = conn.cursor()
                cursor.execute("SELECT coach_id FROM coaches WHERE user_id = %s", (coach_user_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    coach_db_id = result[0]
                    create_training(
                        conn,
                        athlete['id'],
                        coach_db_id,
                        training_date,
                        random.randint(60, 180),  # duration in minutes
                        random.choice(['Conditioning', 'Shooting', 'Ball Handling', 'Defense', 'Strength'])
                    )
                    print(f"  ✓ Created training session")
        
        # Create news
        if managers:
            for n in range(3):
                create_news(
                    conn,
                    random.choice(NEWS_TITLES),
                    random.choice(NEWS_CONTENT),
                    'update',
                    random.choice(managers)
                )
                print(f"  ✓ Created news item")
    
    conn.close()
    
    # Print user table
    print("\n" + "="*120)
    print("USER CREDENTIALS TABLE - All users can log in with password: 'StrongPass123!'")
    print("="*120)
    print(f"{'#':<4} {'Name':<25} {'Email':<45} {'Role':<12} {'Club':<25}")
    print("-"*120)
    
    for i, user in enumerate(all_users, 1):
        print(f"{i:<4} {user['name']:<25} {user['email']:<45} {user['role']:<12} {user['club']:<25}")
    
    print("="*120)
    print(f"Total users created: {len(all_users)}")
    print("="*120)

if __name__ == '__main__':
    main()
