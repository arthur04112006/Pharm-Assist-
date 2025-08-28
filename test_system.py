#!/usr/bin/env python3
"""
Teste do Sistema de Triagem Farmacêutica
Verifica se todos os componentes estão funcionando
"""

import sys
import os

def test_imports():
    """Testa se todas as importações estão funcionando"""
    print("🔍 Testando importações...")
    
    try:
        import flask
        print("✅ Flask importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Flask: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Flask-SQLAlchemy: {e}")
        return False
    
    try:
        import reportlab
        print("✅ ReportLab importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar ReportLab: {e}")
        return False
    
    try:
        import mysql.connector
        print("✅ MySQL Connector importado com sucesso")
    except ImportError as e:
        print(f"⚠️  MySQL Connector não disponível: {e}")
        print("   O sistema usará SQLite como alternativa")
    
    return True

def test_models():
    """Testa se os modelos podem ser importados"""
    print("\n🔍 Testando modelos...")
    
    try:
        from models import db, Paciente, DoencaCronica, Medicamento
        print("✅ Modelos importados com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}")
        return False

def test_triagem_engine():
    """Testa se o motor de triagem pode ser importado"""
    print("\n🔍 Testando motor de triagem...")
    
    try:
        from triagem_engine import TriagemEngine
        engine = TriagemEngine()
        print("✅ Motor de triagem criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar motor de triagem: {e}")
        return False

def test_report_generator():
    """Testa se o gerador de relatórios pode ser importado"""
    print("\n🔍 Testando gerador de relatórios...")
    
    try:
        from report_generator import ReportGenerator
        generator = ReportGenerator()
        print("✅ Gerador de relatórios criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar gerador de relatórios: {e}")
        return False

def test_config():
    """Testa se a configuração pode ser importada"""
    print("\n🔍 Testando configuração...")
    
    try:
        from config import Config
        print("✅ Configuração importada com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar configuração: {e}")
        return False

def test_directories():
    """Testa se os diretórios necessários existem"""
    print("\n🔍 Testando diretórios...")
    
    required_dirs = ['templates', 'uploads', 'reports', 'database']
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Diretório {directory} existe")
        else:
            print(f"❌ Diretório {directory} não existe")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n⚠️  Criando diretórios ausentes...")
        for directory in missing_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Diretório {directory} criado")
            except Exception as e:
                print(f"❌ Erro ao criar diretório {directory}: {e}")
                return False
    
    return True

def test_files():
    """Testa se os arquivos principais existem"""
    print("\n🔍 Testando arquivos principais...")
    
    required_files = [
        'app.py',
        'models.py',
        'triagem_engine.py',
        'report_generator.py',
        'config.py',
        'requirements.txt',
        'run.py',
        'database/schema.sql'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Arquivo {file_path} existe")
        else:
            print(f"❌ Arquivo {file_path} não existe")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Arquivos ausentes: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Função principal de teste"""
    print("🏥 Sistema de Triagem Farmacêutica - Teste de Sistema")
    print("=" * 60)
    
    tests = [
        ("Importações", test_imports),
        ("Modelos", test_models),
        ("Motor de Triagem", test_triagem_engine),
        ("Gerador de Relatórios", test_report_generator),
        ("Configuração", test_config),
        ("Diretórios", test_directories),
        ("Arquivos", test_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Teste '{test_name}' falhou")
        except Exception as e:
            print(f"❌ Teste '{test_name}' falhou com erro: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado dos Testes: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
        print("\n📱 Para executar o sistema:")
        print("   python3 run.py")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        print("\n🔧 Para resolver problemas:")
        print("   1. Execute: ./install.sh")
        print("   2. Ou manualmente: pip3 install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
