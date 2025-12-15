from flask import Blueprint, jsonify, request
from services.auth_service import AuthService
from db_connection import DatabaseConnection
from functools import wraps
import jwt
import os

athlete_bp = Blueprint('athlete', __name__, url_prefix='/api/v1/athletes')
auth_service = AuthService()
db = DatabaseConnection()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt_secret = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
            data = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            current_user_id = data['user_id']
            current_user_role = data['role']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated

@athlete_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@token_required
def get_athlete_dashboard(current_user_id, current_user_role, user_id):
    """Get complete athlete dashboard data"""
    
    # Get athlete profile
    athlete_query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name,
            a.athlete_id, a.position, a.height, a.weight, a.birthdate,
            a.jersey_number, a.bio
        FROM users u
        JOIN athletes a ON u.user_id = a.user_id
        WHERE u.user_id = %s AND u.role = 'athlete'
    """
    athlete = db.fetch_one(athlete_query, (user_id,))
    
    if not athlete:
        return jsonify({'error': 'Athlete not found'}), 404
    
    # Get athlete statistics
    stats_query = """
        SELECT 
            COUNT(DISTINCT s.game_id) as games_played,
            COALESCE(AVG(s.points), 0) as avg_points,
            COALESCE(AVG(s.rebounds), 0) as avg_rebounds,
            COALESCE(AVG(s.assists), 0) as avg_assists,
            COALESCE(AVG(s.steals), 0) as avg_steals,
            COALESCE(AVG(s.blocks), 0) as avg_blocks,
            COALESCE(SUM(s.points), 0) as total_points,
            COALESCE(SUM(s.rebounds), 0) as total_rebounds,
            COALESCE(SUM(s.assists), 0) as total_assists
        FROM statistics s
        WHERE s.athlete_id = %s
    """
    statistics = db.fetch_one(stats_query, (athlete['athlete_id'],))
    
    # Get athlete's club
    club_query = """
        SELECT 
            c.club_id, c.name, c.location, c.founded_year,
            c.contact_email, c.website, c.bio
        FROM clubs c
        JOIN athletes a ON c.club_id = a.club_id
        WHERE a.athlete_id = %s
    """
    club = db.fetch_one(club_query, (athlete['athlete_id'],))
    
    # Get latest news
    news_query = """
        SELECT 
            news_id, title, content, category, 
            created_at, is_published
        FROM news
        WHERE is_published = 1
        ORDER BY created_at DESC
        LIMIT 5
    """
    news = db.fetch_all(news_query)
    
    # Get recent games
    games_query = """
        SELECT 
            g.game_id, g.game_date, g.location, g.status,
            g.home_score, g.away_score,
            hc.name as home_team, ac.name as away_team,
            s.points, s.rebounds, s.assists, s.minutes_played
        FROM games g
        LEFT JOIN clubs hc ON g.home_club_id = hc.club_id
        LEFT JOIN clubs ac ON g.away_club_id = ac.club_id
        LEFT JOIN statistics s ON g.game_id = s.game_id AND s.athlete_id = %s
        WHERE s.athlete_id = %s
        ORDER BY g.game_date DESC
        LIMIT 5
    """
    recent_games = db.fetch_all(games_query, (athlete['athlete_id'], athlete['athlete_id']))
    
    return jsonify({
        'success': True,
        'athlete': athlete,
        'statistics': statistics,
        'club': club,
        'news': news if news else [],
        'recent_games': recent_games if recent_games else []
    }), 200

@athlete_bp.route('/profile/<int:user_id>', methods=['GET'])
@token_required
def get_athlete_profile(current_user_id, current_user_role, user_id):
    """Get athlete profile information"""
    
    query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name,
            a.athlete_id, a.position, a.height, a.weight, a.birthdate,
            a.jersey_number, a.bio
        FROM users u
        JOIN athletes a ON u.user_id = a.user_id
        WHERE u.user_id = %s
    """
    athlete = db.fetch_one(query, (user_id,))
    
    if not athlete:
        return jsonify({'error': 'Athlete not found'}), 404
    
    return jsonify({'success': True, 'athlete': athlete}), 200
