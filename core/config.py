"""
Config - Configurações da aplicação
==================================

Este módulo contém todas as configurações da aplicação Pharm-Assist,
incluindo configurações de banco de dados, uploads, relatórios e outras
configurações específicas do sistema.

Configurações principais:
- SECRET_KEY: Chave secreta para sessões
- DEBUG: Modo de debug
- SQLALCHEMY_DATABASE_URI: URI do banco de dados
- UPLOAD_FOLDER: Diretório para uploads
- REPORTS_FOLDER: Diretório para relatórios
- APP_NAME: Nome da aplicação
- APP_VERSION: Versão da aplicação
- ITEMS_PER_PAGE: Itens por página na paginação
"""

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
