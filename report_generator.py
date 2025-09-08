#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pharm-Assist - Gerador de Relatórios PDF
Sistema de geração de relatórios profissionais para consultas de triagem

Funcionalidades:
- Geração de relatórios PDF com layout profissional
- Inclusão de dados do paciente e histórico
- Análise de sintomas e recomendações
- Formatação automática de tabelas e textos
- Estilos personalizados para diferentes seções

Tecnologias utilizadas:
- ReportLab: Biblioteca para geração de PDFs
- Templates personalizados para layout
- Estilos CSS-like para formatação
- Tabelas responsivas e organizadas
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

class ReportGenerator:
    """
    Gerador de relatórios PDF para consultas de triagem
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para o relatório"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Subtítulos menores
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.darkblue
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Texto destacado
        self.styles.add(ParagraphStyle(
            name='CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        ))
    
    def generate_triagem_report(self, consulta_data: dict, paciente_data: dict, 
                               triagem_result: dict, respostas: list, output_path: str) -> str:
        """
        Gera relatório completo de triagem em PDF
        
        Args:
            consulta_data: Dados da consulta
            paciente_data: Dados do paciente
            triagem_result: Resultado da triagem
            respostas: Lista de perguntas e respostas
            output_path: Caminho para salvar o PDF
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Cabeçalho
        story.extend(self._create_header())
        
        # Informações da consulta
        story.extend(self._create_consulta_info(consulta_data))
        
        # Dados do paciente
        story.extend(self._create_patient_info(paciente_data))
        
        # Resultado da triagem
        story.extend(self._create_triagem_result(triagem_result))
        
        # Perguntas e respostas
        story.extend(self._create_qa_section(respostas))
        
        # Recomendações
        story.extend(self._create_recommendations(triagem_result))
        
        # Observações
        story.extend(self._create_observations(triagem_result))
        
        # Rodapé
        story.extend(self._create_footer())
        
        # Construir PDF
        doc.build(story)
        
        return output_path
    
    def _create_header(self):
        """Cria cabeçalho do relatório"""
        elements = []
        
        # Título principal
        title = Paragraph("SISTEMA DE TRIAGEM FARMACEUTICA", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtítulo
        subtitle = Paragraph("Relatório de Consulta", self.styles['CustomHeading2'])
        subtitle.alignment = TA_CENTER
        elements.append(subtitle)
        
        # Data e hora
        current_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
        date_text = Paragraph(f"Relatório gerado em: {current_time}", self.styles['CustomBody'])
        date_text.alignment = TA_CENTER
        elements.append(date_text)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_consulta_info(self, consulta_data: dict):
        """Cria seção de informações da consulta"""
        elements = []
        
        # Título da seção
        title = Paragraph("INFORMAÇÕES DA CONSULTA", self.styles['CustomHeading2'])
        elements.append(title)
        
        # Tabela de informações
        data = [
            ['Data da Consulta:', consulta_data.get('data', 'N/A')],
            ['ID da Consulta:', str(consulta_data.get('id', 'N/A'))],
            ['Encaminhamento:', 'Sim' if consulta_data.get('encaminhamento') else 'Não']
        ]
        
        if consulta_data.get('encaminhamento'):
            data.append(['Motivo:', consulta_data.get('motivo_encaminhamento', 'N/A')])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_patient_info(self, paciente_data: dict):
        """Cria seção de informações do paciente"""
        elements = []
        
        # Título da seção
        title = Paragraph("DADOS DO PACIENTE", self.styles['CustomHeading2'])
        elements.append(title)
        
        # Tabela de informações pessoais
        data = [
            ['Nome:', paciente_data.get('nome', 'N/A')],
            ['Idade:', f"{paciente_data.get('idade', 'N/A')} anos"],
            ['Sexo:', paciente_data.get('sexo', 'N/A')],
            ['Peso:', f"{paciente_data.get('peso', 'N/A')} kg" if paciente_data.get('peso') else 'N/A'],
            ['Altura:', f"{paciente_data.get('altura', 'N/A')} m" if paciente_data.get('altura') else 'N/A']
        ]
        
        # Hábitos
        habitos = []
        if paciente_data.get('fuma'):
            habitos.append('Fumante')
        if paciente_data.get('bebe'):
            habitos.append('Consome álcool')
        if not habitos:
            habitos.append('Nenhum hábito registrado')
        
        data.append(['Hábitos:', ', '.join(habitos)])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_triagem_result(self, triagem_result: dict):
        """Cria seção de resultado da triagem"""
        elements = []
        
        # Título da seção
        title = Paragraph("RESULTADO DA TRIAGEM", self.styles['CustomHeading2'])
        elements.append(title)
        
        # Score de risco
        score = triagem_result.get('score_risco', 0)
        nivel = triagem_result.get('nivel_risco', 'N/A').upper()
        
        # Tabela de resultado
        data = [
            ['Score de Risco:', f"{score}/100"],
            ['Nível de Risco:', nivel],
            ['Encaminhamento Médico:', 'Sim' if triagem_result.get('encaminhamento_medico') else 'Não']
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Sinais de alerta
        sinais = triagem_result.get('sinais_alerta', [])
        if sinais:
            elements.append(Spacer(1, 10))
            alert_title = Paragraph("SINAIS DE ALERTA IDENTIFICADOS:", self.styles['CustomHeading3'])
            elements.append(alert_title)
            
            for sinal in sinais:
                alert_text = Paragraph(f"• {sinal}", self.styles['CustomHighlight'])
                elements.append(alert_text)
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_qa_section(self, respostas: list):
        """Cria seção de perguntas e respostas"""
        elements = []
        
        # Título da seção
        title = Paragraph("PERGUNTAS E RESPOSTAS DA TRIAGEM", self.styles['CustomHeading2'])
        elements.append(title)
        
        if not respostas:
            no_data = Paragraph("Nenhuma pergunta/resposta registrada.", self.styles['CustomBody'])
            elements.append(no_data)
        else:
            # Tabela de perguntas e respostas
            table_data = [['Pergunta', 'Resposta']]
            
            for i, resposta in enumerate(respostas, 1):
                pergunta = resposta.get('pergunta_texto', f'Pergunta {i}')
                resposta_texto = resposta.get('resposta', 'N/A')
                
                # Quebrar texto longo
                if len(pergunta) > 50:
                    pergunta = pergunta[:47] + "..."
                if len(resposta_texto) > 50:
                    resposta_texto = resposta_texto[:47] + "..."
                
                table_data.append([pergunta, resposta_texto])
            
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_recommendations(self, triagem_result: dict):
        """Cria seção de recomendações"""
        elements = []
        
        # Título da seção
        title = Paragraph("RECOMENDAÇÕES", self.styles['CustomHeading2'])
        elements.append(title)
        
        # Recomendações farmacológicas
        meds = triagem_result.get('recomendacoes_medicamentos', [])
        if meds:
            med_title = Paragraph("Medicamentos Recomendados:", self.styles['CustomHeading3'])
            elements.append(med_title)
            
            for med in meds:
                med_text = Paragraph(f"• {med['medicamento']} ({med['tipo']}) - {med['justificativa']}", 
                                   self.styles['CustomBody'])
                elements.append(med_text)
        
        # Recomendações não farmacológicas
        nao_farm = triagem_result.get('recomendacoes_nao_farmacologicas', [])
        if nao_farm:
            elements.append(Spacer(1, 10))
            nao_farm_title = Paragraph("Medidas Não Farmacológicas:", self.styles['CustomHeading3'])
            elements.append(nao_farm_title)
            
            for rec in nao_farm:
                rec_text = Paragraph(f"• {rec['descricao']}", self.styles['CustomBody'])
                elements.append(rec_text)
        
        # Encaminhamento
        if triagem_result.get('encaminhamento_medico'):
            elements.append(Spacer(1, 10))
            enc_title = Paragraph("Encaminhamento Médico:", self.styles['CustomHeading3'])
            elements.append(enc_title)
            
            motivo = triagem_result.get('motivo_encaminhamento', 'Motivo não especificado')
            enc_text = Paragraph(f"• {motivo}", self.styles['CustomHighlight'])
            elements.append(enc_text)
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_observations(self, triagem_result: dict):
        """Cria seção de observações"""
        elements = []
        
        # Título da seção
        title = Paragraph("OBSERVAÇÕES", self.styles['CustomHeading2'])
        elements.append(title)
        
        observacoes = triagem_result.get('observacoes', [])
        if observacoes:
            for obs in observacoes:
                obs_text = Paragraph(f"• {obs}", self.styles['CustomBody'])
                elements.append(obs_text)
        else:
            no_obs = Paragraph("Nenhuma observação adicional.", self.styles['CustomBody'])
            elements.append(no_obs)
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_footer(self):
        """Cria rodapé do relatório"""
        elements = []
        
        # Linha separadora
        elements.append(Spacer(1, 20))
        
        # Informações do sistema
        footer_text = Paragraph(
            "Este relatorio foi gerado automaticamente pelo Sistema de Triagem Farmaceutica. "
            "Para dúvidas ou esclarecimentos, consulte um farmacêutico.",
            self.styles['CustomBody']
        )
        footer_text.alignment = TA_CENTER
        elements.append(footer_text)
        
        # Assinatura
        elements.append(Spacer(1, 30))
        signature_line = Paragraph("_" * 50, self.styles['CustomBody'])
        signature_line.alignment = TA_CENTER
        elements.append(signature_line)
        
        signature_text = Paragraph("Farmacêutico Responsável", self.styles['CustomBody'])
        signature_text.alignment = TA_CENTER
        elements.append(signature_text)
        
        return elements
