#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Popular o Banco de Dados com Dados de Teste
========================================================

Este script cria 30 pacientes com triagens variadas nos últimos 7 dias,
utilizando os módulos reais de triagem do sistema para gerar dados
realistas que permitam testar os gráficos e estatísticas.

Uso:
    python utils/popular_banco_teste.py
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.app import app
from models.models import (
    db, Paciente, DoencaCronica, PacienteDoenca, 
    Consulta, ConsultaResposta, ConsultaRecomendacao, Pergunta
)
from utils.extractors.perguntas_extractor import (
    extract_questions_for_module, 
    get_patient_profile_from_cadastro
)
from utils.scoring.triagem_scoring import scoring_system

# ==========================================
# CONFIGURAÇÕES E DADOS BASE
# ==========================================

# Seed para reprodutibilidade (pode ser alterado)
SEED = 42
random.seed(SEED)

# Módulos de triagem disponíveis
MODULOS_TRIAGEM = [
    'tosse',
    'febre', 
    'dor_cabeca',
    'dor_garganta',
    'diarreia',
    'constipacao',
    'azia_ma_digestao',
    'dismenorreia',
    'dor_lombar',
    'hemorroidas',
    'espirro_congestao_nasal',
    'infeccoes_fungicas',
    'queimadura_solar'
]

# Nomes brasileiros para geração de pacientes
NOMES_MASCULINOS = [
    'João Silva', 'Pedro Santos', 'Carlos Oliveira', 'Lucas Souza', 
    'Gabriel Costa', 'Rafael Lima', 'Felipe Alves', 'Bruno Pereira',
    'Rodrigo Martins', 'André Fernandes', 'Diego Rocha', 'Matheus Ribeiro',
    'Thiago Carvalho', 'Eduardo Mendes', 'Marcelo Araújo'
]

NOMES_FEMININOS = [
    'Maria Silva', 'Ana Santos', 'Juliana Oliveira', 'Fernanda Souza',
    'Camila Costa', 'Beatriz Lima', 'Larissa Alves', 'Patricia Pereira',
    'Mariana Martins', 'Amanda Fernandes', 'Bruna Rocha', 'Carolina Ribeiro',
    'Renata Carvalho', 'Aline Mendes', 'Vanessa Araújo'
]

# Bairros de Toledo - PR
BAIRROS_TOLEDO = [
    'Centro', 'Vila Becker', 'Jardim La Salle', 'Jardim Coopagro',
    'Jardim Porto Alegre', 'Vila Paulista', 'Jardim Europa', 'Parque Industrial',
    'Jardim Panorama', 'Vila Industrial', 'Jardim Gisela', 'São Francisco'
]

# Doenças crônicas comuns
DOENCAS_CRONICAS = [
    'Hipertensão', 'Diabetes', 'Asma', 'Rinite Alérgica',
    'Gastrite', 'Artrose', 'Colesterol Alto'
]

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def calcular_peso_altura(idade, sexo):
    """
    Calcula peso e altura proporcionais à idade e sexo
    
    Args:
        idade: idade em anos
        sexo: 'M', 'F' ou 'O'
        
    Returns:
        tuple: (peso, altura)
    """
    # Crianças (0-12 anos)
    if idade <= 12:
        altura = Decimal(str(round(0.75 + (idade * 0.08) + random.uniform(-0.05, 0.05), 2)))
        peso = Decimal(str(round(10 + (idade * 3) + random.uniform(-2, 2), 2)))
    # Adolescentes (13-17 anos)
    elif idade <= 17:
        altura = Decimal(str(round(1.50 + (idade - 13) * 0.05 + random.uniform(-0.05, 0.05), 2)))
        peso = Decimal(str(round(45 + (idade - 13) * 4 + random.uniform(-5, 5), 2)))
    # Adultos (18-59 anos)
    elif idade <= 59:
        if sexo == 'M':
            altura = Decimal(str(round(random.uniform(1.65, 1.85), 2)))
            peso = Decimal(str(round(random.uniform(65, 95), 2)))
        else:
            altura = Decimal(str(round(random.uniform(1.55, 1.75), 2)))
            peso = Decimal(str(round(random.uniform(50, 80), 2)))
    # Idosos (60+ anos)
    else:
        if sexo == 'M':
            altura = Decimal(str(round(random.uniform(1.60, 1.75), 2)))
            peso = Decimal(str(round(random.uniform(60, 85), 2)))
        else:
            altura = Decimal(str(round(random.uniform(1.50, 1.65), 2)))
            peso = Decimal(str(round(random.uniform(50, 75), 2)))
    
    return peso, altura


