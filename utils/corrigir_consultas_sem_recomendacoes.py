#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Corrigir Consultas Sem Recomendações
=================================================

Adiciona recomendações não-farmacológicas nas consultas
que ficaram sem recomendações devido a módulos sem medicamentos.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.app import app
from models.models import db, Consulta, ConsultaRecomendacao

def corrigir_consultas():
    """Corrige consultas sem recomendações"""
    with app.app_context():
        print("=" * 70)
        print("  CORRIGINDO CONSULTAS SEM RECOMENDAÇÕES")
        print("=" * 70)
        
        # Buscar consultas sem recomendações
        consultas = Consulta.query.all()
        consultas_sem_recomendacoes = [c for c in consultas if len(c.recomendacoes) == 0]
        
        print(f"\nEncontradas {len(consultas_sem_recomendacoes)} consultas sem recomendações")
        
        if not consultas_sem_recomendacoes:
            print("\n✅ Todas as consultas já têm recomendações!")
            return True
        
        # Recomendações genéricas por módulo
        recomendacoes_por_modulo = {
            'queimadura_solar': [
                'Evitar exposição solar direta',
                'Hidratar bem a pele afetada',
                'Aplicar compressas frias na área afetada'
            ],
            'dismenorreia': [
                'Aplicar compressa quente no abdômen',
                'Repouso durante o período menstrual',
                'Hidratação adequada e alimentação balanceada'
            ],
            'infeccoes_fungicas': [
                'Manter a área afetada limpa e seca',
                'Evitar roupas apertadas e sintéticas',
                'Higiene adequada e troca frequente de roupas'
            ],
            'azia_ma_digestao': [
                'Evitar alimentos gordurosos e condimentados',
                'Fazer refeições menores e mais frequentes',
                'Evitar deitar logo após as refeições'
            ],
            'constipacao': [
                'Aumentar ingestão de fibras na dieta',
                'Beber bastante água (mínimo 2 litros/dia)',
                'Praticar atividade física regular'
            ]
        }
        
        corrigidas = 0
        
        for consulta in consultas_sem_recomendacoes:
            # Identificar módulo
            modulo = 'geral'
            if consulta.observacoes and 'MODULO:' in consulta.observacoes:
                modulo = consulta.observacoes.split('MODULO:')[1].split('\n')[0].strip()
            
            # Obter recomendações para o módulo
            recomendacoes = recomendacoes_por_modulo.get(
                modulo,
                ['Repouso adequado', 'Hidratação', 'Observar evolução dos sintomas']
            )
            
            print(f"\n  Corrigindo Consulta {consulta.id} (Módulo: {modulo})")
            
            # Adicionar recomendações
            for rec_texto in recomendacoes:
                recomendacao = ConsultaRecomendacao(
                    id_consulta=consulta.id,
                    tipo='nao_farmacologico',
                    descricao=rec_texto,
                    justificativa='Recomendação geral de autocuidado'
                )
                db.session.add(recomendacao)
                print(f"    + {rec_texto}")
            
            corrigidas += 1
        
        # Commit das alterações
        db.session.commit()
        
        print(f"\n{'=' * 70}")
        print(f"✅ {corrigidas} consultas corrigidas com sucesso!")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    try:
        corrigir_consultas()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

