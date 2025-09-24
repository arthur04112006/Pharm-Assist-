#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Pontuação para Triagem Farmacêutica
==============================================

Este módulo implementa um sistema de pesos e pontuação para as perguntas
da triagem, permitindo calcular recomendações farmacológicas e não farmacológicas
baseadas nas respostas do paciente.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

@dataclass
class QuestionWeight:
    """Define o peso de uma pergunta específica"""
    question_id: str
    question_text: str
    weight: float
    category: str  # 'sintoma', 'gravidade', 'duracao', 'historico', 'perfil'
    critical: bool = False  # Se True, resposta positiva indica encaminhamento

@dataclass
class AnswerWeight:
    """Define o peso de uma resposta específica"""
    answer_value: str
    weight: float
    category: str  # 'positivo', 'negativo', 'neutro'
    indication: str  # 'farmacologico', 'nao_farmacologico', 'encaminhamento'

@dataclass
class ScoringResult:
    """Resultado do cálculo de pontuação"""
    total_score: float
    category_scores: Dict[str, float]
    recommendations: Dict[str, List[str]]
    risk_level: str  # 'baixo', 'medio', 'alto'
    encaminhamento: bool
    confidence: float  # 0.0 a 1.0

class TriagemScoring:
    """Sistema de pontuação para triagem farmacêutica"""
    
    def __init__(self):
        self.question_weights = self._load_question_weights()
        self.answer_weights = self._load_answer_weights()
        self.thresholds = self._load_thresholds()
    
    def _load_question_weights(self) -> Dict[str, QuestionWeight]:
        """Carrega os pesos das perguntas por módulo"""
        weights = {}
        
        # Pesos para módulo de tosse
        weights.update({
            'tosse_1': QuestionWeight('tosse_1', 'Duração da tosse (dias)', 2.0, 'duracao'),
            'tosse_2': QuestionWeight('tosse_2', 'Tosse produtiva (com secreção)', 1.5, 'sintoma'),
            'tosse_3': QuestionWeight('tosse_3', 'Tosse seca', 1.0, 'sintoma'),
            'tosse_4': QuestionWeight('tosse_4', 'Histórico de rinite/alergia', 1.2, 'historico'),
            'tosse_5': QuestionWeight('tosse_5', 'Tosse noturna recorrente', 1.8, 'sintoma'),
            'tosse_6': QuestionWeight('tosse_6', 'A tosse incapacita atividades diárias', 2.5, 'gravidade', critical=True),
            'tosse_7': QuestionWeight('tosse_7', 'Tosse purulenta, com sangue e/ou odor fétido', 3.0, 'gravidade', critical=True),
            'tosse_8': QuestionWeight('tosse_8', 'Dor/pressão no peito ou falta de ar', 2.8, 'gravidade', critical=True),
            'tosse_9': QuestionWeight('tosse_9', 'Sibilância (chiado no peito)', 2.2, 'sintoma'),
            'tosse_10': QuestionWeight('tosse_10', 'Febre', 2.0, 'sintoma'),
            'tosse_11': QuestionWeight('tosse_11', 'Tosse com sangue (hemoptise)', 3.5, 'gravidade', critical=True),
            'tosse_12': QuestionWeight('tosse_12', 'Rouquidão', 1.5, 'sintoma'),
            'tosse_13': QuestionWeight('tosse_13', 'Anorexia (falta de apetite)', 1.8, 'sintoma'),
            'tosse_14': QuestionWeight('tosse_14', 'Dor de garganta com placas/disfagia', 2.0, 'sintoma'),
            'tosse_15': QuestionWeight('tosse_15', 'Dor intensa ao inspirar', 2.5, 'gravidade', critical=True),
            'tosse_16': QuestionWeight('tosse_16', 'Sintomas gastrointestinais', 1.5, 'sintoma'),
            'tosse_17': QuestionWeight('tosse_17', 'Artralgia (dor nas articulações)', 1.8, 'sintoma'),
            'tosse_18': QuestionWeight('tosse_18', 'Conjuntivite não purulenta', 1.5, 'sintoma'),
            'tosse_19': QuestionWeight('tosse_19', 'Mal-estar geral', 1.2, 'sintoma'),
            'tosse_20': QuestionWeight('tosse_20', 'Dor facial moderada a grave', 2.0, 'sintoma'),
            'tosse_21': QuestionWeight('tosse_21', 'Dor epigástrica', 1.5, 'sintoma'),
            'tosse_22': QuestionWeight('tosse_22', 'Regurgitação ácida', 1.2, 'sintoma'),
            'tosse_23': QuestionWeight('tosse_23', 'Linfonodomegalia (ínguas)', 2.0, 'sintoma'),
            'tosse_24': QuestionWeight('tosse_24', 'Hepatoesplenomegalia', 2.5, 'sintoma', critical=True),
            'tosse_25': QuestionWeight('tosse_25', 'Edema em membros inferiores', 2.2, 'sintoma', critical=True),
            'tosse_26': QuestionWeight('tosse_26', 'Uso de inibidores da ECA', 1.5, 'historico'),
            'tosse_27': QuestionWeight('tosse_27', 'Sem melhora após 7 dias de tratamento OTC', 2.0, 'historico'),
        })
        
        # Pesos para módulo de diarreia
        weights.update({
            'diarreia_1': QuestionWeight('diarreia_1', 'Duração dos sintomas (dias)', 2.0, 'duracao'),
            'diarreia_2': QuestionWeight('diarreia_2', 'Número de evacuações por dia', 1.8, 'gravidade'),
            'diarreia_3': QuestionWeight('diarreia_3', 'Fezes aquosas', 1.5, 'sintoma'),
            'diarreia_4': QuestionWeight('diarreia_4', 'Muco nas fezes', 2.0, 'sintoma'),
            'diarreia_5': QuestionWeight('diarreia_5', 'Sangue nas fezes', 3.0, 'gravidade', critical=True),
            'diarreia_6': QuestionWeight('diarreia_6', 'Diarreia noturna', 2.2, 'sintoma'),
            'diarreia_7': QuestionWeight('diarreia_7', 'Dor abdominal forte', 2.0, 'gravidade'),
            'diarreia_8': QuestionWeight('diarreia_8', 'Tenesmo (vontade de evacuar sem eliminação)', 1.8, 'sintoma'),
            'diarreia_9': QuestionWeight('diarreia_9', 'Vômitos persistentes', 2.5, 'gravidade', critical=True),
            'diarreia_10': QuestionWeight('diarreia_10', 'Febre >38°C', 2.0, 'sintoma'),
            'diarreia_11': QuestionWeight('diarreia_11', 'Sinais de desidratação', 2.8, 'gravidade', critical=True),
            'diarreia_12': QuestionWeight('diarreia_12', 'Fezes pretas como borra de café (melena)', 3.0, 'gravidade', critical=True),
            'diarreia_13': QuestionWeight('diarreia_13', 'Perda de peso', 2.0, 'sintoma'),
            'diarreia_14': QuestionWeight('diarreia_14', 'Uso de antibiótico nos últimos 30 dias', 1.5, 'historico'),
            'diarreia_15': QuestionWeight('diarreia_15', 'Viagem recente ou contato com surto', 2.0, 'historico'),
            'diarreia_16': QuestionWeight('diarreia_16', 'Doença inflamatória intestinal', 2.5, 'historico', critical=True),
            'diarreia_17': QuestionWeight('diarreia_17', 'Síndrome do Intestino Irritável refratária', 2.0, 'historico'),
            'diarreia_18': QuestionWeight('diarreia_18', 'Falha ou reação adversa com OTC', 1.8, 'historico'),
        })
        
        # Pesos para módulo de dor de cabeça
        weights.update({
            'dor_cabeca_1': QuestionWeight('dor_cabeca_1', 'Duração do episódio atual (dias)', 2.0, 'duracao'),
            'dor_cabeca_2': QuestionWeight('dor_cabeca_2', 'Frequência: quantos dias de dor por mês', 1.8, 'duracao'),
            'dor_cabeca_3': QuestionWeight('dor_cabeca_3', 'As crises costumam durar 4–72h', 1.5, 'sintoma'),
            'dor_cabeca_4': QuestionWeight('dor_cabeca_4', 'Dor unilateral, periorbitária/temporal', 2.0, 'sintoma'),
            'dor_cabeca_5': QuestionWeight('dor_cabeca_5', 'Dor pulsátil, início gradual e crescente', 1.8, 'sintoma'),
            'dor_cabeca_6': QuestionWeight('dor_cabeca_6', 'Inicia pela manhã, piora deitado', 2.2, 'sintoma'),
            'dor_cabeca_7': QuestionWeight('dor_cabeca_7', 'Mudança do padrão nos últimos 6 meses', 2.5, 'sintoma', critical=True),
            'dor_cabeca_8': QuestionWeight('dor_cabeca_8', 'Dor occipital grave', 2.8, 'gravidade', critical=True),
            'dor_cabeca_9': QuestionWeight('dor_cabeca_9', 'Dor moderada a grave que incapacita', 2.5, 'gravidade', critical=True),
            'dor_cabeca_10': QuestionWeight('dor_cabeca_10', 'Dor bilateral em aperto', 1.2, 'sintoma'),
            'dor_cabeca_11': QuestionWeight('dor_cabeca_11', 'Aumento da sensibilidade pericraniana', 1.5, 'sintoma'),
            'dor_cabeca_12': QuestionWeight('dor_cabeca_12', 'Padrão estável há ≥6 meses', 0.8, 'sintoma'),
            'dor_cabeca_13': QuestionWeight('dor_cabeca_13', 'Enxaqueca conhecida', 1.0, 'historico'),
            'dor_cabeca_14': QuestionWeight('dor_cabeca_14', 'Há gatilhos', 1.2, 'sintoma'),
            'dor_cabeca_15': QuestionWeight('dor_cabeca_15', 'Alivia em ambiente escuro e silencioso', 1.0, 'sintoma'),
            'dor_cabeca_16': QuestionWeight('dor_cabeca_16', 'Há apenas fotofobia/fonofobia', 1.2, 'sintoma'),
            'dor_cabeca_17': QuestionWeight('dor_cabeca_17', 'Febre ou calafrios', 2.0, 'sintoma'),
            'dor_cabeca_18': QuestionWeight('dor_cabeca_18', 'Sonolência excessiva', 2.2, 'sintoma', critical=True),
            'dor_cabeca_19': QuestionWeight('dor_cabeca_19', 'Náuseas ou vômitos', 1.8, 'sintoma'),
            'dor_cabeca_20': QuestionWeight('dor_cabeca_20', 'Mialgias', 1.5, 'sintoma'),
            'dor_cabeca_21': QuestionWeight('dor_cabeca_21', 'Pressão arterial elevada', 2.0, 'sintoma'),
            'dor_cabeca_22': QuestionWeight('dor_cabeca_22', 'Perda de peso', 2.0, 'sintoma'),
            'dor_cabeca_23': QuestionWeight('dor_cabeca_23', 'Rigidez de nuca', 2.8, 'sintoma', critical=True),
            'dor_cabeca_24': QuestionWeight('dor_cabeca_24', 'Tontura', 1.8, 'sintoma'),
            'dor_cabeca_25': QuestionWeight('dor_cabeca_25', 'Confusão mental', 2.5, 'sintoma', critical=True),
            'dor_cabeca_26': QuestionWeight('dor_cabeca_26', 'Lacrimejamento/vermelhidão ao redor dos olhos', 1.5, 'sintoma'),
            'dor_cabeca_27': QuestionWeight('dor_cabeca_27', 'Rinorreia, sudorese ou agitação', 1.8, 'sintoma'),
            'dor_cabeca_28': QuestionWeight('dor_cabeca_28', 'Sinais neurológicos focais', 3.0, 'sintoma', critical=True),
            'dor_cabeca_29': QuestionWeight('dor_cabeca_29', 'Edema palpebral, miose ou ptose', 2.5, 'sintoma', critical=True),
            'dor_cabeca_30': QuestionWeight('dor_cabeca_30', 'Visão turva ou dupla', 2.8, 'sintoma', critical=True),
            'dor_cabeca_31': QuestionWeight('dor_cabeca_31', 'Papiledema', 3.0, 'sintoma', critical=True),
            'dor_cabeca_32': QuestionWeight('dor_cabeca_32', 'Pupilas desiguais ou que não reagem à luz', 3.0, 'sintoma', critical=True),
            'dor_cabeca_33': QuestionWeight('dor_cabeca_33', 'Aura sem diagnóstico prévio de enxaqueca', 2.0, 'sintoma'),
            'dor_cabeca_34': QuestionWeight('dor_cabeca_34', 'Suspeita de reação a medicamento', 1.8, 'historico'),
            'dor_cabeca_35': QuestionWeight('dor_cabeca_35', 'Falha terapêutica prévia', 1.5, 'historico'),
            'dor_cabeca_36': QuestionWeight('dor_cabeca_36', 'Uso de analgésicos/AINEs ≥15 dias/mês', 2.0, 'historico'),
            'dor_cabeca_37': QuestionWeight('dor_cabeca_37', 'Uso de triptanos/opioides ≥10 dias/mês', 2.2, 'historico'),
        })
        
        return weights
    
    def _load_answer_weights(self) -> Dict[str, AnswerWeight]:
        """Carrega os pesos das respostas"""
        weights = {}
        
        # Respostas booleanas
        weights.update({
            'sim': AnswerWeight('sim', 1.0, 'positivo', 'farmacologico'),
            'nao': AnswerWeight('nao', 0.0, 'negativo', 'nao_farmacologico'),
            'yes': AnswerWeight('yes', 1.0, 'positivo', 'farmacologico'),
            'no': AnswerWeight('no', 0.0, 'negativo', 'nao_farmacologico'),
        })
        
        # Respostas numéricas (duração em dias)
        for days in range(1, 31):
            if days <= 3:
                weights[f'{days}'] = AnswerWeight(f'{days}', 0.5, 'neutro', 'nao_farmacologico')
            elif days <= 7:
                weights[f'{days}'] = AnswerWeight(f'{days}', 1.0, 'positivo', 'farmacologico')
            elif days <= 14:
                weights[f'{days}'] = AnswerWeight(f'{days}', 1.5, 'positivo', 'farmacologico')
            else:
                weights[f'{days}'] = AnswerWeight(f'{days}', 2.0, 'positivo', 'encaminhamento')
        
        # Respostas numéricas (frequência)
        for freq in range(1, 31):
            if freq <= 3:
                weights[f'freq_{freq}'] = AnswerWeight(f'freq_{freq}', 0.5, 'neutro', 'nao_farmacologico')
            elif freq <= 10:
                weights[f'freq_{freq}'] = AnswerWeight(f'freq_{freq}', 1.0, 'positivo', 'farmacologico')
            elif freq <= 20:
                weights[f'freq_{freq}'] = AnswerWeight(f'freq_{freq}', 1.5, 'positivo', 'farmacologico')
            else:
                weights[f'freq_{freq}'] = AnswerWeight(f'freq_{freq}', 2.0, 'positivo', 'encaminhamento')
        
        return weights
    
    def _load_thresholds(self) -> Dict[str, float]:
        """Carrega os limiares para classificação"""
        return {
            'baixo': 0.0,
            'medio': 15.0,
            'alto': 30.0,
            'encaminhamento': 25.0
        }
    
    def calculate_score(self, modulo: str, respostas: List[Dict[str, str]], paciente_profile: Dict) -> ScoringResult:
        """Calcula a pontuação baseada nas respostas"""
        total_score = 0.0
        category_scores = {
            'sintoma': 0.0,
            'gravidade': 0.0,
            'duracao': 0.0,
            'historico': 0.0,
            'perfil': 0.0
        }
        
        recommendations = {
            'farmacologico': [],
            'nao_farmacologico': [],
            'encaminhamento': []
        }
        
        encaminhamento = False
        critical_answers = []
        
        # Processar cada resposta
        for resposta in respostas:
            question_id = resposta['pergunta_id']
            answer_value = resposta['resposta'].lower().strip()
            
            # Buscar peso da pergunta
            if question_id in self.question_weights:
                question_weight = self.question_weights[question_id]
                
                # Buscar peso da resposta
                answer_weight = self.answer_weights.get(answer_value, AnswerWeight(answer_value, 0.5, 'neutro', 'nao_farmacologico'))
                
                # Calcular pontuação
                score = question_weight.weight * answer_weight.weight
                total_score += score
                category_scores[question_weight.category] += score
                
                # Verificar se é crítica
                if question_weight.critical and answer_value in ['sim', 'yes', '1', 'true']:
                    encaminhamento = True
                    critical_answers.append(question_weight.question_text)
                
                # Adicionar à categoria de recomendação
                if answer_weight.indication in recommendations:
                    recommendations[answer_weight.indication].append(question_weight.question_text)
        
        # Aplicar modificadores baseados no perfil do paciente
        if paciente_profile.get('is_frail_elderly', False):
            total_score *= 1.2  # Aumentar pontuação para idosos frágeis
            category_scores['perfil'] += 5.0
        
        if paciente_profile.get('is_pregnant_or_lactating', False):
            total_score *= 1.1  # Aumentar pontuação para gestantes/lactantes
            category_scores['perfil'] += 3.0
        
        # Determinar nível de risco
        if encaminhamento or total_score >= self.thresholds['encaminhamento']:
            risk_level = 'alto'
            encaminhamento = True
        elif total_score >= self.thresholds['alto']:
            risk_level = 'alto'
        elif total_score >= self.thresholds['medio']:
            risk_level = 'medio'
        else:
            risk_level = 'baixo'
        
        # Calcular confiança baseada na consistência das respostas
        confidence = min(1.0, len(respostas) / 10.0)  # Máximo 100% com 10+ respostas
        
        return ScoringResult(
            total_score=total_score,
            category_scores=category_scores,
            recommendations=recommendations,
            risk_level=risk_level,
            encaminhamento=encaminhamento,
            confidence=confidence
        )
    
    def generate_recommendations(self, scoring_result: ScoringResult, modulo: str, 
                                respostas: List[Dict[str, str]] = None, 
                                paciente_profile: Dict = None) -> Dict[str, List[str]]:
        """Gera recomendações baseadas na pontuação e respostas específicas"""
        from recomendacoes_farmacologicas import sistema_recomendacoes
        
        recommendations = {
            'farmacologicas': [],
            'nao_farmacologicas': [],
            'encaminhamento': []
        }
        
        # Gerar recomendações farmacológicas específicas usando o sistema de recomendações
        if respostas and paciente_profile:
            try:
                recomendacoes_farmacologicas = sistema_recomendacoes.gerar_recomendacoes(
                    modulo, respostas, scoring_result, paciente_profile
                )
                
                for rec in recomendacoes_farmacologicas:
                    recomendacao_texto = f"{rec.medicamento}"
                    if rec.principio_ativo and rec.principio_ativo != rec.medicamento:
                        recomendacao_texto += f" ({rec.principio_ativo})"
                    recomendacao_texto += f" - {rec.indicacao}"
                    if rec.posologia:
                        recomendacao_texto += f" | Posologia: {rec.posologia}"
                    if rec.observacoes:
                        recomendacao_texto += f" | {rec.observacoes}"
                    
                    recommendations['farmacologicas'].append(recomendacao_texto)
            except Exception as e:
                print(f"Erro ao gerar recomendações farmacológicas: {e}")
                # Fallback para recomendações genéricas
                recommendations['farmacologicas'] = self._gerar_recomendacoes_genericas(modulo, scoring_result)
        else:
            # Fallback para recomendações genéricas
            recommendations['farmacologicas'] = self._gerar_recomendacoes_genericas(modulo, scoring_result)
        
        # Recomendações não farmacológicas
        recommendations['nao_farmacologicas'] = self._gerar_recomendacoes_nao_farmacologicas(modulo)
        
        # Encaminhamento se necessário
        if scoring_result.encaminhamento:
            recommendations['encaminhamento'].append('Encaminhamento médico necessário')
            if scoring_result.category_scores['gravidade'] > 10.0:
                recommendations['encaminhamento'].append('Avaliação urgente recomendada')
        
        return recommendations
    
    def _gerar_recomendacoes_genericas(self, modulo: str, scoring_result: ScoringResult) -> List[str]:
        """Gera recomendações farmacológicas genéricas baseadas na pontuação"""
        recommendations = []
        
        if scoring_result.category_scores['sintoma'] > 5.0:
            if modulo == 'tosse':
                if scoring_result.category_scores['sintoma'] > 8.0:
                    recommendations.append('Antitussígenos: dextrometorfano, clobutinol')
                if scoring_result.category_scores['sintoma'] > 6.0:
                    recommendations.append('Expectorantes: guaifenesina, ambroxol')
                if scoring_result.category_scores['historico'] > 3.0:
                    recommendations.append('Antialérgicos: loratadina, desloratadina')
            
            elif modulo == 'diarreia':
                if scoring_result.category_scores['sintoma'] > 6.0:
                    recommendations.append('Loperamida (adultos) para reduzir evacuações')
                recommendations.append('Probióticos como adjuvantes')
                if scoring_result.category_scores['perfil'] > 2.0:
                    recommendations.append('Zinco para crianças')
            
            elif modulo == 'dor_cabeca':
                if scoring_result.category_scores['sintoma'] > 8.0:
                    recommendations.append('AINEs: ibuprofeno, naproxeno')
                if scoring_result.category_scores['sintoma'] > 6.0:
                    recommendations.append('Paracetamol como alternativa')
                if scoring_result.category_scores['sintoma'] > 4.0:
                    recommendations.append('Associação com cafeína')
        
        return recommendations
    
    def _gerar_recomendacoes_nao_farmacologicas(self, modulo: str) -> List[str]:
        """Gera recomendações não farmacológicas específicas por módulo"""
        if modulo == 'tosse':
            return [
                'Aumentar ingestão de líquidos (água, sucos, chás)',
                'Ingerir mel (com cautela em diabéticos)',
                'Usar umidificadores ou vaporizadores',
                'Cessar tabagismo',
                'Evitar exposição à poluição e irritantes'
            ]
        
        elif modulo == 'diarreia':
            return [
                'Hidratação com Solução de Reidratação Oral (SRO)',
                'Dieta leve: arroz, batata, banana, maçã',
                'Evitar gorduras e laticínios temporariamente',
                'Higiene das mãos e preparo seguro dos alimentos',
                'Evitar automedicação com antibióticos'
            ]
        
        elif modulo == 'dor_cabeca':
            return [
                'Repouso em ambiente escuro e silencioso',
                'Bolsa térmica (quente ou fria) na cabeça',
                'Manter rotina regular de sono e alimentação',
                'Técnicas de relaxamento',
                'Identificar e evitar gatilhos (estresse, álcool, etc.)'
            ]
        
        elif modulo == 'dor_garganta':
            return [
                'Gargarejos com água morna e sal',
                'Ingerir líquidos mornos (chás, sopas)',
                'Evitar alimentos muito quentes ou frios',
                'Repouso da voz',
                'Umidificar o ambiente'
            ]
        
        elif modulo == 'azia_ma_digestao':
            return [
                'Evitar refeições grandes e gordurosas',
                'Não deitar após as refeições',
                'Elevar a cabeceira da cama',
                'Evitar álcool, café e alimentos ácidos',
                'Comer devagar e mastigar bem'
            ]
        
        elif modulo == 'constipacao':
            return [
                'Aumentar ingestão de fibras (frutas, verduras, cereais)',
                'Beber mais água (2-3 litros/dia)',
                'Praticar atividade física regular',
                'Estabelecer horário regular para evacuação',
                'Evitar segurar a vontade de evacuar'
            ]
        
        elif modulo == 'hemorroidas':
            return [
                'Higiene local com água morna',
                'Evitar papel higiênico áspero',
                'Aplicar compressas frias',
                'Evitar esforço excessivo na evacuação',
                'Aumentar ingestão de fibras e água'
            ]
        
        elif modulo == 'dor_lombar':
            return [
                'Repouso relativo (evitar atividades que pioram a dor)',
                'Aplicar calor local',
                'Manter postura correta',
                'Fortalecimento da musculatura abdominal',
                'Evitar levantar pesos'
            ]
        
        elif modulo == 'espirro_congestao_nasal':
            return [
                'Lavagem nasal com soro fisiológico',
                'Umidificar o ambiente',
                'Evitar alérgenos conhecidos',
                'Usar máscara em ambientes poluídos',
                'Manter ambiente limpo e arejado'
            ]
        
        return []

# Instância global do sistema de pontuação
scoring_system = TriagemScoring()