def gerar_data_aleatoria_ultimos_7_dias():
    """
    Gera uma data/hora aleatória nos últimos 7 dias
    
    Returns:
        datetime: data e hora da consulta
    """
    hoje = datetime.now()
    dias_atras = random.randint(0, 6)  # 0 a 6 dias atrás
    
    # Data base
    data_base = hoje - timedelta(days=dias_atras)
    
    # Horário variado (8h às 18h)
    hora = random.randint(8, 17)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    
    return data_base.replace(hour=hora, minute=minuto, second=segundo, microsecond=0)


def selecionar_modulo_apropriado(idade, sexo):
    """
    Seleciona um módulo de triagem apropriado para idade/sexo
    
    Args:
        idade: idade do paciente
        sexo: sexo do paciente
        
    Returns:
        str: nome do módulo
    """
    # Dismenorreia apenas para mulheres em idade fértil
    if sexo == 'F' and 12 <= idade <= 50:
        modulos = MODULOS_TRIAGEM.copy()
    else:
        modulos = [m for m in MODULOS_TRIAGEM if m != 'dismenorreia']
    
    # Queimadura solar mais comum em crianças/jovens
    if idade < 18:
        # Aumentar chance de queimadura solar
        modulos.extend(['queimadura_solar'] * 2)
    
    return random.choice(modulos)


def print_secao(titulo):
    """Imprime uma seção formatada"""
    print(f"\n{'=' * 60}")
    print(f"  {titulo}")
    print('=' * 60)


def print_progresso(atual, total, mensagem=""):
    """Imprime o progresso da operação"""
    percentual = (atual / total) * 100
    barra = '█' * int(percentual / 5) + '░' * (20 - int(percentual / 5))
    print(f"[{barra}] {percentual:.0f}% - {mensagem}", end='\r')
    if atual == total:
        print()  # Nova linha no final


# ==========================================
# FUNÇÕES PRINCIPAIS
# ==========================================

