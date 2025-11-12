#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Modelos do Banco de Dados
Definição das entidades e relacionamentos com otimizações de performance

Modelos implementados:
- Paciente: Dados pessoais e clínicos dos pacientes
- DoencaCronica: Catálogo de doenças crônicas
- PacienteDoenca: Relacionamento muitos-para-muitos entre pacientes e doenças
- Sintoma: Catálogo de sintomas para triagem
- Pergunta: Perguntas do questionário de triagem
- Medicamento: Base de medicamentos da ANVISA
- Consulta: Registro de consultas de triagem
- ConsultaResposta: Respostas do questionário
- ConsultaRecomendacao: Recomendações geradas pela triagem

Otimizações implementadas:
- Índices para consultas frequentes
- Relacionamentos otimizados
- Métodos de serialização eficientes
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialização do SQLAlchemy
db = SQLAlchemy()

class Usuario(db.Model):
    """
    Modelo para armazenar dados dos usuários do sistema
    
    Campos:
    - id: Identificador único (chave primária)
    - nome: Nome completo do usuário (obrigatório)
    - email: Email único para login (obrigatório)
    - senha_hash: Hash da senha (obrigatório)
    - ativo: Status do usuário (padrão: True)
    - is_admin: Se é administrador (padrão: False)
    - created_at: Data de criação do registro
    - updated_at: Data da última atualização
    - last_login: Data do último login
    
    Métodos:
    - set_password: Define a senha com hash
    - check_password: Verifica se a senha está correta
    - to_dict: Serializa o objeto para dicionário
    """
    __tablename__ = 'usuarios'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True, index=True)
    is_admin = db.Column(db.Boolean, default=False, index=True)
    
    # Timestamps para auditoria
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.TIMESTAMP)
    
    def set_password(self, senha):
        """Define a senha com hash de segurança"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Serializa o objeto para dicionário (sem senha)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Paciente(db.Model):
    """
    Modelo para armazenar dados dos pacientes
    
    Campos:
    - id: Identificador único (chave primária)
    - nome: Nome completo do paciente (máximo 200 caracteres)
    - idade: Idade em anos (obrigatório)
    - peso: Peso em kg (opcional, formato decimal 5,2)
    - altura: Altura em metros (opcional, formato decimal 3,2)
    - sexo: Sexo biológico (M/F/O - obrigatório)
    - fuma: Indica se o paciente fuma (padrão: False)
    - bebe: Indica se o paciente consome álcool (padrão: False)
    - bairro: Bairro onde o paciente reside (opcional, máximo 100 caracteres)
    - cidade: Cidade onde o paciente reside (opcional, máximo 100 caracteres)
    - created_at: Data de criação do registro
    - updated_at: Data da última atualização
    
    Relacionamentos:
    - doencas_cronicas: Lista de doenças crônicas do paciente
    - consultas: Lista de consultas realizadas pelo paciente
    """
    __tablename__ = 'pacientes'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, index=True)  # Índice para busca
    idade = db.Column(db.Integer, nullable=False, index=True)     # Índice para filtros
    peso = db.Column(db.Numeric(5, 2))
    altura = db.Column(db.Numeric(3, 2))
    sexo = db.Column(db.Enum('M', 'F', 'O'), nullable=False, index=True)  # Índice para estatísticas
    fuma = db.Column(db.Boolean, default=False)
    bebe = db.Column(db.Boolean, default=False)
    bairro = db.Column(db.String(100), index=True)  # Índice para análises geográficas
    cidade = db.Column(db.String(100), index=True)  # Índice para análises geográficas
    
    # Timestamps para auditoria
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos otimizados
    doencas_cronicas = relationship('PacienteDoenca', back_populates='paciente', lazy='select')
    consultas = relationship('Consulta', back_populates='paciente', lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'idade': self.idade,
            'peso': float(self.peso) if self.peso else None,
            'altura': float(self.altura) if self.altura else None,
            'sexo': self.sexo,
            'fuma': self.fuma,
            'bebe': self.bebe,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DoencaCronica(db.Model):
    __tablename__ = 'doencas_cronicas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relacionamentos
    pacientes = relationship('PacienteDoenca', back_populates='doenca_cronica')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao
        }

class PacienteDoenca(db.Model):
    __tablename__ = 'paciente_doencas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False)
    id_doenca_cronica = db.Column(db.Integer, db.ForeignKey('doencas_cronicas.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship('Paciente', back_populates='doencas_cronicas')
    doenca_cronica = relationship('DoencaCronica', back_populates='pacientes')

class Sintoma(db.Model):
    __tablename__ = 'sintomas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    categoria = db.Column(db.String(50))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria
        }

class Pergunta(db.Model):
    __tablename__ = 'perguntas'
    
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.Enum('sintoma', 'habito', 'historico', 'geral'), nullable=False)
    ordem = db.Column(db.Integer, default=0)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'texto': self.texto,
            'tipo': self.tipo,
            'ordem': self.ordem,
            'ativa': self.ativa
        }

class Medicamento(db.Model):
    """
    Modelo para armazenar medicamentos da base ANVISA
    
    Campos:
    - id: Identificador único (chave primária)
    - nome_comercial: Nome comercial do medicamento (obrigatório)
    - nome_generico: Nome genérico/princípio ativo (opcional)
    - descricao: Descrição do medicamento (opcional)
    - indicacao: Indicações terapêuticas (opcional)
    - contraindicacao: Contraindicações (opcional)
    - tipo: Tipo do medicamento (farmacologico/fitoterapico)
    - ativo: Status do medicamento (ativo/inativo)
    - created_at: Data de criação do registro
    
    Otimizações:
    - Índices para busca por nome
    - Índice para filtro por tipo
    - Índice para filtro por status ativo
    """
    __tablename__ = 'medicamentos'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome_comercial = db.Column(db.String(200), nullable=False, index=True)  # Índice para busca
    nome_generico = db.Column(db.String(200), index=True)                   # Índice para busca
    descricao = db.Column(db.Text)
    indicacao = db.Column(db.Text)
    contraindicacao = db.Column(db.Text)
    tipo = db.Column(db.Enum('farmacologico', 'fitoterapico'), nullable=False, index=True)  # Índice para filtros
    ativo = db.Column(db.Boolean, default=True, index=True)                 # Índice para filtros
    
    # Timestamp para auditoria
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_comercial': self.nome_comercial,
            'nome_generico': self.nome_generico,
            'descricao': self.descricao,
            'indicacao': self.indicacao,
            'contraindicacao': self.contraindicacao,
            'tipo': self.tipo,
            'ativo': self.ativo
        }

class Consulta(db.Model):
    __tablename__ = 'consultas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    encaminhamento = db.Column(db.Boolean, default=False)
    motivo_encaminhamento = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship('Paciente', back_populates='consultas')
    respostas = relationship('ConsultaResposta', back_populates='consulta')
    recomendacoes = relationship('ConsultaRecomendacao', back_populates='consulta')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_paciente': self.id_paciente,
            'data': self.data.isoformat() if self.data else None,
            'encaminhamento': self.encaminhamento,
            'motivo_encaminhamento': self.motivo_encaminhamento,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ConsultaResposta(db.Model):
    __tablename__ = 'consulta_respostas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id', ondelete='CASCADE'), nullable=False)
    id_pergunta = db.Column(db.Integer, db.ForeignKey('perguntas.id', ondelete='CASCADE'), nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relacionamentos
    consulta = relationship('Consulta', back_populates='respostas')
    pergunta = relationship('Pergunta')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'id_pergunta': self.id_pergunta,
            'resposta': self.resposta,
            'pergunta_texto': self.pergunta.texto if self.pergunta else None
        }

class ConsultaRecomendacao(db.Model):
    __tablename__ = 'consulta_recomendacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.Enum('medicamento', 'nao_farmacologico', 'encaminhamento'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    justificativa = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relacionamentos
    consulta = relationship('Consulta', back_populates='recomendacoes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_consulta': self.id_consulta,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'justificativa': self.justificativa
        }
