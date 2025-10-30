#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Sistema de Triagem Farmacêutica
==============================================

Aplicação Flask principal com otimizações de performance para triagem farmacêutica.

Funcionalidades principais:
- Sistema de triagem farmacêutica automatizada
- Gerenciamento de pacientes e medicamentos
- Relatórios em PDF profissionais
- Interface web responsiva
- Base de dados com medicamentos da ANVISA
- Sistema de pontuação inteligente
- Motor de perguntas modular

Arquitetura:
- Core: Aplicação Flask principal
- Models: Modelos de dados SQLAlchemy
- Services: Lógica de negócio (triagem, relatórios, recomendações)
- Utils: Utilitários e helpers (scoring, extractors)
- Templates: Interface web
- Data: Dados estáticos e configurações

Autor: Sistema Pharm-Assist
Versão: 1.0.0
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from models.models import db, Usuario, Paciente, DoencaCronica, PacienteDoenca, Sintoma, Pergunta, Medicamento, Consulta, ConsultaResposta, ConsultaRecomendacao
from services.reports.report_generator import ReportGenerator
from core.config import Config
import os
from datetime import datetime, timedelta
import json
from functools import lru_cache
from services.triagem.qa_collector import qa_collector
from utils.extractors.perguntas_extractor import list_modules as list_motor_modulos, extract_questions_for_module

# Inicialização da aplicação
# Configurar o caminho correto para os templates
import os
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(Config)

# Inicializar extensões
db.init_app(app)

# Inicializar componentes
report_generator = ReportGenerator()

# Criar diretórios necessários
# Usar o diretório de trabalho atual como referência
project_root = os.getcwd()
reports_dir = os.path.join(project_root, 'reports')
uploads_dir = os.path.join(project_root, 'uploads')

os.makedirs(reports_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)

# ==============================
# SISTEMA DE AUTENTICAÇÃO
# ==============================

def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para proteger rotas que requerem privilégios de administrador"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        user = Usuario.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna o usuário atual da sessão"""
    if 'user_id' in session:
        return Usuario.query.get(session['user_id'])
    return None

def create_admin_user():
    """Cria usuário administrador padrão se não existir"""
    admin_user = Usuario.query.filter_by(email='admin@pharmassist.com').first()
    if not admin_user:
        admin_user = Usuario(
            nome='Administrador do Sistema',
            email='admin@pharmassist.com',
            is_admin=True,
            ativo=True
        )
        admin_user.set_password('admin123')  # Senha padrão - deve ser alterada
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Usuário administrador criado: admin@pharmassist.com / admin123")

# Cache para consultas frequentes (evita múltiplas consultas ao banco)
@lru_cache(maxsize=128)
def get_doencas_cronicas():
    """Cache para doenças crônicas - consulta frequente"""
    return DoencaCronica.query.all()

@lru_cache(maxsize=64)
def get_perguntas_ativas():
    """Cache para perguntas ativas - consulta frequente"""
    return Pergunta.query.filter_by(ativa=True).order_by(Pergunta.ordem).all()

# ==============================
# ROTAS DE AUTENTICAÇÃO
# ==============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        senha = request.form['senha']
        
        # Buscar usuário
        user = Usuario.query.filter_by(email=email, ativo=True).first()
        
        if user and user.check_password(senha):
            # Login bem-sucedido
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['user_email'] = user.email
            session['user_is_admin'] = user.is_admin
            
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Bem-vindo(a), {user.nome}!', 'success')
            
            # Redirecionar para página solicitada ou dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
