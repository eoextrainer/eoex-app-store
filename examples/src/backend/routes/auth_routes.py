from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_service = AuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = auth_service.authenticate_user(email, password)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = auth_service.generate_token(user['user_id'], user['email'], user['role'])
    if not token:
        return jsonify({'error': 'Token generation failed'}), 500
    
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
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    role = data.get('role', 'athlete').strip()
    
    if not all([email, password, first_name, last_name]):
        return jsonify({'error': 'Missing required fields: email, password, first_name, last_name'}), 400
    
    if role not in ['athlete', 'coach', 'club', 'manager']:
        return jsonify({'error': 'Invalid role. Must be: athlete, coach, club, or manager'}), 400
    
    success, result = auth_service.create_user(email, password, first_name, last_name, role)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': result
        }), 201
    else:
        return jsonify({'error': result}), 400

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user information"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    payload = auth_service.verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    user = auth_service.get_user_by_id(payload['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'user_id': user['user_id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role'],
            'created_at': str(user['created_at'])
        }
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change password for authenticated user"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    payload = auth_service.verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Old password and new password required'}), 400
    
    success, message = auth_service.change_password(payload['user_id'], old_password, new_password)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'error': message}), 400

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token_endpoint():
    """Verify if a token is valid"""
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'Token required'}), 400
    
    payload = auth_service.verify_token(data['token'])
    
    if payload:
        return jsonify({
            'valid': True,
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload['role']
        }), 200
    else:
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401
