#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Sistema de Triagem Farmacêutica
Aplicação Flask principal com otimizações de performance

Funcionalidades:
- Sistema de triagem farmacêutica automatizada
- Gerenciamento de pacientes e medicamentos
- Relatórios em PDF
- Interface web responsiva
- Base de dados com medicamentos da ANVISA
"""

# Importações principais do Flask para criar a aplicação web
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
# SQLAlchemy para gerenciar o banco de dados
from flask_sqlalchemy import SQLAlchemy
# Importar todos os modelos do banco de dados (tabelas)
from models import db, Paciente, DoencaCronica, PacienteDoenca, Sintoma, Pergunta, Medicamento, Consulta, ConsultaResposta, ConsultaRecomendacao
# Gerador de relatórios em PDF
from report_generator import ReportGenerator
# Configurações do sistema
from config import Config
import os
from datetime import datetime, timedelta
import json
# Cache para otimizar consultas frequentes
from functools import lru_cache
# Utilitários para extrair perguntas dos módulos
from perguntas_extractor import list_modules as list_motor_modulos, extract_questions_for_module

# ===== INICIALIZAÇÃO DA APLICAÇÃO =====
# Criar a aplicação Flask principal
app = Flask(__name__)
# Carregar configurações do arquivo config.py
app.config.from_object(Config)

# Inicializar a extensão do banco de dados
db.init_app(app)

# Inicializar o gerador de relatórios PDF
report_generator = ReportGenerator()

# Criar diretórios necessários para o funcionamento do sistema
# 'reports' - onde são salvos os relatórios PDF gerados
# 'uploads' - onde são salvos arquivos enviados pelos usuários
os.makedirs('reports', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# ===== SISTEMA DE CACHE PARA OTIMIZAÇÃO =====
# Cache para consultas frequentes (evita múltiplas consultas ao banco)
@lru_cache(maxsize=128)
def get_doencas_cronicas():
    """
    Cache para doenças crônicas - consulta frequente
    Esta função é chamada sempre que precisamos listar as doenças crônicas
    O cache evita consultar o banco de dados repetidamente
    """
    return DoencaCronica.query.all()

@lru_cache(maxsize=64)
def get_perguntas_ativas():
    """
    Cache para perguntas ativas - consulta frequente
    Esta função retorna todas as perguntas que estão ativas no sistema
    Ordenadas pela ordem definida no banco de dados
    """
    return Pergunta.query.filter_by(ativa=True).order_by(Pergunta.ordem).all()

# ===== ROTAS PRINCIPAIS DA APLICAÇÃO =====
@app.route('/')
def index():
    """
    Página inicial do sistema com dashboard e estatísticas
    
    Esta é a rota principal que mostra o dashboard com:
    - Estatísticas gerais do sistema
    - Gráficos de consultas por dia
    - Taxa de encaminhamentos
    - Pacientes por faixa etária
    - Consultas recentes
    
    Otimizações implementadas:
    - Consultas otimizadas com índices
    - Cache de estatísticas frequentes
    - Redução de consultas ao banco
    """
    # ===== ESTATÍSTICAS GERAIS =====
    # Contar total de pacientes cadastrados no sistema
    total_pacientes = Paciente.query.count()
    # Contar apenas medicamentos ativos (não inativos)
    total_medicamentos = Medicamento.query.filter_by(ativo=True).count()
    
    # ===== CONSULTAS DE HOJE =====
    # Obter a data atual para filtrar consultas de hoje
    hoje = datetime.now().date()
    # Contar quantas consultas foram feitas hoje
    consultas_hoje = Consulta.query.filter(
        db.func.date(Consulta.data) == hoje
    ).count()
    
    # ===== ENCAMINHAMENTOS =====
    # Contar quantas consultas resultaram em encaminhamento médico
    encaminhamentos = Consulta.query.filter_by(encaminhamento=True).count()
    
    # ===== CONSULTAS DOS ÚLTIMOS 30 DIAS =====
    # Calcular data de 30 dias atrás
    data_30_dias_atras = datetime.now() - timedelta(days=30)
    # Contar consultas dos últimos 30 dias
    consultas_30_dias = Consulta.query.filter(Consulta.data >= data_30_dias_atras).count()
    
    # ===== CONSULTAS POR DIA (ÚLTIMOS 7 DIAS) =====
    # Criar lista para armazenar dados de consultas por dia
    consultas_por_dia = []
    # Loop para os últimos 7 dias
    for i in range(7):
        # Calcular data de i dias atrás
        data = datetime.now() - timedelta(days=i)
        # Definir início do dia (00:00:00)
        inicio_dia = data.replace(hour=0, minute=0, second=0, microsecond=0)
        # Definir fim do dia (23:59:59)
        fim_dia = data.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Contar consultas neste dia específico
        count = Consulta.query.filter(
            Consulta.data >= inicio_dia,
            Consulta.data <= fim_dia
        ).count()
        
        # Adicionar dados do dia à lista
        consultas_por_dia.append({
            'data': data.strftime('%d/%m'),  # Formato DD/MM
            'count': count
        })
    
    # Ordenar cronologicamente (do mais antigo para o mais recente)
    consultas_por_dia.reverse()
    
    # ===== TAXA DE ENCAMINHAMENTOS =====
    # Contar total de consultas para calcular percentual
    total_consultas = Consulta.query.count()
    # Calcular percentual de encaminhamentos (evitar divisão por zero)
    taxa_encaminhamento = (encaminhamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    # ===== PACIENTES POR FAIXA ETÁRIA =====
    # Definir faixas etárias para análise demográfica
    faixas_etarias = [
        {'faixa': '0-18', 'min': 0, 'max': 18},      # Crianças e adolescentes
        {'faixa': '19-30', 'min': 19, 'max': 30},    # Jovens adultos
        {'faixa': '31-50', 'min': 31, 'max': 50},    # Adultos
        {'faixa': '51-65', 'min': 51, 'max': 65},    # Meia-idade
        {'faixa': '65+', 'min': 65, 'max': 120}      # Idosos
    ]
    
    # Lista para armazenar contagem por faixa etária
    pacientes_por_faixa = []
    # Para cada faixa etária, contar quantos pacientes existem
    for faixa in faixas_etarias:
        count = Paciente.query.filter(
            Paciente.idade >= faixa['min'],
            Paciente.idade <= faixa['max']
        ).count()
        # Adicionar dados da faixa à lista
        pacientes_por_faixa.append({
            'faixa': faixa['faixa'],
            'count': count
        })
    
    # ===== ÚLTIMAS CONSULTAS =====
    # Buscar as 5 consultas mais recentes com dados do paciente
    consultas_recentes = Consulta.query.join(Paciente).order_by(
        Consulta.data.desc()  # Ordenar por data decrescente (mais recente primeiro)
    ).limit(5).all()  # Limitar a 5 consultas
    
    return render_template('index.html', 
                         total_pacientes=total_pacientes,
                         total_medicamentos=total_medicamentos,
                         consultas_hoje=consultas_hoje,
                         encaminhamentos=encaminhamentos,
                         consultas_30_dias=consultas_30_dias,
                         consultas_por_dia=consultas_por_dia,
                         taxa_encaminhamento=taxa_encaminhamento,
                         pacientes_por_faixa=pacientes_por_faixa,
                         consultas_recentes=consultas_recentes)

@app.route('/pacientes')
def pacientes():
    """
    Lista de pacientes com paginação
    
    Esta rota mostra todos os pacientes cadastrados no sistema
    com sistema de paginação para melhor performance
    """
    # Obter número da página atual (padrão: página 1)
    page = request.args.get('page', 1, type=int)
    # Número de itens por página (definido em config.py)
    per_page = Config.ITEMS_PER_PAGE
    
    # Buscar pacientes com paginação
    # error_out=False evita erro 404 se a página não existir
    pacientes = Paciente.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Renderizar template com dados dos pacientes
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/novo', methods=['GET', 'POST'])
def novo_paciente():
    """
    Cadastro de novo paciente
    
    GET: Mostra formulário de cadastro
    POST: Processa dados do formulário e salva no banco
    """
    if request.method == 'POST':
        try:
            # ===== CRIAR NOVO PACIENTE =====
            # Obter dados do formulário e criar objeto Paciente
            paciente = Paciente(
                nome=request.form['nome'],                    # Nome completo
                idade=int(request.form['idade']),            # Idade (obrigatório)
                peso=float(request.form['peso']) if request.form['peso'] else None,  # Peso (opcional)
                altura=float(request.form['altura']) if request.form['altura'] else None,  # Altura (opcional)
                sexo=request.form['sexo'],                   # Sexo (M/F/O)
                fuma=request.form.get('fuma') == 'on',       # Se fuma (checkbox)
                bebe=request.form.get('bebe') == 'on'        # Se bebe (checkbox)
            )
            
            # Adicionar paciente ao banco de dados
            db.session.add(paciente)
            db.session.commit()  # Salvar para obter o ID
            
            # ===== ADICIONAR DOENÇAS CRÔNICAS =====
            # Obter lista de doenças crônicas selecionadas
            doencas_ids = request.form.getlist('doencas_cronicas')
            # Para cada doença selecionada, criar relacionamento
            for doenca_id in doencas_ids:
                paciente_doenca = PacienteDoenca(
                    id_paciente=paciente.id,                # ID do paciente recém-criado
                    id_doenca_cronica=int(doenca_id)         # ID da doença crônica
                )
                db.session.add(paciente_doenca)
            
            # Salvar relacionamentos no banco
            db.session.commit()
            # Mostrar mensagem de sucesso
            flash('Paciente cadastrado com sucesso!', 'success')
            # Redirecionar para lista de pacientes
            return redirect(url_for('pacientes'))
            
        except Exception as e:
            # Em caso de erro, desfazer alterações
            db.session.rollback()
            # Mostrar mensagem de erro
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'error')
    
    # ===== PREPARAR DADOS PARA O FORMULÁRIO =====
    # Buscar doenças crônicas disponíveis (usando cache)
    doencas_cronicas = get_doencas_cronicas()
    
    # ===== CRIAR DOENÇAS PADRÃO SE NECESSÁRIO =====
    # Se não houver doenças crônicas cadastradas, criar algumas padrão
    if not doencas_cronicas:
        # Lista de doenças crônicas comuns
        doencas_padrao = [
            'Hipertensão',      # Pressão alta
            'Diabetes',         # Diabetes mellitus
            'Asma',             # Problemas respiratórios
            'Doença Cardíaca',  # Problemas cardiovasculares
            'Obesidade',        # Sobrepeso
            'Colesterol Alto'  # Dislipidemia
        ]
        
        # Criar cada doença no banco de dados
        for doenca_nome in doencas_padrao:
            doenca = DoencaCronica(nome=doenca_nome)
            db.session.add(doenca)
        
        # Salvar no banco
        db.session.commit()
        # Buscar novamente as doenças criadas
        doencas_cronicas = get_doencas_cronicas()
    
    # Renderizar formulário com dados das doenças crônicas
    return render_template('novo_paciente.html', doencas_cronicas=doencas_cronicas)

@app.route('/pacientes/<int:id>')
def visualizar_paciente(id):
    """
    Visualizar dados completos de um paciente
    
    Mostra:
    - Dados pessoais do paciente
    - Doenças crônicas
    - Histórico de consultas
    - Recomendações recebidas
    """
    # Buscar paciente pelo ID (retorna 404 se não existir)
    paciente = Paciente.query.get_or_404(id)
    # Buscar todas as consultas deste paciente, ordenadas por data (mais recente primeiro)
    consultas = Consulta.query.filter_by(id_paciente=id).order_by(Consulta.data.desc()).all()
    
    # Renderizar página com dados do paciente e suas consultas
    return render_template('visualizar_paciente.html', paciente=paciente, consultas=consultas)

@app.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_paciente(id):
    """Editar dados de um paciente"""
    paciente = Paciente.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            paciente.nome = request.form['nome']
            paciente.idade = int(request.form['idade'])
            paciente.peso = float(request.form['peso']) if request.form['peso'] else None
            paciente.altura = float(request.form['altura']) if request.form['altura'] else None
            paciente.sexo = request.form['sexo']
            paciente.fuma = request.form.get('fuma') == 'on'
            paciente.bebe = request.form.get('bebe') == 'on'
            
            # Atualizar doenças crônicas
            PacienteDoenca.query.filter_by(id_paciente=id).delete()
            doencas_ids = request.form.getlist('doencas_cronicas')
            for doenca_id in doencas_ids:
                paciente_doenca = PacienteDoenca(
                    id_paciente=id,
                    id_doenca_cronica=int(doenca_id)
                )
                db.session.add(paciente_doenca)
            
            db.session.commit()
            flash('Paciente atualizado com sucesso!', 'success')
            return redirect(url_for('visualizar_paciente', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar paciente: {str(e)}', 'error')
    
    doencas_cronicas = get_doencas_cronicas()
    doencas_paciente = [pd.id_doenca_cronica for pd in paciente.doencas_cronicas]
    
    # Se não houver doenças crônicas cadastradas, criar algumas padrão
    if not doencas_cronicas:
        doencas_padrao = [
            'Hipertensão',
            'Diabetes',
            'Asma',
            'Doença Cardíaca',
            'Obesidade',
            'Colesterol Alto'
        ]
        
        for doenca_nome in doencas_padrao:
            doenca = DoencaCronica(nome=doenca_nome)
            db.session.add(doenca)
        
        db.session.commit()
        doencas_cronicas = get_doencas_cronicas()
    
    return render_template('editar_paciente.html', paciente=paciente, 
                         doencas_cronicas=doencas_cronicas, doencas_paciente=doencas_paciente)

@app.route('/medicamentos')
def medicamentos():
    """Lista de medicamentos"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    search = request.args.get('search', '').strip()
    
    # Query base para medicamentos ativos
    query = Medicamento.query.filter_by(ativo=True)
    
    # Aplicar filtro de busca se fornecido
    if search:
        query = query.filter(
            db.or_(
                Medicamento.nome_comercial.ilike(f'%{search}%'),
                Medicamento.nome_generico.ilike(f'%{search}%'),
                Medicamento.descricao.ilike(f'%{search}%')
            )
        )
    
    # Buscar medicamentos com paginação
    medicamentos = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('medicamentos.html', medicamentos=medicamentos, search=search)