@admin_required
def cadastro():
    """Cadastro de novos usuários (apenas administradores)"""
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()
            email = request.form['email'].strip().lower()
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']
            is_admin = request.form.get('is_admin') == 'on'
            
            # Validações
            if not nome or not email or not senha:
                flash('Todos os campos são obrigatórios.', 'error')
                return render_template('cadastro.html')
            
            if senha != confirmar_senha:
                flash('As senhas não coincidem.', 'error')
                return render_template('cadastro.html')
            
            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('cadastro.html')
            
            # Verificar se email já existe
            if Usuario.query.filter_by(email=email).first():
                flash('Este email já está cadastrado.', 'error')
                return render_template('cadastro.html')
            
            # Criar usuário
            user = Usuario(
                nome=nome,
                email=email,
                is_admin=is_admin,
                ativo=True
            )
            user.set_password(senha)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Usuário {nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('admin_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')
    
    return render_template('cadastro.html')

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Lista de usuários (apenas administradores)"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    
    usuarios = Usuario.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/<int:id>/toggle_status', methods=['POST'])
@admin_required
def toggle_usuario_status(id):
    """Ativar/desativar usuário"""
    try:
        user = Usuario.query.get_or_404(id)
        
        # Não permitir desativar a si mesmo
        if user.id == session['user_id']:
            flash('Você não pode desativar sua própria conta.', 'warning')
            return redirect(url_for('admin_usuarios'))
        
        user.ativo = not user.ativo
        db.session.commit()
        
        status = 'ativado' if user.ativo else 'desativado'
        flash(f'Usuário {user.nome} foi {status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar status do usuário: {str(e)}', 'error')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir_usuario(id):
    """Excluir usuário"""
    try:
        user = Usuario.query.get_or_404(id)
        
        # Não permitir excluir a si mesmo
        if user.id == session['user_id']:
            flash('Você não pode excluir sua própria conta.', 'warning')
            return redirect(url_for('admin_usuarios'))
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Usuário {user.nome} foi excluído.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'error')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/perfil')
@login_required
def perfil():
    """Página de perfil do usuário"""
    user = get_current_user()
    return render_template('perfil.html', user=user)

