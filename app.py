from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, Paciente, DoencaCronica, PacienteDoenca, Sintoma, Pergunta, Medicamento, Consulta, ConsultaResposta, ConsultaRecomendacao
from triagem_engine import TriagemEngine
from report_generator import ReportGenerator
from config import Config
import os
from datetime import datetime
import json

# Inicialização da aplicação
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensões
db.init_app(app)

# Inicializar componentes
triagem_engine = TriagemEngine()
report_generator = ReportGenerator()

# Criar diretórios necessários
os.makedirs('reports', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

@app.route('/')
def index():
    """Página inicial do sistema"""
    return render_template('index.html')

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
    doencas_cronicas = DoencaCronica.query.all()
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
    
    doencas_cronicas = DoencaCronica.query.all()
    doencas_paciente = [pd.id_doenca_cronica for pd in paciente.doencas_cronicas]
    
    return render_template('editar_paciente.html', paciente=paciente, 
                         doencas_cronicas=doencas_cronicas, doencas_paciente=doencas_paciente)

@app.route('/medicamentos')
def medicamentos():
    """Lista de medicamentos"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    
    medicamentos = Medicamento.query.filter_by(ativo=True).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('medicamentos.html', medicamentos=medicamentos)

@app.route('/medicamentos/novo', methods=['GET', 'POST'])
def novo_medicamento():
    """Cadastro de novo medicamento"""
    if request.method == 'POST':
        try:
            medicamento = Medicamento(
                nome_comercial=request.form['nome_comercial'],
                nome_generico=request.form['nome_generico'],
                descricao=request.form['descricao'],
                indicacao=request.form['indicacao'],
                contraindicacao=request.form['contraindicacao'],
                tipo=request.form['tipo']
            )
            
            db.session.add(medicamento)
            db.session.commit()
            
            flash('Medicamento cadastrado com sucesso!', 'success')
            return redirect(url_for('medicamentos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar medicamento: {str(e)}', 'error')
    
    return render_template('novo_medicamento.html')

@app.route('/triagem')
def triagem():
    """Página inicial da triagem"""
    return render_template('triagem.html')

@app.route('/triagem/buscar_paciente')
def buscar_paciente_triagem():
    """Buscar paciente para iniciar triagem"""
    query = request.args.get('q', '')
    
    if query:
        pacientes = Paciente.query.filter(
            Paciente.nome.ilike(f'%{query}%')
        ).limit(10).all()
    else:
        pacientes = []
    
    return render_template('buscar_paciente_triagem.html', pacientes=pacientes, query=query)

@app.route('/triagem/novo_paciente', methods=['GET', 'POST'])
def novo_paciente_triagem():
    """Cadastro rápido de paciente para triagem"""
    if request.method == 'POST':
        try:
            paciente = Paciente(
                nome=request.form['nome'],
                idade=int(request.form['idade']),
                sexo=request.form['sexo'],
                fuma=request.form.get('fuma') == 'on',
                bebe=request.form.get('bebe') == 'on'
            )
            
            db.session.add(paciente)
            db.session.commit()
            
            flash('Paciente cadastrado! Iniciando triagem...', 'success')
            return redirect(url_for('iniciar_triagem', paciente_id=paciente.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'error')
    
    return render_template('novo_paciente_triagem.html')

@app.route('/triagem/iniciar/<int:paciente_id>')
def iniciar_triagem(paciente_id):
    """Iniciar triagem para um paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    perguntas = Pergunta.query.filter_by(ativa=True).order_by(Pergunta.ordem).all()
    
    return render_template('iniciar_triagem.html', paciente=paciente, perguntas=perguntas)

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
        for resposta_data in respostas:
            resposta = ConsultaResposta(
                id_consulta=consulta.id,
                id_pergunta=resposta_data['pergunta_id'],
                resposta=resposta_data['resposta']
            )
            db.session.add(resposta)
        
        # Processar triagem
        triagem_result = triagem_engine.analisar_respostas(respostas, paciente_data)
        
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
    
    return render_template('resultado_triagem.html', 
                         consulta=consulta, 
                         paciente=paciente,
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
    total_pacientes = Paciente.query.count()
    total_consultas = Consulta.query.count()
    total_medicamentos = Medicamento.query.filter_by(ativo=True).count()
    
    # Consultas recentes
    consultas_recentes = Consulta.query.order_by(Consulta.data.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         total_pacientes=total_pacientes,
                         total_consultas=total_consultas,
                         total_medicamentos=total_medicamentos,
                         consultas_recentes=consultas_recentes)

@app.route('/api/perguntas')
def api_perguntas():
    """API para buscar perguntas ativas"""
    perguntas = Pergunta.query.filter_by(ativa=True).order_by(Pergunta.ordem).all()
    return jsonify([p.to_dict() for p in perguntas])

@app.route('/api/sintomas')
def api_sintomas():
    """API para buscar sintomas"""
    sintomas = Sintoma.query.all()
    return jsonify([s.to_dict() for s in sintomas])

@app.route('/api/medicamentos')
def api_medicamentos():
    """API para buscar medicamentos ativos"""
    medicamentos = Medicamento.query.filter_by(ativo=True).all()
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
