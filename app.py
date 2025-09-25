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

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from models import db, Paciente, DoencaCronica, PacienteDoenca, Sintoma, Pergunta, Medicamento, Consulta, ConsultaResposta, ConsultaRecomendacao
from report_generator import ReportGenerator
from config import Config
import os
from datetime import datetime, timedelta
import json
from functools import lru_cache, wraps
from perguntas_extractor import list_modules as list_motor_modulos, extract_questions_for_module
import hashlib

# Inicialização da aplicação
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensões
db.init_app(app)

# Inicializar componentes
report_generator = ReportGenerator()

# Criar diretórios necessários
os.makedirs('reports', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# ===== SISTEMA DE AUTENTICAÇÃO =====

def hash_password(password):
    """Criptografa a senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verifica se a senha está correta"""
    return hash_password(password) == hashed

def login_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def check_session_timeout():
    """Verifica se a sessão expirou"""
    if 'last_activity' in session:
        last_activity = session['last_activity']
        if datetime.now().timestamp() - last_activity > app.config['SESSION_TIMEOUT']:
            session.clear()
            return False
    return True

# Cache para consultas frequentes (evita múltiplas consultas ao banco)
@lru_cache(maxsize=128)
def get_doencas_cronicas():
    """Cache para doenças crônicas - consulta frequente"""
    return DoencaCronica.query.all()

@lru_cache(maxsize=64)
def get_perguntas_ativas():
    """Cache para perguntas ativas - consulta frequente"""
    return Pergunta.query.filter_by(ativa=True).order_by(Pergunta.ordem).all()

# ===== ROTAS DE AUTENTICAÇÃO =====

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Página de login do administrador"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Verificar credenciais
        if (username == app.config['ADMIN_USERNAME'] and 
            verify_password(password, hash_password(app.config['ADMIN_PASSWORD']))):
            
            # Login bem-sucedido
            session['admin_logged_in'] = True
            session['last_activity'] = datetime.now().timestamp()
            session['username'] = username
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout do administrador"""
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('admin_login'))

@app.route('/')
def index():
    """
    Página inicial do sistema com dashboard e estatísticas
    
    Otimizações implementadas:
    - Consultas otimizadas com índices
    - Cache de estatísticas frequentes
    - Redução de consultas ao banco
    """
    # Estatísticas gerais (otimizadas)
    total_pacientes = Paciente.query.count()
    total_medicamentos = Medicamento.query.filter_by(ativo=True).count()  # Apenas ativos
    
    # Consultas de hoje (otimizada)
    hoje = datetime.now().date()
    consultas_hoje = Consulta.query.filter(
        db.func.date(Consulta.data) == hoje
    ).count()
    
    # Encaminhamentos (otimizada)
    encaminhamentos = Consulta.query.filter_by(encaminhamento=True).count()
    
    # Consultas dos últimos 30 dias (otimizada)
    data_30_dias_atras = datetime.now() - timedelta(days=30)
    consultas_30_dias = Consulta.query.filter(Consulta.data >= data_30_dias_atras).count()
    
    # Consultas por dia (últimos 7 dias)
    consultas_por_dia = []
    for i in range(7):
        data = datetime.now() - timedelta(days=i)
        inicio_dia = data.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = data.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = Consulta.query.filter(
            Consulta.data >= inicio_dia,
            Consulta.data <= fim_dia
        ).count()
        
        consultas_por_dia.append({
            'data': data.strftime('%d/%m'),
            'count': count
        })
    
    consultas_por_dia.reverse()  # Ordenar cronologicamente
    
    # Taxa de encaminhamentos
    total_consultas = Consulta.query.count()
    taxa_encaminhamento = (encaminhamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    # Pacientes por faixa etária
    faixas_etarias = [
        {'faixa': '0-18', 'min': 0, 'max': 18},
        {'faixa': '19-30', 'min': 19, 'max': 30},
        {'faixa': '31-50', 'min': 31, 'max': 50},
        {'faixa': '51-65', 'min': 51, 'max': 65},
        {'faixa': '65+', 'min': 65, 'max': 120}
    ]
    
    pacientes_por_faixa = []
    for faixa in faixas_etarias:
        count = Paciente.query.filter(
            Paciente.idade >= faixa['min'],
            Paciente.idade <= faixa['max']
        ).count()
        pacientes_por_faixa.append({
            'faixa': faixa['faixa'],
            'count': count
        })
    
    # Últimas consultas
    consultas_recentes = Consulta.query.join(Paciente).order_by(
        Consulta.data.desc()
    ).limit(5).all()
    
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
    """Lista de pacientes"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    
    pacientes = Paciente.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/novo', methods=['GET', 'POST'])
def novo_paciente():
    """Cadastro de novo paciente"""
    if request.method == 'POST':
        try:
            # Dados do paciente
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
            flash('Paciente cadastrado com sucesso!', 'success')
            return redirect(url_for('pacientes'))
            
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
    
    return render_template('novo_paciente.html', doencas_cronicas=doencas_cronicas)

@app.route('/pacientes/<int:id>')
def visualizar_paciente(id):
    """Visualizar dados de um paciente"""
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(id_paciente=id).order_by(Consulta.data.desc()).all()
    
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
    """Processar triagem e gerar resultado"""
    try:
        data = request.get_json()
        paciente_id = data['paciente_id']
        respostas = data['respostas']
        
        # Buscar dados do paciente
        paciente = Paciente.query.get_or_404(paciente_id)
        paciente_data = paciente.to_dict()
        
        # Criar consulta
        consulta = Consulta(
            id_paciente=paciente_id,
            data=datetime.now()
        )
        db.session.add(consulta)
        db.session.commit()
        
        # Salvar respostas
        # Persistir respostas dinâmicas (id_pergunta pode ser slug string). Armazenar como texto no campo resposta e usar pergunta_texto separado? 
        # Para compatibilidade, vamos guardar o id (string) junto com a resposta no campo resposta.
        for resposta_data in respostas:
            try:
                pergunta_id = int(resposta_data['pergunta_id'])
            except Exception:
                pergunta_id = None

            resposta_texto = resposta_data['resposta']

            if pergunta_id is not None:
                resp = ConsultaResposta(
                    id_consulta=consulta.id,
                    id_pergunta=pergunta_id,
                    resposta=resposta_texto
                )
                db.session.add(resp)
            else:
                # Fallback: quando não há id numérico, apenas registrar como observação agregada
                if not consulta.observacoes:
                    consulta.observacoes = ''
                consulta.observacoes += f"\n{resposta_data['pergunta_id']}: {resposta_texto}"
        
        # Processar triagem usando sistema de pontuação
        from triagem_scoring import scoring_system
        from perguntas_extractor import get_patient_profile_from_cadastro
        
        # Obter perfil do paciente
        patient_profile = get_patient_profile_from_cadastro(paciente_data)
        
        # Calcular pontuação
        scoring_result = scoring_system.calculate_score(
            modulo=data.get('modulo', 'tosse'),
            respostas=respostas,
            paciente_profile=patient_profile
        )
        
        # Gerar recomendações baseadas na pontuação e respostas específicas
        recommendations = scoring_system.generate_recommendations(
            scoring_result, 
            data.get('modulo', 'tosse'),
            respostas,
            patient_profile
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
    
    # Calcular score e risk_level baseado nas respostas
    if respostas_completas:
        resultado['score'] = len(respostas_completas) * 10  # Score simples baseado no número de respostas
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
@login_required
def admin():
    """Painel administrativo"""
    # Verificar timeout da sessão
    if not check_session_timeout():
        flash('Sua sessão expirou. Faça login novamente.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Atualizar última atividade
    session['last_activity'] = datetime.now().timestamp()
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
    
    # Converter para dicionários para serialização JSON
    sintomas_comuns = [{'descricao': item.descricao, 'count': item.count} for item in sintomas_comuns]
    
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
    
    # Converter para dicionários para serialização JSON
    medicamentos_recomendados = [{'descricao': item.descricao, 'count': item.count} for item in medicamentos_recomendados]
    
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

if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
