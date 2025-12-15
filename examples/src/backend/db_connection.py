import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """
    Database connection manager for MySQL operations
    """
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'dunes_user')
        self.password = os.getenv('DB_PASSWORD', 'dunes_user_pass_123')
        self.database = os.getenv('DB_NAME', 'dunes_cms')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=False
            )
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"Successfully connected to MySQL Server version {db_info}")
                print(f"Connected to database: {self.database}")
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def get_connection(self):
        """Get active connection, reconnect if necessary"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    def execute_query(self, query, params=None):
        """Execute a query and return cursor"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Error as e:
            print(f"Query execution error: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch all results from query"""
        cursor = self.execute_query(query, params)
        if cursor:
            results = cursor.fetchall()
            cursor.close()
            return results
        return None

    def fetch_one(self, query, params=None):
        """Fetch single result from query"""
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            return result
        return None

    def insert(self, query, params=None):
        """Insert record and return inserted id"""
        try:
            cursor = self.get_connection().cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            inserted_id = cursor.lastrowid
            cursor.close()
            return inserted_id
        except Error as e:
            self.connection.rollback()
            print(f"Insert error: {e}")
            return None

    def update(self, query, params=None):
        """Update records"""
        try:
            cursor = self.get_connection().cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Error as e:
            self.connection.rollback()
            print(f"Update error: {e}")
            return 0

    def delete(self, query, params=None):
        """Delete records"""
        try:
            cursor = self.get_connection().cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Error as e:
            self.connection.rollback()
            print(f"Delete error: {e}")
            return 0

    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback transaction"""
        if self.connection:
            self.connection.rollback()

    def close(self):
        """Close connection"""
        self.disconnect()
