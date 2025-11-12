#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Validar Dados de Teste no Banco de Dados
====================================================

Verifica a consistência e integridade dos dados criados
pelo script popular_banco_teste.py
"""

import sys
import os
from datetime import datetime, timedelta
from collections import Counter

# Adicionar o diretório raiz ao path
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

def validar_dados():
    """Função principal de validação"""
    with app.app_context():
        problemas = []
        avisos = []
        
        print_secao("VALIDAÇÃO DE DADOS DO BANCO DE DADOS")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # ==========================================
        # 1. VALIDAR PACIENTES
        # ==========================================
        print_secao("1. VALIDAÇÃO DE PACIENTES")
        
        pacientes = Paciente.query.all()
        print(f"Total de pacientes: {len(pacientes)}")
        
        if len(pacientes) == 0:
            problemas.append("❌ Nenhum paciente encontrado no banco de dados!")
        
        # Verificar campos obrigatórios
        for p in pacientes:
            if not p.nome:
                problemas.append(f"❌ Paciente {p.id} sem nome")
            if not p.idade or p.idade < 0 or p.idade > 150:
                problemas.append(f"❌ Paciente {p.id} ({p.nome}) com idade inválida: {p.idade}")
            if p.sexo not in ['M', 'F', 'O']:
                problemas.append(f"❌ Paciente {p.id} ({p.nome}) com sexo inválido: {p.sexo}")
            if not p.cidade:
                avisos.append(f"⚠️  Paciente {p.id} ({p.nome}) sem cidade")
        
        # Estatísticas de pacientes
        pacientes_por_idade = {
            'Crianças (0-12)': len([p for p in pacientes if p.idade <= 12]),
            'Adolescentes (13-17)': len([p for p in pacientes if 13 <= p.idade <= 17]),
            'Adultos (18-59)': len([p for p in pacientes if 18 <= p.idade <= 59]),
            'Idosos (60+)': len([p for p in pacientes if p.idade >= 60])
        }
        
        pacientes_por_sexo = {
            'Masculino': len([p for p in pacientes if p.sexo == 'M']),
            'Feminino': len([p for p in pacientes if p.sexo == 'F']),
            'Outro': len([p for p in pacientes if p.sexo == 'O'])
        }
        
        print("\n📊 Distribuição por faixa etária:")
        for faixa, count in pacientes_por_idade.items():
            print(f"   - {faixa}: {count}")
        
        print("\n📊 Distribuição por gênero:")
        for genero, count in pacientes_por_sexo.items():
            print(f"   - {genero}: {count}")
        
        # Verificar cidade
        cidades = Counter([p.cidade for p in pacientes if p.cidade])
        print(f"\n📊 Cidades:")
        for cidade, count in cidades.items():
            print(f"   - {cidade}: {count}")
        
        if 'Toledo' not in cidades:
            problemas.append("❌ Nenhum paciente da cidade Toledo encontrado!")
        
        # Verificar doenças crônicas
        pacientes_com_doencas = [p for p in pacientes if len(p.doencas_cronicas) > 0]
        print(f"\n📊 Pacientes com doenças crônicas: {len(pacientes_com_doencas)}")
        
        print("\n✅ Validação de pacientes concluída")
        
        # ==========================================
        # 2. VALIDAR CONSULTAS
        # ==========================================
        print_secao("2. VALIDAÇÃO DE CONSULTAS")
        
        consultas = Consulta.query.all()
        print(f"Total de consultas: {len(consultas)}")
        
        if len(consultas) == 0:
            problemas.append("❌ Nenhuma consulta encontrada no banco de dados!")
        
        # Verificar datas nos últimos 7 dias
        hoje = datetime.now()
        sete_dias_atras = hoje - timedelta(days=7)
        
        consultas_ultimos_7_dias = [c for c in consultas if c.data and c.data >= sete_dias_atras]
        print(f"Consultas nos últimos 7 dias: {len(consultas_ultimos_7_dias)}")
        
        if len(consultas_ultimos_7_dias) < len(consultas):
            avisos.append(f"⚠️  {len(consultas) - len(consultas_ultimos_7_dias)} consultas fora dos últimos 7 dias")
        
        # Verificar distribuição por dia
        consultas_por_dia = {}
        for c in consultas_ultimos_7_dias:
            dia = c.data.strftime('%d/%m/%Y')
            if dia not in consultas_por_dia:
                consultas_por_dia[dia] = 0
            consultas_por_dia[dia] += 1
        
        print(f"\n📊 Distribuição por dia:")
        for dia in sorted(consultas_por_dia.keys()):
            print(f"   - {dia}: {consultas_por_dia[dia]} consultas")
        
        # Verificar encaminhamentos
        encaminhamentos = [c for c in consultas if c.encaminhamento]
        taxa_encaminhamento = (len(encaminhamentos) / len(consultas) * 100) if consultas else 0
        print(f"\n📊 Encaminhamentos: {len(encaminhamentos)} ({taxa_encaminhamento:.1f}%)")
        
        if taxa_encaminhamento > 40:
            avisos.append(f"⚠️  Taxa de encaminhamento muito alta: {taxa_encaminhamento:.1f}%")
        
        # Verificar módulos utilizados
        modulos = []
        for c in consultas:
            if c.observacoes and 'MODULO:' in c.observacoes:
                modulo = c.observacoes.split('MODULO:')[1].split('\n')[0].strip()
                modulos.append(modulo)
        
        modulos_counter = Counter(modulos)
        print(f"\n📊 Distribuição por módulo:")
        for modulo, count in sorted(modulos_counter.items()):
            print(f"   - {modulo}: {count}")
        
        # Verificar se há variedade de módulos
        if len(modulos_counter) < 5:
            avisos.append(f"⚠️  Poucos módulos diferentes utilizados: {len(modulos_counter)}")
        
        print("\n✅ Validação de consultas concluída")
        
        # ==========================================
        # 3. VALIDAR RESPOSTAS
        # ==========================================
        print_secao("3. VALIDAÇÃO DE RESPOSTAS")
        
        respostas = ConsultaResposta.query.all()
        print(f"Total de respostas: {len(respostas)}")
        
        if len(respostas) == 0:
            problemas.append("❌ Nenhuma resposta encontrada no banco de dados!")
        
        # Verificar consultas sem respostas
        consultas_sem_respostas = [c for c in consultas if len(c.respostas) == 0]
        if consultas_sem_respostas:
            problemas.append(f"❌ {len(consultas_sem_respostas)} consultas sem respostas!")
            for c in consultas_sem_respostas[:5]:  # Mostrar apenas as 5 primeiras
                print(f"   - Consulta {c.id} (Paciente: {c.paciente.nome})")
        
        # Verificar média de respostas por consulta
        if consultas:
            media_respostas = len(respostas) / len(consultas)
            print(f"\n📊 Média de respostas por consulta: {media_respostas:.1f}")
            
            if media_respostas < 3:
                avisos.append(f"⚠️  Média de respostas muito baixa: {media_respostas:.1f}")
        
        # Verificar respostas vazias
        respostas_vazias = [r for r in respostas if not r.resposta or r.resposta.strip() == '']
        if respostas_vazias:
            problemas.append(f"❌ {len(respostas_vazias)} respostas vazias encontradas!")
        
        print("\n✅ Validação de respostas concluída")
        
        # ==========================================
        # 4. VALIDAR RECOMENDAÇÕES
        # ==========================================
        print_secao("4. VALIDAÇÃO DE RECOMENDAÇÕES")
        
        recomendacoes = ConsultaRecomendacao.query.all()
        print(f"Total de recomendações: {len(recomendacoes)}")
        
        if len(recomendacoes) == 0:
            problemas.append("❌ Nenhuma recomendação encontrada no banco de dados!")
        
        # Verificar consultas sem recomendações
        consultas_sem_recomendacoes = [c for c in consultas if len(c.recomendacoes) == 0]
        if consultas_sem_recomendacoes:
            problemas.append(f"❌ {len(consultas_sem_recomendacoes)} consultas sem recomendações!")
        
        # Verificar tipos de recomendações
        recomendacoes_por_tipo = {
            'Medicamento': len([r for r in recomendacoes if r.tipo == 'medicamento']),
            'Não Farmacológico': len([r for r in recomendacoes if r.tipo == 'nao_farmacologico']),
            'Encaminhamento': len([r for r in recomendacoes if r.tipo == 'encaminhamento'])
        }
        
        print(f"\n📊 Distribuição por tipo:")
        for tipo, count in recomendacoes_por_tipo.items():
            print(f"   - {tipo}: {count}")
        
        # Verificar medicamentos recomendados
        medicamentos = [r.descricao for r in recomendacoes if r.tipo == 'medicamento']
        medicamentos_counter = Counter(medicamentos)
        print(f"\n📊 Top 10 medicamentos mais recomendados:")
        for med, count in medicamentos_counter.most_common(10):
            print(f"   - {med}: {count}x")
        
        # Verificar recomendações vazias
        recomendacoes_vazias = [r for r in recomendacoes if not r.descricao or r.descricao.strip() == '']
        if recomendacoes_vazias:
            problemas.append(f"❌ {len(recomendacoes_vazias)} recomendações vazias encontradas!")
        
        print("\n✅ Validação de recomendações concluída")
        
        # ==========================================
        # 5. VALIDAR INTEGRIDADE REFERENCIAL
        # ==========================================
        print_secao("5. VALIDAÇÃO DE INTEGRIDADE REFERENCIAL")
        
        # Verificar se todas as consultas têm pacientes válidos
        consultas_sem_paciente = [c for c in consultas if not c.paciente]
        if consultas_sem_paciente:
            problemas.append(f"❌ {len(consultas_sem_paciente)} consultas sem paciente válido!")
        
        # Verificar se todas as respostas têm consultas válidas
        respostas_sem_consulta = [r for r in respostas if not r.consulta]
        if respostas_sem_consulta:
            problemas.append(f"❌ {len(respostas_sem_consulta)} respostas sem consulta válida!")
        
        # Verificar se todas as recomendações têm consultas válidas
        recomendacoes_sem_consulta = [r for r in recomendacoes if not r.consulta]
        if recomendacoes_sem_consulta:
            problemas.append(f"❌ {len(recomendacoes_sem_consulta)} recomendações sem consulta válida!")
        
        print("\n✅ Validação de integridade referencial concluída")
        
        # ==========================================
        # 6. VALIDAR DADOS PARA GRÁFICOS
        # ==========================================
        print_secao("6. VALIDAÇÃO DE DADOS PARA GRÁFICOS")
        
        # Verificar se há dados suficientes para os gráficos
        print("\n📊 Verificando dados para gráficos:")
        
        # Gráfico de consultas por dia
        if len(consultas_por_dia) > 0:
            print(f"   ✅ Consultas por dia: {len(consultas_por_dia)} dias com dados")
        else:
            problemas.append("❌ Sem dados para gráfico de consultas por dia!")
        
        # Gráfico de faixa etária
        faixas_com_dados = [v for v in pacientes_por_idade.values() if v > 0]
        print(f"   ✅ Faixas etárias: {len(faixas_com_dados)}/4 faixas com pacientes")
        
        # Gráfico de gênero
        generos_com_dados = [v for v in pacientes_por_sexo.values() if v > 0]
        print(f"   ✅ Gêneros: {generos_com_dados} gêneros com pacientes")
        
        # Gráfico de medicamentos
        if len(medicamentos_counter) > 0:
            print(f"   ✅ Medicamentos: {len(medicamentos_counter)} medicamentos diferentes recomendados")
        else:
            avisos.append("⚠️  Nenhum medicamento recomendado!")
        
        # Gráfico de módulos
        if len(modulos_counter) > 0:
            print(f"   ✅ Módulos: {len(modulos_counter)} módulos diferentes utilizados")
        else:
            problemas.append("❌ Nenhum módulo identificado nas consultas!")
        
        print("\n✅ Validação de dados para gráficos concluída")
        
        # ==========================================
        # RESUMO FINAL
        # ==========================================
        print_secao("RESUMO DA VALIDAÇÃO")
        
        print(f"\n📊 Estatísticas Gerais:")
        print(f"   - Pacientes: {len(pacientes)}")
        print(f"   - Consultas: {len(consultas)}")
        print(f"   - Respostas: {len(respostas)}")
        print(f"   - Recomendações: {len(recomendacoes)}")
        print(f"   - Encaminhamentos: {len(encaminhamentos)} ({taxa_encaminhamento:.1f}%)")
        
        if avisos:
            print(f"\n⚠️  AVISOS ENCONTRADOS ({len(avisos)}):")
            for aviso in avisos:
                print(f"   {aviso}")
        
        if problemas:
            print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(problemas)}):")
            for problema in problemas:
                print(f"   {problema}")
            print("\n❌ VALIDAÇÃO FALHOU - Corrija os problemas acima!")
            return False
        else:
            if avisos:
                print(f"\n✅ VALIDAÇÃO PASSOU COM AVISOS")
                print("Os dados estão consistentes, mas há alguns avisos não críticos.")
            else:
                print(f"\n✅ VALIDAÇÃO PASSOU SEM PROBLEMAS!")
                print("Todos os dados estão consistentes e prontos para uso!")
            return True

if __name__ == "__main__":
    try:
        sucesso = validar_dados()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n❌ Erro durante validação: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

