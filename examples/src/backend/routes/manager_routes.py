from flask import Blueprint, jsonify
from db_connection import DatabaseConnection

manager_bp = Blueprint('manager', __name__, url_prefix='/api/v1/managers')
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

@manager_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@token_required
def get_manager_dashboard(current_user_id, current_user_role, user_id):
    """Get manager dashboard with profile, club coaches, players, and news"""
    
    # Get manager profile
    manager_query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name, u.photo_url,
            m.manager_id, m.specialization, m.experience_years, m.bio, m.photo_url as mgr_photo
        FROM users u
        JOIN managers m ON u.user_id = m.user_id
        WHERE u.user_id = %s AND u.role = 'manager'
    """
    manager = db.fetch_one(manager_query, (user_id,))
    
    if not manager:
        return jsonify({'error': 'Manager not found'}), 404
    
    # Get manager's club
    club_query = """
        SELECT 
            cl.club_id, cl.name, cl.location, cl.founded_year,
            cl.contact_email, cl.website, cl.bio, cl.logo_url
        FROM clubs cl
        WHERE cl.club_id = (SELECT club_id FROM managers WHERE manager_id = %s)
    """
    club = db.fetch_one(club_query, (manager['manager_id'],))
    
    # Get all coaches for the club with performance metrics
    coaches_query = """
        SELECT 
            c.coach_id, u.user_id, u.first_name, u.last_name, u.photo_url,
            c.specialization, c.years_experience, c.certification_level,
            COUNT(DISTINCT ac.athlete_id) as athletes_managed,
            AVG(
                COALESCE((
                    SELECT AVG(s.points) 
                    FROM statistics s 
                    JOIN games g ON s.game_id = g.game_id
                    WHERE g.status = 'completed'
                ), 0)
            ) as avg_team_points
        FROM coaches c
        JOIN users u ON c.user_id = u.user_id
        LEFT JOIN athlete_coach ac ON c.coach_id = ac.coach_id
        WHERE c.club_id = (SELECT club_id FROM managers WHERE manager_id = %s)
        GROUP BY c.coach_id, u.user_id, u.first_name, u.last_name, u.photo_url,
                 c.specialization, c.years_experience, c.certification_level
        ORDER BY COUNT(DISTINCT ac.athlete_id) DESC
    """
    coaches = db.fetch_all(coaches_query, (manager['manager_id'],))
    
    # Get all players with statistics (ranked)
    players_query = """
        SELECT 
            a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url,
            a.position, a.jersey_number,
            COUNT(DISTINCT s.game_id) as games_played,
            COALESCE(AVG(s.points), 0) as avg_points,
            COALESCE(SUM(s.points), 0) as total_points,
            COALESCE(AVG(s.rebounds), 0) as avg_rebounds,
            COALESCE(AVG(s.assists), 0) as avg_assists,
            COALESCE(SUM(s.rebounds), 0) as total_rebounds
        FROM athletes a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN statistics s ON a.athlete_id = s.athlete_id
        WHERE a.club_id = (SELECT club_id FROM managers WHERE manager_id = %s)
        GROUP BY a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url,
                 a.position, a.jersey_number
        ORDER BY COALESCE(SUM(s.points), 0) DESC
    """
    players = db.fetch_all(players_query, (manager['manager_id'],))
    
    # Get latest news and industry news
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
        'manager': manager,
        'club': club,
        'coaches': coaches if coaches else [],
        'players': players if players else [],
        'news': news if news else []
    }), 200

@manager_bp.route('/profile/<int:user_id>', methods=['GET'])
@token_required
def get_manager_profile(current_user_id, current_user_role, user_id):
    """Get manager profile information"""
    
    query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name, u.photo_url,
            m.manager_id, m.specialization, m.experience_years, m.bio
        FROM users u
        JOIN managers m ON u.user_id = m.user_id
        WHERE u.user_id = %s
    """
    manager = db.fetch_one(query, (user_id,))
    
    if not manager:
        return jsonify({'error': 'Manager not found'}), 404
    
    return jsonify({'success': True, 'manager': manager}), 200