def criar_pacientes():
    """
    Cria 30 pacientes com dados variados e realistas
    
    Returns:
        list: lista de objetos Paciente criados
    """
    print_secao("CRIANDO PACIENTES")
    
    pacientes_criados = []
    
    # Garantir que temos doenças crônicas no banco
    doencas_existentes = {}
    for doenca_nome in DOENCAS_CRONICAS:
        doenca = DoencaCronica.query.filter_by(nome=doenca_nome).first()
        if not doenca:
            doenca = DoencaCronica(nome=doenca_nome, descricao=f"Doença crônica: {doenca_nome}")
            db.session.add(doenca)
            db.session.flush()
        doencas_existentes[doenca_nome] = doenca
    
    db.session.commit()
    print(f"✓ {len(doencas_existentes)} doenças crônicas disponíveis")
    
    # Distribuição de idades (garantir variedade de faixas etárias)
    distribuicao_idades = (
        list(range(5, 13)) +      # Crianças: 8 pacientes
        list(range(13, 18)) +     # Adolescentes: 5 pacientes
        list(range(18, 60)) * 2 + # Adultos: muitos pacientes (maior grupo)
        list(range(60, 86))       # Idosos: alguns pacientes
    )
    random.shuffle(distribuicao_idades)
    idades_selecionadas = distribuicao_idades[:30]
    
    # Distribuição de gêneros (equilibrada)
    distribuicao_generos = ['M'] * 13 + ['F'] * 16 + ['O'] * 1
    random.shuffle(distribuicao_generos)
    
    print(f"\nCriando 30 pacientes...")
    
    for i in range(30):
        try:
            # Selecionar nome baseado no sexo
            sexo = distribuicao_generos[i]
            if sexo == 'M':
                nome = random.choice(NOMES_MASCULINOS)
            elif sexo == 'F':
                nome = random.choice(NOMES_FEMININOS)
            else:
                nome = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)
            
            # Idade
            idade = idades_selecionadas[i]
            
            # Peso e altura proporcionais
            peso, altura = calcular_peso_altura(idade, sexo)
            
            # Hábitos (probabilidades realistas)
            fuma = random.random() < 0.15  # 15% fumantes
            bebe = random.random() < 0.30  # 30% bebem
            
            # Localização em Toledo
            bairro = random.choice(BAIRROS_TOLEDO)
            cidade = "Toledo"
            
            # Criar paciente
            paciente = Paciente(
                nome=nome,
                idade=idade,
                peso=peso,
                altura=altura,
                sexo=sexo,
                fuma=fuma,
                bebe=bebe,
                bairro=bairro,
                cidade=cidade
            )
            
            db.session.add(paciente)
            db.session.flush()  # Para obter o ID
            
            # Adicionar doenças crônicas (30% dos pacientes têm alguma doença)
            if random.random() < 0.30:
                num_doencas = random.randint(1, 2)
                doencas_selecionadas = random.sample(list(doencas_existentes.values()), num_doencas)
                
                for doenca in doencas_selecionadas:
                    paciente_doenca = PacienteDoenca(
                        id_paciente=paciente.id,
                        id_doenca_cronica=doenca.id
                    )
                    db.session.add(paciente_doenca)
            
            pacientes_criados.append(paciente)
            print_progresso(i + 1, 30, f"Paciente {i+1}/30: {nome}")
            
        except Exception as e:
            print(f"\n⚠️  Erro ao criar paciente {i+1}: {str(e)}")
            db.session.rollback()
            continue
    
    db.session.commit()
    print(f"\n✅ {len(pacientes_criados)} pacientes criados com sucesso!")
    
    # Estatísticas
    print(f"\n📊 Estatísticas dos pacientes:")
    print(f"   - Crianças (0-12): {sum(1 for p in pacientes_criados if p.idade <= 12)}")
    print(f"   - Adolescentes (13-17): {sum(1 for p in pacientes_criados if 13 <= p.idade <= 17)}")
    print(f"   - Adultos (18-59): {sum(1 for p in pacientes_criados if 18 <= p.idade <= 59)}")
    print(f"   - Idosos (60+): {sum(1 for p in pacientes_criados if p.idade >= 60)}")
    print(f"   - Masculino: {sum(1 for p in pacientes_criados if p.sexo == 'M')}")
    print(f"   - Feminino: {sum(1 for p in pacientes_criados if p.sexo == 'F')}")
    print(f"   - Outro: {sum(1 for p in pacientes_criados if p.sexo == 'O')}")
    print(f"   - Com doenças crônicas: {sum(1 for p in pacientes_criados if len(p.doencas_cronicas) > 0)}")
    
    return pacientes_criados


