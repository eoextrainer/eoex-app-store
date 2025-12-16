from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.athlete_routes import athlete_bp
from routes.coach_routes import coach_bp
from routes.club_routes import club_bp
from routes.manager_routes import manager_bp

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(athlete_bp)
app.register_blueprint(coach_bp)
app.register_blueprint(club_bp)
app.register_blueprint(manager_bp)

# Serve static frontend files
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Dunes CMS API',
        'version': '1.0.0'
    }), 200

# API Version endpoint
@app.route('/api/v1', methods=['GET'])
def api_version():
    return jsonify({
        'service': 'Dunes Be One Basketball CMS',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'authentication': '/api/v1/auth',
            'athletes': '/api/v1/athletes',
            'coaches': '/api/v1/coaches',
            'clubs': '/api/v1/clubs',
            'games': '/api/v1/games',
            'training': '/api/v1/training',
            'statistics': '/api/v1/statistics',
            'news': '/api/v1/news'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized - authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden - insufficient permissions'}), 403

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
