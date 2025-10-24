#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Recomendações Farmacológicas
=======================================

Este módulo implementa um sistema inteligente de recomendações farmacológicas
baseado nas respostas da triagem e nas indicações dos medicamentos cadastrados.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode
from models import Medicamento, db

@dataclass
class RecomendacaoFarmacologica:
    """Estrutura para uma recomendação farmacológica"""
    medicamento: str
    principio_ativo: str
    indicacao: str
    posologia: str
    contraindicacoes: str
    observacoes: str
    prioridade: int  # 1-5 (1 = alta prioridade)
    categoria: str  # 'sintomatico', 'terapeutico', 'preventivo'

class SistemaRecomendacoesFarmacologicas:
    """Sistema de recomendações farmacológicas baseado em indicações"""
    
    def __init__(self):
        self.palavras_chave_sintomas = self._carregar_palavras_chave()
        self.medicamentos_cache = None
        self.tfidf_vectorizer = None
        self.medicamentos_tfidf_matrix = None
        self.medicamentos_textos = []
    
    def normalizar_texto(self, texto: str) -> str:
        """Normaliza texto removendo acentos, pontuação e convertendo para minúsculas"""
        if not texto:
            return ""
        
        # Remove acentos usando unidecode
        texto_normalizado = unidecode(texto)
        
        # Converte para minúsculas
        texto_normalizado = texto_normalizado.lower()
        
        # Remove pontuação e caracteres especiais, mantendo apenas letras, números e espaços
        texto_normalizado = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto_normalizado)
        
        # Remove espaços múltiplos
        texto_normalizado = re.sub(r'\s+', ' ', texto_normalizado)
        
        # Remove espaços no início e fim
        texto_normalizado = texto_normalizado.strip()
        
        return texto_normalizado
    
    def expandir_sintomas(self, sintomas: List[str]) -> List[str]:
        """
        Expande uma lista de sintomas incluindo seus sinônimos clínicos.
        
        Args:
            sintomas: Lista de sintomas originais
            
        Returns:
            Lista expandida com sintomas originais e seus sinônimos
        """
        sintomas_expandidos = set()
        
        try:
            # Carregar dicionário de sinônimos
            caminho_sinonimos = os.path.join(os.path.dirname(__file__), 'data', 'sinonimos.json')
            
            if os.path.exists(caminho_sinonimos):
                with open(caminho_sinonimos, 'r', encoding='utf-8') as f:
                    sinonimos = json.load(f)
                
                # Adicionar sintomas originais
                for sintoma in sintomas:
                    sintoma_normalizado = self.normalizar_texto(sintoma)
                    sintomas_expandidos.add(sintoma_normalizado)
                    
                    # Buscar sinônimos para o sintoma
                    for termo_principal, lista_sinonimos in sinonimos.items():
                        termo_principal_normalizado = self.normalizar_texto(termo_principal)
                        
                        # Se o sintoma corresponde ao termo principal
                        if sintoma_normalizado == termo_principal_normalizado:
                            for sinonimo in lista_sinonimos:
                                sinonimo_normalizado = self.normalizar_texto(sinonimo)
                                sintomas_expandidos.add(sinonimo_normalizado)
                        
                        # Se o sintoma corresponde a algum sinônimo
                        for sinonimo in lista_sinonimos:
                            sinonimo_normalizado = self.normalizar_texto(sinonimo)
                            if sintoma_normalizado == sinonimo_normalizado:
                                # Adicionar o termo principal e outros sinônimos
                                sintomas_expandidos.add(termo_principal_normalizado)
                                for outro_sinonimo in lista_sinonimos:
                                    outro_sinonimo_normalizado = self.normalizar_texto(outro_sinonimo)
                                    sintomas_expandidos.add(outro_sinonimo_normalizado)
                                break
            else:
                # Se arquivo não existe, retornar sintomas originais normalizados
                for sintoma in sintomas:
                    sintoma_normalizado = self.normalizar_texto(sintoma)
                    sintomas_expandidos.add(sintoma_normalizado)
                    
        except Exception as e:
            # Em caso de erro, retornar sintomas originais normalizados
            print(f"Erro ao carregar sinônimos: {e}")
            for sintoma in sintomas:
                sintoma_normalizado = self.normalizar_texto(sintoma)
                sintomas_expandidos.add(sintoma_normalizado)
        
        return list(sintomas_expandidos)
    
    def buscar_por_semelhanca(self, sintoma: str, lista_indicacoes: List[str]) -> List[Tuple[str, float]]:
        """
        Busca medicamentos por semelhança semântica usando TF-IDF e similaridade de cosseno.
        
        Args:
            sintoma: Sintoma informado pelo usuário
            lista_indicacoes: Lista de indicações dos medicamentos
            
        Returns:
            Lista de tuplas (indicacao, score_similaridade) ordenada por relevância
        """
        if not sintoma or not lista_indicacoes:
            return []
        
        # Normalizar o sintoma
        sintoma_normalizado = self.normalizar_texto(sintoma)
        
        # Normalizar todas as indicações
        indicacoes_normalizadas = [self.normalizar_texto(ind) for ind in lista_indicacoes]
        
        # Filtrar indicações vazias
        indicacoes_validas = [(i, ind) for i, ind in enumerate(indicacoes_normalizadas) if ind.strip()]
        
        if not indicacoes_validas:
            return []
        
        # Preparar textos para TF-IDF (sintoma + indicações)
        textos = [sintoma_normalizado] + [ind for _, ind in indicacoes_validas]
        
        try:
            # Criar vetorizador TF-IDF
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words=None,  # Não usar stop words em português por enquanto
                ngram_range=(1, 2),  # Unigramas e bigramas
                min_df=1,  # Mínimo 1 documento
                max_df=1.0,  # Máximo 100% dos documentos
                token_pattern=r'\b\w+\b'  # Padrão para tokens
            )
            
            # Calcular matriz TF-IDF
            tfidf_matrix = vectorizer.fit_transform(textos)
            
            # Calcular similaridade de cosseno entre o sintoma e as indicações
            sintoma_vector = tfidf_matrix[0:1]  # Primeiro vetor é o sintoma
            indicacoes_vectors = tfidf_matrix[1:]  # Resto são as indicações
            
            # Calcular similaridades
            similaridades = cosine_similarity(sintoma_vector, indicacoes_vectors).flatten()
            
            # Criar lista de resultados com scores
            resultados = []
            for i, (indice_original, _) in enumerate(indicacoes_validas):
                score = similaridades[i]
                indicacao_original = lista_indicacoes[indice_original]
                resultados.append((indicacao_original, float(score)))
            
            # Ordenar por score (maior primeiro)
            resultados.sort(key=lambda x: x[1], reverse=True)
            
            return resultados
            
        except Exception as e:
            print(f"Erro na busca semântica: {e}")
            # Fallback para busca literal simples
            return self._busca_literal_fallback(sintoma_normalizado, lista_indicacoes)
    
    def _busca_literal_fallback(self, sintoma_normalizado: str, lista_indicacoes: List[str]) -> List[Tuple[str, float]]:
        """Fallback para busca literal quando TF-IDF falha"""
        resultados = []
        palavras_sintoma = sintoma_normalizado.split()
        
        for indicacao in lista_indicacoes:
            if not indicacao:
                continue
                
            indicacao_normalizada = self.normalizar_texto(indicacao)
            score = 0.0
            
            # Contar palavras em comum
            for palavra in palavras_sintoma:
                if palavra in indicacao_normalizada:
                    score += 1.0
            
            # Normalizar score pelo número de palavras do sintoma
            if palavras_sintoma:
                score = score / len(palavras_sintoma)
            
            if score > 0:
                resultados.append((indicacao, score))
        
        # Ordenar por score
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados
    
    def _carregar_palavras_chave(self) -> Dict[str, List[str]]:
        """Carrega palavras-chave para mapear sintomas com indicações"""
        return {
            'tosse': [
                'tosse', 'tossir', 'expectoração', 'expectorar', 'secreção', 'secreções',
                'bronquite', 'bronquial', 'respiratória', 'respiratório', 'pulmonar',
                'antitussígeno', 'expectorante', 'mucolítico', 'broncodilatador'
            ],
            'febre': [
                'febre', 'febril', 'hipertermia', 'temperatura', 'calafrio', 'calafrios',
                'antipirético', 'analgésico', 'anti-inflamatório', 'inflamação'
            ],
            'dor_cabeca': [
                'dor de cabeça', 'cefaleia', 'migrânea', 'enxaqueca', 'tensão',
                'analgésico', 'antimigranoso', 'vasoconstritor', 'vasodilatador'
            ],
            'diarreia': [
                'diarreia', 'diarréia', 'evacuação', 'evacuações', 'fezes', 'intestinal',
                'antidiarreico', 'antiespasmódico', 'probiótico', 'reidratação'
            ],
            'dor_garganta': [
                'dor de garganta', 'faringite', 'amigdalite', 'laringite', 'garganta',
                'analgésico tópico', 'anti-inflamatório', 'antisséptico', 'anestésico'
            ],
            'azia': [
                'azia', 'pirose', 'refluxo', 'gastrite', 'gástrico', 'gástrica',
                'antiácido', 'antagonista', 'inibidor', 'protetor gástrico'
            ],
            'constipacao': [
                'constipação', 'prisão de ventre', 'obstipação', 'intestinal',
                'laxante', 'purgativo', 'emoliente', 'estimulante'
            ],
            'hemorroidas': [
                'hemorroida', 'hemorroidas', 'anal', 'retal', 'prurido anal',
                'anti-inflamatório tópico', 'anestésico tópico', 'vasoconstritor'
            ],
            'dor_lombar': [
                'dor lombar', 'lombalgia', 'coluna', 'vertebral', 'muscular',
                'relaxante muscular', 'anti-inflamatório', 'analgésico'
            ],
            'espirro_congestao': [
                'espirro', 'congestão', 'nasal', 'rinite', 'alérgica', 'alérgico',
                'antihistamínico', 'descongestionante', 'corticosteroide'
            ]
        }
    
    def buscar_medicamentos_por_sintoma(self, sintoma: str, modulo: str) -> List[Medicamento]:
        """Busca medicamentos que tenham indicações relacionadas ao sintoma usando busca semântica"""
        medicamentos_relevantes = []
        
        try:
            # Buscar medicamentos do banco de dados
            medicamentos_ativos = Medicamento.query.filter_by(ativo=True).all()
            
            if not medicamentos_ativos:
                # Fallback para medicamentos simulados
                return self._get_medicamentos_simulados_por_modulo(modulo)
            
            # Preparar lista de indicações para busca semântica
            indicacoes_medicamentos = []
            medicamentos_com_indicacao = []
            
            for medicamento in medicamentos_ativos:
                if medicamento.indicacao:
                    # Combinar nome comercial, genérico e indicação para busca mais abrangente
                    texto_completo = f"{medicamento.nome_comercial} {medicamento.nome_generico or ''} {medicamento.indicacao}"
                    indicacoes_medicamentos.append(texto_completo)
                    medicamentos_com_indicacao.append(medicamento)
            
            if not indicacoes_medicamentos:
                # Se não há indicações, usar busca por palavras-chave
                sintomas_expandidos = self.expandir_sintomas([sintoma])
                return self._buscar_medicamentos_por_palavras_chave(medicamentos_ativos, modulo, sintomas_expandidos)
            
            # Expandir sintomas com sinônimos clínicos
            sintomas_expandidos = self.expandir_sintomas([sintoma])
            
            # Usar busca semântica com sintomas expandidos
            # Criar uma string combinada com todos os sintomas expandidos para busca
            sintomas_para_busca = " ".join(sintomas_expandidos)
            resultados_semanticos = self.buscar_por_semelhanca(sintomas_para_busca, indicacoes_medicamentos)
            
            # Aplicar limiar de similaridade (0.25 conforme requisito)
            limiar_similaridade = 0.25
            
            for indicacao_completa, score in resultados_semanticos:
                if score >= limiar_similaridade:
                    # Encontrar o medicamento correspondente
                    for i, med in enumerate(medicamentos_com_indicacao):
                        texto_med = f"{med.nome_comercial} {med.nome_generico or ''} {med.indicacao}"
                        if texto_med == indicacao_completa:
                            medicamentos_relevantes.append(med)
                            break
            
            # Se não encontrou medicamentos com busca semântica, tentar busca por palavras-chave
            if not medicamentos_relevantes:
                medicamentos_relevantes = self._buscar_medicamentos_por_palavras_chave(medicamentos_ativos, modulo, sintomas_expandidos)
            
            # Se ainda não encontrou, buscar por módulo geral
            if not medicamentos_relevantes:
                medicamentos_relevantes = self._buscar_medicamentos_gerais_por_modulo(modulo, medicamentos_ativos)
            
            # Ordenar por relevância (medicamentos com indicações mais específicas primeiro)
            medicamentos_relevantes.sort(key=lambda m: self._calcular_relevancia_medicamento(m, modulo))
            
        except Exception as e:
            print(f"Erro ao buscar medicamentos do banco: {e}")
            # Fallback para medicamentos simulados
            medicamentos_relevantes = self._get_medicamentos_simulados_por_modulo(modulo)
        
        return medicamentos_relevantes
    
    def _buscar_medicamentos_por_palavras_chave(self, medicamentos_ativos: List[Medicamento], modulo: str, sintomas_expandidos: List[str] = None) -> List[Medicamento]:
        """Busca medicamentos usando palavras-chave incluindo sinônimos"""
        medicamentos_relevantes = []
        palavras_chave = self.palavras_chave_sintomas.get(modulo, [])
        
        # Adicionar sinônimos às palavras-chave se fornecidos
        if sintomas_expandidos:
            palavras_chave.extend(sintomas_expandidos)
        
        for medicamento in medicamentos_ativos:
            if not medicamento.indicacao:
                continue
                
            indicacao_lower = medicamento.indicacao.lower()
            nome_lower = medicamento.nome_comercial.lower()
            generico_lower = (medicamento.nome_generico or "").lower()
            
            # Verificar se a indicação contém palavras-chave do sintoma
            for palavra in palavras_chave:
                if (palavra.lower() in indicacao_lower or 
                    palavra.lower() in nome_lower or 
                    palavra.lower() in generico_lower):
                    medicamentos_relevantes.append(medicamento)
                    break
        
        return medicamentos_relevantes
    
    def _calcular_relevancia_medicamento(self, medicamento: Medicamento, modulo: str) -> float:
        """Calcula a relevância de um medicamento para um módulo específico"""
        if not medicamento.indicacao:
            return 0.0
        
        indicacao_lower = medicamento.indicacao.lower()
        palavras_chave = self.palavras_chave_sintomas.get(modulo, [])
        
        relevancia = 0.0
        
        # Contar quantas palavras-chave estão presentes
        for palavra in palavras_chave:
            if palavra.lower() in indicacao_lower:
                relevancia += 1.0
        
        # Bonus para medicamentos com indicações mais específicas
        if 'específico' in indicacao_lower or 'indicado' in indicacao_lower:
            relevancia += 0.5
        
        # Penalidade para medicamentos genéricos demais
        if 'geral' in indicacao_lower or 'sintomático' in indicacao_lower:
            relevancia -= 0.3
        
        return relevancia
    
    def _get_medicamentos_simulados(self) -> List[Medicamento]:
        """Retorna medicamentos simulados quando o banco não está disponível"""
        class MedicamentoSimulado:
            def __init__(self, nome_comercial, nome_generico, indicacao, contraindicacao=None):
                self.nome_comercial = nome_comercial
                self.nome_generico = nome_generico
                self.indicacao = indicacao
                self.contraindicacao = contraindicacao
                self.ativo = True
        
        return [
            # Medicamentos para tosse
            MedicamentoSimulado("Vick 44", "Dextrometorfano", "Tosse seca e irritativa, antitussígeno"),
            MedicamentoSimulado("Mucosolvan", "Ambroxol", "Tosse produtiva, expectorante, mucolítico"),
            MedicamentoSimulado("Claritin", "Loratadina", "Tosse alérgica, antialérgico, antihistamínico"),
            MedicamentoSimulado("Bisolvon", "Bromexina", "Tosse com secreção, mucolítico, expectorante"),
            MedicamentoSimulado("Benalet", "Clobutinol", "Antitussígeno para tosse seca"),
            MedicamentoSimulado("Xarope de Guaifenesina", "Guaifenesina", "Expectorante para tosse"),
            
            # Medicamentos para febre
            MedicamentoSimulado("Tylenol", "Paracetamol", "Febre e dor, antipirético, analgésico"),
            MedicamentoSimulado("Advil", "Ibuprofeno", "Febre e inflamação, antipirético, anti-inflamatório"),
            MedicamentoSimulado("Novalgina", "Dipirona", "Febre e dor, antipirético, analgésico"),
            MedicamentoSimulado("Aspirina", "Ácido Acetilsalicílico", "Febre e dor, antipirético"),
            
            # Medicamentos para dor de cabeça
            MedicamentoSimulado("Dorflex", "Dipirona + Orfenadrina", "Dor de cabeça, analgésico, relaxante muscular"),
            MedicamentoSimulado("Voltaren", "Diclofenaco", "Dor de cabeça, anti-inflamatório"),
            
            # Medicamentos para diarreia
            MedicamentoSimulado("Imodium", "Loperamida", "Diarreia aguda, antidiarreico"),
            MedicamentoSimulado("Floratil", "Saccharomyces boulardii", "Diarreia, probiótico"),
            MedicamentoSimulado("Smecta", "Diosmectita", "Diarreia e cólicas"),
            
            # Medicamentos para dor de garganta
            MedicamentoSimulado("Strepsils", "Benzocaína + Amilmetacresol", "Dor de garganta, analgésico tópico"),
            MedicamentoSimulado("Cepacol", "Benzocaína + Cetylpiridinium", "Dor de garganta, anestésico tópico"),
            
            # Medicamentos para azia
            MedicamentoSimulado("Pepsamar", "Hidróxido de Alumínio + Magnésio", "Azia e queimação, antiácido"),
            MedicamentoSimulado("Omeprazol", "Omeprazol", "Inibidor de bomba de prótons"),
            
            # Medicamentos para constipação
            MedicamentoSimulado("Lactulona", "Lactulose", "Constipação, laxante"),
            MedicamentoSimulado("Bisacodil", "Bisacodil", "Laxante estimulante"),
            
            # Medicamentos para hemorroidas
            MedicamentoSimulado("Proctyl", "Hidrocortisona + Lidocaína", "Hemorroidas, anti-inflamatório tópico"),
            MedicamentoSimulado("Anusol", "Óxido de Zinco + Bálsamo", "Hemorroidas e fissuras"),
            
            # Medicamentos para dor lombar
            MedicamentoSimulado("Ciclobenzaprina", "Ciclobenzaprina", "Relaxante muscular"),
            MedicamentoSimulado("Tramadol", "Tramadol", "Analgésico para dor intensa"),
            
            # Medicamentos para congestão nasal
            MedicamentoSimulado("Sorine", "Cloridrato de Naftazolina", "Congestão nasal, descongestionante"),
            MedicamentoSimulado("Allegra", "Fexofenadina", "Congestão nasal alérgica, antihistamínico"),
            MedicamentoSimulado("Rinosoro", "Soro Fisiológico", "Lavagem nasal")
        ]
    
    def _get_medicamentos_simulados_por_modulo(self, modulo: str) -> List[Medicamento]:
        """Retorna medicamentos simulados filtrados por módulo"""
        todos_medicamentos = self._get_medicamentos_simulados()
        
        # Filtrar por módulo
        medicamentos_por_modulo = {
            'tosse': ['Vick 44', 'Mucosolvan', 'Claritin', 'Bisolvon', 'Benalet', 'Xarope de Guaifenesina'],
            'febre': ['Tylenol', 'Advil', 'Novalgina', 'Aspirina'],
            'dor_cabeca': ['Dorflex', 'Voltaren'],
            'diarreia': ['Imodium', 'Floratil', 'Smecta'],
            'dor_garganta': ['Strepsils', 'Cepacol'],
            'azia_ma_digestao': ['Pepsamar', 'Omeprazol'],
            'constipacao': ['Lactulona', 'Bisacodil'],
            'hemorroidas': ['Proctyl', 'Anusol'],
            'dor_lombar': ['Ciclobenzaprina', 'Tramadol'],
            'espirro_congestao_nasal': ['Sorine', 'Allegra', 'Rinosoro'],
            'infeccoes_fungicas': ['Canesten', 'Lamisil', 'Nizoral', 'Daktarin']
        }
        
        nomes_relevantes = medicamentos_por_modulo.get(modulo, [])
        return [m for m in todos_medicamentos if m.nome_comercial in nomes_relevantes]
    
    def _buscar_medicamentos_gerais_por_modulo(self, modulo: str, medicamentos_ativos: List[Medicamento] = None) -> List[Medicamento]:
        """Busca medicamentos gerais para o módulo quando não há correspondência específica"""
        medicamentos_gerais = []
        
        if medicamentos_ativos is None:
            try:
                medicamentos_ativos = Medicamento.query.filter_by(ativo=True).all()
            except Exception:
                return self._get_medicamentos_simulados_por_modulo(modulo)
        
        # Mapeamento de módulos para medicamentos gerais
        medicamentos_por_modulo = {
            'tosse': [
                'dextrometorfano', 'guaifenesina', 'ambroxol', 'loratadina', 
                'vick', 'mucosolvan', 'claritin', 'xarope', 'antitussígeno'
            ],
            'febre': [
                'paracetamol', 'ibuprofeno', 'dipirona', 'tylenol', 'advil',
                'antipirético', 'analgésico', 'febre'
            ],
            'dor_cabeca': [
                'paracetamol', 'ibuprofeno', 'naproxeno', 'tylenol', 'advil',
                'analgésico', 'dor de cabeça', 'cefaleia'
            ],
            'diarreia': [
                'loperamida', 'imodium', 'probiótico', 'lactobacillus', 'floratil',
                'antidiarreico', 'diarreia'
            ],
            'dor_garganta': [
                'benzocaína', 'lidocaína', 'strepsils', 'anestésico', 'garganta',
                'faringite', 'amigdalite'
            ],
            'azia_ma_digestao': [
                'hidróxido', 'antiácido', 'pepsamar', 'azia', 'refluxo',
                'gastrite', 'digestão'
            ],
            'constipacao': [
                'lactulose', 'laxante', 'lactulona', 'constipação', 'prisão de ventre'
            ],
            'hemorroidas': [
                'hidrocortisona', 'proctyl', 'hemorroida', 'anal', 'retal'
            ],
            'dor_lombar': [
                'ibuprofeno', 'paracetamol', 'dor lombar', 'lombalgia', 'muscular'
            ],
            'espirro_congestao_nasal': [
                'naftazolina', 'sorine', 'descongestionante', 'nasal', 'rinite'
            ],
            'infeccoes_fungicas': [
                'clotrimazol', 'terbinafina', 'cetoconazol', 'miconazol', 'antifungico', 
                'micose', 'fungo', 'candidíase', 'pé de atleta', 'intertrigo', 'unha'
            ]
        }
        
        palavras_busca = medicamentos_por_modulo.get(modulo, [])
        
        for medicamento in self.medicamentos_cache:
            if not medicamento.indicacao and not medicamento.nome_comercial:
                continue
                
            indicacao_lower = (medicamento.indicacao or "").lower()
            nome_lower = medicamento.nome_comercial.lower()
            generico_lower = (medicamento.nome_generico or "").lower()
            
            # Verificar se contém alguma palavra de busca
            for palavra in palavras_busca:
                if (palavra.lower() in indicacao_lower or 
                    palavra.lower() in nome_lower or 
                    palavra.lower() in generico_lower):
                    medicamentos_gerais.append(medicamento)
                    break
        
        return medicamentos_gerais[:5]  # Retornar até 5 medicamentos gerais
    
    def analisar_respostas_para_sintomas(self, respostas: List[Dict[str, str]], modulo: str) -> Dict[str, bool]:
        """Analisa as respostas para identificar sintomas específicos"""
        sintomas_identificados = {
            'tosse_seca': False,
            'tosse_produtiva': False,
            'febre': False,
            'dor_cabeca': False,
            'diarreia': False,
            'dor_garganta': False,
            'azia': False,
            'constipacao': False,
            'hemorroidas': False,
            'dor_lombar': False,
            'congestao_nasal': False,
            'inflamacao': False,
            'alergia': False,
            'gravidade_alta': False,
            'duracao_longa': False,
            'sinais_alerta': False
        }
        
        # Mapear respostas para sintomas baseado no módulo
        if modulo == 'tosse':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'tosse_2' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['tosse_produtiva'] = True
                elif 'tosse_3' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['tosse_seca'] = True
                elif 'tosse_4' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['alergia'] = True
                elif 'tosse_10' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['febre'] = True
                elif 'tosse_14' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_garganta'] = True
                elif 'tosse_6' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['gravidade_alta'] = True
                elif 'tosse_7' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['sinais_alerta'] = True
                elif 'tosse_1' in pergunta_id:
                    try:
                        duracao = int(resposta_valor)
                        if duracao > 7:
                            sintomas_identificados['duracao_longa'] = True
                    except ValueError:
                        pass
        
        elif modulo == 'febre':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'febre' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['febre'] = True
                elif 'dor_cabeca' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_cabeca'] = True
                elif 'dor_garganta' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_garganta'] = True
        
        elif modulo == 'dor_cabeca':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'dor_cabeca' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_cabeca'] = True
                elif 'febre' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['febre'] = True
        
        elif modulo == 'diarreia':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'diarreia' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['diarreia'] = True
                elif 'febre' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['febre'] = True
        
        elif modulo == 'dor_garganta':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'dor_garganta' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_garganta'] = True
                elif 'febre' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['febre'] = True
        
        elif modulo == 'azia_ma_digestao':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'azia' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['azia'] = True
        
        elif modulo == 'constipacao':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'constipacao' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['constipacao'] = True
        
        elif modulo == 'hemorroidas':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'hemorroida' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['hemorroidas'] = True
        
        elif modulo == 'dor_lombar':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'dor_lombar' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['dor_lombar'] = True
        
        elif modulo == 'espirro_congestao_nasal':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'congestao' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['congestao_nasal'] = True
                elif 'alergia' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['alergia'] = True
        
        elif modulo == 'infeccoes_fungicas':
            for resposta in respostas:
                pergunta_id = resposta['pergunta_id']
                resposta_valor = resposta['resposta'].lower()
                
                if 'coceira' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['coceira'] = True
                elif 'descamacao' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['descamacao'] = True
                elif 'vermelhidao' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['vermelhidao'] = True
                elif 'unha' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['unha_afetada'] = True
                elif 'pe' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['pe_afetado'] = True
                elif 'virilha' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['virilha_afetada'] = True
                elif 'duracao' in pergunta_id and resposta_valor.isdigit():
                    duracao = int(resposta_valor)
                    if duracao > 30:
                        sintomas_identificados['duracao_longa'] = True
                elif 'area' in pergunta_id and resposta_valor in ['sim', 'yes']:
                    sintomas_identificados['area_extensa'] = True
        
        return sintomas_identificados
    
    def gerar_recomendacoes(self, modulo: str, respostas: List[Dict[str, str]] = None, 
                           scoring_result = None, paciente_profile: Dict = None) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações farmacológicas baseadas no módulo, respostas e perfil do paciente"""
        
        # Analisar sintomas específicos das respostas
        sintomas_identificados = {}
        if respostas:
            sintomas_identificados = self.analisar_respostas_para_sintomas(respostas, modulo)
        
        # Buscar medicamentos do banco de dados
        medicamentos_relevantes = self.buscar_medicamentos_por_sintoma(modulo, modulo)
        
        # Se não encontrou medicamentos, tentar busca mais ampla
        if not medicamentos_relevantes:
            print(f"Nenhum medicamento encontrado para módulo {modulo}, tentando busca ampla...")
            medicamentos_relevantes = self._buscar_medicamentos_gerais_por_modulo(modulo)
        
        # Gerar recomendações baseadas nos sintomas identificados
        recomendacoes = self._gerar_recomendacoes_inteligentes(
            modulo, sintomas_identificados, medicamentos_relevantes, scoring_result
        )
        
        # Se não houver medicamentos específicos, usar recomendações fixas
        if not recomendacoes:
            recomendacoes = self._gerar_recomendacoes_fixas_por_modulo(modulo)
        
        # Aplicar modificadores baseados no perfil do paciente
        if paciente_profile:
            recomendacoes = self._aplicar_modificadores_paciente(recomendacoes, paciente_profile)
        
        # Aplicar filtros de contraindicações
        recomendacoes = self._aplicar_filtros_contraindicacoes(recomendacoes, paciente_profile)
        
        # Ordenar por prioridade e retornar até 12 medicamentos (6 iniciais + 6 adicionais)
        recomendacoes.sort(key=lambda x: x.prioridade)
        return recomendacoes[:12]
    
    def _gerar_recomendacoes_fixas_por_modulo(self, modulo: str) -> List[RecomendacaoFarmacologica]:
        """Gera 6 medicamentos fixos para cada módulo"""
        recomendacoes_fixas = {
            'tosse': [
                {
                    'medicamento': 'Vick 44',
                    'principio_ativo': 'Dextrometorfano',
                    'indicacao': 'Tosse seca e irritativa',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Não associar com expectorantes',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Mucosolvan',
                    'principio_ativo': 'Ambroxol',
                    'indicacao': 'Tosse produtiva',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Aumentar ingestão de líquidos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Claritin',
                    'principio_ativo': 'Loratadina',
                    'indicacao': 'Tosse alérgica',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Evitar exposição a alérgenos',
                    'prioridade': 3,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Bisolvon',
                    'principio_ativo': 'Bromexina',
                    'indicacao': 'Tosse com secreção',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com bastante água',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Xarope de Guaifenesina',
                    'principio_ativo': 'Guaifenesina',
                    'indicacao': 'Expectorante para tosse',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Aumentar ingestão de líquidos',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Benalet',
                    'principio_ativo': 'Clobutinol',
                    'indicacao': 'Antitussígeno para tosse seca',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Não usar por mais de 7 dias',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Xarope de Mel',
                    'principio_ativo': 'Mel de Abelha',
                    'indicacao': 'Tosse seca e irritativa',
                    'posologia': '1 colher de sopa a cada 4-6 horas',
                    'observacoes': 'Natural, seguro para crianças',
                    'prioridade': 7,
                    'categoria': 'natural'
                },
                {
                    'medicamento': 'Xarope de Guaco',
                    'principio_ativo': 'Mikania glomerata',
                    'indicacao': 'Expectorante natural',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Fitoterápico, sem contraindicações',
                    'prioridade': 8,
                    'categoria': 'fitoterapico'
                },
                {
                    'medicamento': 'Xarope de Eucalipto',
                    'principio_ativo': 'Eucalyptus globulus',
                    'indicacao': 'Tosse com secreção',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Ação expectorante e antisséptica',
                    'prioridade': 9,
                    'categoria': 'fitoterapico'
                },
                {
                    'medicamento': 'Xarope de Alcaçuz',
                    'principio_ativo': 'Glycyrrhiza glabra',
                    'indicacao': 'Tosse seca e irritativa',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Ação anti-inflamatória',
                    'prioridade': 10,
                    'categoria': 'fitoterapico'
                },
                {
                    'medicamento': 'Xarope de Propolis',
                    'principio_ativo': 'Própolis',
                    'indicacao': 'Tosse e irritação da garganta',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Ação antisséptica e cicatrizante',
                    'prioridade': 11,
                    'categoria': 'natural'
                },
                {
                    'medicamento': 'Xarope de Gengibre',
                    'principio_ativo': 'Zingiber officinale',
                    'indicacao': 'Tosse e inflamação',
                    'posologia': '1 colher de sopa a cada 6 horas',
                    'observacoes': 'Ação anti-inflamatória e expectorante',
                    'prioridade': 12,
                    'categoria': 'fitoterapico'
                }
            ],
            'febre': [
                {
                    'medicamento': 'Tylenol',
                    'principio_ativo': 'Paracetamol',
                    'indicacao': 'Febre e dor',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Monitorar temperatura',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Febre e inflamação',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Novalgina',
                    'principio_ativo': 'Dipirona',
                    'indicacao': 'Febre e dor',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Pode causar sonolência',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Aspirina',
                    'principio_ativo': 'Ácido Acetilsalicílico',
                    'indicacao': 'Febre e dor',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Evitar em crianças e gestantes',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Dorflex',
                    'principio_ativo': 'Dipirona + Orfenadrina',
                    'indicacao': 'Febre com dor muscular',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Relaxante muscular',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Cimegripe',
                    'principio_ativo': 'Paracetamol + Fenilefrina',
                    'indicacao': 'Febre com congestão nasal',
                    'posologia': '1 comprimido a cada 6 horas',
                    'observacoes': 'Descongestionante nasal',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                }
            ],
            'dor_cabeca': [
                {
                    'medicamento': 'Tylenol',
                    'principio_ativo': 'Paracetamol',
                    'indicacao': 'Dor de cabeça leve a moderada',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Repouso em ambiente escuro',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Dor de cabeça com inflamação',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Aspirina',
                    'principio_ativo': 'Ácido Acetilsalicílico',
                    'indicacao': 'Dor de cabeça tensional',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Evitar em crianças',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Dorflex',
                    'principio_ativo': 'Dipirona + Orfenadrina',
                    'indicacao': 'Dor de cabeça com tensão muscular',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Relaxante muscular',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Cefalium',
                    'principio_ativo': 'Paracetamol + Cafeína',
                    'indicacao': 'Dor de cabeça com cansaço',
                    'posologia': '1 comprimido a cada 6 horas',
                    'observacoes': 'Cafeína pode causar insônia',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Neosaldina',
                    'principio_ativo': 'Dipirona + Cafeína + Isometepteno',
                    'indicacao': 'Enxaqueca e dor de cabeça',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Vasoconstritor',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                }
            ],
            'diarreia': [
                {
                    'medicamento': 'Imodium',
                    'principio_ativo': 'Loperamida',
                    'indicacao': 'Diarreia aguda',
                    'posologia': '1 comprimido após cada evacuação líquida',
                    'observacoes': 'Hidratação adequada é essencial',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Floratil',
                    'principio_ativo': 'Saccharomyces boulardii',
                    'indicacao': 'Diarreia - adjuvante',
                    'posologia': '1 cápsula ao dia',
                    'observacoes': 'Tomar longe das refeições',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Racecadotril',
                    'principio_ativo': 'Racecadotril',
                    'indicacao': 'Antidiarreico',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Reduz secreção intestinal',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Enterogermina',
                    'principio_ativo': 'Bacillus clausii',
                    'indicacao': 'Probiótico para diarreia',
                    'posologia': '1 frasco ao dia',
                    'observacoes': 'Restaura flora intestinal',
                    'prioridade': 4,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Smecta',
                    'principio_ativo': 'Diosmectita',
                    'indicacao': 'Diarreia e cólicas',
                    'posologia': '1 sachê a cada 8 horas',
                    'observacoes': 'Protege mucosa intestinal',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Carbomix',
                    'principio_ativo': 'Carvão Ativado',
                    'indicacao': 'Diarreia por intoxicação',
                    'posologia': '2 comprimidos a cada 6 horas',
                    'observacoes': 'Adsorve toxinas',
                    'prioridade': 6,
                    'categoria': 'terapeutico'
                }
            ],
            'dor_garganta': [
                {
                    'medicamento': 'Strepsils',
                    'principio_ativo': 'Benzocaína + Amilmetacresol',
                    'indicacao': 'Dor de garganta',
                    'posologia': '1 pastilha a cada 2-3 horas',
                    'observacoes': 'Fazer gargarejos',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Neo-Saldan',
                    'principio_ativo': 'Benzocaína + Ciprofloxacino',
                    'indicacao': 'Dor de garganta com infecção',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Cepacol',
                    'principio_ativo': 'Benzocaína + Cetylpiridinium',
                    'indicacao': 'Dor de garganta e mau hálito',
                    'posologia': '1 pastilha a cada 2-3 horas',
                    'observacoes': 'Antisséptico bucal',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Benzetacil',
                    'principio_ativo': 'Benzilpenicilina',
                    'indicacao': 'Infecção de garganta',
                    'posologia': '1 injeção intramuscular',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 4,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Amoxicilina',
                    'principio_ativo': 'Amoxicilina',
                    'indicacao': 'Infecção bacteriana de garganta',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 5,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Ibuprofeno',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Anti-inflamatório para garganta',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                }
            ],
            'azia_ma_digestao': [
                {
                    'medicamento': 'Pepsamar',
                    'principio_ativo': 'Hidróxido de Alumínio + Magnésio',
                    'indicacao': 'Azia e queimação',
                    'posologia': '1 comprimido após as refeições',
                    'observacoes': 'Evitar refeições grandes',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Digiazia',
                    'principio_ativo': 'Ácido Cítrico + Bicarbonato',
                    'indicacao': 'Azia e má digestão',
                    'posologia': '1 comprimido após as refeições',
                    'observacoes': 'Efervescente',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Omeprazol',
                    'principio_ativo': 'Omeprazol',
                    'indicacao': 'Inibidor de bomba de prótons',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Tomar em jejum',
                    'prioridade': 3,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Ranitidina',
                    'principio_ativo': 'Ranitidina',
                    'indicacao': 'Antagonista H2',
                    'posologia': '1 comprimido a cada 12 horas',
                    'observacoes': 'Reduz produção de ácido',
                    'prioridade': 4,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Simeticona',
                    'principio_ativo': 'Simeticona',
                    'indicacao': 'Gases e flatulência',
                    'posologia': '1 comprimido após as refeições',
                    'observacoes': 'Antiflatulento',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Domperidona',
                    'principio_ativo': 'Domperidona',
                    'indicacao': 'Náuseas e vômitos',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Procinético',
                    'prioridade': 6,
                    'categoria': 'terapeutico'
                }
            ],
            'constipacao': [
                {
                    'medicamento': 'Lactulona',
                    'principio_ativo': 'Lactulose',
                    'indicacao': 'Constipação',
                    'posologia': '1 colher de sopa ao dia',
                    'observacoes': 'Aumentar ingestão de fibras e água',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Amitiza',
                    'principio_ativo': 'Lubiprostona',
                    'indicacao': 'Constipação crônica',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Bisacodil',
                    'principio_ativo': 'Bisacodil',
                    'indicacao': 'Laxante estimulante',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Tomar à noite',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Plantago',
                    'principio_ativo': 'Psyllium',
                    'indicacao': 'Laxante de volume',
                    'posologia': '1 colher de sopa ao dia',
                    'observacoes': 'Tomar com muita água',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Dulcolax',
                    'principio_ativo': 'Bisacodil',
                    'indicacao': 'Laxante para constipação',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Pode causar cólicas',
                    'prioridade': 5,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Enema',
                    'principio_ativo': 'Fosfato de Sódio',
                    'indicacao': 'Constipação severa',
                    'posologia': '1 aplicação',
                    'observacoes': 'Uso ocasional',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                }
            ],
            'hemorroidas': [
                {
                    'medicamento': 'Proctyl',
                    'principio_ativo': 'Hidrocortisona + Lidocaína',
                    'indicacao': 'Hemorroidas',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Aplicar após higiene local',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Pomada de Hamamélis',
                    'principio_ativo': 'Hamamélis',
                    'indicacao': 'Hemorroidas externas',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Fitoterápico',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Anusol',
                    'principio_ativo': 'Óxido de Zinco + Bálsamo',
                    'indicacao': 'Hemorroidas e fissuras',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Protege a pele',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Venalot',
                    'principio_ativo': 'Diosmina + Hesperidina',
                    'indicacao': 'Circulação venosa',
                    'posologia': '1 comprimido a cada 12 horas',
                    'observacoes': 'Melhora circulação',
                    'prioridade': 4,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Daflon',
                    'principio_ativo': 'Diosmina',
                    'indicacao': 'Insuficiência venosa',
                    'posologia': '1 comprimido a cada 12 horas',
                    'observacoes': 'Flebotônico',
                    'prioridade': 5,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Ibuprofeno',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Anti-inflamatório para dor',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 6,
                    'categoria': 'sintomatico'
                }
            ],
            'dor_lombar': [
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Dor lombar',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Repouso e calor local',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Tylenol',
                    'principio_ativo': 'Paracetamol',
                    'indicacao': 'Dor lombar leve',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Analgésico simples',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Dorflex',
                    'principio_ativo': 'Dipirona + Orfenadrina',
                    'indicacao': 'Dor lombar com espasmo',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Relaxante muscular',
                    'prioridade': 3,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Voltaren',
                    'principio_ativo': 'Diclofenaco',
                    'indicacao': 'Anti-inflamatório para dor',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Ciclobenzaprina',
                    'principio_ativo': 'Ciclobenzaprina',
                    'indicacao': 'Relaxante muscular',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 5,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Tramadol',
                    'principio_ativo': 'Tramadol',
                    'indicacao': 'Analgésico para dor intensa',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 6,
                    'categoria': 'terapeutico'
                }
            ],
            'espirro_congestao_nasal': [
                {
                    'medicamento': 'Sorine',
                    'principio_ativo': 'Cloridrato de Naftazolina',
                    'indicacao': 'Congestão nasal',
                    'posologia': '2-3 jatos em cada narina a cada 12 horas',
                    'observacoes': 'Não usar por mais de 3 dias',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Allegra',
                    'principio_ativo': 'Fexofenadina',
                    'indicacao': 'Congestão nasal alérgica',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Pode causar sonolência',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Claritin',
                    'principio_ativo': 'Loratadina',
                    'indicacao': 'Antihistamínico para alergia',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Não causa sonolência',
                    'prioridade': 3,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Rinosoro',
                    'principio_ativo': 'Soro Fisiológico',
                    'indicacao': 'Lavagem nasal',
                    'posologia': 'Aplicar várias vezes ao dia',
                    'observacoes': 'Higiene nasal',
                    'prioridade': 4,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Nasonex',
                    'principio_ativo': 'Mometasona',
                    'indicacao': 'Spray nasal anti-inflamatório',
                    'posologia': '2 jatos em cada narina ao dia',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 5,
                    'categoria': 'terapeutico'
                },
                {
                    'medicamento': 'Benadryl',
                    'principio_ativo': 'Difenidramina',
                    'indicacao': 'Antihistamínico sedativo',
                    'posologia': '1 comprimido a cada 6 horas',
                    'observacoes': 'Causa sonolência',
                    'prioridade': 6,
                    'categoria': 'terapeutico'
                }
            ],
            'infeccoes_fungicas': [
                {
                    'medicamento': 'Canesten',
                    'principio_ativo': 'Clotrimazol',
                    'indicacao': 'Micoses superficiais (pé de atleta, candidíase)',
                    'posologia': 'Aplicar 2-3 vezes ao dia por 2-4 semanas',
                    'observacoes': 'Manter área limpa e seca',
                    'prioridade': 1,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Lamisil',
                    'principio_ativo': 'Terbinafina',
                    'indicacao': 'Micoses de unhas e pele',
                    'posologia': 'Aplicar 1-2 vezes ao dia por 1-2 semanas',
                    'observacoes': 'Não usar em gestantes',
                    'prioridade': 2,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Nizoral',
                    'principio_ativo': 'Cetoconazol',
                    'indicacao': 'Micoses superficiais e candidíase',
                    'posologia': 'Aplicar 1-2 vezes ao dia por 2-4 semanas',
                    'observacoes': 'Evitar exposição solar',
                    'prioridade': 3,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Daktarin',
                    'principio_ativo': 'Miconazol',
                    'indicacao': 'Micoses superficiais e intertrigo',
                    'posologia': 'Aplicar 2 vezes ao dia por 2-4 semanas',
                    'observacoes': 'Adequado para áreas úmidas',
                    'prioridade': 4,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Fungicort',
                    'principio_ativo': 'Clotrimazol + Hidrocortisona',
                    'indicacao': 'Micoses com inflamação',
                    'posologia': 'Aplicar 2-3 vezes ao dia por 1-2 semanas',
                    'observacoes': 'Não usar por mais de 2 semanas',
                    'prioridade': 5,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Pomada de Enxofre',
                    'principio_ativo': 'Enxofre',
                    'indicacao': 'Micoses superficiais leves',
                    'posologia': 'Aplicar 1-2 vezes ao dia por 2-4 semanas',
                    'observacoes': 'Produto natural, menos agressivo',
                    'prioridade': 6,
                    'categoria': 'natural'
                },
                {
                    'medicamento': 'Creme de Aloe Vera',
                    'principio_ativo': 'Aloe Vera',
                    'indicacao': 'Alívio de sintomas de micoses',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Ação calmante e hidratante',
                    'prioridade': 7,
                    'categoria': 'natural'
                },
                {
                    'medicamento': 'Óleo de Melaleuca',
                    'principio_ativo': 'Melaleuca alternifolia',
                    'indicacao': 'Micoses superficiais',
                    'posologia': 'Aplicar 2-3 gotas 2 vezes ao dia',
                    'observacoes': 'Diluir em óleo carreador',
                    'prioridade': 8,
                    'categoria': 'fitoterapico'
                },
                {
                    'medicamento': 'Pomada de Calêndula',
                    'principio_ativo': 'Calendula officinalis',
                    'indicacao': 'Micoses com irritação',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Ação anti-inflamatória',
                    'prioridade': 9,
                    'categoria': 'fitoterapico'
                },
                {
                    'medicamento': 'Creme de Própolis',
                    'principio_ativo': 'Própolis',
                    'indicacao': 'Micoses superficiais',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Ação antisséptica natural',
                    'prioridade': 10,
                    'categoria': 'natural'
                },
                {
                    'medicamento': 'Pomada de Iodo',
                    'principio_ativo': 'Iodo',
                    'indicacao': 'Micoses superficiais',
                    'posologia': 'Aplicar 1-2 vezes ao dia',
                    'observacoes': 'Ação antisséptica e antifúngica',
                    'prioridade': 11,
                    'categoria': 'antifungico'
                },
                {
                    'medicamento': 'Creme de Bicarbonato',
                    'principio_ativo': 'Bicarbonato de Sódio',
                    'indicacao': 'Alívio de sintomas de micoses',
                    'posologia': 'Aplicar pasta 2 vezes ao dia',
                    'observacoes': 'Misturar com água até formar pasta',
                    'prioridade': 12,
                    'categoria': 'natural'
                }
            ]
        }
        
        recomendacoes_modulo = recomendacoes_fixas.get(modulo, [])
        recomendacoes = []
        
        for rec_data in recomendacoes_modulo:
            recomendacoes.append(RecomendacaoFarmacologica(
                medicamento=rec_data['medicamento'],
                principio_ativo=rec_data['principio_ativo'],
                indicacao=rec_data['indicacao'],
                posologia=rec_data['posologia'],
                contraindicacoes="Verificar bula",
                observacoes=rec_data['observacoes'],
                prioridade=rec_data['prioridade'],
                categoria=rec_data['categoria']
            ))
        
        return recomendacoes
    
    def _gerar_recomendacoes_inteligentes(self, modulo: str, sintomas: Dict[str, bool], 
                                         medicamentos: List[Medicamento], scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações inteligentes baseadas nos sintomas identificados"""
        recomendacoes = []
        
        # Mapear sintomas para medicamentos específicos
        if modulo == 'tosse':
            recomendacoes = self._recomendar_para_tosse(sintomas, medicamentos, scoring_result)
        elif modulo == 'febre':
            recomendacoes = self._recomendar_para_febre(sintomas, medicamentos, scoring_result)
        elif modulo == 'dor_cabeca':
            recomendacoes = self._recomendar_para_dor_cabeca(sintomas, medicamentos, scoring_result)
        elif modulo == 'diarreia':
            recomendacoes = self._recomendar_para_diarreia(sintomas, medicamentos, scoring_result)
        elif modulo == 'dor_garganta':
            recomendacoes = self._recomendar_para_dor_garganta(sintomas, medicamentos, scoring_result)
        elif modulo == 'azia_ma_digestao':
            recomendacoes = self._recomendar_para_azia(sintomas, medicamentos, scoring_result)
        elif modulo == 'constipacao':
            recomendacoes = self._recomendar_para_constipacao(sintomas, medicamentos, scoring_result)
        elif modulo == 'hemorroidas':
            recomendacoes = self._recomendar_para_hemorroidas(sintomas, medicamentos, scoring_result)
        elif modulo == 'dor_lombar':
            recomendacoes = self._recomendar_para_dor_lombar(sintomas, medicamentos, scoring_result)
        elif modulo == 'espirro_congestao_nasal':
            recomendacoes = self._recomendar_para_congestao_nasal(sintomas, medicamentos, scoring_result)
        elif modulo == 'infeccoes_fungicas':
            recomendacoes = self._recomendar_para_infeccoes_fungicas(sintomas, medicamentos, scoring_result)
        
        return recomendacoes
    
    def _aplicar_filtros_contraindicacoes(self, recomendacoes: List[RecomendacaoFarmacologica], 
                                        paciente_profile: Dict) -> List[RecomendacaoFarmacologica]:
        """Aplica filtros de contraindicações baseados no perfil do paciente"""
        if not paciente_profile:
            return recomendacoes
        
        recomendacoes_filtradas = []
        
        for rec in recomendacoes:
            # Verificar contraindicações para gestantes/lactantes
            if paciente_profile.get('is_pregnant_or_lactating', False):
                if any(termo in rec.medicamento.lower() for termo in ['aspirina', 'ibuprofeno', 'naproxeno']):
                    rec.observacoes += " | Cautela em gestantes - consultar médico"
                    rec.prioridade = min(5, rec.prioridade + 1)
            
            # Verificar contraindicações para idosos
            if paciente_profile.get('is_frail_elderly', False):
                if any(termo in rec.medicamento.lower() for termo in ['dipirona', 'tramadol']):
                    rec.observacoes += " | Reduzir dose em idosos"
                    rec.prioridade = min(5, rec.prioridade + 1)
            
            # Verificar contraindicações para crianças
            if paciente_profile.get('age_years', 0) < 12:
                if any(termo in rec.medicamento.lower() for termo in ['aspirina', 'tramadol']):
                    rec.observacoes += " | Contraindicado em crianças"
                    rec.prioridade = min(5, rec.prioridade + 2)
            
            recomendacoes_filtradas.append(rec)
        
        return recomendacoes_filtradas
    
    def _gerar_recomendacoes_gerais_por_modulo(self, modulo: str, medicamentos: List[Medicamento]) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações gerais quando não há correspondência específica"""
        recomendacoes = []
        
        # Mapeamento de recomendações gerais por módulo
        recomendacoes_gerais = {
            'tosse': [
                {
                    'medicamento': 'Vick 44',
                    'principio_ativo': 'Dextrometorfano',
                    'indicacao': 'Tosse seca e irritativa',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Não associar com expectorantes',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Mucosolvan',
                    'principio_ativo': 'Ambroxol',
                    'indicacao': 'Tosse produtiva',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Aumentar ingestão de líquidos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Claritin',
                    'principio_ativo': 'Loratadina',
                    'indicacao': 'Tosse alérgica',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Evitar exposição a alérgenos',
                    'prioridade': 3,
                    'categoria': 'terapeutico'
                }
            ],
            'febre': [
                {
                    'medicamento': 'Tylenol',
                    'principio_ativo': 'Paracetamol',
                    'indicacao': 'Febre e dor',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Monitorar temperatura',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Febre e inflamação',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                }
            ],
            'dor_cabeca': [
                {
                    'medicamento': 'Tylenol',
                    'principio_ativo': 'Paracetamol',
                    'indicacao': 'Dor de cabeça leve a moderada',
                    'posologia': '1 comprimido a cada 6-8 horas',
                    'observacoes': 'Repouso em ambiente escuro',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Dor de cabeça com inflamação',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Tomar com alimentos',
                    'prioridade': 2,
                    'categoria': 'sintomatico'
                }
            ],
            'diarreia': [
                {
                    'medicamento': 'Imodium',
                    'principio_ativo': 'Loperamida',
                    'indicacao': 'Diarreia aguda',
                    'posologia': '1 comprimido após cada evacuação líquida',
                    'observacoes': 'Hidratação adequada é essencial',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Floratil',
                    'principio_ativo': 'Saccharomyces boulardii',
                    'indicacao': 'Diarreia - adjuvante',
                    'posologia': '1 cápsula ao dia',
                    'observacoes': 'Tomar longe das refeições',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                }
            ],
            'dor_garganta': [
                {
                    'medicamento': 'Strepsils',
                    'principio_ativo': 'Benzocaína + Amilmetacresol',
                    'indicacao': 'Dor de garganta',
                    'posologia': '1 pastilha a cada 2-3 horas',
                    'observacoes': 'Fazer gargarejos',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Neo-Saldan',
                    'principio_ativo': 'Benzocaína + Cloridrato de Ciprofloxacino',
                    'indicacao': 'Dor de garganta com infecção',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Só com prescrição médica',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                }
            ],
            'azia_ma_digestao': [
                {
                    'medicamento': 'Pepsamar',
                    'principio_ativo': 'Hidróxido de Alumínio + Magnésio',
                    'indicacao': 'Azia e queimação',
                    'posologia': '1 comprimido após as refeições',
                    'observacoes': 'Evitar refeições grandes',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                }
            ],
            'constipacao': [
                {
                    'medicamento': 'Lactulona',
                    'principio_ativo': 'Lactulose',
                    'indicacao': 'Constipação',
                    'posologia': '1 colher de sopa ao dia',
                    'observacoes': 'Aumentar ingestão de fibras e água',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                }
            ],
            'hemorroidas': [
                {
                    'medicamento': 'Proctyl',
                    'principio_ativo': 'Hidrocortisona + Lidocaína',
                    'indicacao': 'Hemorroidas',
                    'posologia': 'Aplicar 2-3 vezes ao dia',
                    'observacoes': 'Aplicar após higiene local',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                }
            ],
            'dor_lombar': [
                {
                    'medicamento': 'Advil',
                    'principio_ativo': 'Ibuprofeno',
                    'indicacao': 'Dor lombar',
                    'posologia': '1 comprimido a cada 8 horas',
                    'observacoes': 'Repouso e calor local',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                }
            ],
            'espirro_congestao_nasal': [
                {
                    'medicamento': 'Sorine',
                    'principio_ativo': 'Cloridrato de Naftazolina',
                    'indicacao': 'Congestão nasal',
                    'posologia': '2-3 jatos em cada narina a cada 12 horas',
                    'observacoes': 'Não usar por mais de 3 dias',
                    'prioridade': 1,
                    'categoria': 'sintomatico'
                },
                {
                    'medicamento': 'Allegra',
                    'principio_ativo': 'Fexofenadina',
                    'indicacao': 'Congestão nasal alérgica',
                    'posologia': '1 comprimido ao dia',
                    'observacoes': 'Pode causar sonolência',
                    'prioridade': 2,
                    'categoria': 'terapeutico'
                }
            ]
        }
        
        # Buscar medicamentos do banco que correspondam às recomendações gerais
        recomendacoes_modulo = recomendacoes_gerais.get(modulo, [])
        
        for rec_geral in recomendacoes_modulo:
            # Tentar encontrar o medicamento no banco
            medicamento_encontrado = None
            for med in medicamentos:
                if (rec_geral['medicamento'].lower() in med.nome_comercial.lower() or
                    rec_geral['principio_ativo'].lower() in (med.nome_generico or "").lower()):
                    medicamento_encontrado = med
                    break
            
            if medicamento_encontrado:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=medicamento_encontrado.nome_comercial,
                    principio_ativo=medicamento_encontrado.nome_generico or rec_geral['principio_ativo'],
                    indicacao=rec_geral['indicacao'],
                    posologia=rec_geral['posologia'],
                    contraindicacoes=medicamento_encontrado.contraindicacao or "Verificar bula",
                    observacoes=rec_geral['observacoes'],
                    prioridade=rec_geral['prioridade'],
                    categoria=rec_geral['categoria']
                ))
            else:
                # Usar recomendação geral mesmo sem encontrar no banco
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=rec_geral['medicamento'],
                    principio_ativo=rec_geral['principio_ativo'],
                    indicacao=rec_geral['indicacao'],
                    posologia=rec_geral['posologia'],
                    contraindicacoes="Verificar bula",
                    observacoes=rec_geral['observacoes'],
                    prioridade=rec_geral['prioridade'],
                    categoria=rec_geral['categoria']
                ))
        
        return recomendacoes
    
    def _recomendar_para_tosse(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                              scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para tosse"""
        recomendacoes = []
        
        # Buscar medicamentos específicos para tosse
        medicamentos_tosse = [m for m in medicamentos if self._medicamento_para_tosse(m)]
        
        # Ajustar prioridade baseada na gravidade
        prioridade_base = 1
        if sintomas.get('gravidade_alta', False):
            prioridade_base = 1
        elif sintomas.get('duracao_longa', False):
            prioridade_base = 2
        else:
            prioridade_base = 3
        
        if sintomas['tosse_seca']:
            # Antitussígenos
            antitussigenos = [m for m in medicamentos_tosse if self._e_antitussigeno(m)]
            for med in antitussigenos[:2]:  # Máximo 2 antitussígenos
                observacoes = "Não associar com expectorantes"
                if sintomas.get('duracao_longa', False):
                    observacoes += " | Se persistir >7 dias, consultar médico"
                
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Tosse seca",
                    posologia=self._gerar_posologia(med, 'antitussigeno'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes=observacoes,
                    prioridade=prioridade_base,
                    categoria='sintomatico'
                ))
        
        if sintomas['tosse_produtiva']:
            # Expectorantes e mucolíticos
            expectorantes = [m for m in medicamentos_tosse if self._e_expectorante(m)]
            for med in expectorantes[:2]:
                observacoes = "Aumentar ingestão de líquidos"
                if sintomas.get('gravidade_alta', False):
                    observacoes += " | Monitorar evolução"
                
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Tosse produtiva",
                    posologia=self._gerar_posologia(med, 'expectorante'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes=observacoes,
                    prioridade=prioridade_base,
                    categoria='sintomatico'
                ))
        
        if sintomas['alergia']:
            # Antialérgicos
            antialergicos = [m for m in medicamentos_tosse if self._e_antialergico(m)]
            for med in antialergicos[:1]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Tosse alérgica",
                    posologia=self._gerar_posologia(med, 'antialergico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Evitar exposição a alérgenos",
                    prioridade=prioridade_base + 1,
                    categoria='terapeutico'
                ))
        
        # Se há sinais de alerta, adicionar observação especial
        if sintomas.get('sinais_alerta', False):
            for rec in recomendacoes:
                rec.observacoes += " | ATENÇÃO: Sinais de alerta detectados - monitorar evolução"
                rec.prioridade = 1
        
        return recomendacoes
    
    def _recomendar_para_febre(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                               scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para febre"""
        recomendacoes = []
        
        if sintomas['febre']:
            # Antipiréticos
            antipireticos = [m for m in medicamentos if self._e_antipiretico(m)]
            for med in antipireticos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Febre",
                    posologia=self._gerar_posologia(med, 'antipiretico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Monitorar temperatura",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_dor_cabeca(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                   scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para dor de cabeça"""
        recomendacoes = []
        
        if sintomas['dor_cabeca']:
            # Analgésicos
            analgesicos = [m for m in medicamentos if self._e_analgesico(m)]
            for med in analgesicos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Dor de cabeça",
                    posologia=self._gerar_posologia(med, 'analgesico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Repouso em ambiente escuro",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_diarreia(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                 scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para diarreia"""
        recomendacoes = []
        
        if sintomas['diarreia']:
            # Antidiarreicos
            antidiarreicos = [m for m in medicamentos if self._e_antidiarreico(m)]
            for med in antidiarreicos[:1]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Diarreia",
                    posologia=self._gerar_posologia(med, 'antidiarreico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Hidratação adequada é essencial",
                    prioridade=1,
                    categoria='sintomatico'
                ))
            
            # Probióticos
            probioticos = [m for m in medicamentos if self._e_probiotico(m)]
            for med in probioticos[:1]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Diarreia - adjuvante",
                    posologia=self._gerar_posologia(med, 'probiotico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Tomar longe das refeições",
                    prioridade=3,
                    categoria='terapeutico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_dor_garganta(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                     scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para dor de garganta"""
        recomendacoes = []
        
        if sintomas['dor_garganta']:
            # Analgésicos tópicos
            analgesicos_topicos = [m for m in medicamentos if self._e_analgesico_topico(m)]
            for med in analgesicos_topicos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Dor de garganta",
                    posologia=self._gerar_posologia(med, 'analgesico_topico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Fazer gargarejos",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_azia(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                             scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para azia"""
        recomendacoes = []
        
        if sintomas['azia']:
            # Antiácidos
            antiacidos = [m for m in medicamentos if self._e_antiacido(m)]
            for med in antiacidos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Azia",
                    posologia=self._gerar_posologia(med, 'antiacido'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Tomar após as refeições",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_constipacao(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                    scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para constipação"""
        recomendacoes = []
        
        if sintomas['constipacao']:
            # Laxantes
            laxantes = [m for m in medicamentos if self._e_laxante(m)]
            for med in laxantes[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Constipação",
                    posologia=self._gerar_posologia(med, 'laxante'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Aumentar ingestão de fibras e água",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_hemorroidas(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                    scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para hemorroidas"""
        recomendacoes = []
        
        if sintomas['hemorroidas']:
            # Medicamentos tópicos
            topicos = [m for m in medicamentos if self._e_topico_hemorroidas(m)]
            for med in topicos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Hemorroidas",
                    posologia=self._gerar_posologia(med, 'topico_hemorroidas'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Aplicar após higiene local",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_dor_lombar(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                   scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para dor lombar"""
        recomendacoes = []
        
        if sintomas['dor_lombar']:
            # Analgésicos e anti-inflamatórios
            analgesicos = [m for m in medicamentos if self._e_analgesico(m)]
            for med in analgesicos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Dor lombar",
                    posologia=self._gerar_posologia(med, 'analgesico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Repouso e calor local",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_congestao_nasal(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                        scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para congestão nasal"""
        recomendacoes = []
        
        if sintomas['congestao_nasal']:
            # Descongestionantes
            descongestionantes = [m for m in medicamentos if self._e_descongestionante(m)]
            for med in descongestionantes[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Congestão nasal",
                    posologia=self._gerar_posologia(med, 'descongestionante'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Não usar por mais de 3 dias",
                    prioridade=1,
                    categoria='sintomatico'
                ))
        
        if sintomas['alergia']:
            # Antihistamínicos
            antihistaminicos = [m for m in medicamentos if self._e_antihistaminico(m)]
            for med in antihistaminicos[:1]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Congestão nasal alérgica",
                    posologia=self._gerar_posologia(med, 'antihistaminico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Pode causar sonolência",
                    prioridade=2,
                    categoria='terapeutico'
                ))
        
        return recomendacoes
    
    def _recomendar_para_infeccoes_fungicas(self, sintomas: Dict[str, bool], medicamentos: List[Medicamento], 
                                           scoring_result) -> List[RecomendacaoFarmacologica]:
        """Gera recomendações específicas para infecções fúngicas"""
        recomendacoes = []
        
        # Antifúngicos tópicos para casos leves
        if sintomas.get('coceira', False) or sintomas.get('descamacao', False):
            antifungicos = [m for m in medicamentos if self._e_antifungico(m)]
            for med in antifungicos[:3]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Micose superficial",
                    posologia=self._gerar_posologia(med, 'antifungico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Manter área limpa e seca",
                    prioridade=1,
                    categoria='antifungico'
                ))
        
        # Casos mais graves ou duração longa
        if sintomas.get('duracao_longa', False) or sintomas.get('area_extensa', False):
            antifungicos_sistemicos = [m for m in medicamentos if self._e_antifungico_sistemico(m)]
            for med in antifungicos_sistemicos[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Micose extensa ou duradoura",
                    posologia=self._gerar_posologia(med, 'antifungico_sistemico'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Consulte médico se não melhorar em 2 semanas",
                    prioridade=1,
                    categoria='antifungico'
                ))
        
        # Unhas afetadas
        if sintomas.get('unha_afetada', False):
            antifungicos_unha = [m for m in medicamentos if self._e_antifungico_unha(m)]
            for med in antifungicos_unha[:2]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Micose de unha",
                    posologia=self._gerar_posologia(med, 'antifungico_unha'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Tratamento pode durar 3-6 meses",
                    prioridade=2,
                    categoria='antifungico'
                ))
        
        # Inflamação associada
        if sintomas.get('vermelhidao', False):
            antifungicos_inflamacao = [m for m in medicamentos if self._e_antifungico_inflamacao(m)]
            for med in antifungicos_inflamacao[:1]:
                recomendacoes.append(RecomendacaoFarmacologica(
                    medicamento=med.nome_comercial,
                    principio_ativo=med.nome_generico or med.nome_comercial,
                    indicacao="Micose com inflamação",
                    posologia=self._gerar_posologia(med, 'antifungico_inflamacao'),
                    contraindicacoes=med.contraindicacao or "Verificar bula",
                    observacoes="Não usar por mais de 2 semanas",
                    prioridade=1,
                    categoria='antifungico'
                ))
        
        return recomendacoes
    
    # Métodos auxiliares para classificar medicamentos
    def _medicamento_para_tosse(self, medicamento: Medicamento) -> bool:
        """Verifica se o medicamento é indicado para tosse"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['tosse', 'expectorante', 'antitussígeno', 'mucolítico'])
    
    def _e_antitussigeno(self, medicamento: Medicamento) -> bool:
        """Verifica se é antitussígeno"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antitussígeno', 'antitussigeno', 'dextrometorfano', 'clobutinol'])
    
    def _e_expectorante(self, medicamento: Medicamento) -> bool:
        """Verifica se é expectorante"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['expectorante', 'guaifenesina', 'ambroxol', 'mucolítico'])
    
    def _e_antialergico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antialérgico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antialérgico', 'antialergico', 'loratadina', 'desloratadina', 'dexclorfeniramina'])
    
    def _e_antipiretico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antipirético"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antipirético', 'antipiretico', 'paracetamol', 'ibuprofeno', 'dipirona'])
    
    def _e_analgesico(self, medicamento: Medicamento) -> bool:
        """Verifica se é analgésico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['analgésico', 'analgesico', 'paracetamol', 'ibuprofeno', 'dipirona', 'naproxeno'])
    
    def _e_antidiarreico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antidiarreico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antidiarreico', 'loperamida', 'racecadotril'])
    
    def _e_probiotico(self, medicamento: Medicamento) -> bool:
        """Verifica se é probiótico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['probiótico', 'probiotico', 'lactobacillus', 'bifidobacterium'])
    
    def _e_analgesico_topico(self, medicamento: Medicamento) -> bool:
        """Verifica se é analgésico tópico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['analgésico tópico', 'anestésico tópico', 'benzocaína', 'lidocaína'])
    
    def _e_antiacido(self, medicamento: Medicamento) -> bool:
        """Verifica se é antiácido"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antiácido', 'antiacido', 'hidróxido de alumínio', 'hidróxido de magnésio'])
    
    def _e_laxante(self, medicamento: Medicamento) -> bool:
        """Verifica se é laxante"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['laxante', 'purgativo', 'lactulose', 'sorbitol'])
    
    def _e_topico_hemorroidas(self, medicamento: Medicamento) -> bool:
        """Verifica se é tópico para hemorroidas"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['hemorroida', 'hemorroidas', 'anal', 'retal'])
    
    def _e_descongestionante(self, medicamento: Medicamento) -> bool:
        """Verifica se é descongestionante"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['descongestionante', 'pseudoefedrina', 'fenilefrina'])
    
    def _e_antihistaminico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antihistamínico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antihistamínico', 'antihistaminico', 'loratadina', 'cetirizina'])
    
    def _e_antifungico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antifúngico tópico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['antifúngico', 'antifungico', 'clotrimazol', 'miconazol', 'cetoconazol'])
    
    def _e_antifungico_sistemico(self, medicamento: Medicamento) -> bool:
        """Verifica se é antifúngico sistêmico"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['terbinafina', 'fluconazol', 'itraconazol', 'griseofulvina'])
    
    def _e_antifungico_unha(self, medicamento: Medicamento) -> bool:
        """Verifica se é antifúngico para unhas"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['unha', 'onicomicose', 'terbinafina', 'ciclopirox'])
    
    def _e_antifungico_inflamacao(self, medicamento: Medicamento) -> bool:
        """Verifica se é antifúngico com anti-inflamatório"""
        if not medicamento.indicacao:
            return False
        indicacao = medicamento.indicacao.lower()
        return any(palavra in indicacao for palavra in ['clotrimazol + hidrocortisona', 'miconazol + hidrocortisona', 'fungicort'])
    
    def _gerar_posologia(self, medicamento: Medicamento, tipo: str) -> str:
        """Gera posologia baseada no tipo de medicamento"""
        posologias = {
            'antitussigeno': '1 comprimido a cada 6-8 horas',
            'expectorante': '1 comprimido a cada 8 horas',
            'antialergico': '1 comprimido ao dia',
            'antipiretico': '1 comprimido a cada 6-8 horas',
            'analgesico': '1 comprimido a cada 6-8 horas',
            'antidiarreico': '1 comprimido após cada evacuação líquida',
            'probiotico': '1 cápsula ao dia',
            'analgesico_topico': 'Aplicar 3-4 vezes ao dia',
            'antiacido': '1 comprimido após as refeições',
            'laxante': '1 comprimido ao dia',
            'topico_hemorroidas': 'Aplicar 2-3 vezes ao dia',
            'descongestionante': '1 comprimido a cada 12 horas',
            'antihistaminico': '1 comprimido ao dia',
            'antifungico': 'Aplicar 2-3 vezes ao dia por 2-4 semanas',
            'antifungico_sistemico': '1 comprimido ao dia por 1-2 semanas',
            'antifungico_unha': 'Aplicar 1-2 vezes ao dia por 3-6 meses',
            'antifungico_inflamacao': 'Aplicar 2-3 vezes ao dia por 1-2 semanas'
        }
        return posologias.get(tipo, 'Seguir orientação médica')
    
    def _aplicar_modificadores_paciente(self, recomendacoes: List[RecomendacaoFarmacologica], 
                                      paciente_profile: Dict) -> List[RecomendacaoFarmacologica]:
        """Aplica modificadores baseados no perfil do paciente"""
        for recomendacao in recomendacoes:
            # Modificadores para idosos
            if paciente_profile.get('is_frail_elderly', False):
                if 'analgésico' in recomendacao.indicacao.lower():
                    recomendacao.observacoes += " | Reduzir dose em idosos"
                    recomendacao.prioridade = min(5, recomendacao.prioridade + 1)
            
            # Modificadores para gestantes/lactantes
            if paciente_profile.get('is_pregnant_or_lactating', False):
                if 'antitussígeno' in recomendacao.indicacao.lower():
                    recomendacao.observacoes += " | Cautela em gestantes"
                    recomendacao.prioridade = min(5, recomendacao.prioridade + 1)
        
        return recomendacoes

# Instância global do sistema de recomendações
sistema_recomendacoes = SistemaRecomendacoesFarmacologicas()