def gerar_respostas_para_modulo(modulo, perguntas, paciente, forcar_encaminhamento=False):
    """
    Gera respostas realistas para as perguntas do módulo
    
    Args:
        modulo: nome do módulo de triagem
        perguntas: lista de perguntas do módulo
        paciente: objeto Paciente
        forcar_encaminhamento: se True, gera respostas que levam a encaminhamento
        
    Returns:
        list: lista de dicionários com pergunta_id e resposta
    """
    respostas = []
    
    for pergunta in perguntas:
        pergunta_id = pergunta.get('id', pergunta.get('texto', ''))
        pergunta_texto = pergunta.get('texto', '').lower()
        tipo = pergunta.get('tipo', 'string')
        critica = pergunta.get('critica', False)
        
        resposta = None
        
        # Se forçar encaminhamento e a pergunta é crítica, dar resposta positiva
        if forcar_encaminhamento and critica:
            if tipo == 'bool':
                resposta = 'sim'
            elif tipo == 'number':
                resposta = str(random.randint(8, 15))  # Valor alto
            else:
                resposta = 'sim'
        
        # Caso contrário, gerar resposta baseada no tipo
        elif tipo == 'bool':
            # Perguntas críticas têm menor chance de ser "sim" (10%)
            # Perguntas normais têm 40% de chance de ser "sim"
            probabilidade_sim = 0.10 if critica else 0.40
            resposta = 'sim' if random.random() < probabilidade_sim else 'não'
        
        elif tipo == 'number':
            # Gerar números baseados no contexto da pergunta
            if 'quantos dias' in pergunta_texto or 'há quantos dias' in pergunta_texto:
                # Dias de sintoma: 1-7 dias normalmente
                resposta = str(random.randint(1, 7))
            elif 'idade' in pergunta_texto:
                resposta = str(paciente.idade)
            elif 'temperatura' in pergunta_texto or 'febre' in pergunta_texto:
                # Temperatura: 37-39°C
                resposta = str(round(random.uniform(37.5, 39.0), 1))
            elif 'intensidade' in pergunta_texto or 'escala' in pergunta_texto:
                # Escala 1-10
                resposta = str(random.randint(3, 8))
            elif 'vezes' in pergunta_texto or 'frequência' in pergunta_texto:
                # Frequência: 2-6 vezes
                resposta = str(random.randint(2, 6))
            else:
                # Número genérico
                resposta = str(random.randint(1, 10))
        
        elif tipo == 'string':
            # Respostas em texto livre baseadas no contexto
            if 'cor' in pergunta_texto:
                cores = ['amarela', 'verde', 'transparente', 'branca', 'vermelha']
                resposta = random.choice(cores)
            elif 'local' in pergunta_texto or 'onde' in pergunta_texto:
                locais = ['cabeça', 'peito', 'garganta', 'abdômen', 'costas']
                resposta = random.choice(locais)
            elif 'medicamento' in pergunta_texto:
                meds = ['paracetamol', 'ibuprofeno', 'nenhum', 'dipirona']
                resposta = random.choice(meds)
            elif 'alergia' in pergunta_texto:
                alergias = ['não tenho', 'penicilina', 'nenhuma', 'AAS']
                resposta = random.choice(alergias)
            else:
                # Resposta genérica
                respostas_genericas = ['sim', 'não', 'às vezes', 'moderado', 'leve']
                resposta = random.choice(respostas_genericas)
        
        else:
            # Tipo desconhecido, usar resposta padrão
            resposta = 'não'
        
        respostas.append({
            'pergunta_id': pergunta_id,
            'resposta': resposta
        })
    
    return respostas


