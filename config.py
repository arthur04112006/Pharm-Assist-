import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Usar SQLite como alternativa
    SQLALCHEMY_DATABASE_URI = 'sqlite:///triagem_farmaceutica.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    REPORTS_FOLDER = 'reports'
    
    APP_NAME = 'Sistema de Triagem Farmacêutica'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 20
