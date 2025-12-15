from flask import Blueprint, jsonify
from db_connection import DatabaseConnection

coach_bp = Blueprint('coach', __name__, url_prefix='/api/v1/coaches')
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

@coach_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@token_required
def get_coach_dashboard(current_user_id, current_user_role, user_id):
    """Get coach dashboard with profile, assigned athletes with stats, club info, and news"""
    
    # Get coach profile
    coach_query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name, u.photo_url,
            c.coach_id, c.specialization, c.certification_level, c.years_experience, 
            c.bio, c.photo_url as coach_photo
        FROM users u
        JOIN coaches c ON u.user_id = c.user_id
        WHERE u.user_id = %s AND u.role = 'coach'
    """
    coach = db.fetch_one(coach_query, (user_id,))
    
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    # Get coach's club
    club_query = """
        SELECT 
            cl.club_id, cl.name, cl.location, cl.founded_year,
            cl.contact_email, cl.website, cl.bio, cl.logo_url
        FROM clubs cl
        WHERE cl.club_id = (SELECT club_id FROM coaches WHERE coach_id = %s)
    """
    club = db.fetch_one(club_query, (coach['coach_id'],))
    
    # Get assigned athletes with statistics (ranked by total points)
    athletes_query = """
        SELECT 
            a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url,
            a.position, a.jersey_number, a.height, a.weight,
            COUNT(DISTINCT s.game_id) as games_played,
            COALESCE(AVG(s.points), 0) as avg_points,
            COALESCE(AVG(s.rebounds), 0) as avg_rebounds,
            COALESCE(AVG(s.assists), 0) as avg_assists,
            COALESCE(SUM(s.points), 0) as total_points,
            COALESCE(SUM(s.rebounds), 0) as total_rebounds,
            COALESCE(SUM(s.assists), 0) as total_assists
        FROM athletes a
        JOIN users u ON a.user_id = u.user_id
        JOIN athlete_coach ac ON a.athlete_id = ac.athlete_id
        LEFT JOIN statistics s ON a.athlete_id = s.athlete_id
        WHERE ac.coach_id = %s
        GROUP BY a.athlete_id, u.user_id, u.first_name, u.last_name, u.photo_url,
                 a.position, a.jersey_number, a.height, a.weight
        ORDER BY COALESCE(SUM(s.points), 0) DESC
    """
    athletes = db.fetch_all(athletes_query, (coach['coach_id'],))
    
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
        'coach': coach,
        'club': club,
        'athletes': athletes if athletes else [],
        'news': news if news else []
    }), 200

@coach_bp.route('/profile/<int:user_id>', methods=['GET'])
@token_required
def get_coach_profile(current_user_id, current_user_role, user_id):
    """Get coach profile information"""
    
    query = """
        SELECT 
            u.user_id, u.email, u.first_name, u.last_name, u.photo_url,
            c.coach_id, c.specialization, c.certification_level, c.years_experience, c.bio
        FROM users u
        JOIN coaches c ON u.user_id = c.user_id
        WHERE u.user_id = %s
    """
    coach = db.fetch_one(query, (user_id,))
    
    if not coach:
        return jsonify({'error': 'Coach not found'}), 404
    
    return jsonify({'success': True, 'coach': coach}), 200
