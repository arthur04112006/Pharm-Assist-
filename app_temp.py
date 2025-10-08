#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo temporário para fazer a correção
"""

# Ler o arquivo original
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fazer as correções
content = content.replace(
    """    # Sintomas mais comuns
    sintomas_comuns = db.session.query(
        ConsultaRecomendacao.descricao,
        func.count(ConsultaRecomendacao.id).label('count')
    ).filter(
        ConsultaRecomendacao.tipo == 'nao_farmacologico'
    ).group_by(
        ConsultaRecomendacao.descricao
    ).order_by(
        func.count(ConsultaRecomendacao.id).desc()
    ).limit(10).all()""",
    """    # Sintomas mais comuns - convertido para lista de dicionários
    sintomas_comuns = db.session.query(
        ConsultaRecomendacao.descricao,
        func.count(ConsultaRecomendacao.id).label('count')
    ).filter(
        ConsultaRecomendacao.tipo == 'nao_farmacologico'
    ).group_by(
        ConsultaRecomendacao.descricao
    ).order_by(
        func.count(ConsultaRecomendacao.id).desc()
    ).limit(10).all()
    
    # Converter para lista de dicionários para serialização JSON
    sintomas_comuns = [{'descricao': s.descricao, 'count': s.count} for s in sintomas_comuns]"""
)

content = content.replace(
    """    # Medicamentos mais recomendados
    medicamentos_recomendados = db.session.query(
        ConsultaRecomendacao.descricao,
        func.count(ConsultaRecomendacao.id).label('count')
    ).filter(
        ConsultaRecomendacao.tipo == 'medicamento'
    ).group_by(
        ConsultaRecomendacao.descricao
    ).order_by(
        func.count(ConsultaRecomendacao.id).desc()
    ).limit(10).all()""",
    """    # Medicamentos mais recomendados - convertido para lista de dicionários
    medicamentos_recomendados = db.session.query(
        ConsultaRecomendacao.descricao,
        func.count(ConsultaRecomendacao.id).label('count')
    ).filter(
        ConsultaRecomendacao.tipo == 'medicamento'
    ).group_by(
        ConsultaRecomendacao.descricao
    ).order_by(
        func.count(ConsultaRecomendacao.id).desc()
    ).limit(10).all()
    
    # Converter para lista de dicionários para serialização JSON
    medicamentos_recomendados = [{'descricao': m.descricao, 'count': m.count} for m in medicamentos_recomendados]"""
)

# Salvar o arquivo corrigido
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Correção aplicada no app.py!")

