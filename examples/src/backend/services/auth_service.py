import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from db_connection import DatabaseConnection

class AuthService:
    """
    Authentication service for user login, registration, and token management
    """
    def __init__(self):
        self.db = DatabaseConnection()
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

    def hash_password(self, password):
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            print(f"Password hashing error: {e}")
            return None

    def verify_password(self, password, password_hash):
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def create_user(self, email, password, first_name, last_name, role='athlete'):
        """Create a new user account"""
        if not email or not password or not first_name or not last_name:
            return False, "Missing required fields"
        
        # Check if email already exists
        existing_user = self.db.fetch_one(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )
        if existing_user:
            return False, "Email already registered"
        
        password_hash = self.hash_password(password)
        if not password_hash:
            return False, "Password hashing failed"
        
        query = """
        INSERT INTO users (email, password_hash, first_name, last_name, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            user_id = self.db.insert(query, 
                (email, password_hash, first_name, last_name, role))
            if user_id:
                return True, user_id
            else:
                return False, "Failed to create user"
        except Exception as e:
            return False, str(e)

    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        if not email or not password:
            return None
        
        query = """
        SELECT user_id, email, password_hash, first_name, last_name, role 
        FROM users WHERE email = %s
        """
        user = self.db.fetch_one(query, (email,))
        
        if user and self.verify_password(password, user['password_hash']):
            return {
                'user_id': user['user_id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            }
        return None

    def generate_token(self, user_id, email, role):
        """Generate JWT token for authenticated user"""
        try:
            payload = {
                'user_id': user_id,
                'email': email,
                'role': role,
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
        except Exception as e:
            print(f"Token generation error: {e}")
            return None

    def verify_token(self, token):
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user information by user_id"""
        query = """
        SELECT user_id, email, first_name, last_name, role, created_at
        FROM users WHERE user_id = %s
        """
        return self.db.fetch_one(query, (user_id,))

    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        # Get current password hash
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Verify old password
        query = "SELECT password_hash FROM users WHERE user_id = %s"
        result = self.db.fetch_one(query, (user_id,))
        if not result or not self.verify_password(old_password, result['password_hash']):
            return False, "Current password is incorrect"
        
        # Hash and update new password
        new_hash = self.hash_password(new_password)
        if not new_hash:
            return False, "Password hashing failed"
        
        update_query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        affected = self.db.update(update_query, (new_hash, user_id))
        
        if affected > 0:
            return True, "Password changed successfully"
        else:
            return False, "Failed to update password"
