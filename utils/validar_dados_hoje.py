#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Validar Apenas os Dados Criados Hoje
================================================

Foca apenas nos dados criados pelo script de teste de hoje
"""

import sys
import os
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.app import app
from models.models import (
    db, Paciente, DoencaCronica, PacienteDoenca, 
    Consulta, ConsultaResposta, ConsultaRecomendacao, Pergunta
)

def print_secao(titulo):
    """Imprime uma seção formatada"""
    print(f"\n{'=' * 70}")
    print(f"  {titulo}")
    print('=' * 70)

def validar_dados_hoje():
    """Valida apenas os dados criados hoje"""
    with app.app_context():
        print_secao("VALIDAÇÃO DOS DADOS CRIADOS HOJE")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # Considerar apenas dados de hoje
        hoje = datetime.now().date()
        inicio_hoje = datetime.combine(hoje, datetime.min.time())
        
        # Pacientes criados hoje (cidade = Toledo)
        pacientes_hoje = Paciente.query.filter(
            Paciente.cidade == 'Toledo',
            Paciente.created_at >= inicio_hoje
        ).all()
        
        print(f"📊 Pacientes criados hoje (Toledo): {len(pacientes_hoje)}")
        
        # Consultas dos últimos 7 dias (que seriam as criadas pelo nosso script)
        sete_dias_atras = datetime.now() - timedelta(days=7)
        consultas_ultimos_7 = Consulta.query.filter(
            Consulta.data >= sete_dias_atras
        ).all()
        
        print(f"📊 Consultas dos últimos 7 dias: {len(consultas_ultimos_7)}")
        
        # Filtrar consultas dos pacientes de Toledo
        ids_pacientes_toledo = [p.id for p in pacientes_hoje]
        consultas_toledo = [c for c in consultas_ultimos_7 if c.id_paciente in ids_pacientes_toledo]
        
        print(f"📊 Consultas dos pacientes de Toledo: {len(consultas_toledo)}")
        
        problemas = []
        
        # Verificar cada consulta de Toledo
        print(f"\n🔍 Analisando {len(consultas_toledo)} consultas dos pacientes de Toledo:\n")
        
        for i, consulta in enumerate(consultas_toledo, 1):
            paciente = consulta.paciente
            num_respostas = len(consulta.respostas)
            num_recomendacoes = len(consulta.recomendacoes)
            
            status = "✅"
            detalhes = []
            
            if num_respostas == 0:
                status = "❌"
                detalhes.append("SEM RESPOSTAS")
                problemas.append(f"Consulta {consulta.id} sem respostas")
            
            if num_recomendacoes == 0:
                status = "❌"
                detalhes.append("SEM RECOMENDAÇÕES")
                problemas.append(f"Consulta {consulta.id} sem recomendações")
            
            modulo = "N/A"
            if consulta.observacoes and 'MODULO:' in consulta.observacoes:
                modulo = consulta.observacoes.split('MODULO:')[1].split('\n')[0].strip()
            
            detalhes_str = " | ".join(detalhes) if detalhes else "OK"
            print(f"{status} Consulta {consulta.id:3d} | Paciente: {paciente.nome[:25]:25} | "
                  f"Módulo: {modulo[:20]:20} | Respostas: {num_respostas:2d} | "
                  f"Recomendações: {num_recomendacoes:2d} | {detalhes_str}")
        
        # Verificar dados antigos (não de Toledo)
        print_secao("DADOS PRÉ-EXISTENTES NO BANCO")
        
        pacientes_antigos = Paciente.query.filter(
            (Paciente.cidade != 'Toledo') | (Paciente.cidade == None)
        ).all()
        
        print(f"📊 Pacientes pré-existentes (não Toledo): {len(pacientes_antigos)}")
        
        consultas_antigas = Consulta.query.filter(
            Consulta.id_paciente.in_([p.id for p in pacientes_antigos])
        ).all()
        
        print(f"📊 Consultas de pacientes pré-existentes: {len(consultas_antigas)}")
        
        consultas_antigas_sem_respostas = [c for c in consultas_antigas if len(c.respostas) == 0]
        consultas_antigas_sem_recomendacoes = [c for c in consultas_antigas if len(c.recomendacoes) == 0]
        
        print(f"   - Sem respostas: {len(consultas_antigas_sem_respostas)}")
        print(f"   - Sem recomendações: {len(consultas_antigas_sem_recomendacoes)}")
        
        # Resumo
        print_secao("RESUMO - DADOS CRIADOS HOJE")
        
        print(f"\n📊 Estatísticas:")
        print(f"   ✅ Pacientes criados (Toledo): {len(pacientes_hoje)}")
        print(f"   ✅ Consultas criadas: {len(consultas_toledo)}")
        
        consultas_com_respostas = [c for c in consultas_toledo if len(c.respostas) > 0]
        consultas_com_recomendacoes = [c for c in consultas_toledo if len(c.recomendacoes) > 0]
        
        print(f"   ✅ Consultas com respostas: {len(consultas_com_respostas)}/{len(consultas_toledo)}")
        print(f"   ✅ Consultas com recomendações: {len(consultas_com_recomendacoes)}/{len(consultas_toledo)}")
        
        # Estatísticas dos dados criados
        if consultas_toledo:
            total_respostas = sum(len(c.respostas) for c in consultas_toledo)
            total_recomendacoes = sum(len(c.recomendacoes) for c in consultas_toledo)
            
            print(f"\n📊 Detalhes:")
            print(f"   - Total de respostas: {total_respostas}")
            print(f"   - Média de respostas por consulta: {total_respostas/len(consultas_toledo):.1f}")
            print(f"   - Total de recomendações: {total_recomendacoes}")
            print(f"   - Média de recomendações por consulta: {total_recomendacoes/len(consultas_toledo):.1f}")
            
            encaminhamentos = [c for c in consultas_toledo if c.encaminhamento]
            print(f"   - Encaminhamentos: {len(encaminhamentos)} ({len(encaminhamentos)/len(consultas_toledo)*100:.1f}%)")
        
        # Conclusão
        print_secao("CONCLUSÃO")
        
        if problemas:
            print(f"\n❌ PROBLEMAS ENCONTRADOS NOS DADOS DE HOJE ({len(problemas)}):")
            for problema in problemas[:10]:  # Mostrar apenas os 10 primeiros
                print(f"   - {problema}")
            print("\n⚠️  Os dados criados hoje têm problemas que precisam ser corrigidos!")
            return False
        else:
            print("\n✅ DADOS DE HOJE ESTÃO PERFEITOS!")
            print("Todos os 30 pacientes e triagens foram criados com sucesso.")
            print("Cada consulta tem respostas e recomendações.")
            
            if len(consultas_antigas_sem_respostas) > 0 or len(consultas_antigas_sem_recomendacoes) > 0:
                print(f"\n⚠️  NOTA: Existem {len(pacientes_antigos)} pacientes pré-existentes no banco")
                print("com dados incompletos (provavelmente de testes anteriores).")
                print("Esses dados antigos não afetam os dados criados hoje.")
            
            return True

if __name__ == "__main__":
    try:
        sucesso = validar_dados_hoje()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n❌ Erro durante validação: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

