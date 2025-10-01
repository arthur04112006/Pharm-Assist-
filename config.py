import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Usar SQLite como alternativa - caminho absoluto
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "triagem_farmaceutica.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    REPORTS_FOLDER = 'reports'
    
    APP_NAME = 'Pharm-Assist - Sistema de Triagem Farmaceutica'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 20
