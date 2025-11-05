#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReportGenerator - Gerador de Relatórios PDF
============================================

Gera relatórios profissionais em PDF para consultas de triagem farmacêutica.
Utiliza ReportLab para criação de PDFs formatados.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


class ReportGenerator:
    """Gerador de relatórios PDF para triagens farmacêuticas"""
    
    def __init__(self):
        """Inicializa o gerador de relatórios"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para o relatório"""
        # Estilo para título
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Estilo para subtítulo
        self.styles.add(ParagraphStyle(
            name='SubtitleStyle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=20,
            spaceBefore=20
        ))
        
        # Estilo para corpo do texto
        self.styles.add(ParagraphStyle(
            name='BodyStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para informações importantes
        self.styles.add(ParagraphStyle(
            name='InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=8
        ))
    
    def generate_triagem_report(self, consulta_data, paciente_data, triagem_result, qa_data, output_path):
        """
        Gera relatório PDF de triagem farmacêutica
        
        Args:
            consulta_data: Dicionário com dados da consulta
            paciente_data: Dicionário com dados do paciente
            triagem_result: Dicionário com resultado da triagem
            qa_data: Dicionário com perguntas e respostas
            output_path: Caminho onde o PDF será salvo
        """
        # Criar documento PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Lista de elementos que compõem o documento
        story = []
        
        # === CABEÇALHO ===
        story.append(Paragraph("PHARM-ASSIST", self.styles['TitleStyle']))
        story.append(Paragraph("Relatório de Triagem Farmacêutica", self.styles['SubtitleStyle']))
        story.append(Spacer(1, 0.5*cm))
        
        # === DADOS DO PACIENTE ===
        story.append(Paragraph("Dados do Paciente", self.styles['SubtitleStyle']))
        
        paciente_info = [
            ['Nome:', paciente_data.get('nome', 'N/A')],
            ['Idade:', f"{paciente_data.get('idade', 'N/A')} anos"],
            ['Sexo:', 'Masculino' if paciente_data.get('sexo') == 'M' else 'Feminino' if paciente_data.get('sexo') == 'F' else 'N/A'],
        ]
        
        if paciente_data.get('peso'):
            paciente_info.append(['Peso:', f"{paciente_data.get('peso')} kg"])
        if paciente_data.get('altura'):
            paciente_info.append(['Altura:', f"{paciente_data.get('altura')} m"])
        
        paciente_table = Table(paciente_info, colWidths=[4*cm, 12*cm])
        paciente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        story.append(paciente_table)
        story.append(Spacer(1, 0.5*cm))
        
        # === DADOS DA CONSULTA ===
        story.append(Paragraph("Dados da Consulta", self.styles['SubtitleStyle']))
        
        consulta_date = consulta_data.get('data')
        if isinstance(consulta_date, str):
            try:
                consulta_date = datetime.fromisoformat(consulta_date.replace('Z', '+00:00'))
            except:
                pass
        
        if isinstance(consulta_date, datetime):
            data_str = consulta_date.strftime('%d/%m/%Y às %H:%M')
        else:
            data_str = str(consulta_data.get('data', 'N/A'))
        
        consulta_info = [
            ['Data/Hora:', data_str],
            ['ID da Consulta:', str(consulta_data.get('id', 'N/A'))],
        ]
        
        consulta_table = Table(consulta_info, colWidths=[4*cm, 12*cm])
        consulta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        story.append(consulta_table)
        story.append(Spacer(1, 0.5*cm))
        
        # === PERGUNTAS E RESPOSTAS ===
        if qa_data and qa_data.get('perguntas_respostas'):
            story.append(Paragraph("Anamnese - Perguntas e Respostas", self.styles['SubtitleStyle']))
            
            for idx, qa in enumerate(qa_data.get('perguntas_respostas', []), 1):
                pergunta_texto = qa.get('pergunta_texto', qa.get('pergunta', 'Pergunta não disponível'))
                resposta_texto = qa.get('resposta', 'Sem resposta')
                
                story.append(Paragraph(f"<b>{idx}. {pergunta_texto}</b>", self.styles['BodyStyle']))
                story.append(Paragraph(f"Resposta: {resposta_texto}", self.styles['InfoStyle']))
                story.append(Spacer(1, 0.3*cm))
            
            story.append(Spacer(1, 0.5*cm))
        
        
        # === RESULTADO DA TRIAGEM ===
        story.append(Paragraph("Resultado da Triagem", self.styles['SubtitleStyle']))
        
        scoring = triagem_result.get('scoring_result', {})
        score = scoring.get('total_score', 0)
        risk_level = scoring.get('risk_level', 'baixo')
        confidence = scoring.get('confidence', 0)
        
        # Determinar cor do risco
        if risk_level == 'alto':
            risk_color = colors.HexColor('#e74c3c')
        elif risk_level == 'medio':
            risk_color = colors.HexColor('#f39c12')
        else:
            risk_color = colors.HexColor('#27ae60')
        
        resultado_info = [
            ['Pontuação Total:', f"{score:.1f}"],
            ['Nível de Risco:', risk_level.upper()],
            ['Confiança:', f"{confidence*100:.1f}%"],
            ['Encaminhamento:', 'SIM' if triagem_result.get('encaminhamento_medico') else 'NÃO'],
        ]
        
        if triagem_result.get('motivo_encaminhamento'):
            resultado_info.append(['Motivo do Encaminhamento:', triagem_result.get('motivo_encaminhamento')])
        
        resultado_table = Table(resultado_info, colWidths=[5*cm, 11*cm])
        resultado_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 1), (1, 1), risk_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        story.append(resultado_table)
        story.append(Spacer(1, 0.5*cm))
        
        # === RECOMENDAÇÕES FARMACOLÓGICAS ===
        recomendacoes_med = triagem_result.get('recomendacoes_medicamentos', [])
        if recomendacoes_med:
            story.append(Paragraph("Recomendações Farmacológicas", self.styles['SubtitleStyle']))
            
            med_data = [['#', 'Medicamento', 'Justificativa']]
            for idx, rec in enumerate(recomendacoes_med, 1):
                medicamento = rec.get('medicamento', rec.get('descricao', 'N/A'))
                if isinstance(medicamento, dict):
                    medicamento = medicamento.get('nome', 'N/A')
                justificativa = rec.get('justificativa', 'Recomendado pela triagem')
                med_data.append([str(idx), medicamento, justificativa])
            
            med_table = Table(med_data, colWidths=[1*cm, 8*cm, 7*cm])
            med_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ]))
            story.append(med_table)
            story.append(Spacer(1, 0.5*cm))
        
        # === RECOMENDAÇÕES NÃO FARMACOLÓGICAS ===
        recomendacoes_nao_med = triagem_result.get('recomendacoes_nao_farmacologicas', [])
        if recomendacoes_nao_med:
            story.append(Paragraph("Recomendações Não Farmacológicas", self.styles['SubtitleStyle']))
            
            for idx, rec in enumerate(recomendacoes_nao_med, 1):
                descricao = rec.get('descricao', rec.get('titulo', 'N/A'))
                if isinstance(descricao, str):
                    story.append(Paragraph(f"<b>{idx}. {descricao}</b>", self.styles['BodyStyle']))
                    justificativa = rec.get('justificativa', '')
                    if justificativa:
                        story.append(Paragraph(justificativa, self.styles['InfoStyle']))
                story.append(Spacer(1, 0.3*cm))
            
            story.append(Spacer(1, 0.5*cm))
        
        # === OBSERVAÇÕES ===
        observacoes = triagem_result.get('observacoes', [])
        if observacoes:
            story.append(Paragraph("Observações", self.styles['SubtitleStyle']))
            for obs in observacoes:
                if isinstance(obs, str):
                    story.append(Paragraph(f"• {obs}", self.styles['InfoStyle']))
            story.append(Spacer(1, 0.5*cm))
        
        # === RODAPÉ ===
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", 
                              self.styles['InfoStyle']))
        story.append(Paragraph("Pharm-Assist - Sistema de Triagem Farmacêutica", 
                              ParagraphStyle(name='Footer', parent=self.styles['InfoStyle'], alignment=TA_CENTER)))
        
        # Construir PDF
        doc.build(story)

