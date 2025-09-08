
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar medicamentos da ANVISA
Importa dados de planilha Excel para o banco de dados do Pharm-Assist
"""

import pandas as pd
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import db, Medicamento
from config import Config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_medicamentos.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ImportadorMedicamentosANVISA:
    def __init__(self, arquivo_excel):
        """
        Inicializa o importador
        
        Args:
            arquivo_excel (str): Caminho para o arquivo Excel da ANVISA
        """
        self.arquivo_excel = arquivo_excel
        self.engine = None
        self.session = None
        self.medicamentos_importados = 0
        self.medicamentos_ignorados = 0
        self.erros = []
        
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            # Usar a mesma configuração do app
            database_url = Config.SQLALCHEMY_DATABASE_URI
            self.engine = create_engine(database_url, echo=False)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("Conectado ao banco de dados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def mapear_campos(self, row):
        """
        Mapeia os campos da planilha ANVISA para o modelo Medicamento
        
        Args:
            row: Linha da planilha Excel/CSV
            
        Returns:
            dict: Dados mapeados para o modelo
        """
        # Mapeamento específico para dados abertos da ANVISA
        medicamento_data = {
            'nome_comercial': self._limpar_texto(
                row.get('NOME_PRODUTO') or 
                row.get('NOME_COMERCIAL') or 
                row.get('PRODUTO') or 
                row.get('NOME') or
                row.get('NOME DO PRODUTO') or
                row.get('DENOMINAÇÃO COMERCIAL') or
                row.get('DENOMINACAO COMERCIAL')
            ),
            'nome_generico': self._limpar_texto(
                row.get('PRINCIPIO_ATIVO') or
                row.get('NOME_GENERICO') or 
                row.get('SUBSTANCIA_ATIVA') or
                row.get('SUBSTÂNCIA ATIVA') or
                row.get('PRINCÍPIO ATIVO') or
                row.get('PRINCIPIO ATIVO')
            ),
            'descricao': self._limpar_texto(
                row.get('CLASSE_TERAPEUTICA') or
                row.get('CATEGORIA_REGULATORIA') or
                row.get('DESCRICAO') or 
                row.get('APRESENTACAO') or
                row.get('APRESENTAÇÃO') or
                row.get('FORMA FARMACÊUTICA') or
                row.get('FORMA FARMACEUTICA')
            ),
            'indicacao': self._limpar_texto(
                row.get('CLASSE_TERAPEUTICA') or
                row.get('INDICACAO') or 
                row.get('INDICACOES') or
                row.get('INDICAÇÃO') or
                row.get('INDICAÇÕES') or
                row.get('INDICAÇÃO TERAPÊUTICA') or
                row.get('INDICACAO TERAPEUTICA')
            ),
            'contraindicacao': self._limpar_texto(
                row.get('CONTRAINDICACAO') or 
                row.get('CONTRAINDICACOES') or
                row.get('CONTRAINDICAÇÃO') or
                row.get('CONTRAINDICAÇÕES') or
                row.get('CONTRA-INDICAÇÃO') or
                row.get('CONTRA-INDICAÇÕES')
            ),
            'tipo': self._determinar_tipo(row),
            'ativo': self._determinar_ativo(row)
        }
        
        return medicamento_data
    
    def _limpar_texto(self, texto):
        """Limpa e normaliza texto"""
        if pd.isna(texto) or texto is None:
            return None
        
        texto = str(texto).strip()
        if texto == '' or texto.lower() in ['nan', 'none', 'null', 'n/a', 'na']:
            return None
            
        return texto
    
    def _determinar_tipo(self, row):
        """Determina se é farmacológico ou fitoterápico"""
        # Buscar em diferentes campos
        campos_para_verificar = [
            'NOME_COMERCIAL', 'PRODUTO', 'NOME', 'NOME DO PRODUTO',
            'DENOMINAÇÃO COMERCIAL', 'DENOMINACAO COMERCIAL',
            'NOME_GENERICO', 'PRINCIPIO_ATIVO', 'SUBSTANCIA_ATIVA',
            'SUBSTÂNCIA ATIVA', 'PRINCÍPIO ATIVO', 'PRINCIPIO ATIVO'
        ]
        
        texto_completo = ''
        for campo in campos_para_verificar:
            valor = row.get(campo)
            if valor and not pd.isna(valor):
                texto_completo += str(valor).lower() + ' '
        
        # Palavras-chave para fitoterápicos
        fitoterapicos_keywords = [
            'fitoterápico', 'fitoterapico', 'planta', 'extrato', 'chá', 'cha',
            'herbal', 'natural', 'vegetal', 'botânico', 'botanico'
        ]
        
        if any(keyword in texto_completo for keyword in fitoterapicos_keywords):
            return 'fitoterapico'
        
        return 'farmacologico'
    
    def _determinar_ativo(self, row):
        """Determina se o medicamento está ativo baseado na situação do registro"""
        situacao = str(row.get('SITUACAO_REGISTRO', '')).lower()
        
        # Medicamentos ativos
        situacoes_ativas = [
            'ativo', 'vigente', 'válido', 'valido', 'aprovado'
        ]
        
        # Medicamentos inativos
        situacoes_inativas = [
            'caduco', 'cancelado', 'suspenso', 'cassado', 'vencido'
        ]
        
        if any(situacao_ativa in situacao for situacao_ativa in situacoes_ativas):
            return True
        elif any(situacao_inativa in situacao for situacao_inativa in situacoes_inativas):
            return False
        else:
            # Se não conseguir determinar, assume como ativo
            return True
    
    def verificar_duplicata(self, nome_comercial, nome_generico):
        """
        Verifica se já existe um medicamento similar no banco
        
        Args:
            nome_comercial (str): Nome comercial
            nome_generico (str): Nome genérico
            
        Returns:
            bool: True se já existe, False caso contrário
        """
        if not nome_comercial:
            return True  # Ignorar se não tem nome comercial
            
        # Buscar por nome comercial exato
        existe = self.session.query(Medicamento).filter(
            Medicamento.nome_comercial.ilike(f"%{nome_comercial}%")
        ).first()
        
        if existe:
            return True
            
        # Buscar por nome genérico se disponível
        if nome_generico:
            existe = self.session.query(Medicamento).filter(
                Medicamento.nome_generico.ilike(f"%{nome_generico}%")
            ).first()
            
        return existe is not None
    
    def processar_planilha(self, amostra=None):
        """
        Processa a planilha Excel e importa os medicamentos
        
        Args:
            amostra (int): Número de linhas para processar (para teste)
        """
        try:
            logger.info(f"Iniciando importação do arquivo: {self.arquivo_excel}")
            
            # Ler arquivo (Excel ou CSV)
            if self.arquivo_excel.endswith('.csv'):
                # Tentar diferentes encodings e separadores para CSV
                try:
                    df = pd.read_csv(self.arquivo_excel, encoding='utf-8')
                except:
                    try:
                        df = pd.read_csv(self.arquivo_excel, encoding='latin-1', sep=';')
                    except:
                        df = pd.read_csv(self.arquivo_excel, encoding='latin-1')
            else:
                df = pd.read_excel(self.arquivo_excel)
            logger.info(f"Planilha carregada com {len(df)} linhas")
            
            # Mostrar colunas disponíveis
            logger.info(f"Colunas disponíveis: {list(df.columns)}")
            
            # Processar apenas uma amostra se especificado
            if amostra:
                df = df.head(amostra)
                logger.info(f"Processando amostra de {len(df)} linhas")
            
            # Processar em lotes para otimizar performance
            tamanho_lote = 100
            total_linhas = len(df)
            
            for i in range(0, total_linhas, tamanho_lote):
                lote = df.iloc[i:i+tamanho_lote]
                self._processar_lote(lote, i+1, total_linhas)
                
                # Commit a cada lote
                self.session.commit()
                
        except Exception as e:
            logger.error(f"Erro ao processar planilha: {e}")
            self.session.rollback()
            raise
    
    def _processar_lote(self, lote, inicio, total):
        """Processa um lote de medicamentos"""
        for idx, row in lote.iterrows():
            try:
                # Mapear dados
                medicamento_data = self.mapear_campos(row)
                
                # Verificar se tem dados mínimos
                if not medicamento_data['nome_comercial']:
                    self.medicamentos_ignorados += 1
                    continue
                
                # Verificar duplicata
                if self.verificar_duplicata(
                    medicamento_data['nome_comercial'], 
                    medicamento_data['nome_generico']
                ):
                    self.medicamentos_ignorados += 1
                    continue
                
                # Criar medicamento
                medicamento = Medicamento(**medicamento_data)
                self.session.add(medicamento)
                self.medicamentos_importados += 1
                
                # Log de progresso
                if self.medicamentos_importados % 50 == 0:
                    logger.info(f"Progresso: {inicio + idx} de {total} - "
                              f"Importados: {self.medicamentos_importados}, "
                              f"Ignorados: {self.medicamentos_ignorados}")
                
            except Exception as e:
                self.erros.append(f"Linha {idx + 1}: {str(e)}")
                logger.warning(f"Erro na linha {idx + 1}: {e}")
    
    def gerar_relatorio(self):
        """Gera relatório final da importação"""
        logger.info("=" * 50)
        logger.info("RELATÓRIO DE IMPORTAÇÃO")
        logger.info("=" * 50)
        logger.info(f"Medicamentos importados: {self.medicamentos_importados}")
        logger.info(f"Medicamentos ignorados: {self.medicamentos_ignorados}")
        logger.info(f"Total de erros: {len(self.erros)}")
        
        if self.erros:
            logger.info("\nERROS ENCONTRADOS:")
            for erro in self.erros[:10]:  # Mostrar apenas os primeiros 10
                logger.info(f"  - {erro}")
            if len(self.erros) > 10:
                logger.info(f"  ... e mais {len(self.erros) - 10} erros")
    
    def fechar_conexao(self):
        """Fecha conexão com o banco"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python import_medicamentos_anvisa.py <arquivo_excel> [amostra]")
        print("Exemplo: python import_medicamentos_anvisa.py medicamentos_anvisa.xlsx 100")
        sys.exit(1)
    
    arquivo_excel = sys.argv[1]
    amostra = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(arquivo_excel):
        logger.error(f"Arquivo não encontrado: {arquivo_excel}")
        sys.exit(1)
    
    importador = ImportadorMedicamentosANVISA(arquivo_excel)
    
    try:
        importador.conectar_banco()
        importador.processar_planilha(amostra)
        importador.gerar_relatorio()
        
    except Exception as e:
        logger.error(f"Erro durante importação: {e}")
        sys.exit(1)
    finally:
        importador.fechar_conexao()

if __name__ == "__main__":
    main()
