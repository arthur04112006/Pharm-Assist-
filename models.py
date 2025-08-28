#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Modelos do Banco de Dados
Definicao das entidades e relacionamentos
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Numeric(5, 2))
    altura = db.Column(db.Numeric(3, 2))
    sexo = db.Column(db.Enum('M', 'F', 'O'), nullable=False)
    fuma = db.Column(db.Boolean, default=False)
    bebe = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    doencas_cronicas = relationship('PacienteDoenca', back_populates='paciente')
    consultas = relationship('Consulta', back_populates='paciente')
    
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
    __tablename__ = 'medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_comercial = db.Column(db.String(200), nullable=False)
    nome_generico = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    indicacao = db.Column(db.Text)
    contraindicacao = db.Column(db.Text)
    tipo = db.Column(db.Enum('farmacologico', 'fitoterapico'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
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
