import os
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF
import logging

logger = logging.getLogger(__name__)

pdf_bp = Blueprint('pdf', __name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#00d4ff'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#ff6b00'),
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#00d4ff'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=black,
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        ))
        
        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=HexColor('#ff3d71'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#f8f9fa')
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=4,
            textColor=HexColor('#00d4ff'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))

    def generate_report(self, analysis_data):
        """Generate complete PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Cover page
        story.extend(self.create_cover_page(analysis_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self.create_executive_summary(analysis_data))
        story.append(PageBreak())
        
        # Scope section
        story.extend(self.create_scope_section(analysis_data.get('escopo', {})))
        story.append(PageBreak())
        
        # Avatar section
        story.extend(self.create_avatar_section(analysis_data.get('avatar_ultra_detalhado', {})))
        story.append(PageBreak())
        
        # Pain mapping section
        story.extend(self.create_pain_section(analysis_data.get('mapeamento_dores_ultra_detalhado', {})))
        story.append(PageBreak())
        
        # Competition section
        story.extend(self.create_competition_section(analysis_data.get('analise_concorrencia_detalhada', {})))
        story.append(PageBreak())
        
        # Market intelligence section
        story.extend(self.create_market_section(analysis_data.get('inteligencia_mercado', {})))
        story.append(PageBreak())
        
        # Keywords strategy section
        story.extend(self.create_keywords_section(analysis_data.get('estrategia_palavras_chave', {})))
        story.append(PageBreak())
        
        # Performance metrics section
        story.extend(self.create_metrics_section(analysis_data.get('metricas_performance_detalhadas', {})))
        story.append(PageBreak())
        
        # Market voice section
        story.extend(self.create_voice_section(analysis_data.get('voz_mercado_linguagem', {})))
        story.append(PageBreak())
        
        # Projections section
        story.extend(self.create_projections_section(analysis_data.get('projecoes_cenarios', {})))
        story.append(PageBreak())
        
        # Action plan section
        story.extend(self.create_action_plan_section(analysis_data.get('plano_acao_detalhado', [])))
        story.append(PageBreak())
        
        # Insights section
        story.extend(self.create_insights_section(analysis_data.get('insights_exclusivos', [])))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def create_cover_page(self, analysis_data):
        """Create cover page"""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("ARQUEOLOGIA DO AVATAR", self.styles['CustomTitle']))
        story.append(Paragraph("Análise Ultra-Detalhada com Gemini Pro 2.5", self.styles['Heading2']))
        
        story.append(Spacer(1, 1*inch))
        
        # Segment info
        escopo = analysis_data.get('escopo', {})
        if escopo.get('segmento_principal'):
            story.append(Paragraph(f"<b>Segmento:</b> {escopo['segmento_principal']}", self.styles['Highlight']))
        
        if escopo.get('produto_ideal'):
            story.append(Paragraph(f"<b>Produto:</b> {escopo['produto_ideal']}", self.styles['BodyText']))
        
        story.append(Spacer(1, 1*inch))
        
        # Key metrics overview
        projecoes = analysis_data.get('projecoes_cenarios', {})
        realista = projecoes.get('cenario_realista', {})
        
        if realista:
            story.append(Paragraph("MÉTRICAS PRINCIPAIS", self.styles['SectionHeader']))
            
            metrics_data = [
                ['Métrica', 'Valor'],
                ['ROI Projetado', realista.get('roi', 'N/A')],
                ['Taxa de Conversão', realista.get('taxa_conversao', 'N/A')],
                ['Faturamento Mensal', realista.get('faturamento_mensal', 'N/A')],
                ['Break Even', realista.get('break_even', 'N/A')]
            ]
            
            table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 1*inch))
        
        # Generation info
        story.append(Paragraph(f"<b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['BodyText']))
        story.append(Paragraph("<b>Powered by:</b> Gemini Pro 2.5 + Pesquisa em Tempo Real", self.styles['BodyText']))
        
        return story

    def create_executive_summary(self, analysis_data):
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("SUMÁRIO EXECUTIVO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Overview
        escopo = analysis_data.get('escopo', {})
        if escopo.get('proposta_valor'):
            story.append(Paragraph("PROPOSTA DE VALOR", self.styles['SectionHeader']))
            story.append(Paragraph(escopo['proposta_valor'], self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        # Market size
        tamanho_mercado = escopo.get('tamanho_mercado', {})
        if tamanho_mercado:
            story.append(Paragraph("TAMANHO DO MERCADO", self.styles['SectionHeader']))
            
            market_data = [
                ['Métrica', 'Valor'],
                ['TAM (Total Addressable Market)', tamanho_mercado.get('tam', 'N/A')],
                ['SAM (Serviceable Addressable Market)', tamanho_mercado.get('sam', 'N/A')],
                ['SOM (Serviceable Obtainable Market)', tamanho_mercado.get('som', 'N/A')]
            ]
            
            table = Table(market_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ff6b00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
            story.append(Spacer(1, 15))
        
        # Key insights
        insights = analysis_data.get('insights_exclusivos', [])
        if insights:
            story.append(Paragraph("PRINCIPAIS INSIGHTS", self.styles['SectionHeader']))
            for i, insight in enumerate(insights[:3], 1):  # Top 3 insights
                story.append(Paragraph(f"<b>{i}.</b> {insight}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        return story

    def create_scope_section(self, escopo):
        """Create scope section"""
        story = []
        
        story.append(Paragraph("DEFINIÇÃO DO ESCOPO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        if escopo.get('segmento_principal'):
            story.append(Paragraph("SEGMENTO PRINCIPAL", self.styles['SectionHeader']))
            story.append(Paragraph(escopo['segmento_principal'], self.styles['Highlight']))
            story.append(Spacer(1, 15))
        
        if escopo.get('subsegmentos'):
            story.append(Paragraph("SUBSEGMENTOS IDENTIFICADOS", self.styles['SectionHeader']))
            for subsegmento in escopo['subsegmentos']:
                story.append(Paragraph(f"• {subsegmento}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        if escopo.get('produto_ideal'):
            story.append(Paragraph("PRODUTO IDEAL", self.styles['SectionHeader']))
            story.append(Paragraph(escopo['produto_ideal'], self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        if escopo.get('proposta_valor'):
            story.append(Paragraph("PROPOSTA DE VALOR", self.styles['SectionHeader']))
            story.append(Paragraph(escopo['proposta_valor'], self.styles['BodyText']))
        
        return story

    def create_avatar_section(self, avatar):
        """Create avatar section"""
        story = []
        
        story.append(Paragraph("AVATAR ULTRA-DETALHADO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Persona principal
        persona = avatar.get('persona_principal', {})
        if persona:
            story.append(Paragraph("PERSONA PRINCIPAL", self.styles['SectionHeader']))
            
            persona_data = [
                ['Atributo', 'Valor'],
                ['Nome', persona.get('nome', 'N/A')],
                ['Idade', persona.get('idade', 'N/A')],
                ['Profissão', persona.get('profissao', 'N/A')],
                ['Renda Mensal', persona.get('renda_mensal', 'N/A')],
                ['Localização', persona.get('localizacao', 'N/A')],
                ['Estado Civil', persona.get('estado_civil', 'N/A')],
                ['Escolaridade', persona.get('escolaridade', 'N/A')]
            ]
            
            table = Table(persona_data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Demografia detalhada
        demografia = avatar.get('demografia_detalhada', {})
        if demografia:
            story.append(Paragraph("DEMOGRAFIA DETALHADA", self.styles['SectionHeader']))
            
            for key, value in demografia.items():
                if value:
                    label = key.replace('_', ' ').title()
                    story.append(Paragraph(f"<b>{label}:</b> {value}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        # Psicografia profunda
        psicografia = avatar.get('psicografia_profunda', {})
        if psicografia:
            story.append(Paragraph("PSICOGRAFIA PROFUNDA", self.styles['SectionHeader']))
            
            if psicografia.get('valores_fundamentais'):
                story.append(Paragraph("<b>Valores Fundamentais:</b>", self.styles['SubsectionHeader']))
                for valor in psicografia['valores_fundamentais']:
                    story.append(Paragraph(f"• {valor}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
            
            if psicografia.get('estilo_vida_detalhado'):
                story.append(Paragraph("<b>Estilo de Vida:</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(psicografia['estilo_vida_detalhado'], self.styles['BodyText']))
                story.append(Spacer(1, 10))
            
            if psicografia.get('aspiracoes_profissionais'):
                story.append(Paragraph("<b>Aspirações Profissionais:</b>", self.styles['SubsectionHeader']))
                for aspiracao in psicografia['aspiracoes_profissionais']:
                    story.append(Paragraph(f"• {aspiracao}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
            
            if psicografia.get('medos_profundos'):
                story.append(Paragraph("<b>Medos Profundos:</b>", self.styles['SubsectionHeader']))
                for medo in psicografia['medos_profundos']:
                    story.append(Paragraph(f"• {medo}", self.styles['BodyText']))
        
        return story

    def create_pain_section(self, dores):
        """Create pain mapping section"""
        story = []
        
        story.append(Paragraph("MAPEAMENTO DE DORES", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Dores críticas
        nivel1 = dores.get('dores_nivel_1_criticas', [])
        if nivel1:
            story.append(Paragraph("DORES CRÍTICAS (NÍVEL 1)", self.styles['SectionHeader']))
            for i, dor in enumerate(nivel1, 1):
                story.append(Paragraph(f"<b>Dor {i}:</b> {dor.get('dor', 'N/A')}", self.styles['Highlight']))
                story.append(Paragraph(f"<b>Intensidade:</b> {dor.get('intensidade', 'N/A')} | <b>Frequência:</b> {dor.get('frequencia', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Impacto:</b> {dor.get('impacto_vida', 'N/A')}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
        
        # Dores importantes
        nivel2 = dores.get('dores_nivel_2_importantes', [])
        if nivel2:
            story.append(Paragraph("DORES IMPORTANTES (NÍVEL 2)", self.styles['SectionHeader']))
            for i, dor in enumerate(nivel2, 1):
                story.append(Paragraph(f"<b>Dor {i}:</b> {dor.get('dor', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Intensidade:</b> {dor.get('intensidade', 'N/A')} | <b>Frequência:</b> {dor.get('frequencia', 'N/A')}", self.styles['BodyText']))
                story.append(Spacer(1, 8))
        
        # Jornada da dor
        jornada = dores.get('jornada_dor', {})
        if jornada:
            story.append(Paragraph("JORNADA DA DOR", self.styles['SectionHeader']))
            
            jornada_data = [
                ['Etapa', 'Descrição'],
                ['Gatilho Inicial', jornada.get('gatilho_inicial', 'N/A')],
                ['Evolução da Dor', jornada.get('evolucao_dor', 'N/A')],
                ['Ponto Insuportável', jornada.get('ponto_insuportavel', 'N/A')],
                ['Busca por Solução', jornada.get('busca_solucao', 'N/A')]
            ]
            
            table = Table(jornada_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ff3d71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(table)
        
        return story

    def create_competition_section(self, concorrencia):
        """Create competition section"""
        story = []
        
        story.append(Paragraph("ANÁLISE DA CONCORRÊNCIA", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Concorrentes diretos
        diretos = concorrencia.get('concorrentes_diretos', [])
        if diretos:
            story.append(Paragraph("CONCORRENTES DIRETOS", self.styles['SectionHeader']))
            
            for concorrente in diretos:
                story.append(Paragraph(f"<b>{concorrente.get('nome', 'N/A')}</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(f"<b>Preço:</b> {concorrente.get('preco_range', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Proposta:</b> {concorrente.get('proposta_valor', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Share de Mercado:</b> {concorrente.get('share_mercado_estimado', 'N/A')}", self.styles['BodyText']))
                
                if concorrente.get('pontos_fortes'):
                    story.append(Paragraph("<b>Pontos Fortes:</b>", self.styles['BodyText']))
                    for ponto in concorrente['pontos_fortes']:
                        story.append(Paragraph(f"• {ponto}", self.styles['BodyText']))
                
                if concorrente.get('pontos_fracos'):
                    story.append(Paragraph("<b>Pontos Fracos:</b>", self.styles['BodyText']))
                    for ponto in concorrente['pontos_fracos']:
                        story.append(Paragraph(f"• {ponto}", self.styles['BodyText']))
                
                story.append(Spacer(1, 15))
        
        # Gaps e oportunidades
        gaps = concorrencia.get('gaps_oportunidades', [])
        if gaps:
            story.append(Paragraph("GAPS E OPORTUNIDADES", self.styles['SectionHeader']))
            for gap in gaps:
                story.append(Paragraph(f"• {gap}", self.styles['BodyText']))
        
        return story

    def create_market_section(self, mercado):
        """Create market intelligence section"""
        story = []
        
        story.append(Paragraph("INTELIGÊNCIA DE MERCADO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Tendências em crescimento
        tendencias = mercado.get('tendencias_crescimento', [])
        if tendencias:
            story.append(Paragraph("TENDÊNCIAS EM CRESCIMENTO", self.styles['SectionHeader']))
            
            for tendencia in tendencias:
                story.append(Paragraph(f"<b>{tendencia.get('tendencia', 'N/A')}</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(f"<b>Impacto:</b> {tendencia.get('impacto', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Timeline:</b> {tendencia.get('timeline', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Oportunidade:</b> {tendencia.get('oportunidade', 'N/A')}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
        
        # Sazonalidade
        sazonalidade = mercado.get('sazonalidade_detalhada', {})
        if sazonalidade:
            story.append(Paragraph("SAZONALIDADE", self.styles['SectionHeader']))
            
            sazon_data = [
                ['Tipo', 'Períodos'],
                ['Picos de Demanda', ', '.join(sazonalidade.get('picos_demanda', []))],
                ['Baixas de Demanda', ', '.join(sazonalidade.get('baixas_demanda', []))]
            ]
            
            table = Table(sazon_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ff6b00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
        
        return story

    def create_keywords_section(self, palavras):
        """Create keywords strategy section"""
        story = []
        
        story.append(Paragraph("ESTRATÉGIA DE PALAVRAS-CHAVE", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Palavras primárias
        primarias = palavras.get('palavras_primarias', [])
        if primarias:
            story.append(Paragraph("PALAVRAS-CHAVE PRIMÁRIAS", self.styles['SectionHeader']))
            
            kw_data = [['Termo', 'Volume/Mês', 'CPC', 'Dificuldade', 'Oportunidade']]
            
            for kw in primarias[:5]:  # Top 5
                kw_data.append([
                    kw.get('termo', 'N/A'),
                    kw.get('volume_mensal', 'N/A'),
                    kw.get('cpc_estimado', 'N/A'),
                    kw.get('dificuldade', 'N/A'),
                    kw.get('oportunidade', 'N/A')
                ])
            
            table = Table(kw_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Custos por plataforma
        custos = palavras.get('custos_aquisicao_canal', {})
        if custos:
            story.append(Paragraph("CUSTOS POR PLATAFORMA", self.styles['SectionHeader']))
            
            platform_data = [['Plataforma', 'CPC', 'CPM', 'CPA']]
            
            for platform, costs in custos.items():
                platform_data.append([
                    platform.title(),
                    costs.get('cpc_medio', 'N/A'),
                    costs.get('cpm_medio', 'N/A'),
                    costs.get('cpa_estimado', 'N/A')
                ])
            
            table = Table(platform_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ff6b00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
        
        return story

    def create_metrics_section(self, metricas):
        """Create performance metrics section"""
        story = []
        
        story.append(Paragraph("MÉTRICAS DE PERFORMANCE", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Benchmarks
        benchmarks = metricas.get('benchmarks_segmento', {})
        if benchmarks:
            story.append(Paragraph("BENCHMARKS DO SEGMENTO", self.styles['SectionHeader']))
            
            bench_data = [
                ['Métrica', 'Valor'],
                ['CAC Médio', benchmarks.get('cac_medio_segmento', 'N/A')],
                ['LTV Médio', benchmarks.get('ltv_medio_segmento', 'N/A')],
                ['Churn Rate', benchmarks.get('churn_rate_medio', 'N/A')],
                ['Ticket Médio', benchmarks.get('ticket_medio_segmento', 'N/A')]
            ]
            
            table = Table(bench_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # KPIs críticos
        kpis = metricas.get('kpis_criticos', [])
        if kpis:
            story.append(Paragraph("KPIs CRÍTICOS", self.styles['SectionHeader']))
            
            for kpi in kpis:
                story.append(Paragraph(f"<b>{kpi.get('metrica', 'N/A')}</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(f"<b>Valor Ideal:</b> {kpi.get('valor_ideal', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Como Medir:</b> {kpi.get('como_medir', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Frequência:</b> {kpi.get('frequencia', 'N/A')}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
        
        return story

    def create_voice_section(self, voz):
        """Create market voice section"""
        story = []
        
        story.append(Paragraph("VOZ DO MERCADO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Linguagem do avatar
        linguagem = voz.get('linguagem_avatar', {})
        if linguagem:
            story.append(Paragraph("LINGUAGEM DO AVATAR", self.styles['SectionHeader']))
            
            if linguagem.get('termos_tecnicos'):
                story.append(Paragraph("<b>Termos Técnicos:</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(', '.join(linguagem['termos_tecnicos']), self.styles['BodyText']))
                story.append(Spacer(1, 8))
            
            if linguagem.get('palavras_poder'):
                story.append(Paragraph("<b>Palavras de Poder:</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(', '.join(linguagem['palavras_poder']), self.styles['BodyText']))
                story.append(Spacer(1, 8))
            
            if linguagem.get('palavras_evitar'):
                story.append(Paragraph("<b>Palavras a Evitar:</b>", self.styles['SubsectionHeader']))
                story.append(Paragraph(', '.join(linguagem['palavras_evitar']), self.styles['BodyText']))
                story.append(Spacer(1, 15))
        
        # Principais objeções
        objecoes = voz.get('objecoes_principais', [])
        if objecoes:
            story.append(Paragraph("PRINCIPAIS OBJEÇÕES", self.styles['SectionHeader']))
            
            for i, obj in enumerate(objecoes, 1):
                story.append(Paragraph(f"<b>Objeção {i}:</b> {obj.get('objecao', 'N/A')}", self.styles['Highlight']))
                story.append(Paragraph(f"<b>Estratégia:</b> {obj.get('estrategia_contorno', 'N/A')}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
        
        return story

    def create_projections_section(self, projecoes):
        """Create projections section"""
        story = []
        
        story.append(Paragraph("PROJEÇÕES DE CENÁRIOS", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        # Tabela comparativa dos cenários
        conservador = projecoes.get('cenario_conservador', {})
        realista = projecoes.get('cenario_realista', {})
        otimista = projecoes.get('cenario_otimista', {})
        
        if conservador or realista or otimista:
            scenario_data = [
                ['Métrica', 'Conservador', 'Realista', 'Otimista'],
                ['Taxa de Conversão', 
                 conservador.get('taxa_conversao', 'N/A'),
                 realista.get('taxa_conversao', 'N/A'),
                 otimista.get('taxa_conversao', 'N/A')],
                ['Faturamento Mensal',
                 conservador.get('faturamento_mensal', 'N/A'),
                 realista.get('faturamento_mensal', 'N/A'),
                 otimista.get('faturamento_mensal', 'N/A')],
                ['ROI',
                 conservador.get('roi', 'N/A'),
                 realista.get('roi', 'N/A'),
                 otimista.get('roi', 'N/A')],
                ['Break Even',
                 conservador.get('break_even', 'N/A'),
                 realista.get('break_even', 'N/A'),
                 otimista.get('break_even', 'N/A')]
            ]
            
            table = Table(scenario_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00d4ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Premissas de cada cenário
        if realista.get('premissas'):
            story.append(Paragraph("PREMISSAS DO CENÁRIO REALISTA", self.styles['SectionHeader']))
            for premissa in realista['premissas']:
                story.append(Paragraph(f"• {premissa}", self.styles['BodyText']))
        
        return story

    def create_action_plan_section(self, plano):
        """Create action plan section"""
        story = []
        
        story.append(Paragraph("PLANO DE AÇÃO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        for i, fase in enumerate(plano, 1):
            story.append(Paragraph(f"FASE {i}: {fase.get('fase', 'N/A')}", self.styles['SectionHeader']))
            story.append(Paragraph(f"<b>Duração:</b> {fase.get('duracao', 'N/A')}", self.styles['BodyText']))
            story.append(Spacer(1, 10))
            
            acoes = fase.get('acoes', [])
            for j, acao in enumerate(acoes, 1):
                story.append(Paragraph(f"<b>Ação {j}:</b> {acao.get('acao', 'N/A')}", self.styles['SubsectionHeader']))
                story.append(Paragraph(f"<b>Responsável:</b> {acao.get('responsavel', 'N/A')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Prazo:</b> {acao.get('prazo', 'N/A')}", self.styles['BodyText']))
                
                if acao.get('recursos_necessarios'):
                    story.append(Paragraph(f"<b>Recursos:</b> {', '.join(acao['recursos_necessarios'])}", self.styles['BodyText']))
                
                if acao.get('metricas_sucesso'):
                    story.append(Paragraph(f"<b>Métricas de Sucesso:</b> {', '.join(acao['metricas_sucesso'])}", self.styles['BodyText']))
                
                story.append(Spacer(1, 10))
            
            story.append(Spacer(1, 15))
        
        return story

    def create_insights_section(self, insights):
        """Create insights section"""
        story = []
        
        story.append(Paragraph("INSIGHTS EXCLUSIVOS", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 20))
        
        for i, insight in enumerate(insights, 1):
            story.append(Paragraph(f"<b>Insight {i}:</b> {insight}", self.styles['Highlight']))
            story.append(Spacer(1, 10))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#00d4ff')))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Relatório gerado pela Arqueologia do Avatar com Gemini Pro 2.5", self.styles['BodyText']))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['BodyText']))
        
        return story

@pdf_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF report from analysis data"""
    try:
        analysis_data = request.get_json()
        
        if not analysis_data:
            return jsonify({'error': 'Dados de análise não fornecidos'}), 400
        
        # Generate PDF
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_report(analysis_data)
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'analise-avatar-gemini-{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        return jsonify({'error': 'Erro interno ao gerar PDF', 'details': str(e)}), 500