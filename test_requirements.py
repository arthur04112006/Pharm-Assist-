#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se todas as dependências estão instaladas corretamente
"""

import sys

dependencies = [
    'flask',
    'flask_sqlalchemy',
    'sqlalchemy',
    'reportlab',
    'dotenv',
    'sklearn',
    'numpy',
    'pandas',
    'werkzeug',
    'unidecode'
]

missing = []
installed = []

print("Verificando dependencias...\n")

for dep in dependencies:
    try:
        module = __import__(dep)
        version = getattr(module, '__version__', 'N/A')
        installed.append((dep, version))
        print(f"[OK] {dep:20} - versao {version}")
    except ImportError:
        missing.append(dep)
        print(f"[ERRO] {dep:20} - NAO INSTALADO")

print("\n" + "="*50)

if missing:
    print(f"\n[ERRO] {len(missing)} dependencia(s) faltando:")
    for dep in missing:
        print(f"   - {dep}")
    print("\nExecute: pip install -r requirements.txt")
    sys.exit(1)
else:
    print(f"\n[OK] Todas as {len(installed)} dependencias estao instaladas!")
    
    # Teste de importação do app
    try:
        print("\nTestando importacao do app...")
        from core.app import app
        print("[OK] App importado com sucesso!")
        print("\nTudo pronto para rodar o projeto!")
    except Exception as e:
        print(f"❌ Erro ao importar app: {e}")
        sys.exit(1)

