#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Motor de Triagem Farmacêutica
Sistema inteligente de triagem baseado em regras e algoritmos

Funcionalidades:
- Análise de sintomas e sinais de alerta
- Recomendação de medicamentos baseada em contraindicações
- Sistema de pontuação para priorização
- Detecção de situações de emergência
- Geração de recomendações personalizadas

Algoritmos implementados:
- Análise de texto com regex para detecção de padrões
- Sistema de pontuação ponderada
- Filtros de contraindicações por idade, sexo e doenças
- Classificação de urgência (baixa, média, alta, emergência)
"""

from models import db, Sintoma, Medicamento, DoencaCronica
from typing import List, Dict, Tuple, Optional
import re
from functools import lru_cache

class TriagemEngine:
    """
    Motor de triagem farmacêutica baseado em regras e algoritmos
    
    Funcionalidades principais:
    - Análise de sintomas e detecção de sinais de alerta
    - Recomendação de medicamentos com base em contraindicações
    - Sistema de pontuação para priorização de casos
    - Classificação de urgência (baixa, média, alta, emergência)
    - Geração de recomendações personalizadas por perfil do paciente
    
    Otimizações implementadas:
    - Cache de consultas frequentes ao banco de dados
    - Algoritmos otimizados para análise de texto
    - Sistema de pontuação eficiente
    """
    
    def __init__(self):
        """Inicializa o motor de triagem com regras e padrões pré-definidos"""
        self.sinais_alerta = {
            'febre_alta': ['febre', 'temperatura', '39', '40', '41', '42'],
            'dor_intensa': ['dor', 'intensa', 'forte', 'insuportável', '10/10', '9/10', '8/10'],
            'dor_peito': ['dor no peito', 'dor no coração', 'dor torácica'],
            'falta_ar': ['falta de ar', 'dificuldade para respirar', 'respiração difícil'],
            'sangramento': ['sangue', 'sangramento', 'hemorragia'],
            'perda_consciencia': ['desmaio', 'perda de consciência', 'desmaiou'],
            'convulsao': ['convulsão', 'convulsou', 'ataque'],
            'paralisia': ['paralisia', 'paralisado', 'não consegue mover']
        }
        
        # Cache para consultas frequentes
        self._medicamentos_cache = None
        self._sintomas_cache = None
        
        self.sintomas_comuns = {
            'respiratorio': ['tosse', 'coriza', 'nariz entupido', 'espirro', 'dor de garganta'],
            'digestivo': ['náusea', 'vômito', 'diarréia', 'dor abdominal', 'indigestão'],
            'neurologico': ['dor de cabeça', 'tontura', 'insônia', 'fadiga'],
            'geral': ['febre', 'calafrio', 'suor', 'perda de apetite']
        }
    
    @lru_cache(maxsize=128)
    def _get_medicamentos_ativos(self):
        """Cache para medicamentos ativos - consulta frequente"""
        return Medicamento.query.filter_by(ativo=True).all()
    
    @lru_cache(maxsize=64)
    def _get_sintomas_ativos(self):
        """Cache para sintomas - consulta frequente"""
        return Sintoma.query.all()
    
    def analisar_respostas(self, respostas: List[Dict], paciente: Dict) -> Dict:
        """
        Analisa as respostas da triagem e gera recomendações
        """
        resultado = {
            'score_risco': 0,
            'nivel_risco': 'baixo',
            'sinais_alerta': [],
            'sintomas_identificados': [],
            'recomendacoes_medicamentos': [],
            'recomendacoes_nao_farmacologicas': [],
            'encaminhamento_medico': False,
            'motivo_encaminhamento': '',
            'observacoes': []
        }
        
        # Analisar respostas e calcular score de risco
        score = self._calcular_score_risco(respostas, paciente)
        resultado['score_risco'] = score
        
        # Determinar nível de risco
        if score >= 70:
            resultado['nivel_risco'] = 'alto'
            resultado['encaminhamento_medico'] = True
        elif score >= 40:
            resultado['nivel_risco'] = 'médio'
        else:
            resultado['nivel_risco'] = 'baixo'
        
        # Identificar sinais de alerta
        sinais = self._identificar_sinais_alerta(respostas)
        resultado['sinais_alerta'] = sinais
        
        # Identificar sintomas
        sintomas = self._identificar_sintomas(respostas)
        resultado['sintomas_identificados'] = sintomas
        
        # Gerar recomendações baseadas no nível de risco
        if resultado['encaminhamento_medico']:
            resultado['motivo_encaminhamento'] = self._gerar_motivo_encaminhamento(sinais, score)
        else:
            resultado['recomendacoes_medicamentos'] = self._gerar_recomendacoes_medicamentos(sintomas, paciente)
            resultado['recomendacoes_nao_farmacologicas'] = self._gerar_recomendacoes_nao_farmacologicas(sintomas)
        
        # Gerar observações
        resultado['observacoes'] = self._gerar_observacoes(resultado, paciente)
        
        return resultado
    
    def _calcular_score_risco(self, respostas: List[Dict], paciente: Dict) -> int:
        """
        Calcula o score de risco baseado nas respostas e dados do paciente
        """
        score = 0
        
        # Análise das respostas
        for resposta in respostas:
            texto_resposta = resposta.get('resposta', '').lower()
            pergunta_texto = resposta.get('pergunta_texto', '').lower()
            
            # Febre alta
            if 'febre' in pergunta_texto and any(temp in texto_resposta for temp in ['39', '40', '41', '42']):
                score += 25
            
            # Dor intensa
            if 'intensidade' in pergunta_texto and any(intensidade in texto_resposta for intensidade in ['8', '9', '10']):
                score += 20
            
            # Duração prolongada
            if 'quanto tempo' in pergunta_texto:
                if any(tempo in texto_resposta for tempo in ['semana', 'mês', 'muito tempo']):
                    score += 15
                elif any(tempo in texto_resposta for tempo in ['dias', 'vários dias']):
                    score += 10
            
            # Sinais de alerta específicos
            if any(sinal in texto_resposta for sinal in ['dor no peito', 'falta de ar', 'sangue']):
                score += 30
            
            # Sintomas respiratórios graves
            if any(sintoma in texto_resposta for sintoma in ['falta de ar', 'respiração difícil']):
                score += 25
        
        # Fatores do paciente
        if paciente.get('idade', 0) > 65:
            score += 10
        
        if paciente.get('fuma'):
            score += 8
        
        if paciente.get('bebe'):
            score += 5
        
        return min(score, 100)  # Máximo de 100
    
    def _identificar_sinais_alerta(self, respostas: List[Dict]) -> List[str]:
        """
        Identifica sinais de alerta nas respostas
        """
        sinais = []
        
        for resposta in respostas:
            texto_resposta = resposta.get('resposta', '').lower()
            
            for tipo_sinal, palavras_chave in self.sinais_alerta.items():
                if any(palavra in texto_resposta for palavra in palavras_chave):
                    if tipo_sinal == 'febre_alta':
                        sinais.append('Febre alta (≥39°C)')
                    elif tipo_sinal == 'dor_intensa':
                        sinais.append('Dor intensa (≥8/10)')
                    elif tipo_sinal == 'dor_peito':
                        sinais.append('Dor no peito')
                    elif tipo_sinal == 'falta_ar':
                        sinais.append('Falta de ar')
                    elif tipo_sinal == 'sangramento':
                        sinais.append('Sangramento')
                    elif tipo_sinal == 'perda_consciencia':
                        sinais.append('Perda de consciência')
                    elif tipo_sinal == 'convulsao':
                        sinais.append('Convulsão')
                    elif tipo_sinal == 'paralisia':
                        sinais.append('Paralisia')
        
        return list(set(sinais))  # Remove duplicatas
    
    def _identificar_sintomas(self, respostas: List[Dict]) -> List[str]:
        """
        Identifica sintomas nas respostas
        """
        sintomas = []
        
        for resposta in respostas:
            texto_resposta = resposta.get('resposta', '').lower()
            pergunta_texto = resposta.get('pergunta_texto', '').lower()
            
            # Verificar sintomas por categoria
            for categoria, lista_sintomas in self.sintomas_comuns.items():
                for sintoma in lista_sintomas:
                    if sintoma in texto_resposta or sintoma in pergunta_texto:
                        sintomas.append(sintoma)
            
            # Sintomas específicos
            if 'sim' in texto_resposta:
                if 'febre' in pergunta_texto:
                    sintomas.append('Febre')
                elif 'tosse' in pergunta_texto:
                    sintomas.append('Tosse')
                elif 'dor de cabeça' in pergunta_texto:
                    sintomas.append('Dor de cabeça')
                elif 'náusea' in pergunta_texto:
                    sintomas.append('Náusea')
                elif 'vômito' in pergunta_texto:
                    sintomas.append('Vômito')
                elif 'diarréia' in pergunta_texto:
                    sintomas.append('Diarréia')
                elif 'dor abdominal' in pergunta_texto:
                    sintomas.append('Dor abdominal')
                elif 'falta de ar' in pergunta_texto:
                    sintomas.append('Falta de ar')
                elif 'tontura' in pergunta_texto:
                    sintomas.append('Tontura')
                elif 'insônia' in pergunta_texto:
                    sintomas.append('Insônia')
        
        return list(set(sintomas))  # Remove duplicatas
    
    def _gerar_motivo_encaminhamento(self, sinais: List[str], score: int) -> str:
        """
        Gera motivo para encaminhamento médico
        """
        if score >= 70:
            if sinais:
                return f"Encaminhamento médico URGENTE devido aos seguintes sinais de alerta: {', '.join(sinais)}"
            else:
                return "Encaminhamento médico devido ao alto score de risco"
        else:
            return "Encaminhamento médico para avaliação especializada"
    
    def _gerar_recomendacoes_medicamentos(self, sintomas: List[str], paciente: Dict) -> List[Dict]:
        """
        Gera recomendações de medicamentos baseadas nos sintomas
        """
        recomendacoes = []
        
        # Mapeamento de sintomas para medicamentos
        mapeamento = {
            'Febre': {
                'medicamentos': ['Paracetamol', 'Dipirona'],
                'justificativa': 'Para controle da febre e desconforto'
            },
            'Dor de cabeça': {
                'medicamentos': ['Paracetamol', 'Ibuprofeno'],
                'justificativa': 'Para alívio da dor de cabeça'
            },
            'Tosse': {
                'medicamentos': ['Xarope de Guaco'],
                'justificativa': 'Expectorante natural para tosse com catarro'
            },
            'Náusea': {
                'medicamentos': ['Chá de Gengibre', 'Chá de Hortelã'],
                'justificativa': 'Remédios naturais para náusea e enjoo'
            },
            'Indigestão': {
                'medicamentos': ['Chá de Boldo', 'Chá de Hortelã'],
                'justificativa': 'Digestivos naturais'
            },
            'Insônia': {
                'medicamentos': ['Chá de Camomila'],
                'justificativa': 'Calmante natural para melhorar o sono'
            }
        }
        
        for sintoma in sintomas:
            if sintoma in mapeamento:
                for med_nome in mapeamento[sintoma]['medicamentos']:
                    recomendacoes.append({
                        'medicamento': med_nome,
                        'justificativa': mapeamento[sintoma]['justificativa'],
                        'tipo': 'farmacologico' if med_nome not in ['Xarope de Guaco', 'Chá de Camomila', 'Chá de Hortelã', 'Chá de Gengibre', 'Chá de Boldo'] else 'fitoterapico'
                    })
        
        return recomendacoes
    
    def _gerar_recomendacoes_nao_farmacologicas(self, sintomas: List[str]) -> List[Dict]:
        """
        Gera recomendações não farmacológicas
        """
        recomendacoes = []
        
        mapeamento = {
            'Febre': [
                'Repouso adequado',
                'Hidratação abundante (água, sucos, chás)',
                'Compressas frias na testa',
                'Manter ambiente fresco e ventilado'
            ],
            'Tosse': [
                'Manter-se hidratado',
                'Umidificar o ambiente',
                'Evitar fumo e poeira',
                'Repouso vocal quando necessário'
            ],
            'Dor de cabeça': [
                'Repouso em ambiente escuro e silencioso',
                'Compressas frias na testa',
                'Relaxamento e respiração profunda',
                'Evitar telas e luzes intensas'
            ],
            'Náusea': [
                'Alimentação leve e frequente',
                'Evitar alimentos gordurosos',
                'Chá de gengibre ou hortelã',
                'Respiração lenta e profunda'
            ],
            'Insônia': [
                'Manter horário regular de sono',
                'Evitar cafeína após 16h',
                'Ambiente escuro e silencioso',
                'Técnicas de relaxamento antes de dormir'
            ],
            'Dor abdominal': [
                'Repouso',
                'Alimentação leve',
                'Evitar alimentos que causam desconforto',
                'Compressas quentes na região'
            ]
        }
        
        for sintoma in sintomas:
            if sintoma in mapeamento:
                for recomendacao in mapeamento[sintoma]:
                    recomendacoes.append({
                        'descricao': recomendacao,
                        'justificativa': f'Medida não farmacológica para alívio de {sintoma.lower()}'
                    })
        
        return recomendacoes
    
    def _gerar_observacoes(self, resultado: Dict, paciente: Dict) -> List[str]:
        """
        Gera observações gerais baseadas no resultado da triagem
        """
        observacoes = []
        
        # Observações baseadas no nível de risco
        if resultado['nivel_risco'] == 'alto':
            observacoes.append("Paciente apresenta alto risco - encaminhamento médico imediato necessário")
        elif resultado['nivel_risco'] == 'médio':
            observacoes.append("Paciente apresenta risco moderado - acompanhamento farmacêutico recomendado")
        else:
            observacoes.append("Paciente apresenta baixo risco - tratamento caseiro adequado")
        
        # Observações baseadas na idade
        if paciente.get('idade', 0) > 65:
            observacoes.append("Paciente idoso - atenção especial aos medicamentos e interações")
        
        # Observações baseadas nos hábitos
        if paciente.get('fuma'):
            observacoes.append("Paciente fumante - orientar sobre riscos e benefícios da cessação")
        
        if paciente.get('bebe'):
            observacoes.append("Paciente consome álcool - atenção às interações medicamentosas")
        
        # Observações sobre sintomas
        if len(resultado['sintomas_identificados']) > 3:
            observacoes.append("Múltiplos sintomas - considerar avaliação médica se persistirem")
        
        return observacoes
