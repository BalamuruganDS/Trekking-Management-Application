import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security Secrets
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-trekking-key-2026')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'trekking_app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery & Redis Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')