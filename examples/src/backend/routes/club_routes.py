from flask import Blueprint, jsonify
from db_connection import DatabaseConnection

club_bp = Blueprint('club', __name__, url_prefix='/api/v1/clubs')
db = DatabaseConnection()

def token_required(f):
    """Decorator to check JWT token"""
    from functools import wraps
    from flask import request
    import jwt
    import os
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_role = data['role']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, current_user_role, *args, **kwargs)
    return decorated

@club_bp.route('/dashboard/<int:club_id>', methods=['GET'])
@token_required
def get_club_dashboard(current_user_id, current_user_role, club_id):
    """Get club dashboard with info, coaches, players, and news"""
    
    # Get club information
    club_query = """
        SELECT 
            club_id, name, location, founded_year,
            contact_email, website, bio, logo_url
        FROM clubs
        WHERE club_id = %s
    """
    club = db.fetch_one(club_query, (club_id,))
    
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    
    # Get all coaches for the club with their statistics
    coaches_query = """
        SELECT 
            c.coach_id, u.user_id, u.first_name, u.last_name, u.photo_url,
            c.specialization, c.years_experience,
            COUNT(DISTINCT ac.athlete_id) as athletes_managed,
            COUNT(DISTINCT s.game_id) as total_games_coached
        FROM coaches c
        JOIN users u ON c.user_id = u.user_id
        LEFT JOIN athlete_coach ac ON c.coach_id = ac.coach_id
        LEFT JOIN games g ON (g.home_club_id = c.club_id OR g.away_club_id = c.club_id) AND g.status = 'completed'
        LEFT JOIN statistics s ON g.game_id = s.game_id
        WHERE c.club_id = %s
        GROUP BY c.coach_id, u.user_id, u.first_name, u.last_name, u.photo_url, c.specialization, c.years_experience
        ORDER BY COUNT(DISTINCT ac.athlete_id) DESC
    """
    coaches = db.fetch_all(coaches_query, (club_id,))
    
    # Get all players for the club with statistics (ranked)
    players_query = """
        SELECT 
            a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url,
            a.position, a.jersey_number,
            COUNT(DISTINCT s.game_id) as games_played,
            COALESCE(AVG(s.points), 0) as avg_points,
            COALESCE(SUM(s.points), 0) as total_points,
            COALESCE(AVG(s.rebounds), 0) as avg_rebounds,
            COALESCE(AVG(s.assists), 0) as avg_assists
        FROM athletes a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN statistics s ON a.athlete_id = s.athlete_id
        WHERE a.club_id = %s
        GROUP BY a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url, 
                 a.position, a.jersey_number
        ORDER BY COALESCE(SUM(s.points), 0) DESC
    """
    players = db.fetch_all(players_query, (club_id,))
    
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
    
    return jsonify({
        'success': True,
        'club': club,
        'coaches': coaches if coaches else [],
        'players': players if players else [],
        'news': news if news else []
    }), 200

@club_bp.route('/info/<int:club_id>', methods=['GET'])
@token_required
def get_club_info(current_user_id, current_user_role, club_id):
    """Get club information"""
    
    query = """
        SELECT 
            club_id, name, location, founded_year,
            contact_email, website, bio, logo_url
        FROM clubs
        WHERE club_id = %s
    """
    club = db.fetch_one(query, (club_id,))
    
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    
    return jsonify({'success': True, 'club': club}), 200
