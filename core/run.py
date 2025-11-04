#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Triagem Farmaceutica
Pharm-Assist - Interface moderna para triagem farmacêutica
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def install_requirements():
    """Instala as dependências necessárias"""
    requirements_path = PROJECT_ROOT / "requirements.txt"
    if not requirements_path.exists():
        print("❌ Arquivo requirements.txt não encontrado.")
        print(f"   Caminho esperado: {requirements_path}")
        return False

    print("Instalando/verificando dependências do requirements.txt...")

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
            cwd=str(PROJECT_ROOT)
        )
        print("Dependências conforme requirements.txt instaladas/verificadas ✅")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['uploads', 'reports', 'instance']
    
    for directory in directories:
        target_dir = PROJECT_ROOT / directory
        target_dir.mkdir(parents=True, exist_ok=True)
    
    print("Diretórios criados/verificados")

def check_database():
    """Verifica se o banco de dados existe"""
    db_path = PROJECT_ROOT / "instance" / "triagem_farmaceutica.db"
    
    if db_path.exists():
        print("Banco de dados encontrado")
        return True
    else:
        print("Banco de dados será criado automaticamente")
        return False

def start_system():
    """Inicia o sistema"""
    print("Iniciando Pharm-Assist...")
    
    # Criar diretórios
    create_directories()
    
    # Verificar banco
    check_database()
    
    # Configurar variáveis de ambiente
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_DEBUG'] = 'True'
    
    try:
        # Importar e executar a aplicação
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))

        from core.app import app
        
        print("Sistema iniciado com sucesso!")
        print("Abrindo navegador automaticamente...")
        
        # Aguardar um pouco para o sistema inicializar
        time.sleep(2)
        
        # Abrir navegador
        webbrowser.open('http://localhost:5000')
        
        print("Pharm-Assist está rodando em: http://localhost:5000")
        print("Para parar: Pressione Ctrl+C")
        
        # Executar a aplicação
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        print("Verifique se todas as dependências estão instaladas")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("Pharm-Assist - Sistema de Triagem Farmaceutica")
    print("=" * 60)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return
    
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detectado")

    # Garantir execução a partir da raiz do projeto
    os.chdir(PROJECT_ROOT)
    
    # Instalar dependências se necessário
    if not install_requirements():
        print("Falha na instalação das dependências")
        return
    
    # Iniciar sistema
    if not start_system():
        print("Falha ao iniciar o sistema")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistema interrompido pelo usuário")
        print("Até logo!")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        print("Verifique os logs para mais detalhes")
