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

# ===== IMPORTAÇÕES NECESSÁRIAS =====
# SQLAlchemy para gerenciar o banco de dados
from flask_sqlalchemy import SQLAlchemy
# datetime para timestamps automáticos
from datetime import datetime
# relationship para definir relacionamentos entre tabelas
from sqlalchemy.orm import relationship
# Index para criar índices de performance
from sqlalchemy import Index

# ===== INICIALIZAÇÃO DO BANCO DE DADOS =====
# Criar instância do SQLAlchemy para gerenciar o banco
db = SQLAlchemy()

class Paciente(db.Model):
    """
    Modelo para armazenar dados dos pacientes
    
    Esta é a tabela principal que armazena informações pessoais e clínicas
    de todos os pacientes cadastrados no sistema.
    
    Campos:
    - id: Identificador único (chave primária)
    - nome: Nome completo do paciente (máximo 200 caracteres)
    - idade: Idade em anos (obrigatório)
    - peso: Peso em kg (opcional, formato decimal 5,2)
    - altura: Altura em metros (opcional, formato decimal 3,2)
    - sexo: Sexo biológico (M/F/O - obrigatório)
    - fuma: Indica se o paciente fuma (padrão: False)
    - bebe: Indica se o paciente consome álcool (padrão: False)
    - created_at: Data de criação do registro
    - updated_at: Data da última atualização
    
    Relacionamentos:
    - doencas_cronicas: Lista de doenças crônicas do paciente
    - consultas: Lista de consultas realizadas pelo paciente
    """
    __tablename__ = 'pacientes'
    
    # ===== CAMPOS PRINCIPAIS =====
    # Chave primária (ID único)
    id = db.Column(db.Integer, primary_key=True)
    # Nome completo com índice para busca rápida
    nome = db.Column(db.String(200), nullable=False, index=True)
    # Idade com índice para filtros por faixa etária
    idade = db.Column(db.Integer, nullable=False, index=True)
    # Peso em kg (opcional, formato: 999.99)
    peso = db.Column(db.Numeric(5, 2))
    # Altura em metros (opcional, formato: 9.99)
    altura = db.Column(db.Numeric(3, 2))
    # Sexo biológico com índice para estatísticas
    sexo = db.Column(db.Enum('M', 'F', 'O'), nullable=False, index=True)
    # Hábitos de vida
    fuma = db.Column(db.Boolean, default=False)
    bebe = db.Column(db.Boolean, default=False)
    
    # ===== TIMESTAMPS PARA AUDITORIA =====
    # Data de criação (automática)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    # Data de atualização (automática)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== RELACIONAMENTOS OTIMIZADOS =====
    # Lista de doenças crônicas do paciente (relacionamento muitos-para-muitos)
    doencas_cronicas = relationship('PacienteDoenca', back_populates='paciente', lazy='select')
    # Lista de consultas realizadas pelo paciente
    consultas = relationship('Consulta', back_populates='paciente', lazy='select')
    
    def to_dict(self):
        """
        Converte o objeto Paciente para dicionário
        
        Este método é usado para:
        - Serializar dados para JSON (APIs)
        - Converter para formato usado pelo sistema de pontuação
        - Facilitar a manipulação de dados no frontend
        
        Retorna: Dicionário com todos os dados do paciente
        """
        return {
            'id': self.id,                                    # ID único
            'nome': self.nome,                               # Nome completo
            'idade': self.idade,                             # Idade em anos
            'peso': float(self.peso) if self.peso else None, # Peso convertido para float
            'altura': float(self.altura) if self.altura else None, # Altura convertida para float
            'sexo': self.sexo,                               # Sexo biológico
            'fuma': self.fuma,                               # Se fuma
            'bebe': self.bebe,                              # Se bebe
            'created_at': self.created_at.isoformat() if self.created_at else None  # Data de criação
        }

