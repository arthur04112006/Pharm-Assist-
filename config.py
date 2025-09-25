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
    
    APP_NAME = 'Pharm-Assist - Sistema de Triagem Farmaceutica'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 20
    
    # Configurações de autenticação
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    SESSION_TIMEOUT = 3600  # 1 hora em segundos