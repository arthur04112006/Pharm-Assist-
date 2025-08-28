#!/usr/bin/env python3
"""
Sistema de Triagem Farmacêutica
Arquivo principal de execução
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8+ é necessário!")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import flask_sqlalchemy
        import mysql.connector
        import reportlab
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Instalando dependências...")
        return False

def install_dependencies():
    """Instala as dependências necessárias"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def check_mysql():
    """Verifica se o MySQL está rodando"""
    try:
        import mysql.connector
        # Tentar conectar ao MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3306
        )
        conn.close()
        print("✅ MySQL está rodando")
        return True
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível conectar ao MySQL: {e}")
        print("   O sistema tentará usar SQLite como alternativa")
        return False

def setup_database():
    """Configura o banco de dados"""
    if check_mysql():
        print("📊 Configurando banco MySQL...")
        try:
            # Executar script SQL para criar banco e tabelas
            subprocess.run([
                "mysql", "-u", "root", "-e", 
                "source database/schema.sql"
            ], check=True)
            print("✅ Banco MySQL configurado!")
        except subprocess.CalledProcessError:
            print("⚠️  Erro ao configurar MySQL, usando SQLite")
            setup_sqlite()
    else:
        setup_sqlite()

def setup_sqlite():
    """Configura SQLite como alternativa"""
    print("📊 Configurando SQLite...")
    # Modificar config.py para usar SQLite
    config_content = '''import os
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
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("✅ SQLite configurado como alternativa")

def create_directories():
    """Cria diretórios necessários"""
    directories = ['uploads', 'reports', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Diretórios criados")

def start_application():
    """Inicia a aplicação Flask"""
    print("🚀 Iniciando Sistema de Triagem Farmacêutica...")
    
    # Aguardar um pouco para o servidor inicializar
    time.sleep(2)
    
    # Abrir navegador
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Navegador aberto automaticamente")
    except:
        print("🌐 Acesse: http://localhost:5000")
    
    print("\n🎉 Sistema iniciado com sucesso!")
    print("📱 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("\n" + "="*50)

def main():
    """Função principal"""
    print("🏥 Sistema de Triagem Farmacêutica")
    print("=" * 50)
    
    # Verificar versão do Python
    check_python_version()
    
    # Verificar e instalar dependências
    if not check_dependencies():
        if not install_dependencies():
            print("❌ Falha ao instalar dependências")
            sys.exit(1)
    
    # Verificar MySQL
    check_mysql()
    
    # Configurar banco de dados
    setup_database()
    
    # Criar diretórios
    create_directories()
    
    # Iniciar aplicação
    try:
        start_application()
        
        # Executar Flask
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Sistema parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