def criar_triagem_completa(paciente, data_consulta):
    """
    Cria uma triagem completa para um paciente
    
    Args:
        paciente: objeto Paciente
        data_consulta: datetime da consulta
        
    Returns:
        tuple: (consulta, encaminhamento_bool, modulo_usado)
    """
    try:
        # Selecionar módulo apropriado
        modulo = selecionar_modulo_apropriado(paciente.idade, paciente.sexo)
        
        # Extrair perguntas do módulo
        try:
            perguntas = extract_questions_for_module(modulo, filter_unnecessary=True)
        except Exception as e:
            print(f"\n⚠️  Erro ao extrair perguntas do módulo {modulo}: {str(e)}")
            # Fallback: usar módulo de febre
            modulo = 'febre'
            perguntas = extract_questions_for_module(modulo, filter_unnecessary=True)
        
        if not perguntas:
            raise Exception(f"Nenhuma pergunta encontrada para o módulo {modulo}")
        
        # Decidir se forçar encaminhamento (20% de chance)
        forcar_encaminhamento = random.random() < 0.20
        
        # Gerar respostas
        respostas = gerar_respostas_para_modulo(modulo, perguntas, paciente, forcar_encaminhamento)
        
        # Criar consulta
        consulta = Consulta(
            id_paciente=paciente.id,
            data=data_consulta
        )
        db.session.add(consulta)
        db.session.flush()  # Para obter o ID
        
        # Salvar respostas no banco
        for resposta_data in respostas:
            pergunta_id_str = str(resposta_data['pergunta_id'])
            resposta_texto = resposta_data['resposta']
            
            # Tentar converter para inteiro
            try:
                pergunta_id = int(pergunta_id_str)
            except (ValueError, TypeError):
                # Se não conseguiu, criar hash
                import hashlib
                pergunta_id_hash = abs(hash(pergunta_id_str)) % 1000000
                
                # Verificar se já existe
                pergunta_existente = Pergunta.query.filter_by(id=pergunta_id_hash).first()
                
                if not pergunta_existente:
                    nova_pergunta = Pergunta(
                        id=pergunta_id_hash,
                        texto=pergunta_id_str,
                        tipo='sintoma',
                        ordem=999,
                        ativa=True
                    )
                    db.session.add(nova_pergunta)
                    db.session.flush()
                
                pergunta_id = pergunta_id_hash
            
            # Criar resposta
            resp = ConsultaResposta(
                id_consulta=consulta.id,
                id_pergunta=pergunta_id,
                resposta=resposta_texto
            )
            db.session.add(resp)
        
        # Processar através do sistema de scoring
        try:
            # Obter perfil do paciente
            paciente_data = paciente.to_dict()
            patient_profile = get_patient_profile_from_cadastro(paciente_data)
            
            # Calcular pontuação
            scoring_result = scoring_system.calculate_score(
                modulo=modulo,
                respostas=respostas,
                paciente_profile=patient_profile
            )
            
            # Gerar recomendações
            recommendations = scoring_system.generate_recommendations(
                scoring_result,
                modulo,
                respostas,
                patient_profile
            )
            
            # Separar medicamentos
            medicamentos_todos = recommendations.get('farmacologicas', [])
            medicamentos_iniciais = medicamentos_todos[:6]
            
            # Atualizar consulta com resultado
            consulta.encaminhamento = scoring_result.encaminhamento
            if scoring_result.encaminhamento:
                consulta.motivo_encaminhamento = 'Pontuação alta ou sinais críticos detectados'
            
            # Adicionar observações
            observacoes_list = [f'MODULO: {modulo}']
            observacoes_list.append(f'Pontuação total: {scoring_result.total_score:.1f}')
            observacoes_list.append(f'Nível de risco: {scoring_result.risk_level}')
            observacoes_list.append(f'Confiança: {scoring_result.confidence:.1%}')
            consulta.observacoes = '\n'.join(observacoes_list)
            
            # Salvar recomendações de medicamentos
            for med in medicamentos_iniciais:
                recomendacao = ConsultaRecomendacao(
                    id_consulta=consulta.id,
                    tipo='medicamento',
                    descricao=med,
                    justificativa=f'Baseado na pontuação: {scoring_result.total_score:.1f}'
                )
                db.session.add(recomendacao)
            
            # Salvar recomendações não farmacológicas
            nao_farmacologicas = recommendations.get('nao_farmacologicas', [])
            
            # Se não há recomendações não farmacológicas, adicionar genéricas baseadas no módulo
            if not nao_farmacologicas:
                recomendacoes_genericas = {
                    'queimadura_solar': ['Evitar exposição solar', 'Hidratar a pele', 'Compressas frias'],
                    'dismenorreia': ['Compressa quente no abdômen', 'Repouso', 'Hidratação adequada'],
                    'infeccoes_fungicas': ['Manter área limpa e seca', 'Evitar roupas apertadas', 'Higiene adequada'],
                }
                nao_farmacologicas = recomendacoes_genericas.get(modulo, ['Repouso', 'Hidratação', 'Observar evolução'])
            
            for rec in nao_farmacologicas[:3]:  # Limitar a 3
                recomendacao = ConsultaRecomendacao(
                    id_consulta=consulta.id,
                    tipo='nao_farmacologico',
                    descricao=rec,
                    justificativa='Recomendação não farmacológica'
                )
                db.session.add(recomendacao)
            
            # Adicionar recomendação de encaminhamento se necessário
            if scoring_result.encaminhamento:
                recomendacao = ConsultaRecomendacao(
                    id_consulta=consulta.id,
                    tipo='encaminhamento',
                    descricao='Encaminhamento médico necessário',
                    justificativa=consulta.motivo_encaminhamento
                )
                db.session.add(recomendacao)
            
            db.session.flush()
            
            return consulta, scoring_result.encaminhamento, modulo
            
        except Exception as e:
            print(f"\n⚠️  Erro no scoring: {str(e)}")
            # Fallback: criar consulta básica sem scoring
            consulta.encaminhamento = False
            consulta.observacoes = f'MODULO: {modulo}\nTriagem básica (erro no scoring)'
            
            # Adicionar recomendações genéricas baseadas no módulo
            recomendacoes_genericas = {
                'queimadura_solar': ['Evitar exposição solar', 'Hidratar a pele', 'Compressas frias'],
                'dismenorreia': ['Compressa quente no abdômen', 'Repouso', 'Hidratação adequada'],
                'infeccoes_fungicas': ['Manter área limpa e seca', 'Evitar roupas apertadas', 'Higiene adequada'],
            }
            recomendacoes = recomendacoes_genericas.get(modulo, ['Repouso', 'Hidratação', 'Observar evolução'])
            
            for rec in recomendacoes:
                recomendacao = ConsultaRecomendacao(
                    id_consulta=consulta.id,
                    tipo='nao_farmacologico',
                    descricao=rec,
                    justificativa='Recomendação geral'
                )
                db.session.add(recomendacao)
            
            return consulta, False, modulo
        
    except Exception as e:
        print(f"\n❌ Erro ao criar triagem: {str(e)}")
        db.session.rollback()
        raise


