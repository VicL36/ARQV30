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

pdf_bp = Blueprint("pdf", __name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='TitleStyle', fontSize=24, leading=28, alignment=TA_CENTER, textColor=HexColor('#333333')))
        self.styles.add(ParagraphStyle(name='SubtitleStyle', fontSize=18, leading=22, alignment=TA_CENTER, textColor=HexColor('#666666')))
        self.styles.add(ParagraphStyle(name='Heading1', fontSize=16, leading=20, textColor=HexColor('#0056b3'), spaceAfter=12, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='Heading2', fontSize=14, leading=18, textColor=HexColor('#007bff'), spaceAfter=10, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='BodyText', fontSize=10, leading=14, textColor=HexColor('#333333'), spaceAfter=6, alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle(name='Caption', fontSize=8, leading=10, textColor=HexColor('#999999'), alignment=TA_CENTER, spaceAfter=6))
        self.styles.add(ParagraphStyle(name='ListText', fontSize=10, leading=14, textColor=HexColor('#333333'), leftIndent=20))
        self.styles.add(ParagraphStyle(name='Quote', fontSize=10, leading=14, textColor=HexColor('#555555'), leftIndent=20, rightIndent=20, spaceBefore=10, spaceAfter=10, backColor=HexColor('#f0f0f0'), borderPadding=5))

    def _add_header_and_footer(self, canvas, doc):
        canvas.saveState()
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#0056b3'))
        canvas.drawString(inch, A4[1] - 0.75 * inch, "Relatório de Arqueologia de Avatar - UP Lançamentos")

        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#666666'))
        canvas.drawString(A4[0] / 2, 0.75 * inch, f"Página {doc.page}")
        canvas.restoreState()

    def generate_pdf_report(self, data: dict, filename: str):
        """Generate a comprehensive PDF report from analysis data"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # Extract data safely
        segmento = data.get('escopo', {}).get('segmento_principal', 'Segmento não especificado')
        avatar_data = data.get('avatar_ultra_detalhado', {})
        persona = avatar_data.get('persona_principal', {})
        
        # Title Page
        story.append(Paragraph("Relatório de Arqueologia de Avatar", self.styles["TitleStyle"]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Análise Ultra-Detalhada: {segmento}", self.styles["SubtitleStyle"]))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles["Caption"]))
        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph("Resumo Executivo", self.styles["Heading1"]))
        story.append(Paragraph(f"Este relatório apresenta uma análise ultra-detalhada do segmento {segmento}, utilizando inteligência artificial avançada e pesquisa em tempo real na internet. A análise revela insights profundos sobre o avatar ideal, estratégias de marketing e oportunidades de mercado.", self.styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

        # Avatar Profile
        if persona:
            story.append(Paragraph("Perfil do Avatar Principal", self.styles["Heading1"]))
            story.append(Paragraph(f"Nome: {persona.get('nome', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Idade: {persona.get('idade', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Profissão: {persona.get('profissao', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Renda: {persona.get('renda_mensal', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Localização: {persona.get('localizacao', 'N/A')}", self.styles["BodyText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Market Scope
        escopo = data.get('escopo', {})
        if escopo:
            story.append(Paragraph("Escopo de Mercado", self.styles["Heading1"]))
            story.append(Paragraph(f"Segmento Principal: {escopo.get('segmento_principal', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Produto Ideal: {escopo.get('produto_ideal', 'N/A')}", self.styles["BodyText"]))
            story.append(Paragraph(f"Proposta de Valor: {escopo.get('proposta_valor', 'N/A')}", self.styles["BodyText"]))
            
            tamanho_mercado = escopo.get('tamanho_mercado', {})
            if tamanho_mercado:
                story.append(Paragraph("Tamanho do Mercado:", self.styles["Heading2"]))
                story.append(Paragraph(f"TAM (Total Addressable Market): {tamanho_mercado.get('tam', 'N/A')}", self.styles["ListText"]))
                story.append(Paragraph(f"SAM (Serviceable Addressable Market): {tamanho_mercado.get('sam', 'N/A')}", self.styles["ListText"]))
                story.append(Paragraph(f"SOM (Serviceable Obtainable Market): {tamanho_mercado.get('som', 'N/A')}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Pain Points Analysis
        dores = data.get('mapeamento_dores_ultra_detalhado', {})
        if dores:
            story.append(Paragraph("Mapeamento de Dores", self.styles["Heading1"]))
            
            dores_criticas = dores.get('dores_nivel_1_criticas', [])
            if dores_criticas:
                story.append(Paragraph("Dores Críticas (Nível 1):", self.styles["Heading2"]))
                for dor in dores_criticas[:3]:  # Limit to top 3
                    if isinstance(dor, dict):
                        story.append(Paragraph(f"• {dor.get('dor', 'N/A')}", self.styles["ListText"]))
                        story.append(Paragraph(f"  Intensidade: {dor.get('intensidade', 'N/A')} | Frequência: {dor.get('frequencia', 'N/A')}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Marketing Strategy
        marketing = data.get('estrategia_palavras_chave', {})
        if marketing:
            story.append(Paragraph("Estratégia de Marketing", self.styles["Heading1"]))
            
            palavras_primarias = marketing.get('palavras_primarias', [])
            if palavras_primarias:
                story.append(Paragraph("Palavras-Chave Primárias:", self.styles["Heading2"]))
                for palavra in palavras_primarias[:5]:  # Top 5
                    if isinstance(palavra, dict):
                        story.append(Paragraph(f"• {palavra.get('termo', 'N/A')} - Volume: {palavra.get('volume_mensal', 'N/A')}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Competitive Analysis
        competicao = data.get('analise_concorrencia_detalhada', {})
        if competicao:
            story.append(Paragraph("Análise Competitiva", self.styles["Heading1"]))
            
            concorrentes = competicao.get('concorrentes_diretos', [])
            if concorrentes:
                story.append(Paragraph("Principais Concorrentes:", self.styles["Heading2"]))
                for concorrente in concorrentes[:3]:  # Top 3
                    if isinstance(concorrente, dict):
                        story.append(Paragraph(f"• {concorrente.get('nome', 'N/A')}", self.styles["ListText"]))
                        story.append(Paragraph(f"  Preço: {concorrente.get('preco_range', 'N/A')}", self.styles["ListText"]))
                        story.append(Paragraph(f"  Posicionamento: {concorrente.get('posicionamento', 'N/A')}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Action Plan
        plano_acao = data.get('plano_acao_detalhado', [])
        if plano_acao:
            story.append(Paragraph("Plano de Ação", self.styles["Heading1"]))
            for fase in plano_acao[:3]:  # Top 3 phases
                if isinstance(fase, dict):
                    story.append(Paragraph(f"{fase.get('fase', 'Fase')}", self.styles["Heading2"]))
                    story.append(Paragraph(f"Duração: {fase.get('duracao', 'N/A')}", self.styles["BodyText"]))
                    
                    acoes = fase.get('acoes', [])
                    if acoes:
                        for acao in acoes[:2]:  # Top 2 actions per phase
                            if isinstance(acao, dict):
                                story.append(Paragraph(f"• {acao.get('acao', 'N/A')}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Insights
        insights = data.get('insights_exclusivos', [])
        if insights:
            story.append(Paragraph("Insights Exclusivos", self.styles["Heading1"]))
            for i, insight in enumerate(insights[:5], 1):  # Top 5 insights
                story.append(Paragraph(f"{i}. {insight}", self.styles["ListText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Footer
        story.append(PageBreak())
        story.append(Paragraph("Conclusão", self.styles["Heading1"]))
        story.append(Paragraph("Esta análise ultra-detalhada fornece uma base sólida para o desenvolvimento de estratégias de marketing eficazes e o lançamento bem-sucedido do produto no mercado brasileiro.", self.styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Relatório gerado pela plataforma UP Lançamentos - Arqueologia do Avatar com IA", self.styles["Caption"]))

        try:
            doc.build(story, onFirstPage=self._add_header_and_footer, onLaterPages=self._add_header_and_footer)
            logger.info(f"Relatório PDF '{filename}' gerado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar o relatório PDF: {e}")
            return False

@pdf_bp.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """Generate PDF report from analysis data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        report_data = data.get("report_data", data)  # Accept both formats
        user_id = data.get("user_id", "anonymous")

        if not report_data:
            return jsonify({"error": "Dados do relatório são obrigatórios"}), 400

        generator = PDFReportGenerator()
        filename = f"relatorio_arqueologia_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create file in a temporary location
        temp_path = os.path.join("/tmp", filename)
        success = generator.generate_pdf_report(report_data, temp_path)

        if success and os.path.exists(temp_path):
            return send_file(
                temp_path, 
                as_attachment=True, 
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({"error": "Falha ao gerar o relatório PDF"}), 500

    except Exception as e:
        logger.error(f"Erro na rota de geração de PDF: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@pdf_bp.route("/generate", methods=["POST"])
def generate_pdf_legacy():
    """Legacy PDF generation endpoint for backward compatibility"""
    return generate_pdf()