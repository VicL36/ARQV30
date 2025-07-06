import os
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, blue, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
import logging

logger = logging.getLogger(__name__)

pdf_bp = Blueprint("pdf", __name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configure estilos personalizados para o PDF"""
        # Estilos de título
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=HexColor('#1a365d'),
            fontName='Helvetica-Bold',
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubtitleStyle',
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=HexColor('#2d3748'),
            fontName='Helvetica',
            spaceAfter=30
        ))
        
        # Estilos de cabeçalho
        self.styles.add(ParagraphStyle(
            name='Heading1',
            fontSize=16,
            leading=20,
            textColor=HexColor('#0056b3'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2',
            fontSize=14,
            leading=18,
            textColor=HexColor('#007bff'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading3',
            fontSize=12,
            leading=16,
            textColor=HexColor('#0056b3'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilos de texto
        self.styles.add(ParagraphStyle(
            name='BodyText',
            fontSize=11,
            leading=14,
            textColor=HexColor('#2d3748'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ListText',
            fontSize=11,
            leading=14,
            textColor=HexColor('#2d3748'),
            leftIndent=20,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Quote',
            fontSize=10,
            leading=14,
            textColor=HexColor('#4a5568'),
            leftIndent=30,
            rightIndent=30,
            spaceBefore=10,
            spaceAfter=10,
            backColor=HexColor('#f7fafc'),
            borderPadding=10,
            borderColor=HexColor('#e2e8f0'),
            borderWidth=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='Caption',
            fontSize=9,
            leading=12,
            textColor=HexColor('#718096'),
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Highlight',
            fontSize=11,
            leading=14,
            textColor=HexColor('#2d3748'),
            backColor=HexColor('#e6fffa'),
            borderPadding=8,
            spaceAfter=8,
            fontName='Helvetica'
        ))

    def _add_header_and_footer(self, canvas, doc):
        """Adiciona cabeçalho e rodapé às páginas"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#0056b3'))
        canvas.drawString(inch, A4[1] - 0.75 * inch, "Relatório de Arqueologia de Avatar - ARQV30")
        
        # Linha do cabeçalho
        canvas.setStrokeColor(HexColor('#e2e8f0'))
        canvas.setLineWidth(1)
        canvas.line(inch, A4[1] - 0.85 * inch, A4[0] - inch, A4[1] - 0.85 * inch)
        
        # Rodapé
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#718096'))
        canvas.drawCentredText(A4[0] / 2, 0.75 * inch, f"Página {doc.page}")
        canvas.drawString(inch, 0.75 * inch, f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        
        # Linha do rodapé
        canvas.line(inch, 0.85 * inch, A4[0] - inch, 0.85 * inch)
        
        canvas.restoreState()

    def _create_summary_table(self, data):
        """Cria tabela resumo com dados principais"""
        table_data = [
            ['Elemento', 'Descrição'],
            ['Avatar Principal', data.get('avatar_name', 'Não informado')],
            ['Contexto Cultural', data.get('cultural_context', 'Não informado')[:100] + '...'],
            ['Arquétipo Principal', data.get('main_archetype', 'Não informado')],
            ['Padrão Comportamental', data.get('behavioral_pattern', 'Não informado')[:100] + '...'],
        ]
        
        table = Table(table_data, colWidths=[3*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0056b3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table

    def generate_pdf_report(self, data: dict, filename: str = None):
        """Gera relatório PDF completo"""
        if not filename:
            filename = f"relatorio_arqueologia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Usar BytesIO para criar PDF em memória
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)
        story = []

        # Página de título
        story.append(Paragraph("Relatório de Arqueologia de Avatar", self.styles['TitleStyle']))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Análise Profunda de Persona com Inteligência Artificial", self.styles['SubtitleStyle']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Informações do relatório
        story.append(Paragraph(f"<b>Data de Geração:</b> {datetime.now().strftime('%d de %B de %Y')}", self.styles['BodyText']))
        story.append(Paragraph(f"<b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}", self.styles['BodyText']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Linha decorativa
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#0056b3')))
        story.append(PageBreak())

        # Sumário executivo
        story.append(Paragraph("Sumário Executivo", self.styles['Heading1']))
        story.append(Paragraph("Este relatório apresenta uma análise detalhada do avatar identificado através da metodologia de Arqueologia de Avatar, utilizando técnicas avançadas de Inteligência Artificial para revelar insights profundos sobre comportamentos, motivações e características do público-alvo.", self.styles['BodyText']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Tabela resumo
        if data:
            story.append(self._create_summary_table(data))
        story.append(PageBreak())

        # Análise inicial
        if data.get('initial_analysis'):
            story.append(Paragraph("1. Análise Inicial", self.styles['Heading1']))
            story.append(Paragraph(data['initial_analysis'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Contexto cultural
        if data.get('cultural_context'):
            story.append(Paragraph("2. Contexto Cultural", self.styles['Heading1']))
            story.append(Paragraph(data['cultural_context'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Arquétipos e símbolos
        if data.get('archetypes_symbols'):
            story.append(Paragraph("3. Arquétipos e Símbolos", self.styles['Heading1']))
            story.append(Paragraph(data['archetypes_symbols'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Padrões comportamentais
        if data.get('behavioral_patterns'):
            story.append(Paragraph("4. Padrões Comportamentais", self.styles['Heading1']))
            story.append(Paragraph(data['behavioral_patterns'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Narrativa do avatar
        if data.get('avatar_narrative'):
            story.append(Paragraph("5. Narrativa do Avatar", self.styles['Heading1']))
            story.append(Paragraph(data['avatar_narrative'], self.styles['Quote']))
            story.append(Spacer(1, 0.2 * inch))

        # Descrição visual
        if data.get('visual_description'):
            story.append(Paragraph("6. Descrição Visual", self.styles['Heading1']))
            story.append(Paragraph(data['visual_description'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Insights de marketing
        if data.get('marketing_insights'):
            story.append(Paragraph("7. Insights de Marketing", self.styles['Heading1']))
            story.append(Paragraph(data['marketing_insights'], self.styles['Highlight']))
            story.append(Spacer(1, 0.2 * inch))

        # Análise de concorrentes
        if data.get('competitor_analysis'):
            story.append(Paragraph("8. Análise de Concorrentes", self.styles['Heading1']))
            story.append(Paragraph(data['competitor_analysis'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

        # Conclusões e recomendações
        story.append(Paragraph("9. Conclusões e Recomendações", self.styles['Heading1']))
        story.append(Paragraph("Com base na análise realizada, recomendamos:", self.styles['BodyText']))
        story.append(Paragraph("• Implementar estratégias de marketing personalizadas baseadas nos insights identificados", self.styles['ListText']))
        story.append(Paragraph("• Desenvolver conteúdo que ressoe com os arquétipos e símbolos identificados", self.styles['ListText']))
        story.append(Paragraph("• Monitorar continuamente o comportamento do avatar para refinamento das estratégias", self.styles['ListText']))
        story.append(Paragraph("• Utilizar a descrição visual para criar materiais de marketing mais eficazes", self.styles['ListText']))

        # Rodapé final
        story.append(Spacer(1, 0.5 * inch))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0')))
        story.append(Paragraph("Relatório gerado pelo sistema ARQV30 - Arqueologia de Avatar", self.styles['Caption']))

        try:
            doc.build(story, onFirstPage=self._add_header_and_footer, onLaterPages=self._add_header_and_footer)
            buffer.seek(0)
            logger.info(f"Relatório PDF gerado com sucesso")
            return buffer
        except Exception as e:
            logger.error(f"Erro ao gerar o relatório PDF: {e}")
            raise

@pdf_bp.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """Endpoint para gerar PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        report_data = data.get("report_data", {})
        user_id = data.get("user_id", "anonymous")

        generator = PDFReportGenerator()
        filename = f"relatorio_arqueologia_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Gerar PDF em buffer
        pdf_buffer = generator.generate_pdf_report(report_data, filename)
        
        # Retornar arquivo
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro na geração do PDF: {str(e)}")
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500

@pdf_bp.route("/test-pdf", methods=["GET"])
def test_pdf():
    """Endpoint de teste para gerar PDF"""
    try:
        # Dados de teste
        test_data = {
            "avatar_name": "Avatar de Teste",
            "initial_analysis": "Esta é uma análise inicial de teste para verificar a geração do PDF.",
            "cultural_context": "Contexto cultural de teste com informações relevantes sobre o avatar.",
            "archetypes_symbols": "Arquétipos e símbolos identificados durante a análise.",
            "behavioral_patterns": "Padrões comportamentais observados no avatar analisado.",
            "avatar_narrative": "Esta é a narrativa do avatar, contando sua história e características principais.",
            "visual_description": "Descrição visual detalhada do avatar para criação de representações gráficas.",
            "marketing_insights": "Insights de marketing acionáveis baseados na análise do avatar.",
            "competitor_analysis": "Análise dos principais concorrentes e posicionamento no mercado."
        }
        
        generator = PDFReportGenerator()
        filename = f"teste_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        pdf_buffer = generator.generate_pdf_report(test_data, filename)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro no teste do PDF: {str(e)}")
        return jsonify({"error": f"Erro ao gerar PDF de teste: {str(e)}"}), 500

@pdf_bp.route("/health", methods=["GET"])
def health_check():
    """Endpoint de verificação de saúde"""
    return jsonify({"status": "ok", "service": "PDF Generator", "timestamp": datetime.now().isoformat()})