def popular_banco():
    """Função principal que popula o banco de dados"""
    print_secao("POPULANDO BANCO DE DADOS COM DADOS DE TESTE")
    print(f"Seed: {SEED}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    with app.app_context():
        print("\n✓ Contexto Flask iniciado")
        
        # Estatísticas
        estatisticas = {
            'pacientes_criados': 0,
            'triagens_criadas': 0,
            'encaminhamentos': 0,
            'modulos_usados': {},
            'erros': 0
        }
        
        # ETAPA 1: Criar pacientes
        pacientes = criar_pacientes()
        estatisticas['pacientes_criados'] = len(pacientes)
        
        # ETAPA 2: Criar triagens distribuídas nos últimos 7 dias
        print_secao("CRIANDO TRIAGENS")
        print(f"Criando triagens para {len(pacientes)} pacientes...")
        print("Distribuindo nos últimos 7 dias com horários variados\n")
        
        for i, paciente in enumerate(pacientes):
            try:
                # Gerar data aleatória nos últimos 7 dias
                data_consulta = gerar_data_aleatoria_ultimos_7_dias()
                
                # Criar triagem completa
                consulta, encaminhamento, modulo = criar_triagem_completa(paciente, data_consulta)
                
                # Commit após cada triagem
                db.session.commit()
                
                # Atualizar estatísticas
                estatisticas['triagens_criadas'] += 1
                if encaminhamento:
                    estatisticas['encaminhamentos'] += 1
                
                if modulo not in estatisticas['modulos_usados']:
                    estatisticas['modulos_usados'][modulo] = 0
                estatisticas['modulos_usados'][modulo] += 1
                
                # Exibir progresso
                status = '🚨' if encaminhamento else '✓'
                data_str = data_consulta.strftime('%d/%m %H:%M')
                print_progresso(
                    i + 1, 
                    len(pacientes), 
                    f"{status} Triagem {i+1}/30: {paciente.nome[:20]:20} | {modulo:25} | {data_str}"
                )
                
            except Exception as e:
                print(f"\n⚠️  Erro ao criar triagem para paciente {paciente.nome}: {str(e)}")
                estatisticas['erros'] += 1
                db.session.rollback()
                continue
        
        print(f"\n✅ {estatisticas['triagens_criadas']} triagens criadas com sucesso!")
        
        return estatisticas


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    try:
        estatisticas = popular_banco()
        
        print_secao("RESUMO DA EXECUÇÃO")
        print(f"✅ Pacientes criados: {estatisticas['pacientes_criados']}")
        print(f"✅ Triagens realizadas: {estatisticas['triagens_criadas']}")
        print(f"✅ Encaminhamentos: {estatisticas['encaminhamentos']}")
        
        if estatisticas['modulos_usados']:
            print(f"\n📊 Distribuição por módulo:")
            for modulo, count in sorted(estatisticas['modulos_usados'].items()):
                print(f"   - {modulo}: {count}")
        
        if estatisticas['erros'] > 0:
            print(f"\n⚠️  Erros encontrados: {estatisticas['erros']}")
        
        print("\n✅ Script executado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

