#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor Unificado de Perguntas e Respostas da Triagem
====================================================

Este serviço fornece uma interface única para coletar todas as perguntas e respostas
de uma consulta de triagem, independentemente dos módulos utilizados.

Funcionalidades:
- Coleta perguntas e respostas de múltiplos módulos
- Consolida dados em estrutura única
- Ordena perguntas por ordem de exibição
- Vincula corretamente ao ID da consulta
- Fornece logging detalhado para depuração
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from models.models import db, Consulta, ConsultaResposta, Pergunta
from utils.extractors.perguntas_extractor import extract_questions_for_module, get_patient_profile_from_cadastro

# Configurar logging
logger = logging.getLogger(__name__)

class QACollector:
    """
    Coletor unificado para perguntas e respostas da triagem
    """
    
    def __init__(self):
        self.logger = logger
    
    def collect_qa_for_consulta(self, consulta_id: int) -> Dict:
        """
        Coleta todas as perguntas e respostas de uma consulta específica
        
        Args:
            consulta_id: ID da consulta
            
        Returns:
            Dict com estrutura consolidada de perguntas e respostas
        """
        try:
            # Buscar consulta
            consulta = Consulta.query.get_or_404(consulta_id)
            
            # Log inicial
            self.logger.info(f"Iniciando coleta de Q&A para consulta {consulta_id}")
            
            # Coletar respostas persistidas
            respostas_persistidas = self._collect_persisted_responses(consulta)
            
            # Se não há respostas, retornar estrutura vazia
            if not respostas_persistidas:
                self.logger.warning(f"Nenhuma resposta encontrada para consulta {consulta_id}")
                return {
                    'consulta_id': consulta.id,
                    'data_consulta': consulta.data.isoformat() if consulta.data else None,
                    'paciente_id': consulta.id_paciente,
                    'modulos_utilizados': [],
                    'total_perguntas': 0,
                    'perguntas_respostas': [],
                    'coletado_em': datetime.now().isoformat()
                }
            
            # Detectar módulos utilizados
            modulos_detectados = self._detect_modules_from_responses(respostas_persistidas)
            
            # Coletar perguntas dos módulos detectados
            perguntas_modulos = self._collect_module_questions(modulos_detectados)
            
            # Consolidar perguntas e respostas
            qa_consolidado = self._consolidate_qa(respostas_persistidas, perguntas_modulos, consulta)
            
            # Log de resumo
            self._log_collection_summary(consulta_id, qa_consolidado, modulos_detectados)
            
            return qa_consolidado
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar Q&A para consulta {consulta_id}: {str(e)}")
            raise
    
    def _collect_persisted_responses(self, consulta: Consulta) -> List[Dict]:
        """
        Coleta respostas persistidas no banco de dados
        """
        respostas = []
        
        for resposta in consulta.respostas:
            # Buscar texto da pergunta
            pergunta = Pergunta.query.get(resposta.id_pergunta)
            pergunta_texto = pergunta.texto if pergunta else f"Pergunta ID {resposta.id_pergunta}"
            
            respostas.append({
                'id': resposta.id,
                'pergunta_id': resposta.id_pergunta,
                'pergunta_texto': pergunta_texto,
                'resposta': resposta.resposta,
                'modulo': self._detect_module_from_question_text(pergunta_texto),
                'ordem': pergunta.ordem if pergunta else 999
            })
        
        self.logger.info(f"Coletadas {len(respostas)} respostas persistidas")
        return respostas
    
    def _detect_modules_from_responses(self, respostas: List[Dict]) -> List[str]:
        """
        Detecta módulos utilizados baseado nas respostas
        """
        modulos = set()
        
        for resposta in respostas:
            modulo = resposta.get('modulo')
            if modulo and modulo != 'geral':
                modulos.add(modulo)
        
        # Se não há módulos detectados, retornar lista vazia em vez de ['geral']
        modulos_list = list(modulos) if modulos else []
        self.logger.info(f"Módulos detectados: {modulos_list}")
        return modulos_list
    
    def _detect_module_from_question_text(self, texto: str) -> str:
        """
        Detecta módulo baseado no texto da pergunta
        """
        if not texto:
            return 'geral'
        
        texto_lower = texto.lower()
        
        # Mapear palavras-chave para módulos
        module_keywords = {
            'tosse': ['tosse', 'tossir', 'expectoração', 'tosse seca', 'tosse produtiva'],
            'febre': ['febre', 'temperatura', 'calafrio', 'febril'],
            'dor_cabeca': ['dor de cabeça', 'cefaleia', 'enxaqueca'],
            'diarreia': ['diarreia', 'evacuação', 'fezes', 'evacuações', 'banheiro'],
            'dor_garganta': ['garganta', 'dor de garganta', 'faringite'],
            'azia_ma_digestao': ['azia', 'queimação', 'refluxo', 'digestão', 'estômago'],
            'constipacao': ['constipação', 'prisão de ventre', 'intestino', 'evacuar'],
            'hemorroidas': ['hemorroida', 'hemorroidas', 'anal', 'sangramento anal'],
            'dor_lombar': ['lombar', 'coluna', 'costas', 'dor lombar'],
            'espirro_congestao_nasal': ['congestão', 'nasal', 'espirro', 'rinite', 'nariz'],
            'dismenorreia': ['dismenorreia', 'menstruação', 'cólica menstrual'],
            'infeccoes_fungicas': ['fungica', 'micose', 'candidíase', 'fungo'],
            'queimadura_solar': ['queimadura', 'solar', 'sol', 'pele']
        }
        
        for modulo, keywords in module_keywords.items():
            if any(keyword in texto_lower for keyword in keywords):
                return modulo
        
        return 'geral'
    
    def _collect_module_questions(self, modulos: List[str]) -> Dict[str, List[Dict]]:
        """
        Coleta perguntas dos módulos detectados
        """
        perguntas_modulos = {}
        
        for modulo in modulos:
            try:
                perguntas = extract_questions_for_module(modulo, filter_unnecessary=True)
                perguntas_modulos[modulo] = perguntas
                self.logger.info(f"Coletadas {len(perguntas)} perguntas do módulo {modulo}")
            except Exception as e:
                self.logger.warning(f"Erro ao coletar perguntas do módulo {modulo}: {str(e)}")
                perguntas_modulos[modulo] = []
        
        return perguntas_modulos
    
    def _consolidate_qa(self, respostas: List[Dict], perguntas_modulos: Dict[str, List[Dict]], consulta: Consulta) -> Dict:
        """
        Consolida perguntas e respostas em estrutura única
        """
        # Criar mapa de perguntas por texto (já que os IDs não coincidem)
        perguntas_map = {}
        for modulo, perguntas in perguntas_modulos.items():
            for pergunta in perguntas:
                # Usar o texto da pergunta como chave para mapeamento
                perguntas_map[pergunta['texto']] = pergunta
        
        # Consolidar respostas com informações das perguntas
        qa_consolidado = []
        
        for resposta in respostas:
            # Usar o texto da pergunta para buscar informações adicionais
            pergunta_texto = resposta['pergunta_texto']
            pergunta_info = perguntas_map.get(pergunta_texto, {})
            
            qa_item = {
                'pergunta_id': resposta['pergunta_id'],
                'pergunta_texto': resposta['pergunta_texto'],
                'resposta': resposta['resposta'],
                'modulo': resposta['modulo'],
                'ordem': resposta.get('ordem', 999),
                'tipo': pergunta_info.get('tipo', 'string'),
                'categoria': pergunta_info.get('categoria', 'sintoma'),
                'peso': pergunta_info.get('peso', 1.0),
                'critica': pergunta_info.get('critica', False),
                'indication': pergunta_info.get('indication', 'nao_farmacologico')
            }
            
            qa_consolidado.append(qa_item)
        
        # Ordenar por ordem de exibição
        qa_consolidado.sort(key=lambda x: (x['modulo'], x['ordem']))
        
        return {
            'consulta_id': consulta.id,
            'data_consulta': consulta.data.isoformat() if consulta.data else None,
            'paciente_id': consulta.id_paciente,
            'modulos_utilizados': list(perguntas_modulos.keys()),
            'total_perguntas': len(qa_consolidado),
            'perguntas_respostas': qa_consolidado,
            'coletado_em': datetime.now().isoformat()
        }
    
    def _log_collection_summary(self, consulta_id: int, qa_consolidado: Dict, modulos_detectados: List[str]):
        """
        Registra resumo da coleta para depuração
        """
        total_perguntas = qa_consolidado['total_perguntas']
        modulos = qa_consolidado['modulos_utilizados']
        
        self.logger.info(f"RESUMO COLETA Q&A - Consulta {consulta_id}:")
        self.logger.info(f"  - Total de perguntas: {total_perguntas}")
        self.logger.info(f"  - Módulos utilizados: {modulos}")
        self.logger.info(f"  - Origem: {'persistidas' if total_perguntas > 0 else 'nenhuma'}")
        
        # Log detalhado por módulo
        for modulo in modulos:
            perguntas_modulo = [qa for qa in qa_consolidado['perguntas_respostas'] if qa['modulo'] == modulo]
            self.logger.info(f"  - Módulo {modulo}: {len(perguntas_modulo)} perguntas")
    
    def collect_qa_from_session(self, session_data: Dict, modulo: str) -> Dict:
        """
        Coleta perguntas e respostas do estado atual da sessão/triagem
        
        Args:
            session_data: Dados da sessão atual
            modulo: Módulo da triagem
            
        Returns:
            Dict com estrutura consolidada
        """
        try:
            self.logger.info(f"Coletando Q&A da sessão para módulo {modulo}")
            
            # Extrair perguntas do módulo
            perguntas_modulo = extract_questions_for_module(modulo, filter_unnecessary=True)
            
            # Preparar respostas da sessão
            respostas_sessao = session_data.get('respostas', [])
            
            # Consolidar
            qa_consolidado = []
            
            for i, pergunta in enumerate(perguntas_modulo):
                resposta_encontrada = None
                
                # Buscar resposta correspondente
                for resposta in respostas_sessao:
                    if resposta.get('pergunta_id') == pergunta['id']:
                        resposta_encontrada = resposta.get('resposta', 'N/A')
                        break
                
                qa_item = {
                    'pergunta_id': pergunta['id'],
                    'pergunta_texto': pergunta['texto'],
                    'resposta': resposta_encontrada or 'N/A',
                    'modulo': modulo,
                    'ordem': pergunta['ordem'],
                    'tipo': pergunta['tipo'],
                    'categoria': pergunta['categoria'],
                    'peso': pergunta['peso'],
                    'critica': pergunta['critica'],
                    'indication': pergunta['indication']
                }
                
                qa_consolidado.append(qa_item)
            
            # Ordenar por ordem
            qa_consolidado.sort(key=lambda x: x['ordem'])
            
            return {
                'consulta_id': session_data.get('consulta_id'),
                'modulo': modulo,
                'total_perguntas': len(qa_consolidado),
                'perguntas_respostas': qa_consolidado,
                'coletado_em': datetime.now().isoformat(),
                'origem': 'sessao'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar Q&A da sessão: {str(e)}")
            raise


# Instância global do coletor
qa_collector = QACollector()
