import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from extensions import db

from models.user import User
from models.booking import Booking
from models.trek import Trek


from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from routes.staff_routes import staff_bp
from utils.celery_app import celery_init_app  # Imported Celery helper


from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and allow requests from Vite frontend
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this-in-production"

    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)

    # Initialize Celery with Flask app context
    celery_app = celery_init_app(app)

    # Register API Blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(staff_bp)

    
    with app.app_context():
        db.create_all()
        init_admin_user()

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'Success',
            'message': 'Trekking Application Backend is running smoothly!'
        }), 200

    return app

def init_admin_user():
    admin_email = "24f2004871@ds.study.iitm.ac.in"
    existing_admin = User.query.filter_by(email=admin_email).first()

    if not existing_admin:
        admin = User(
            full_name="System Admin",
            email=admin_email,
            role="Admin",
            status="Active"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Success: Default Admin user created.")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
