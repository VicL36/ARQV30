import os
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, blue, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
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
            textColor=HexColor('#1e40af'),
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
            textColor=HexColor('#ea580c'),
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#1e40af'),
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
            textColor=HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#f8fafc')
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=4,
            textColor=HexColor('#1e40af'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))

    def generate_report(self, analysis_data):
        """Generate complete PDF report"""
        try:
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
            escopo = analysis_data.get('escopo', {})
            if escopo:
                story.extend(self.create_scope_section(escopo))
                story.append(PageBreak())
            
            # Avatar section
            avatar = analysis_data.get('avatar_ultra_detalhado', {})
            if avatar:
                story.extend(self.create_avatar_section(avatar))
                story.append(PageBreak())
            
            # Pain mapping section
            dores = analysis_data.get('mapeamento_dores_ultra_detalhado', {})
            if dores:
                story.extend(self.create_pain_section(dores))
                story.append(PageBreak())
            
            # Competition section
            concorrencia = analysis_data.get('analise_concorrencia_detalhada', {})
            if concorrencia:
                story.extend(self.create_competition_section(concorrencia))
                story.append(PageBreak())
            
            # Market intelligence section
            mercado = analysis_data.get('inteligencia_mercado', {})
            if mercado:
                story.extend(self.create_market_section(mercado))
                story.append(PageBreak())
            
            # Keywords strategy section
            palavras = analysis_data.get('estrategia_palavras_chave', {})
            if palavras:
                story.extend(self.create_keywords_section(palavras))
                story.append(PageBreak())
            
            # Performance metrics section
            metricas = analysis_data.get('metricas_performance_detalhadas', {})
            if metricas:
                story.extend(self.create_metrics_section(metricas))
                story.append(PageBreak())
            
            # Projections section
            projecoes = analysis_data.get('projecoes_cenarios', {})
            if projecoes:
                story.extend(self.create_projections_section(projecoes))
                story.append(PageBreak())
            
            # Action plan section
            plano = analysis_data.get('plano_acao_detalhado', [])
            if plano:
                story.extend(self.create_action_plan_section(plano))
                story.append(PageBreak())
            
            # Insights section
            insights = analysis_data.get('insights_exclusivos', [])
            if insights:
                story.extend(self.create_insights_section(insights))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Erro na geração do PDF: {str(e)}")
            raise

    def create_cover_page(self, analysis_data):
        """Create cover page"""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("ARQUEOLOGIA DO AVATAR", self.styles['CustomTitle']))
        story.append(Paragraph("Análise Ultra-Detalhada com IA", self.styles['Heading2']))
        
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
                ['ROI Projetado', str(realista.get('roi', 'N/A'))],
                ['Taxa de Conversão', str(realista.get('taxa_conversao', 'N/A'))],
                ['Faturamento Mensal', str(realista.get('faturamento_mensal', 'N/A'))],
                ['Break Even', str(realista.get('break_even', 'N/A'))]
            ]
            
            table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 1*inch))
        
        # Generation info
        story.append(Paragraph(f"<b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['BodyText']))
        story.append(Paragraph("<b>Powered by:</b> IA + Pesquisa em Tempo Real", self.styles['BodyText']))
        
        return story

    def create_executive_summary(self, analysis_data):
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("SUMÁRIO EXECUTIVO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Overview
        escopo = analysis_data.get('escopo', {})
        if escopo.get('proposta_valor'):
            story.append(Paragraph("PROPOSTA DE VALOR", self.styles['SectionHeader']))
            story.append(Paragraph(str(escopo['proposta_valor']), self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        # Market size
        tamanho_mercado = escopo.get('tamanho_mercado', {})
        if tamanho_mercado:
            story.append(Paragraph("TAMANHO DO MERCADO", self.styles['SectionHeader']))
            
            market_data = [
                ['Métrica', 'Valor'],
                ['TAM (Total Addressable Market)', str(tamanho_mercado.get('tam', 'N/A'))],
                ['SAM (Serviceable Addressable Market)', str(tamanho_mercado.get('sam', 'N/A'))],
                ['SOM (Serviceable Obtainable Market)', str(tamanho_mercado.get('som', 'N/A'))]
            ]
            
            table = Table(market_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ea580c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
            story.append(Spacer(1, 15))
        
        # Key insights
        insights = analysis_data.get('insights_exclusivos', [])
        if insights:
            story.append(Paragraph("PRINCIPAIS INSIGHTS", self.styles['SectionHeader']))
            for i, insight in enumerate(insights[:3], 1):  # Top 3 insights
                story.append(Paragraph(f"<b>{i}.</b> {str(insight)}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        return story

    def create_scope_section(self, escopo):
        """Create scope section"""
        story = []
        
        story.append(Paragraph("DEFINIÇÃO DO ESCOPO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        if escopo.get('segmento_principal'):
            story.append(Paragraph("SEGMENTO PRINCIPAL", self.styles['SectionHeader']))
            story.append(Paragraph(str(escopo['segmento_principal']), self.styles['Highlight']))
            story.append(Spacer(1, 15))
        
        if escopo.get('subsegmentos'):
            story.append(Paragraph("SUBSEGMENTOS IDENTIFICADOS", self.styles['SectionHeader']))
            for subsegmento in escopo['subsegmentos']:
                story.append(Paragraph(f"• {str(subsegmento)}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        if escopo.get('produto_ideal'):
            story.append(Paragraph("PRODUTO IDEAL", self.styles['SectionHeader']))
            story.append(Paragraph(str(escopo['produto_ideal']), self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        if escopo.get('proposta_valor'):
            story.append(Paragraph("PROPOSTA DE VALOR", self.styles['SectionHeader']))
            story.append(Paragraph(str(escopo['proposta_valor']), self.styles['BodyText']))
        
        return story

    def create_avatar_section(self, avatar):
        """Create avatar section"""
        story = []
        
        story.append(Paragraph("AVATAR ULTRA-DETALHADO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Persona principal
        persona = avatar.get('persona_principal', {})
        if persona:
            story.append(Paragraph("PERSONA PRINCIPAL", self.styles['SectionHeader']))
            
            persona_data = [
                ['Atributo', 'Valor'],
                ['Nome', str(persona.get('nome', 'N/A'))],
                ['Idade', str(persona.get('idade', 'N/A'))],
                ['Profissão', str(persona.get('profissao', 'N/A'))],
                ['Renda Mensal', str(persona.get('renda_mensal', 'N/A'))],
                ['Localização', str(persona.get('localizacao', 'N/A'))],
                ['Estado Civil', str(persona.get('estado_civil', 'N/A'))],
                ['Escolaridade', str(persona.get('escolaridade', 'N/A'))]
            ]
            
            table = Table(persona_data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
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
                    story.append(Paragraph(f"<b>{label}:</b> {str(value)}", self.styles['BodyText']))
            story.append(Spacer(1, 15))
        
        return story

    def create_pain_section(self, dores):
        """Create pain mapping section"""
        story = []
        
        story.append(Paragraph("MAPEAMENTO DE DORES", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Dores críticas
        nivel1 = dores.get('dores_nivel_1_criticas', [])
        if nivel1:
            story.append(Paragraph("DORES CRÍTICAS (NÍVEL 1)", self.styles['SectionHeader']))
            for i, dor in enumerate(nivel1, 1):
                if isinstance(dor, dict):
                    story.append(Paragraph(f"<b>Dor {i}:</b> {str(dor.get('dor', 'N/A'))}", self.styles['Highlight']))
                    story.append(Paragraph(f"<b>Intensidade:</b> {str(dor.get('intensidade', 'N/A'))} | <b>Frequência:</b> {str(dor.get('frequencia', 'N/A'))}", self.styles['BodyText']))
                    story.append(Paragraph(f"<b>Impacto:</b> {str(dor.get('impacto_vida', 'N/A'))}", self.styles['BodyText']))
                else:
                    story.append(Paragraph(f"<b>Dor {i}:</b> {str(dor)}", self.styles['Highlight']))
                story.append(Spacer(1, 10))
        
        return story

    def create_competition_section(self, concorrencia):
        """Create competition section"""
        story = []
        
        story.append(Paragraph("ANÁLISE DA CONCORRÊNCIA", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Concorrentes diretos
        diretos = concorrencia.get('concorrentes_diretos', [])
        if diretos:
            story.append(Paragraph("CONCORRENTES DIRETOS", self.styles['SectionHeader']))
            
            for concorrente in diretos:
                if isinstance(concorrente, dict):
                    story.append(Paragraph(f"<b>{str(concorrente.get('nome', 'N/A'))}</b>", self.styles['SubsectionHeader']))
                    story.append(Paragraph(f"<b>Preço:</b> {str(concorrente.get('preco_range', 'N/A'))}", self.styles['BodyText']))
                    story.append(Paragraph(f"<b>Proposta:</b> {str(concorrente.get('proposta_valor', 'N/A'))}", self.styles['BodyText']))
                    story.append(Spacer(1, 15))
        
        return story

    def create_market_section(self, mercado):
        """Create market intelligence section"""
        story = []
        
        story.append(Paragraph("INTELIGÊNCIA DE MERCADO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Tendências em crescimento
        tendencias = mercado.get('tendencias_crescimento', [])
        if tendencias:
            story.append(Paragraph("TENDÊNCIAS EM CRESCIMENTO", self.styles['SectionHeader']))
            
            for tendencia in tendencias:
                if isinstance(tendencia, dict):
                    story.append(Paragraph(f"<b>{str(tendencia.get('tendencia', 'N/A'))}</b>", self.styles['SubsectionHeader']))
                    story.append(Paragraph(f"<b>Impacto:</b> {str(tendencia.get('impacto', 'N/A'))}", self.styles['BodyText']))
                    story.append(Spacer(1, 10))
        
        return story

    def create_keywords_section(self, palavras):
        """Create keywords strategy section"""
        story = []
        
        story.append(Paragraph("ESTRATÉGIA DE PALAVRAS-CHAVE", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Palavras primárias
        primarias = palavras.get('palavras_primarias', [])
        if primarias:
            story.append(Paragraph("PALAVRAS-CHAVE PRIMÁRIAS", self.styles['SectionHeader']))
            
            kw_data = [['Termo', 'Volume/Mês', 'CPC', 'Dificuldade', 'Oportunidade']]
            
            for kw in primarias[:5]:  # Top 5
                if isinstance(kw, dict):
                    kw_data.append([
                        str(kw.get('termo', 'N/A')),
                        str(kw.get('volume_mensal', 'N/A')),
                        str(kw.get('cpc_estimado', 'N/A')),
                        str(kw.get('dificuldade', 'N/A')),
                        str(kw.get('oportunidade', 'N/A'))
                    ])
            
            if len(kw_data) > 1:
                table = Table(kw_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                story.append(table)
        
        return story

    def create_metrics_section(self, metricas):
        """Create performance metrics section"""
        story = []
        
        story.append(Paragraph("MÉTRICAS DE PERFORMANCE", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Benchmarks
        benchmarks = metricas.get('benchmarks_segmento', {})
        if benchmarks:
            story.append(Paragraph("BENCHMARKS DO SEGMENTO", self.styles['SectionHeader']))
            
            bench_data = [
                ['Métrica', 'Valor'],
                ['CAC Médio', str(benchmarks.get('cac_medio_segmento', 'N/A'))],
                ['LTV Médio', str(benchmarks.get('ltv_medio_segmento', 'N/A'))],
                ['Churn Rate', str(benchmarks.get('churn_rate_medio', 'N/A'))],
                ['Ticket Médio', str(benchmarks.get('ticket_medio_segmento', 'N/A'))]
            ]
            
            table = Table(bench_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(table)
        
        return story

    def create_projections_section(self, projecoes):
        """Create projections section"""
        story = []
        
        story.append(Paragraph("PROJEÇÕES DE CENÁRIOS", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        # Tabela comparativa dos cenários
        conservador = projecoes.get('cenario_conservador', {})
        realista = projecoes.get('cenario_realista', {})
        otimista = projecoes.get('cenario_otimista', {})
        
        if conservador or realista or otimista:
            scenario_data = [
                ['Métrica', 'Conservador', 'Realista', 'Otimista'],
                ['Taxa de Conversão', 
                 str(conservador.get('taxa_conversao', 'N/A')),
                 str(realista.get('taxa_conversao', 'N/A')),
                 str(otimista.get('taxa_conversao', 'N/A'))],
                ['Faturamento Mensal',
                 str(conservador.get('faturamento_mensal', 'N/A')),
                 str(realista.get('faturamento_mensal', 'N/A')),
                 str(otimista.get('faturamento_mensal', 'N/A'))],
                ['ROI',
                 str(conservador.get('roi', 'N/A')),
                 str(realista.get('roi', 'N/A')),
                 str(otimista.get('roi', 'N/A'))]
            ]
            
            table = Table(scenario_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            story.append(table)
        
        return story

    def create_action_plan_section(self, plano):
        """Create action plan section"""
        story = []
        
        story.append(Paragraph("PLANO DE AÇÃO", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        for i, fase in enumerate(plano, 1):
            if isinstance(fase, dict):
                story.append(Paragraph(f"FASE {i}: {str(fase.get('fase', 'N/A'))}", self.styles['SectionHeader']))
                story.append(Paragraph(f"<b>Duração:</b> {str(fase.get('duracao', 'N/A'))}", self.styles['BodyText']))
                story.append(Spacer(1, 15))
        
        return story

    def create_insights_section(self, insights):
        """Create insights section"""
        story = []
        
        story.append(Paragraph("INSIGHTS EXCLUSIVOS", self.styles['CustomTitle']))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1e40af')))
        story.append(Spacer(1, 20))
        
        for i, insight in enumerate(insights, 1):
            story.append(Paragraph(f"<b>Insight {i}:</b> {str(insight)}", self.styles['Highlight']))
            story.append(Spacer(1, 10))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#1e40af')))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Relatório gerado pela Arqueologia do Avatar com IA", self.styles['BodyText']))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['BodyText']))
        
        return story

@pdf_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF report from analysis data"""
    try:
        analysis_data = request.get_json()
        
        if not analysis_data:
            logger.error("Dados de análise não fornecidos")
            return jsonify({'error': 'Dados de análise não fornecidos'}), 400
        
        logger.info("Iniciando geração de PDF...")
        
        # Generate PDF
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_report(analysis_data)
        
        logger.info("PDF gerado com sucesso")
        
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
