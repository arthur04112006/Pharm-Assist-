#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Sistema de Triagem Farmacêutica
Aplicação Flask principal com otimizações de performance

Este arquivo é um wrapper que importa a aplicação principal do novo local.
"""

from core.app import app

if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas se não existirem
        from models.models import db
        db.create_all()
        
        # Criar usuário administrador padrão
        from core.app import create_admin_user
        create_admin_user()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