@app.route('/alterar_senha', methods=['POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário"""
    try:
        user = get_current_user()
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        # Verificar senha atual
        if not user.check_password(senha_atual):
            flash('Senha atual incorreta.', 'error')
            return redirect(url_for('perfil'))
        
        # Validar nova senha
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('perfil'))
        
        if len(nova_senha) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
            return redirect(url_for('perfil'))
        
        # Alterar senha
        user.set_password(nova_senha)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar senha: {str(e)}', 'error')
    
    return redirect(url_for('perfil'))

# ==============================
# ROTAS PRINCIPAIS (PROTEGIDAS)
# ==============================

@app.route('/teste')
@login_required
def teste():
    """Rota de teste para verificar se o login está funcionando"""
    return render_template('test.html')

@app.route('/')
@login_required
def index():
    """
    Página inicial do sistema com dashboard e estatísticas
    """
    try:
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
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return render_template('test.html')

@app.route('/pacientes')
@login_required
def pacientes():
    """Lista de pacientes"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    
    pacientes = Paciente.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/novo', methods=['GET', 'POST'])
@login_required
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
@login_required
def visualizar_paciente(id):
    """Visualizar dados de um paciente"""
    paciente = Paciente.query.get_or_404(id)
    consultas = Consulta.query.filter_by(id_paciente=id).order_by(Consulta.data.desc()).all()
    
    return render_template('visualizar_paciente.html', paciente=paciente, consultas=consultas)

@app.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
        from models.models import ConsultaRecomendacao
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
@login_required
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
            pergunta_id_str = resposta_data['pergunta_id']
            resposta_texto = resposta_data['resposta']

            # Tentar converter para inteiro primeiro (para perguntas antigas)
            try:
                pergunta_id = int(pergunta_id_str)
                # Se conseguiu converter, usar o ID numérico
                resp = ConsultaResposta(
                    id_consulta=consulta.id,
                    id_pergunta=pergunta_id,
                    resposta=resposta_texto
                )
                db.session.add(resp)
            except (ValueError, TypeError):
                # Se não conseguiu converter, é um ID string (formato: modulo_ordem)
                # Para perguntas dinâmicas, usar um ID fixo baseado no hash
                import hashlib
                pergunta_id_hash = abs(hash(pergunta_id_str)) % 1000000  # ID entre 0 e 999999
                
                # Verificar se já existe uma pergunta com esse ID
                pergunta_existente = Pergunta.query.filter_by(id=pergunta_id_hash).first()
                
                if not pergunta_existente:
                    # Criar nova pergunta com ID baseado no hash
                    nova_pergunta = Pergunta(
                        id=pergunta_id_hash,
                        texto=pergunta_id_str,
                        tipo='sintoma',  # Usar um tipo válido do ENUM
                        ordem=999,
                        ativa=True
                    )
                    db.session.add(nova_pergunta)
                    pergunta_id = pergunta_id_hash
                else:
                    pergunta_id = pergunta_id_hash
                
                resp = ConsultaResposta(
                    id_consulta=consulta.id,
                    id_pergunta=pergunta_id,
                    resposta=resposta_texto
                )
                db.session.add(resp)
        
        # Processar triagem usando sistema de pontuação
        from utils.scoring.triagem_scoring import scoring_system
        from utils.extractors.perguntas_extractor import get_patient_profile_from_cadastro
        
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
        
        # Separar medicamentos em grupos de 6 (iniciais e adicionais)
        medicamentos_todos = recommendations['farmacologicas']
        medicamentos_iniciais = medicamentos_todos[:6]  # Primeiros 6
        medicamentos_adicionais = medicamentos_todos[6:]  # Restantes
        
        # Preparar resultado da triagem
        triagem_result = {
            'encaminhamento_medico': scoring_result.encaminhamento,
            'motivo_encaminhamento': 'Pontuação alta ou sinais críticos detectados' if scoring_result.encaminhamento else None,
            'recomendacoes_medicamentos': [{'medicamento': med, 'justificativa': f'Baseado na pontuação: {scoring_result.total_score:.1f}'} for med in medicamentos_iniciais],
            'recomendacoes_medicamentos_adicionais': [{'medicamento': med, 'justificativa': f'Baseado na pontuação: {scoring_result.total_score:.1f}'} for med in medicamentos_adicionais],
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
        
        # Adicionar o módulo/sintoma principal nas observações de forma destacada
        modulo_usado = data.get('modulo', 'geral')
        observacoes_list = [f'MODULO: {modulo_usado}']  # Primeiro item é sempre o módulo
        observacoes_list.extend(triagem_result.get('observacoes', []))
        consulta.observacoes = '\n'.join(observacoes_list)
        
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
            # Extrair posologia da descrição
            posologia = 'Consultar bula'
            if 'Posologia:' in rec.descricao:
                try:
                    posologia = rec.descricao.split('Posologia:')[1].split('|')[0].strip()
                except:
                    posologia = 'Consultar bula'
            
            # Extrair indicação da descrição
            indicacao = 'Verificar bula'
            if ' - ' in rec.descricao and 'Posologia:' in rec.descricao:
                try:
                    indicacao = rec.descricao.split(' - ')[1].split(' | Posologia:')[0].strip()
                except:
                    indicacao = 'Verificar bula'
            elif ' - ' in rec.descricao:
                try:
                    indicacao = rec.descricao.split(' - ')[1].split(' | ')[0].strip()
                except:
                    indicacao = 'Verificar bula'
            
            # Extrair observações da descrição
            observacoes = None
            if ' | ' in rec.descricao and 'Posologia:' in rec.descricao:
                try:
                    partes = rec.descricao.split(' | ')
                    if len(partes) > 2:
                        observacoes = partes[2].strip()
                except:
                    pass
            
            resultado['recomendacoes_farmacologicas'].append({
                'medicamento': {'nome': rec.descricao},
                'posologia': posologia,
                'indicacao': indicacao,
                'observacoes': observacoes,
                'prioridade': 3,  # Prioridade padrão
                'categoria': 'Medicamento'
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
            from utils.scoring.triagem_scoring import scoring_system
            from utils.extractors.perguntas_extractor import get_patient_profile_from_cadastro
            
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
        
        # Log detalhado da geração de PDF
        print(f"=== GERAÇÃO DE RELATÓRIO PDF - Consulta {consulta_id} ===")
        print(f"Data da consulta: {consulta.data}")
        print(f"Paciente: {paciente.nome} (ID: {paciente.id})")
        print(f"Total de respostas persistidas: {len(respostas)}")
        print(f"Total de recomendações: {len(recomendacoes)}")
        
        # Usar coletor unificado para obter dados consolidados de perguntas e respostas
        respostas_completas = []
        try:
            qa_data = qa_collector.collect_qa_for_consulta(consulta_id)
            print(f"Q&A coletado com sucesso: {qa_data['total_perguntas']} perguntas de {len(qa_data['modulos_utilizados'])} módulos")
            # Extrair respostas_completas do qa_data para uso posterior
            respostas_completas = qa_data.get('perguntas_respostas', [])
        except Exception as e:
            print(f"Erro ao coletar Q&A unificado: {e}")
            import traceback
            traceback.print_exc()
            # Fallback para método antigo se houver erro
            respostas_completas = []
            for resposta in respostas:
                pergunta = Pergunta.query.get(resposta.id_pergunta)
                pergunta_texto = pergunta.texto if pergunta else f'Pergunta ID {resposta.id_pergunta}'
                
                respostas_completas.append({
                    'pergunta_id': resposta.id_pergunta,
                    'pergunta_texto': pergunta_texto,
                    'resposta': resposta.resposta
                })
            
            # Converter para formato esperado pelo coletor
            qa_data = {
                'consulta_id': consulta_id,
                'perguntas_respostas': respostas_completas,
                'modulos_utilizados': ['geral'],
                'total_perguntas': len(respostas_completas)
            }
            print(f"Fallback usado: {qa_data['total_perguntas']} perguntas")
        
        # Separar recomendações por tipo e converter para dicionários
        medicamentos_principais = []
        medicamentos_adicionais = []
        recomendacoes_nao_farmacologicas = []
        
        for rec in recomendacoes:
            if rec.tipo == 'medicamento':
                # Extrair posologia da descrição
                posologia = 'Consultar bula'
                if 'Posologia:' in rec.descricao:
                    try:
                        posologia = rec.descricao.split('Posologia:')[1].split('|')[0].strip()
                    except:
                        posologia = 'Consultar bula'
                
                # Extrair indicação da descrição
                indicacao = 'Verificar bula'
                if ' - ' in rec.descricao and 'Posologia:' in rec.descricao:
                    try:
                        indicacao = rec.descricao.split(' - ')[1].split(' | Posologia:')[0].strip()
                    except:
                        indicacao = 'Verificar bula'
                elif ' - ' in rec.descricao:
                    try:
                        indicacao = rec.descricao.split(' - ')[1].split(' | ')[0].strip()
                    except:
                        indicacao = 'Verificar bula'
                
                # Extrair observações da descrição
                observacoes = None
                if ' | ' in rec.descricao and 'Posologia:' in rec.descricao:
                    try:
                        partes = rec.descricao.split(' | ')
                        if len(partes) > 2:
                            observacoes = partes[2].strip()
                    except:
                        pass
                
                # Converter objeto para dicionário
                rec_dict = {
                    'medicamento': {'nome': rec.descricao},
                    'posologia': posologia,
                    'indicacao': indicacao,
                    'observacoes': observacoes,
                    'justificativa': rec.justificativa or 'Recomendado pela triagem',
                    'prioridade': 3,
                    'categoria': 'Medicamento'
                }
                
                # Separar medicamentos principais dos adicionais baseado na ordem
                if len(medicamentos_principais) < 6:
                    medicamentos_principais.append(rec_dict)
                else:
                    medicamentos_adicionais.append(rec_dict)
            elif rec.tipo == 'nao_farmacologico':
                # Converter objeto para dicionário
                rec_dict = {
                    'titulo': rec.descricao,
                    'descricao': rec.descricao,
                    'justificativa': rec.justificativa or 'Recomendação não-farmacológica'
                }
                recomendacoes_nao_farmacologicas.append(rec_dict)
        
        # Buscar resultado da triagem das recomendações
        triagem_result = {
            'encaminhamento_medico': consulta.encaminhamento,
            'motivo_encaminhamento': consulta.motivo_encaminhamento,
            'recomendacoes_medicamentos': medicamentos_principais,
            'recomendacoes_medicamentos_adicionais': medicamentos_adicionais,
            'recomendacoes_nao_farmacologicas': recomendacoes_nao_farmacologicas,
            'observacoes': consulta.observacoes.split('\n') if consulta.observacoes else [],
            'scoring_result': {
                'total_score': 0.0,
                'risk_level': 'baixo',
                'confidence': 0.0,
                'category_scores': {}
            }
        }
        
        # Tentar extrair dados de pontuação das observações
        observacoes_texto = consulta.observacoes or ''
        if 'Pontuação total:' in observacoes_texto:
            try:
                import re
                score_match = re.search(r'Pontuação total: ([\d.]+)', observacoes_texto)
                if score_match:
                    triagem_result['scoring_result']['total_score'] = float(score_match.group(1))
                
                nivel_match = re.search(r'Nível de risco: (\w+)', observacoes_texto)
                if nivel_match:
                    triagem_result['scoring_result']['risk_level'] = nivel_match.group(1).lower()
                
                confianca_match = re.search(r'Confiança: ([\d.]+%)', observacoes_texto)
                if confianca_match:
                    confianca_str = confianca_match.group(1).replace('%', '')
                    triagem_result['scoring_result']['confidence'] = float(confianca_str) / 100.0
            except Exception:
                pass  # Manter valores padrão se houver erro
        
        # Se não há dados de pontuação nas observações, tentar recalcular
        if triagem_result['scoring_result']['total_score'] == 0.0 and respostas_completas:
            try:
                from utils.scoring.triagem_scoring import scoring_system
                from utils.extractors.perguntas_extractor import get_patient_profile_from_cadastro
                
                # Obter perfil do paciente
                paciente_data_dict = paciente.to_dict()
                patient_profile = get_patient_profile_from_cadastro(paciente_data_dict)
                
                # Preparar respostas no formato esperado
                respostas_formatadas = []
                for resposta in respostas_completas:
                    respostas_formatadas.append({
                        'pergunta_id': str(resposta['pergunta_id']),
                        'resposta': resposta['resposta']
                    })
                
                # Detectar módulo
                modulo_detectado = _detectar_modulo_das_perguntas(consulta.respostas)
                
                # Calcular pontuação
                scoring_result = scoring_system.calculate_score(
                    modulo=modulo_detectado,
                    respostas=respostas_formatadas,
                    paciente_profile=patient_profile
                )
                
                # Atualizar resultado com dados reais
                triagem_result['scoring_result'] = {
                    'total_score': scoring_result.total_score,
                    'risk_level': scoring_result.risk_level,
                    'confidence': scoring_result.confidence,
                    'category_scores': scoring_result.category_scores
                }
                
            except Exception as e:
                print(f"Erro ao recalcular pontuação: {e}")
                # Manter valores padrão
        
        # Gerar PDF
        filename = f"relatorio_consulta_{consulta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(reports_dir, filename)
        
        print(f"Iniciando geração do PDF: {filename}")
        print(f"Caminho de saída: {output_path}")
        
        report_generator.generate_triagem_report(
            consulta_data, paciente_data, triagem_result, 
            qa_data, output_path
        )
        
        print(f"PDF gerado com sucesso: {filename}")
        print(f"Tamanho do arquivo: {os.path.getsize(output_path)} bytes")
        print("=== FIM DA GERAÇÃO DE RELATÓRIO ===")
        
        return send_file(output_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('resultado_triagem', consulta_id=consulta_id))

@app.route('/admin')
@admin_required
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
    ).limit(5).all()
    
    # Converter para lista de dicionários para serialização JSON
    # Extrair apenas o nome do medicamento (antes do primeiro " - " ou " | ")
    medicamentos_recomendados_formatados = []
    for m in medicamentos_recomendados:
        nome_medicamento = m.descricao.split(' - ')[0].split(' | ')[0].strip()
        medicamentos_recomendados_formatados.append({
            'descricao': nome_medicamento, 
            'count': m.count
        })
    medicamentos_recomendados = medicamentos_recomendados_formatados
    
    # Taxa de encaminhamentos
    taxa_encaminhamento = (total_encaminhamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    # Eficácia das recomendações (baseado em feedback se implementado)
    eficacia_recomendacoes = {
        'muito_eficaz': 75,
        'eficaz': 20,
        'pouco_eficaz': 5
    }
    
    # Consultas por mês (últimos 6 meses)
    from datetime import datetime, timedelta
    import calendar
    
    consultas_por_mes = []
    hoje = datetime.now()
    
    for i in range(5, -1, -1):  # Últimos 6 meses
        # Calcular o mês
        mes_data = hoje - timedelta(days=30 * i)
        mes_inicio = mes_data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Último dia do mês
        ultimo_dia = calendar.monthrange(mes_inicio.year, mes_inicio.month)[1]
        mes_fim = mes_inicio.replace(day=ultimo_dia, hour=23, minute=59, second=59)
        
        # Contar consultas do mês
        count = Consulta.query.filter(
            Consulta.data >= mes_inicio,
            Consulta.data <= mes_fim
        ).count()
        
        # Nome do mês em português
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        mes_nome = meses_pt[mes_inicio.month - 1]
        
        consultas_por_mes.append({
            'mes': f'{mes_nome}/{mes_inicio.year}',
            'count': count
        })
    
    # Pacientes por faixa etária
    faixas_etarias = [
        {'faixa': '0-18 anos', 'min': 0, 'max': 18},
        {'faixa': '19-35 anos', 'min': 19, 'max': 35},
        {'faixa': '36-60 anos', 'min': 36, 'max': 60},
        {'faixa': '60+ anos', 'min': 61, 'max': 150}
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
    
    # Consultas recentes
    consultas_recentes = Consulta.query.join(Paciente).order_by(Consulta.data.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         total_pacientes=total_pacientes,
                         total_consultas=total_consultas,
                         total_medicamentos=total_medicamentos,
                         total_encaminhamentos=total_encaminhamentos,
                         total_pacientes_masculino=total_pacientes_masculino,
                         total_pacientes_feminino=total_pacientes_feminino,
                         medicamentos_recomendados=medicamentos_recomendados,
                         taxa_encaminhamento=taxa_encaminhamento,
                         eficacia_recomendacoes=eficacia_recomendacoes,
                         consultas_recentes=consultas_recentes,
                         consultas_por_mes=consultas_por_mes,
                         pacientes_por_faixa=pacientes_por_faixa)



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
            from utils.extractors.perguntas_extractor import get_patient_profile_from_cadastro
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

@app.route('/api/triagem/medicamentos_adicionais/<int:consulta_id>')
def api_medicamentos_adicionais(consulta_id):
    """API para buscar medicamentos adicionais de uma consulta"""
    try:
        consulta = Consulta.query.get_or_404(consulta_id)
        
        # Buscar medicamentos adicionais salvos na consulta
        medicamentos_adicionais = []
        
        # Se houver medicamentos adicionais salvos, retornar eles
        if hasattr(consulta, 'medicamentos_adicionais') and consulta.medicamentos_adicionais:
            medicamentos_adicionais = consulta.medicamentos_adicionais
        else:
            # Gerar medicamentos adicionais dinamicamente
            from utils.scoring.triagem_scoring import scoring_system
            from utils.extractors.perguntas_extractor import get_patient_profile_from_cadastro
            
            # Obter perfil do paciente
            paciente_data = consulta.paciente.to_dict()
            patient_profile = get_patient_profile_from_cadastro(paciente_data)
            
            # Preparar respostas no formato esperado
            respostas_formatadas = []
            for resposta in consulta.respostas:
                respostas_formatadas.append({
                    'pergunta_id': str(resposta.id_pergunta),
                    'resposta': resposta.resposta
                })
            
            # Detectar módulo
            modulo_detectado = _detectar_modulo_das_perguntas(consulta.respostas)
            
            # Calcular pontuação
            scoring_result = scoring_system.calculate_score(
                modulo=modulo_detectado,
                respostas=respostas_formatadas,
                paciente_profile=patient_profile
            )
            
            # Gerar recomendações
            recommendations = scoring_system.generate_recommendations(
                scoring_result, 
                modulo_detectado,
                respostas_formatadas,
                patient_profile
            )
            
            # Pegar apenas os medicamentos adicionais (a partir do 7º)
            medicamentos_todos = recommendations['farmacologicas']
            medicamentos_adicionais = medicamentos_todos[6:]  # A partir do 7º medicamento
        
        return jsonify({
            'success': True,
            'medicamentos_adicionais': medicamentos_adicionais,
            'total': len(medicamentos_adicionais)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        return 'geral'  # Módulo padrão para perguntas genéricas
    
    # Mapear IDs de perguntas para módulos
    modulo_por_pergunta = {}
    sintomas_detectados = set()
    
    # Buscar todas as perguntas no banco e mapear para módulos
    for resposta in respostas:
        pergunta = Pergunta.query.get(resposta.id_pergunta)
        if pergunta and pergunta.texto:
            # Detectar módulo baseado no texto da pergunta
            texto_lower = pergunta.texto.lower()
            
            # Detectar módulo baseado em palavras-chave específicas dos módulos
            if any(palavra in texto_lower for palavra in ['tosse', 'tossir', 'expectoração', 'tosse seca', 'tosse produtiva']):
                modulo_por_pergunta[resposta.id_pergunta] = 'tosse'
                sintomas_detectados.add('tosse')
            elif any(palavra in texto_lower for palavra in ['febre', 'temperatura', 'calafrio', 'febril']):
                modulo_por_pergunta[resposta.id_pergunta] = 'febre'
                sintomas_detectados.add('febre')
            elif any(palavra in texto_lower for palavra in ['dor de cabeça', 'cefaleia', 'enxaqueca', 'dor de cabeça']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_cabeca'
                sintomas_detectados.add('dor_cabeca')
            elif any(palavra in texto_lower for palavra in ['diarreia', 'evacuação', 'fezes', 'evacuações', 'banheiro']):
                modulo_por_pergunta[resposta.id_pergunta] = 'diarreia'
                sintomas_detectados.add('diarreia')
            elif any(palavra in texto_lower for palavra in ['garganta', 'dor de garganta', 'faringite', 'dor garganta']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_garganta'
                sintomas_detectados.add('dor_garganta')
            elif any(palavra in texto_lower for palavra in ['azia', 'queimação', 'refluxo', 'digestão', 'estômago']):
                modulo_por_pergunta[resposta.id_pergunta] = 'azia_ma_digestao'
                sintomas_detectados.add('azia_ma_digestao')
            elif any(palavra in texto_lower for palavra in ['constipação', 'prisão de ventre', 'intestino', 'evacuar']):
                modulo_por_pergunta[resposta.id_pergunta] = 'constipacao'
                sintomas_detectados.add('constipacao')
            elif any(palavra in texto_lower for palavra in ['hemorroida', 'hemorroidas', 'anal', 'sangramento anal']):
                modulo_por_pergunta[resposta.id_pergunta] = 'hemorroidas'
                sintomas_detectados.add('hemorroidas')
            elif any(palavra in texto_lower for palavra in ['lombar', 'coluna', 'costas', 'dor lombar']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dor_lombar'
                sintomas_detectados.add('dor_lombar')
            elif any(palavra in texto_lower for palavra in ['congestão', 'nasal', 'espirro', 'rinite', 'nariz']):
                modulo_por_pergunta[resposta.id_pergunta] = 'espirro_congestao_nasal'
                sintomas_detectados.add('espirro_congestao_nasal')
            elif any(palavra in texto_lower for palavra in ['dismenorreia', 'menstruação', 'cólica menstrual']):
                modulo_por_pergunta[resposta.id_pergunta] = 'dismenorreia'
                sintomas_detectados.add('dismenorreia')
            elif any(palavra in texto_lower for palavra in ['fungica', 'micose', 'candidíase', 'fungo']):
                modulo_por_pergunta[resposta.id_pergunta] = 'infeccoes_fungicas'
                sintomas_detectados.add('infeccoes_fungicas')
            elif any(palavra in texto_lower for palavra in ['queimadura', 'solar', 'sol', 'pele']):
                modulo_por_pergunta[resposta.id_pergunta] = 'queimadura_solar'
                sintomas_detectados.add('queimadura_solar')
            else:
                # Para perguntas genéricas, usar módulo 'geral'
                modulo_por_pergunta[resposta.id_pergunta] = 'geral'
    
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
        
        # Criar usuário administrador padrão
        create_admin_user()
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
