import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ===== CONFIGURAÇÕES BÁSICAS =====
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ===== CONFIGURAÇÕES DO BANCO DE DADOS =====
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "triagem_farmaceutica.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ===== CONFIGURAÇÕES DE ARQUIVOS =====
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    REPORTS_FOLDER = 'reports'
    
    # ===== CONFIGURAÇÕES DA APLICAÇÃO =====
    APP_NAME = 'Pharm-Assist - Sistema de Triagem Farmaceutica'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 20
    
    # ===== CONFIGURAÇÕES DE CACHE =====
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # ===== CONFIGURAÇÕES DE SEGURANÇA =====
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    
    # ===== CONFIGURAÇÕES DE LOGGING =====
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(basedir, 'logs', 'app.log')
    
    # ===== CONFIGURAÇÕES DE PAGINAÇÃO =====
    MAX_ITEMS_PER_PAGE = 100
    DEFAULT_ITEMS_PER_PAGE = 20
    
    # ===== CONFIGURAÇÕES DE TRIAGEM =====
    MAX_QUESTIONS_PER_MODULE = 50
    SCORING_THRESHOLD_HIGH = 30.0
    SCORING_THRESHOLD_MEDIUM = 15.0
    SCORING_THRESHOLD_LOW = 0.0