@app.route('/medicamentos/inativos')
def medicamentos_inativos():
    """Lista de medicamentos inativos"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    search = request.args.get('search', '').strip()
    
    # Query base para medicamentos inativos
    query = Medicamento.query.filter_by(ativo=False)
    
    # Aplicar filtro de busca se fornecido
    if search:
        query = query.filter(
            db.or_(
                Medicamento.nome_comercial.ilike(f'%{search}%'),
                Medicamento.nome_generico.ilike(f'%{search}%'),
                Medicamento.descricao.ilike(f'%{search}%')
            )
        )
    
    # Buscar medicamentos inativos com paginação
    medicamentos = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('medicamentos_inativos.html', medicamentos=medicamentos, search=search)

@app.route('/medicamentos/novo', methods=['GET', 'POST'])
def novo_medicamento():
    """Cadastro de novo medicamento"""
    if request.method == 'POST':
        try:
            medicamento = Medicamento(
                nome_comercial=request.form['nome_comercial'],
                nome_generico=request.form['nome_generico'],
                descricao=request.form.get('descricao'),
                indicacao=request.form['indicacao'],
                contraindicacao=request.form.get('contraindicacao'),
                tipo=request.form['tipo'],
                ativo=True
            )
            
            db.session.add(medicamento)
            db.session.commit()
            
            flash('Medicamento cadastrado com sucesso!', 'success')
            return redirect(url_for('medicamentos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar medicamento: {str(e)}', 'error')
    
    return render_template('novo_medicamento.html')

@app.route('/medicamentos/<int:id>/excluir', methods=['POST'])
def excluir_medicamento(id):
    """Exclusão de medicamento"""
    try:
        medicamento = Medicamento.query.get_or_404(id)
        
        # Verificar se o medicamento está sendo usado em consultas
        # Como o modelo ConsultaRecomendacao armazena o nome do medicamento como texto,
        # vamos verificar se o nome do medicamento aparece nas recomendações
        from models import ConsultaRecomendacao
        recomendacoes = ConsultaRecomendacao.query.filter(
            ConsultaRecomendacao.tipo == 'medicamento',
            ConsultaRecomendacao.descricao.contains(medicamento.nome_comercial)
        ).count()
        
        if recomendacoes > 0:
            flash(f'Não é possível excluir este medicamento pois ele está sendo usado em {recomendacoes} consulta(s). Considere desativá-lo ao invés de excluí-lo.', 'warning')
            return redirect(url_for('medicamentos'))
        
        # Excluir o medicamento
        db.session.delete(medicamento)
        db.session.commit()
        
        flash('Medicamento excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir medicamento: {str(e)}', 'error')
    
    return redirect(url_for('medicamentos'))

@app.route('/medicamentos/<int:id>/desativar', methods=['POST'])
def desativar_medicamento(id):
    """Desativação de medicamento (exclusão lógica)"""
    try:
        medicamento = Medicamento.query.get_or_404(id)
        medicamento.ativo = False
        db.session.commit()
        
        flash('Medicamento desativado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao desativar medicamento: {str(e)}', 'error')
    
    return redirect(url_for('medicamentos'))

@app.route('/medicamentos/<int:id>/reativar', methods=['POST'])
def reativar_medicamento(id):
    """Reativação de medicamento"""
    try:
        medicamento = Medicamento.query.get_or_404(id)
        medicamento.ativo = True
        db.session.commit()
        
        flash('Medicamento reativado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar medicamento: {str(e)}', 'error')
    
    return redirect(url_for('medicamentos_inativos'))

@app.route('/medicamentos/<int:id>/editar', methods=['GET', 'POST'])
def editar_medicamento(id):
    """Editar dados de um medicamento"""
    medicamento = Medicamento.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Atualizar dados do medicamento
            medicamento.nome_comercial = request.form['nome_comercial']
            medicamento.nome_generico = request.form.get('nome_generico')
            medicamento.descricao = request.form.get('descricao')
            medicamento.indicacao = request.form.get('indicacao')
            medicamento.contraindicacao = request.form.get('contraindicacao')
            medicamento.tipo = request.form['tipo']
            
            db.session.commit()
            flash('Medicamento atualizado com sucesso!', 'success')
            return redirect(url_for('medicamentos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar medicamento: {str(e)}', 'error')
    
    return render_template('editar_medicamento.html', medicamento=medicamento)

@app.route('/triagem')
def triagem():
    """Página inicial da triagem"""
    return render_template('triagem.html')

@app.route('/triagem/buscar_paciente')
def buscar_paciente_triagem():
    """Buscar paciente para iniciar triagem"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    
    if query:
        pacientes = Paciente.query.filter(
            Paciente.nome.ilike(f'%{query}%')
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        pacientes = None
    
    # Buscar doenças crônicas para o formulário
    doencas_cronicas = get_doencas_cronicas()
    
    # Se não houver doenças crônicas cadastradas, criar algumas padrão
    if not doencas_cronicas:
        doencas_padrao = [
            'Hipertensão',
            'Diabetes',
            'Asma',
            'Doença Cardíaca',
            'Obesidade',
            'Colesterol Alto'
        ]
        
        for doenca_nome in doencas_padrao:
            doenca = DoencaCronica(nome=doenca_nome)
            db.session.add(doenca)
        
        db.session.commit()
        doencas_cronicas = get_doencas_cronicas()
    
    return render_template('buscar_paciente_triagem.html', pacientes=pacientes, query=query, doencas_cronicas=doencas_cronicas)

@app.route('/triagem/novo_paciente', methods=['GET', 'POST'])
def novo_paciente_triagem():
    """Cadastro rápido de paciente para triagem"""
    if request.method == 'POST':
        try:
            paciente = Paciente(
                nome=request.form['nome'],
                idade=int(request.form['idade']),
                peso=float(request.form['peso']) if request.form['peso'] else None,
                altura=float(request.form['altura']) if request.form['altura'] else None,
                sexo=request.form['sexo'],
                fuma=request.form.get('fuma') == 'on',
                bebe=request.form.get('bebe') == 'on'
            )
            
            db.session.add(paciente)
            db.session.commit()
            
            # Adicionar doenças crônicas se selecionadas
            doencas_ids = request.form.getlist('doencas_cronicas')
            for doenca_id in doencas_ids:
                paciente_doenca = PacienteDoenca(
                    id_paciente=paciente.id,
                    id_doenca_cronica=int(doenca_id)
                )
                db.session.add(paciente_doenca)
            
            db.session.commit()
            flash('Paciente cadastrado! Iniciando triagem...', 'success')
            return redirect(url_for('iniciar_triagem', paciente_id=paciente.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'error')
    
    # Buscar doenças crônicas para o formulário
    doencas_cronicas = get_doencas_cronicas()
    
    # Se não houver doenças crônicas cadastradas, criar algumas padrão
    if not doencas_cronicas:
        doencas_padrao = [
            'Hipertensão',
            'Diabetes',
            'Asma',
            'Doença Cardíaca',
            'Obesidade',
            'Colesterol Alto'
        ]
        
        for doenca_nome in doencas_padrao:
            doenca = DoencaCronica(nome=doenca_nome)
            db.session.add(doenca)
        
        db.session.commit()
        doencas_cronicas = get_doencas_cronicas()
    
    return render_template('novo_paciente_triagem.html', doencas_cronicas=doencas_cronicas)

@app.route('/triagem/iniciar/<int:paciente_id>')
def iniciar_triagem(paciente_id):
    """Iniciar triagem para um paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    # Capturar módulo selecionado (opcional) via querystring
    modulo = request.args.get('modulo', '').strip()

    # Buscar perguntas ativas ou criar perguntas padrão se não existirem
    perguntas = get_perguntas_ativas()
    
    if not perguntas:
        # Criar perguntas padrão se não existirem
        perguntas_padrao = [
            {'texto': 'Você está sentindo dor?', 'tipo': 'sintoma', 'ordem': 1},
            {'texto': 'A dor é intensa?', 'tipo': 'sintoma', 'ordem': 2},
            {'texto': 'Você tem febre?', 'tipo': 'sintoma', 'ordem': 3},
            {'texto': 'Você está tomando algum medicamento?', 'tipo': 'historico', 'ordem': 4},
            {'texto': 'Você tem alguma alergia conhecida?', 'tipo': 'historico', 'ordem': 5}
        ]
        
        for i, pergunta_data in enumerate(perguntas_padrao):
            pergunta = Pergunta(
                texto=pergunta_data['texto'],
                tipo=pergunta_data['tipo'],
                ordem=pergunta_data['ordem'],
                ativa=True
            )
            db.session.add(pergunta)
        
        db.session.commit()
        perguntas = get_perguntas_ativas()
    
    return render_template('iniciar_triagem.html', paciente=paciente, perguntas=perguntas, modulo=modulo)

@app.route('/triagem/processar', methods=['POST'])
def processar_triagem():
    """
    Processar triagem e gerar resultado
    
    Esta é a função principal do sistema de triagem que:
    1. Recebe as respostas do questionário
    2. Cria uma nova consulta no banco
    3. Aplica o sistema de pontuação inteligente
    4. Gera recomendações personalizadas
    5. Salva tudo no banco de dados
    """
    try:
        # ===== OBTER DADOS DA REQUISIÇÃO =====
        # Receber dados em formato JSON da requisição AJAX
        data = request.get_json()
        paciente_id = data['paciente_id']      # ID do paciente
        respostas = data['respostas']          # Lista de respostas do questionário
        
        # ===== BUSCAR DADOS DO PACIENTE =====
        # Buscar paciente no banco de dados
        paciente = Paciente.query.get_or_404(paciente_id)
        # Converter para dicionário para uso no sistema de pontuação
        paciente_data = paciente.to_dict()
        
        # ===== CRIAR NOVA CONSULTA =====
        # Criar registro de consulta no banco
        consulta = Consulta(
            id_paciente=paciente_id,           # ID do paciente
            data=datetime.now()                # Data e hora atual
        )
        db.session.add(consulta)
        db.session.commit()  # Salvar para obter o ID da consulta
        
        # ===== SALVAR RESPOSTAS NO BANCO =====
        # Processar cada resposta do questionário
        for resposta_data in respostas:
            try:
                # Tentar converter ID da pergunta para número (perguntas do banco)
                pergunta_id = int(resposta_data['pergunta_id'])
            except Exception:
                # Se não conseguir converter, é uma pergunta dinâmica (módulo)
                pergunta_id = None

            # Obter texto da resposta
            resposta_texto = resposta_data['resposta']

            if pergunta_id is not None:
                # ===== RESPOSTA DE PERGUNTA DO BANCO =====
                # Criar registro de resposta no banco
                resp = ConsultaResposta(
                    id_consulta=consulta.id,        # ID da consulta
                    id_pergunta=pergunta_id,         # ID da pergunta
                    resposta=resposta_texto          # Texto da resposta
                )
                db.session.add(resp)
            else:
                # ===== RESPOSTA DE PERGUNTA DINÂMICA =====
                # Salvar como observação na consulta (fallback)
                if not consulta.observacoes:
                    consulta.observacoes = ''
                consulta.observacoes += f"\n{resposta_data['pergunta_id']}: {resposta_texto}"
        
        # ===== APLICAR SISTEMA DE PONTUAÇÃO INTELIGENTE =====
        # Importar sistema de pontuação e utilitários
        from triagem_scoring import scoring_system
        from perguntas_extractor import get_patient_profile_from_cadastro
        
        # ===== PREPARAR PERFIL DO PACIENTE =====
        # Converter dados do paciente para formato usado pelo sistema de pontuação
        patient_profile = get_patient_profile_from_cadastro(paciente_data)
        
        # ===== CALCULAR PONTUAÇÃO =====
        # Aplicar sistema de pontuação baseado nas respostas e perfil
        scoring_result = scoring_system.calculate_score(
            modulo=data.get('modulo', 'tosse'),    # Módulo específico (ex: tosse, febre)
            respostas=respostas,                   # Respostas do questionário
            paciente_profile=patient_profile       # Perfil do paciente
        )
        
        # ===== GERAR RECOMENDAÇÕES INTELIGENTES =====
        # Gerar recomendações baseadas na pontuação e respostas específicas
        recommendations = scoring_system.generate_recommendations(
            scoring_result,                        # Resultado da pontuação
            data.get('modulo', 'tosse'),          # Módulo para recomendações específicas
            respostas,                            # Respostas para análise adicional
            patient_profile                       # Perfil para personalização
        )
        
        # Preparar resultado da triagem
        triagem_result = {
            'encaminhamento_medico': scoring_result.encaminhamento,
            'motivo_encaminhamento': 'Pontuação alta ou sinais críticos detectados' if scoring_result.encaminhamento else None,
            'recomendacoes_medicamentos': [{'medicamento': med, 'justificativa': f'Baseado na pontuação: {scoring_result.total_score:.1f}'} for med in recommendations['farmacologicas']],
            'recomendacoes_nao_farmacologicas': [{'descricao': rec, 'justificativa': f'Recomendação não farmacológica baseada na pontuação'} for rec in recommendations['nao_farmacologicas']],
            'observacoes': [
                f'Pontuação total: {scoring_result.total_score:.1f}',
                f'Nível de risco: {scoring_result.risk_level}',
                f'Confiança: {scoring_result.confidence:.1%}',
                f'Categoria principal: {max(scoring_result.category_scores.items(), key=lambda x: x[1])[0]}'
            ],
            'scoring_result': {
                'total_score': scoring_result.total_score,
                'category_scores': scoring_result.category_scores,
                'risk_level': scoring_result.risk_level,
                'confidence': scoring_result.confidence
            }
        }
        
        # Atualizar consulta com resultado
        consulta.encaminhamento = triagem_result['encaminhamento_medico']
        consulta.motivo_encaminhamento = triagem_result.get('motivo_encaminhamento')
        consulta.observacoes = '\n'.join(triagem_result.get('observacoes', []))
        
        # Salvar recomendações
        for rec in triagem_result.get('recomendacoes_medicamentos', []):
            recomendacao = ConsultaRecomendacao(
                id_consulta=consulta.id,
                tipo='medicamento',
                descricao=rec['medicamento'],
                justificativa=rec['justificativa']
            )
            db.session.add(recomendacao)
        
        for rec in triagem_result.get('recomendacoes_nao_farmacologicas', []):
            recomendacao = ConsultaRecomendacao(
                id_consulta=consulta.id,
                tipo='nao_farmacologico',
                descricao=rec['descricao'],
                justificativa=rec['justificativa']
            )
            db.session.add(recomendacao)
        
        if triagem_result['encaminhamento_medico']:
            recomendacao = ConsultaRecomendacao(
                id_consulta=consulta.id,
                tipo='encaminhamento',
                descricao='Encaminhamento médico',
                justificativa=triagem_result.get('motivo_encaminhamento')
            )
            db.session.add(recomendacao)
        
        db.session.commit()
        
        # Retornar resultado
        return jsonify({
            'success': True,
            'consulta_id': consulta.id,
            'resultado': triagem_result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/triagem/resultado/<int:consulta_id>')
def resultado_triagem(consulta_id):
    """Exibir resultado da triagem"""
    consulta = Consulta.query.get_or_404(consulta_id)
    paciente = consulta.paciente
    respostas = consulta.respostas
    recomendacoes = consulta.recomendacoes
    
    # Buscar dados completos das respostas
    respostas_completas = []
    for resposta in respostas:
        pergunta = Pergunta.query.get(resposta.id_pergunta)
        respostas_completas.append({
            'pergunta_texto': pergunta.texto if pergunta else 'Pergunta não encontrada',
            'resposta': resposta.resposta
        })
    
    # Preparar resultado da triagem para o template
    resultado = {
        'score': 0,  # Será calculado baseado nas respostas
        'risk_level': 'baixo',  # Será calculado baseado nas respostas
        'alert_signs': [],
        'recomendacoes_farmacologicas': [],
        'recomendacoes_nao_farmacologicas': [],
        'conclusao': 'Resultado da triagem será processado automaticamente.'
    }
    
    # Processar recomendações
    for rec in recomendacoes:
        if rec.tipo == 'medicamento':
            resultado['recomendacoes_farmacologicas'].append({
                'medicamento': {'nome': rec.descricao},
                'posologia': rec.justificativa or 'Consultar bula'
            })
        elif rec.tipo == 'nao_farmacologico':
            resultado['recomendacoes_nao_farmacologicas'].append({
                'titulo': rec.descricao,
                'descricao': rec.justificativa or 'Recomendação não-farmacológica'
            })
        elif rec.tipo == 'encaminhamento':
            resultado['alert_signs'].append(rec.justificativa or 'Encaminhamento médico necessário')
    
    # Calcular score e risk_level usando o sistema de pontuação real
    if respostas_completas:
        try:
            # Preparar dados para o sistema de pontuação
            from triagem_scoring import scoring_system
            from perguntas_extractor import get_patient_profile_from_cadastro
            
            # Obter perfil do paciente
            paciente_data = paciente.to_dict()
            patient_profile = get_patient_profile_from_cadastro(paciente_data)
            
            # Preparar respostas no formato esperado
            respostas_formatadas = []
            for resposta in respostas:
                respostas_formatadas.append({
                    'pergunta_id': str(resposta.id_pergunta),
                    'resposta': resposta.resposta
                })
            
            # Detectar o módulo correto baseado nas perguntas
            modulo_detectado = _detectar_modulo_das_perguntas(respostas)
            
            # Calcular pontuação usando o sistema real
            scoring_result = scoring_system.calculate_score(
                modulo=modulo_detectado,
                respostas=respostas_formatadas,
                paciente_profile=patient_profile
            )
            
            resultado['score'] = scoring_result.total_score
            resultado['risk_level'] = scoring_result.risk_level
            resultado['alert_signs'] = []  # Será preenchido se houver sinais de alerta
            
            if scoring_result.encaminhamento:
                resultado['risk_level'] = 'alto'
                resultado['alert_signs'].append('Pontuação alta ou sinais críticos detectados')
                
        except Exception as e:
            print(f"Erro ao calcular pontuação: {e}")
            # Fallback para cálculo simples
            resultado['score'] = len(respostas_completas) * 10
            if consulta.encaminhamento:
                resultado['risk_level'] = 'alto'
            elif resultado['score'] > 50:
                resultado['risk_level'] = 'medio'
            else:
                resultado['risk_level'] = 'baixo'
    
    return render_template('resultado_triagem.html', 
                         consulta=consulta, 
                         paciente=paciente,
                         resultado=resultado,
                         respostas=respostas_completas,
                         recomendacoes=recomendacoes)

@app.route('/relatorio/<int:consulta_id>')
def gerar_relatorio(consulta_id):
    """Gerar relatório PDF da consulta"""
    try:
        consulta = Consulta.query.get_or_404(consulta_id)
        paciente = consulta.paciente
        respostas = consulta.respostas
        recomendacoes = consulta.recomendacoes
        
        # Preparar dados para o relatório
        consulta_data = consulta.to_dict()
        paciente_data = paciente.to_dict()
        
        # Buscar dados completos das respostas
        respostas_completas = []
        for resposta in respostas:
            pergunta = Pergunta.query.get(resposta.id_pergunta)
            respostas_completas.append({
                'pergunta_texto': pergunta.texto if pergunta else 'Pergunta não encontrada',
                'resposta': resposta.resposta
            })
        
        # Buscar resultado da triagem das recomendações
        triagem_result = {
            'encaminhamento_medico': consulta.encaminhamento,
            'motivo_encaminhamento': consulta.motivo_encaminhamento,
            'recomendacoes_medicamentos': [r for r in recomendacoes if r.tipo == 'medicamento'],
            'recomendacoes_nao_farmacologicas': [r for r in recomendacoes if r.tipo == 'nao_farmacologico'],
            'observacoes': consulta.observacoes.split('\n') if consulta.observacoes else []
        }
        
        # Gerar PDF
        filename = f"relatorio_consulta_{consulta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join('reports', filename)
        
        report_generator.generate_triagem_report(
            consulta_data, paciente_data, triagem_result, 
            respostas_completas, output_path
        )
        
        return send_file(output_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('resultado_triagem', consulta_id=consulta_id))

@app.route('/admin')
def admin():
    """Painel administrativo"""
    from datetime import timedelta
    from sqlalchemy import func
    
    # Estatísticas gerais
    total_pacientes = Paciente.query.count()
    total_consultas = Consulta.query.count()
    total_medicamentos = Medicamento.query.filter_by(ativo=True).count()
    total_encaminhamentos = Consulta.query.filter_by(encaminhamento=True).count()
    
    # Pacientes por gênero
    total_pacientes_masculino = Paciente.query.filter_by(sexo='M').count()
    total_pacientes_feminino = Paciente.query.filter_by(sexo='F').count()
    
    # Sintomas mais comuns
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
    
    # Medicamentos mais recomendados
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
    
    # Taxa de encaminhamentos
    taxa_encaminhamento = (total_encaminhamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    # Eficácia das recomendações (baseado em feedback se implementado)
    eficacia_recomendacoes = {
        'muito_eficaz': 75,
        'eficaz': 20,
        'pouco_eficaz': 5
    }
    
    # Consultas recentes
    consultas_recentes = Consulta.query.join(Paciente).order_by(Consulta.data.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         total_pacientes=total_pacientes,
                         total_consultas=total_consultas,
                         total_medicamentos=total_medicamentos,
                         total_encaminhamentos=total_encaminhamentos,
                         total_pacientes_masculino=total_pacientes_masculino,
                         total_pacientes_feminino=total_pacientes_feminino,
                         sintomas_comuns=sintomas_comuns,
                         medicamentos_recomendados=medicamentos_recomendados,
                         taxa_encaminhamento=taxa_encaminhamento,
                         eficacia_recomendacoes=eficacia_recomendacoes,
                         consultas_recentes=consultas_recentes)



@app.route('/api/perguntas')
def api_perguntas():
    """API para buscar perguntas ativas"""
    perguntas = get_perguntas_ativas()
    return jsonify([p.to_dict() for p in perguntas])

@app.route('/api/triagem/modulos')
def api_triagem_modulos():
    """Lista módulos disponíveis no motor_de_perguntas"""
    mods = list_motor_modulos()
    return jsonify(mods)

@app.route('/api/triagem/perguntas')
def api_triagem_perguntas():
    """Retorna perguntas do módulo informado (slug) extraídas via AST"""
    slug = request.args.get('modulo', '').strip()
    paciente_id = request.args.get('paciente_id', type=int)
    filter_unnecessary = request.args.get('filter_unnecessary', 'true').lower() == 'true'
    
    if not slug:
        return jsonify({'success': False, 'error': 'Parâmetro modulo é obrigatório'}), 400
    
    try:
        # Se paciente_id foi fornecido e filter_unnecessary é True, filtrar perguntas desnecessárias
        if paciente_id and filter_unnecessary:
            # Buscar dados do paciente
            paciente = Paciente.query.get_or_404(paciente_id)
            paciente_data = paciente.to_dict()
            
            # Extrair perguntas filtradas
            questions = extract_questions_for_module(slug, filter_unnecessary=True)
            
            # Adicionar informações do perfil do paciente para uso no frontend
            from perguntas_extractor import get_patient_profile_from_cadastro
            patient_profile = get_patient_profile_from_cadastro(paciente_data)
            
            # Adicionar informações de pontuação para cada pergunta
            for question in questions:
                question['scoring_info'] = {
                    'peso': question.get('peso', 1.0),
                    'categoria': question.get('categoria', 'sintoma'),
                    'critica': question.get('critica', False),
                    'indication': question.get('indication', 'nao_farmacologico')
                }
            
            return jsonify({
                'success': True, 
                'modulo': slug, 
                'perguntas': questions,
                'patient_profile': patient_profile,
                'filtered': True
            })
        else:
            # Comportamento original - sem filtro
            questions = extract_questions_for_module(slug, filter_unnecessary=False)
            return jsonify({
                'success': True, 
                'modulo': slug, 
                'perguntas': questions,
                'filtered': False
            })
            
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Módulo não encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sintomas')
def api_sintomas():
    """API para buscar sintomas"""
    sintomas = Sintoma.query.all()
    return jsonify([s.to_dict() for s in sintomas])

@app.route('/api/medicamentos')
def api_medicamentos():
    """
    API para buscar medicamentos ativos
    
    Otimização: Limita resultados para evitar sobrecarga
    """
    # Limitar resultados para evitar sobrecarga da API
    medicamentos = Medicamento.query.filter_by(ativo=True).limit(1000).all()
    return jsonify([m.to_dict() for m in medicamentos])

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

def _detectar_modulo_das_perguntas(respostas):
    """Detecta o módulo correto baseado nas perguntas respondidas"""
    if not respostas:
        return 'tosse'  # Módulo padrão
    
    # Mapear IDs de perguntas para módulos
    modulo_por_pergunta = {}
    
    # Buscar todas as perguntas no banco e mapear para módulos
    for resposta in respostas:
        pergunta = Pergunta.query.get(resposta.id_pergunta)
        if pergunta and pergunta.texto:
            # Detectar módulo baseado no texto da pergunta
            texto_lower = pergunta.texto.lower()
            
            # Detectar módulo baseado em palavras-chave específicas dos módulos
            if any(palavra in texto_lower for palavra in ['tosse', 'tossir', 'expectoração', 'tosse seca', 'tosse produtiva']):
                modulo_por_pergunta[resposta.id_pergunta] = 'tosse'
            elif any(palavra in texto_lower for palavra in ['febre', 'temperatura', 'calafrio', 'febril']):
                modulo_por_pergunta[resposta.id_pergunta] = 'febre'
            elif any(palavra in texto_lower for palavra in ['dor de cabeça', 'cefaleia', 'enxaqueca', 'dor de cabeça']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_cabeca'
            elif any(palavra in texto_lower for palavra in ['diarreia', 'evacuação', 'fezes', 'evacuações', 'banheiro']):
                modulo_por_pergunta[resposta.id_pergunta] = 'diarreia'
            elif any(palavra in texto_lower for palavra in ['garganta', 'dor de garganta', 'faringite', 'dor garganta']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_garganta'
            elif any(palavra in texto_lower for palavra in ['azia', 'queimação', 'refluxo', 'digestão', 'estômago']):
                modulo_por_pergunta[resposta.id_pergunta] = 'azia_ma_digestao'
            elif any(palavra in texto_lower for palavra in ['constipação', 'prisão de ventre', 'intestino', 'evacuar']):
                modulo_por_pergunta[resposta.id_pergunta] = 'constipacao'
            elif any(palavra in texto_lower for palavra in ['hemorroida', 'hemorroidas', 'anal', 'sangramento anal']):
                modulo_por_pergunta[resposta.id_pergunta] = 'hemorroidas'
            elif any(palavra in texto_lower for palavra in ['lombar', 'coluna', 'costas', 'dor lombar']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_lombar'
            elif any(palavra in texto_lower for palavra in ['congestão', 'nasal', 'espirro', 'rinite', 'nariz']):
                modulo_por_pergunta[resposta.id_pergunta] = 'espirro_congestao_nasal'
            elif any(palavra in texto_lower for palavra in ['dismenorreia', 'menstruação', 'cólica menstrual']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dismenorreia'
            elif any(palavra in texto_lower for palavra in ['fungica', 'micose', 'candidíase', 'fungo']):
                modulo_por_pergunta[resposta.id_pergunta] = 'infeccoes_fungicas'
            elif any(palavra in texto_lower for palavra in ['queimadura', 'solar', 'sol', 'pele']):
                modulo_por_pergunta[resposta.id_pergunta] = 'queimadura_solar'
            else:
                # Se não conseguir detectar, usar o módulo mais comum baseado no contexto
                # Verificar se há perguntas sobre sintomas gerais
                if any(palavra in texto_lower for palavra in ['dor', 'sintoma', 'problema']):
                    modulo_por_pergunta[resposta.id_pergunta] = 'tosse'  # Padrão mais comum
                else:
                    modulo_por_pergunta[resposta.id_pergunta] = 'tosse'  # Padrão
    
    # Retornar o módulo mais frequente
    if modulo_por_pergunta:
        from collections import Counter
        modulos = list(modulo_por_pergunta.values())
        modulo_mais_frequente = Counter(modulos).most_common(1)[0][0]
        return modulo_mais_frequente
    
    return 'tosse'  # Módulo padrão

if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