class DoencaCronica(db.Model):
    """
    Modelo para armazenar doenças crônicas
    
    Esta tabela armazena o catálogo de doenças crônicas que podem
    ser associadas aos pacientes para melhor análise clínica.
    
    Campos:
    - id: Identificador único
    - nome: Nome da doença (único)
    - descricao: Descrição detalhada da doença
    - created_at: Data de criação
    """
    __tablename__ = 'doencas_cronicas'
    
    # ===== CAMPOS PRINCIPAIS =====
    # Chave primária
    id = db.Column(db.Integer, primary_key=True)
    # Nome da doença (único para evitar duplicatas)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    # Descrição detalhada (opcional)
    descricao = db.Column(db.Text)
    # Data de criação
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # ===== RELACIONAMENTOS =====
    # Lista de pacientes que possuem esta doença
    pacientes = relationship('PacienteDoenca', back_populates='doenca_cronica')
    
    def to_dict(self):
        """
        Converte o objeto DoencaCronica para dicionário
        
        Usado para serialização em APIs e frontend
        """
        return {
            'id': self.id,           # ID único
            'nome': self.nome,        # Nome da doença
            'descricao': self.descricao  # Descrição
        }

class PacienteDoenca(db.Model):
    __tablename__ = 'paciente_doencas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False, index=True)
    id_doenca_cronica = db.Column(db.Integer, db.ForeignKey('doencas_cronicas.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    paciente = relationship('Paciente', back_populates='doencas_cronicas')
    doenca_cronica = relationship('DoencaCronica', back_populates='pacientes')
    
    # Índice composto para consultas eficientes
    __table_args__ = (
        Index('idx_paciente_doenca', 'id_paciente', 'id_doenca_cronica'),
    )

class Sintoma(db.Model):
    __tablename__ = 'sintomas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True, index=True)
    categoria = db.Column(db.String(50), index=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
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
    tipo = db.Column(db.Enum('sintoma', 'habito', 'historico', 'geral'), nullable=False, index=True)
    ordem = db.Column(db.Integer, default=0, index=True)
    ativa = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
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
    - categoria: Categoria do medicamento (opcional)
    - indicacao: Indicações terapêuticas (opcional)
    - contraindicacao: Contraindicações (opcional)
    - tipo: Tipo do medicamento (farmacologico/fitoterapico)
    - ativo: Status do medicamento (ativo/inativo)
    - created_at: Data de criação do registro
    
    Otimizações:
    - Índices para busca por nome
    - Índice para filtro por tipo
    - Índice para filtro por status ativo
    - Índice para filtro por categoria
    """
    __tablename__ = 'medicamentos'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    nome_comercial = db.Column(db.String(200), nullable=False, index=True)  # Índice para busca
    nome_generico = db.Column(db.String(200), index=True)                   # Índice para busca
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(100), index=True)                       # Categoria do medicamento
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
            'categoria': self.categoria,
            'indicacao': self.indicacao,
            'contraindicacao': self.contraindicacao,
            'tipo': self.tipo,
            'ativo': self.ativo
        }

class Consulta(db.Model):
    """
    Modelo para armazenar consultas de triagem
    
    Esta é a tabela central que registra cada consulta de triagem
    realizada no sistema, incluindo resultados e recomendações.
    """
    __tablename__ = 'consultas'
    
    # ===== CAMPOS PRINCIPAIS =====
    # Chave primária
    id = db.Column(db.Integer, primary_key=True)
    # ID do paciente (chave estrangeira com CASCADE para exclusão)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False, index=True)
    # Data e hora da consulta (padrão: agora)
    data = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # Se houve encaminhamento médico
    encaminhamento = db.Column(db.Boolean, default=False, index=True)
    # Motivo do encaminhamento (texto livre)
    motivo_encaminhamento = db.Column(db.Text)
    # Observações adicionais da consulta
    observacoes = db.Column(db.Text)
    # Data de criação do registro
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
    # ===== RELACIONAMENTOS =====
    # Dados do paciente (relacionamento um-para-muitos)
    paciente = relationship('Paciente', back_populates='consultas')
    # Lista de respostas do questionário
    respostas = relationship('ConsultaResposta', back_populates='consulta')
    # Lista de recomendações geradas
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
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id', ondelete='CASCADE'), nullable=False, index=True)
    id_pergunta = db.Column(db.Integer, db.ForeignKey('perguntas.id', ondelete='CASCADE'), nullable=False, index=True)
    resposta = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
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
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo = db.Column(db.Enum('medicamento', 'nao_farmacologico', 'encaminhamento'), nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=False)
    justificativa = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, index=True)
    
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
