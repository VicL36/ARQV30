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
        canvas.drawString(inch, A4[1] - 0.75 * inch, "Relatório de Arqueologia de Avatar - ARQV30")

        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#666666'))
        canvas.drawString(A4[0] / 2, 0.75 * inch, f"Página {doc.page}")
        canvas.restoreState()

    def generate_pdf_report(self, data: dict, filename: str):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # Title Page
        story.append(Paragraph("Relatório Abrangente de Arqueologia de Avatar", self.styles["TitleStyle"])))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Desvendando a Essência do Seu Público com IA", self.styles["SubtitleStyle"])))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles["Caption"])))
        story.append(PageBreak())

        # Table of Contents (Placeholder - would be generated dynamically in a real app)
        story.append(Paragraph("Sumário", self.styles["Heading1"])))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("1. Introdução", self.styles["ListText"])))
        story.append(Paragraph("2. Visão Geral do ARQV30", self.styles["ListText"])))
        story.append(Paragraph("3. Análise de Mercado e Posicionamento Competitivo", self.styles["ListText"])))
        story.append(Paragraph("4. Detalhamento do Avatar", self.styles["ListText"])))
        story.append(Paragraph("5. Insights de Marketing Acionáveis", self.styles["ListText"])))
        story.append(Paragraph("6. Conclusão e Recomendações", self.styles["ListText"])))
        story.append(PageBreak())

        # Introduction
        story.append(Paragraph("1. Introdução", self.styles["Heading1"])))
        story.append(Paragraph("O ARQV30 é uma aplicação inovadora que se propõe a revolucionar a forma como empresas e profissionais compreendem seu público-alvo, utilizando o conceito de \"Arqueologia de Avatar\". Diferente das abordagens tradicionais de criação de personas, que muitas vezes dependem de dados demográficos superficiais ou de entrevistas limitadas, o ARQV30 emprega Inteligência Artificial avançada, especificamente o modelo Gemini Pro, para realizar uma análise profunda de dados textuais e visuais. O objetivo é desvendar camadas ocultas de significado, contexto cultural, arquétipos e padrões comportamentais, culminando na construção de um avatar digital altamente detalhado e multifacetado. Este relatório visa apresentar uma análise aprofundada do ARQV30, seu funcionamento, posicionamento no mercado, e seu vasto potencial para impulsionar estratégias de marketing e desenvolvimento de produtos.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.2 * inch))

        # General Overview of ARQV30
        story.append(Paragraph("2. Visão Geral do ARQV30", self.styles["Heading1"])))
        story.append(Paragraph("O ARQV30 é construído sobre uma arquitetura robusta, utilizando Flask como framework web, Supabase para gerenciamento de banco de dados e autenticação, e o modelo Gemini Pro para as capacidades de IA. A aplicação é modular, com blueprints dedicados para diferentes funcionalidades, o que facilita a manutenção e a escalabilidade.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("2.1. Componentes Chave:", self.styles["Heading2"])))
        story.append(Paragraph("\u2022 \u00a0`main.py` (Aplicação Principal): Responsável pela inicialização da aplicação Flask, configuração do CORS, conexão com o banco de dados Supabase e registro dos blueprints. Serve arquivos estáticos (HTML, CSS, JS) para a interface do usuário.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0`database.py` (Gerenciamento de Banco de Dados): Contém a configuração e a instância do SQLAlchemy para interação com o Supabase, permitindo a persistência dos dados de análise e usuários.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0`services/gemini_client.py` (Cliente Gemini): Encapsula a lógica de comunicação com a API do Gemini Pro, sendo o coração da capacidade analítica do ARQV30. Permite o envio de prompts e o recebimento de respostas do modelo de IA.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0`routes/user.py` (Rotas de Usuário): Gerencia a autenticação e o registro de usuários, garantindo um ambiente seguro e personalizado para cada usuário.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0`routes/analysis.py` (Rotas de Análise de Arqueologia): Este é o módulo central onde a \"mágica\" da arqueologia de avatar acontece. Ele orquestra uma série de chamadas ao Gemini Pro para realizar análises em várias etapas. Também gerencia o armazenamento e a recuperação dos resultados de análise no Supabase.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0`routes/pdf_generator.py` (Rotas de Geração de PDF): Responsável por gerar relatórios em formato PDF a partir dos dados de análise. Utiliza a biblioteca ReportLab para criar documentos formatados.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("2.2. Fluxo de Análise de Arqueologia de Avatar:", self.styles["Heading2"])))
        story.append(Paragraph("O processo de \"Arqueologia de Avatar\" no ARQV30 é uma sequência de etapas inteligentes, onde cada fase aprofunda a compreensão do avatar com base nas informações geradas anteriormente. Este fluxo iterativo e cumulativo é o que confere ao ARQV30 sua capacidade de gerar insights ricos e detalhados. As etapas incluem:", self.styles["BodyText"])))
        story.append(Paragraph("1. \u00a0Análise Inicial: O Gemini Pro realiza uma primeira varredura do texto ou imagem fornecidos, identificando elementos chave, contexto cultural, período aproximado e possíveis significados. Esta etapa estabelece a base para as análises subsequentes.", self.styles["ListText"])))
        story.append(Paragraph("2. \u00a0Contexto Cultural Aprofundado: Com base na análise inicial, o Gemini aprofunda-se no contexto cultural do avatar. Isso inclui informações sobre rituais, crenças, organização social e artefatos relevantes, fornecendo uma base antropológica para a persona.", self.styles["ListText"])))
        story.append(Paragraph("3. \u00a0Identificação de Arquétipos e Símbolos: Nesta fase, o modelo de IA identifica arquétipos (padrões universais de comportamento e personalidade) e símbolos presentes nos dados, interpretando seus significados e como eles se manifestam no avatar. Isso adiciona uma dimensão psicológica e mitológica à análise.", self.styles["ListText"])))
        story.append(Paragraph("4. \u00a0Padrões Comportamentais e Insights Psicológicos: O Gemini Pro descreve padrões comportamentais e insights psicológicos do avatar, correlacionando-os com o contexto cultural e os arquétipos identificados. Esta etapa ajuda a prever como o avatar pode reagir a diferentes estímulos e situações.", self.styles["ListText"])))
        story.append(Paragraph("5. \u00a0Construção da Narrativa do Avatar: Uma das funcionalidades mais poderosas do ARQV30 é a criação de uma narrativa envolvente e detalhada para o avatar. Esta história inclui sua trajetória, motivações, desafios e potencial evolução, transformando a persona em um personagem vivo e compreensível.", self.styles["ListText"])))
        story.append(Paragraph("6. \u00a0Geração de Descrição Visual: A partir da narrativa e de todas as análises anteriores, o Gemini gera uma descrição visual detalhada do avatar. Esta descrição é rica em elementos como vestimenta, ambiente, expressões faciais, cores e estilo artístico, sendo ideal para a criação de representações visuais do avatar (por exemplo, com ferramentas de geração de imagem).", self.styles["ListText"])))
        story.append(Paragraph("7. \u00a0Insights de Marketing Acionáveis: O ARQV30 vai além da compreensão da persona, fornecendo insights de marketing práticos. Isso inclui sugestões de canais de comunicação, mensagens-chave, produtos/serviços relevantes e estratégias de engajamento específicas para o avatar.", self.styles["ListText"])))
        story.append(Paragraph("8. \u00a0Análise de Concorrentes (Placeholder): Atualmente, esta etapa é um placeholder, indicando a intenção de identificar potenciais concorrentes e suas estratégias com base nos insights de marketing. Este é um ponto crucial para expansão futura, conforme abordado na seção de oportunidades.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("2.3. Outras Funcionalidades:", self.styles["Heading2"])))
        story.append(Paragraph("\u2022 \u00a0Histórico de Análises: Permite que os usuários visualizem e gerenciem todas as análises de arqueologia de avatar realizadas.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0Métricas: Fornece dados sobre o uso da ferramenta, como o número total de análises e análises por período.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0Geração de Relatórios: Capacidade de gerar relatórios completos ou resumidos em formato Markdown (e futuramente PDF aprimorado), consolidando todos os insights gerados.", self.styles["ListText"])))
        story.append(PageBreak())

        # Market Analysis and Competitive Positioning
        story.append(Paragraph("3. Análise de Mercado e Posicionamento Competitivo", self.styles["Heading1"])))
        story.append(Paragraph("O mercado de ferramentas de IA e análise de dados está em constante evolução, com diversas soluções que, de alguma forma, tangenciam a proposta do ARQV30. Para entender o posicionamento único do ARQV30, é fundamental analisar seus concorrentes diretos e indiretos.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("3.1. Concorrentes Indiretos / Parceiros Potenciais: Ferramentas de Geração de Vídeo com Avatares de IA", self.styles["Heading2"])))
        story.append(Paragraph("Essas ferramentas focam na criação visual de avatares e vídeos, um processo que pode ser alimentado pelas descrições visuais geradas pelo ARQV30. Elas não realizam a análise profunda de persona, mas são cruciais para a materialização do avatar.", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**HeyGen:** Líder em geração de vídeo com IA, oferece avatares realistas, suporte multilíngue, clonagem de voz e uma vasta biblioteca de templates. Seu foco é a produção de conteúdo de vídeo de alta qualidade com avatares falantes. É um concorrente no sentido de que também lida com avatares, mas complementar na medida em que o ARQV30 pode fornecer o \"cérebro\" por trás do avatar visual.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Hour One:** Especializado em criação de vídeo consistente e de marca em escala, com tecnologia Gen-AI e produção de conteúdo multilíngue. Ideal para equipes que buscam escalar a produção de vídeo com avatares virtuais. Similar ao HeyGen em sua proposta, mas com um foco ligeiramente diferente em automação e escala.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Colossyan:** Destaca-se pela simplicidade e eficiência na criação de vídeos profissionais com avatares de IA. Oferece diversos avatares, idiomas, vozes e um recurso de \"Instant Avatar\" que cria representações digitais a partir de filmagens. Sua facilidade de uso é um diferencial.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Kreado AI:** Um gerador de vídeo AI gratuito com uma vasta gama de avatares digitais (mais de 1000) e vozes de IA (mais de 1600), além de suporte a 140 idiomas. Permite a criação de avatares personalizados e a transformação de texto em retratos de IA. Seu diferencial é a grande variedade e a gratuidade.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Akool Avatar:** Focado na criação de avatares digitais altamente realistas e dinâmicos para marketing visual. Possui mais de 80 avatares, suporte multilíngue, integração com LLMs e rastreamento facial sofisticado. Sua ênfase no realismo e na integração com LLMs o torna um player forte no segmento de avatares visuais.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("3.2. Concorrentes Diretos / Complementares: Ferramentas de Criação de Persona Digital", self.styles["Heading2"])))
        story.append(Paragraph("Estas ferramentas visam a criação de personas de usuário ou comprador, o que é o objetivo final da \"arqueologia de avatar\" do ARQV30. A principal diferença é que o ARQV30 utiliza IA para *derivar* a persona de dados brutos, enquanto a maioria dessas ferramentas é mais manual ou baseada em questionários.", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Miro (Ferramenta para Criar Personas Online):** Uma plataforma de colaboração visual que oferece templates para criação de personas. Embora útil, requer entrada manual de dados e não possui a capacidade de análise profunda do ARQV30.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**UXPressia (Criador de Personas Online):** Ferramenta dedicada com modelos variados para criação de personas. Oferece uma interface amigável, mas o processo é predominantemente manual.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Geradores de Personas (Rock Content & Maikon.biz):** Ferramentas gratuitas que auxiliam na definição da persona através de questionários. Algumas incorporam IA para sugestões, mas não realizam a \"arqueologia\" de dados brutos como o ARQV30.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Delve AI:** Uma das ferramentas mais alinhadas com a proposta do ARQV30, pois oferece soluções full-stack orientadas por dados que geram automaticamente personas. Seu diferencial é a abordagem mais automatizada e baseada em dados, o que a torna um concorrente direto no aspecto de automação da criação de personas.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("3.3. Posicionamento Único do ARQV30", self.styles["Heading2"])))
        story.append(Paragraph("O ARQV30 se destaca no mercado por sua abordagem de \"arqueologia\" baseada em IA. Enquanto as ferramentas de geração de vídeo com avatares focam na *materialização visual* e as ferramentas de criação de persona focam na *estruturação de dados existentes* (muitas vezes manuais), o ARQV30 se concentra na *análise profunda e na descoberta de insights* a partir de dados brutos (texto e imagem). Ele não apenas cria uma persona, mas desvenda as camadas subjacentes que a compõem, oferecendo uma compreensão holística.", self.styles["BodyText"])))
        story.append(Paragraph("**Pontos Fortes Competitivos do ARQV30:**", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Análise Profunda com IA (Gemini Pro):** A capacidade de ir além da superfície, explorando contexto cultural, arquétipos e padrões comportamentais de forma automatizada, é um diferencial significativo. Isso permite insights que seriam difíceis ou demorados de obter manualmente.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Geração de Narrativa e Descrição Visual:** A criação de uma história completa para o avatar e uma descrição visual detalhada facilita a comunicação da persona e a criação de ativos de marketing, preenchendo a lacuna entre a análise e a aplicação prática.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Insights de Marketing Acionáveis:** A ferramenta não se limita a descrever o avatar, mas oferece sugestões práticas sobre como alcançá-lo, o que é de grande valor para equipes de marketing.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Potencial de Integração:** O ARQV30 pode atuar como uma ferramenta estratégica que alimenta tanto a criação de personas tradicionais quanto a geração de avatares visuais em outras plataformas, posicionando-o como um elo valioso na cadeia de valor do marketing digital.", self.styles["ListText"])))
        story.append(Paragraph("**Oportunidades de Mercado para o ARQV30:**", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Integração Direta com Ferramentas de Geração de Avatar:** Desenvolver APIs ou plugins para integrar diretamente as descrições visuais do ARQV30 com plataformas como HeyGen, Hour One ou Akool Avatar. Isso criaria um fluxo de trabalho contínuo da análise à criação visual.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Visualização de Dados Aprimorada:** Investir em dashboards interativos e gráficos que visualizem os insights gerados, tornando o relatório ainda mais impactante e fácil de consumir.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Expansão da Análise de Concorrentes:** Aprofundar a funcionalidade de análise de concorrentes, permitindo que o ARQV30 não apenas identifique, mas também analise as estratégias, pontos fortes e fracos dos concorrentes, oferecendo uma vantagem competitiva ainda maior.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Segmentação Avançada de Público:** Incorporar funcionalidades que permitam aos usuários segmentar ainda mais seus públicos-alvo com base nos avatares gerados, identificando nichos e micro-segmentos.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Personalização em Escala:** Explorar o uso dos avatares gerados para personalizar campanhas de marketing em larga escala, desde e-mails até anúncios digitais.", self.styles["ListText"])))
        story.append(PageBreak())

        # Avatar Detailing
        story.append(Paragraph("4. Detalhamento do Avatar: Aprofundando a Compreensão da Persona", self.styles["Heading1"])))
        story.append(Paragraph("O coração do ARQV30 reside em sua capacidade de construir avatares digitais com uma profundidade sem precedentes. Um avatar detalhado vai muito além de dados demográficos superficiais, mergulhando em aspectos psicológicos, comportamentais, motivacionais e contextuais. A metodologia do ARQV30, impulsionada pelo Gemini Pro, permite desvendar essas camadas complexas. Abaixo, revisitamos e expandimos os elementos essenciais de um perfil de avatar completo, ilustrando como o ARQV30 pode gerar esses insights.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("4.1. Dimensões de um Avatar Abrangente", self.styles["Heading2"])))
        story.append(Paragraph("Para construir um avatar verdadeiramente útil, o ARQV30 foca nas seguintes dimensões:", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Dados Demográficos e Socioeconômicos:** Embora básicos, são o ponto de partida. O ARQV30 pode inferir esses dados a partir de textos e imagens, como idade aparente, gênero, localização (se mencionada), e até mesmo estimativas de renda ou ocupação com base no vocabulário e no estilo de vida descritos. Por exemplo, a menção a \"startup de e-commerce\" e \"pós-graduação em Marketing Digital\" para a Ana Paula (exemplo fictício) permite inferir um nível educacional e ocupacional elevado.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Psicografia e Comportamento:** Esta é uma área onde o Gemini Pro brilha. Ao analisar o texto e o contexto, o ARQV30 pode identificar:", self.styles["ListText"])))
        story.append(Paragraph("\u00a0\u00a0\u00a0\u00a0\u2022 \u00a0Interesses e Hobbies: Palavras-chave como \"viagens\", \"yoga\", \"culinária saudável\" revelam os interesses do avatar.", self.styles["ListText"])))
        story.append(Paragraph("\u00a0\u00a0\u00a0\u00a0\u2022 \u00a0Valores e Crenças: A análise de sentimentos e o reconhecimento de padrões em textos podem inferir valores como \"autenticidade\", \"sustentabilidade\" e \"empoderamento feminino\".", self.styles["ListText"])))
        story.append(Paragraph("\u00a0\u00a0\u00a0\u00a0\u2022 \u00a0Personalidade: O tone da comunicação, a escolha de palavras e a forma como o avatar reage a desafios podem indicar traços de personalidade como \"proativa\", \"ambiciosa\" ou \"analítica\".", self.styles["ListText"])))
        story.append(Paragraph("\u00a0\u00a0\u00a0\u00a0\u2022 \u00a0Estilo de Vida: Descrições de rotina, hábitos de consumo e lazer fornecem um panorama do estilo de vida. O ARQV30 pode inferir se o avatar busca \"otimizar o tempo\" ou é um \"consumidor consciente\".", self.styles["ListText"])))
        story.append(Paragraph("\u00a0\u00a0\u00a0\u00a0\u2022 \u00a0Comportamento Online e de Compra: A análise de menções a plataformas (Instagram, LinkedIn), tipos de conteúdo consumido (blogs de negócios, podcasts) e o processo de decisão de compra (pesquisa extensiva, valorização de reviews) são cruciais para estratégias de marketing digital.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Motivações e Desafios (Dores e Ganhos):** O ARQV30 é projetado para extrair as \"dores\" (problemas, frustrações, medos) e os \"ganhos\" (objetivos, aspirações, benefícios desejados) do avatar. Por exemplo, a \"dificuldade em escalar o negócio sem perder a essência artesanal\" e o desejo de \"inspirar outras mulheres a empreender\" são insights valiosos para a criação de mensagens que ressoem profundamente.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Contexto Cultural e Social:** A IA pode identificar referências culturais, sociais e regionais que moldam a perspectiva do avatar. Isso inclui influências culturais (artesanato brasileiro, tendências globais), círculo social (empreendedores, designers) e a sensibilidade a eventos e tendências (slow fashion, economia criativa).", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Narrativa e História do Avatar:** Esta é uma das entregas mais poderosas do ARQV30. Ao sintetizar todas as informações, o Gemini Pro constrói uma história coesa e envolvente, transformando um conjunto de dados em um \"personagem\" com trajetória, conflitos e aspirações. A narrativa da \"Ana Paula\" é um exemplo de como o ARQV30 pode criar uma história que humaniza a persona e facilita a empatia.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Descrição Visual:** A capacidade de gerar uma descrição visual detalhada é um diferencial. Ela permite que designers e equipes de marketing visualizem o avatar, facilitando a criação de representações gráficas precisas. Elementos como \"cabelos castanhos claros e ondulados\", \"roupas casuais-chiques\" e \"ambiente de trabalho moderno e iluminado\" são exemplos de como o ARQV30 traduz insights em diretrizes visuais.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("4.2. Aprofundando a Análise com o ARQV30: O Potencial da IA", self.styles["Heading2"])))
        story.append(Paragraph("Para maximizar o potencial do ARQV30 e aprofundar ainda mais a análise de avatar, as seguintes abordagens podem ser exploradas:", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Refinamento Contínuo dos Prompts:** A qualidade da saída da IA é diretamente proporcional à qualidade dos prompts. O ARQV30 pode implementar um sistema de feedback onde os usuários avaliam a relevância e a profundidade dos insights gerados, permitindo um ajuste fino dos prompts do Gemini Pro ao longo do tempo. Isso pode incluir a adição de instruções para explorar sub-arquétipos, nuances emocionais ou aprofundar em micro-tendências culturais.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Análise de Sentimento e Emoções:** Integrar módulos de análise de sentimento mais sofisticados pode permitir ao ARQV30 identificar não apenas o que o avatar pensa, mas como ele se sente em relação a diferentes tópicos, produtos ou situações. Isso adicionaria uma camada emocional crucial à persona.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Identificação de Gatilhos e Barreiras Comportamentais:** A IA pode ser treinada para identificar explicitamente os \"gatilhos\" que levam o avatar a tomar uma ação (por exemplo, uma necessidade não atendida, uma promoção, uma recomendação social) e as \"barreiras\" que o impedem (por exemplo, preço, falta de confiança, complexidade). Isso é fundamental para otimizar funis de marketing e vendas.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Cenários de Interação e Testes de Hipóteses:** O ARQV30 pode gerar pequenos cenários ou \"vinhetas\" que simulam como o avatar interagiria com um produto, serviço ou mensagem de marketing. Isso permitiria testar hipóteses sobre a eficácia de diferentes abordagens antes de implementá-las em larga escala.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Integração de Dados Multimodais:** Embora o ARQV30 já analise texto e imagem, a integração de outros tipos de dados (áudio, vídeo, dados de navegação, dados de CRM) poderia enriquecer ainda mais a análise, criando um avatar verdadeiramente 360 graus.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Personalização Dinâmica:** Com um avatar tão detalhado, o ARQV30 poderia ser a base para sistemas de personalização dinâmica, onde o conteúdo de um site, e-mail ou anúncio é adaptado em tempo real com base no perfil do avatar que está interagindo.", self.styles["ListText"])))
        story.append(PageBreak())

        # Report Generation
        story.append(Paragraph("5. Criação do Relatório Completo e Abrangente", self.styles["Heading1"])))
        story.append(Paragraph("Este relatório, em si, serve como um exemplo da profundidade e abrangência que o ARQV30 pode inspirar. Ele sintetiza as informações coletadas sobre o repositório, a análise de mercado e o detalhamento do avatar, apresentando-as de forma estruturada e informativa. A capacidade do ARQV30 de gerar relatórios completos é um de seus maiores ativos, permitindo que as empresas transformem dados brutos em insights acionáveis e comunicáveis.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("5.1. Estrutura e Conteúdo do Relatório", self.styles["Heading2"])))
        story.append(Paragraph("Um relatório gerado pelo ARQV30, ou inspirado por suas capacidades, deve incluir:", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Resumo Executivo:** Uma visão geral concisa dos principais achados e recomendações.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Introdução:** Contextualização do avatar e dos objetivos da análise.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Metodologia:** Explicação de como a \"arqueologia de avatar\" foi realizada, incluindo as etapas de análise da IA.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Perfil Detalhado do Avatar:** Apresentação de todas as dimensões do avatar (demográficas, psicográficas, motivacionais, culturais, narrativas e visuais).", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Insights de Marketing e Vendas:** Recomendações práticas para alcançar e engajar o avatar, incluindo canais, mensagens e ofertas.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Análise de Concorrentes e Posicionamento:** Como o avatar se relaciona com o cenário competitivo e como a empresa pode se diferenciar.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Oportunidades e Recomendações:** Sugestões para futuras ações baseadas nos insights do avatar.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Conclusão:** Síntese dos principais pontos e o valor agregado da análise.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Apêndices (Opcional):** Dados brutos, transcrições, imagens de referência, etc.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("5.2. Qualidade e Relevância", self.styles["Heading2"])))
        story.append(Paragraph("Para garantir que o relatório seja \"muito mais completo e relevante\" e \"impressione o cliente\", o ARQV30 deve focar em:", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Profundidade dos Insights:** Ir além do óbvio, revelando motivações subconscientes, barreiras ocultas e aspirações não expressas. A capacidade do Gemini Pro de processar e correlacionar grandes volumes de dados é fundamental aqui.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Acionabilidade:** Cada insight deve levar a uma recomendação prática. O relatório não deve apenas descrever o avatar, mas também indicar \"o que fazer\" com essa informação.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Narrativa Envolvente:** A apresentação dos dados deve ser feita de forma a contar uma história, tornando o avatar real e fácil de ser compreendido e internalizado pelas equipes.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Visualização de Dados:** A inclusão de gráficos, infográficos e representações visuais do avatar (geradas a partir da descrição visual) tornará o relatório mais atraente e compreensível.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Linguagem Profissional e Persuasiva:** O texto deve ser claro, conciso e persuasivo, utilizando uma linguagem que ressoe com o público-alvo (clientes, stakeholders).", self.styles["ListText"])))
        story.append(PageBreak())

        # Design and PDF Creation
        story.append(Paragraph("6. Design e Criação do PDF Profissional", self.styles["Heading1"])))
        story.append(Paragraph("Para que o relatório seja \"um documento de apresentação lindo\" com um \"layout e design muito melhor e aprimorado\", a fase de geração de PDF é crucial. O ARQV30 já possui um módulo `pdf_generator.py` que utiliza ReportLab, uma excelente base para aprimoramento.", self.styles["BodyText"])))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("6.1. Princípios de Design para um PDF Impactante", self.styles["Heading2"])))
        story.append(Paragraph("\u2022 \u00a0**Identidade Visual Consistente:** Utilizar cores, fontes e elementos gráficos que reflitam a marca do cliente ou a identidade do ARQV30. Um manual de estilo pode ser criado para garantir essa consistência.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Layout Limpo e Organizado:** Espaços em branco adequados, alinhamento preciso e hierarquia visual clara. Isso facilita a leitura e a compreensão.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Tipografia Apropriada:** Escolha de fontes legíveis e que transmitam a seriedade e a inovação da solução. Títulos, subtítulos e corpo de texto devem ter tamanhos e estilos distintos.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Uso Estratégico de Imagens e Gráficos:** As descrições visuais do avatar geradas pelo ARQV30 podem ser usadas para criar ilustrações ou fotos realistas do avatar, que seriam incorporadas ao PDF. Gráficos de barras, pizza ou linhas podem visualizar métricas e insights de forma eficaz.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Elementos Visuais de Destaque:** Caixas de texto para citações, ícones para destacar pontos-chave, linhas divisórias para separar seções. O uso de `HRFlowable` no ReportLab é um bom começo.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Navegação Facilitada:** Sumário interativo com links para as seções, cabeçalhos e rodapés consistentes com números de página.", self.styles["ListText"])))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("6.2. Aprimoramentos Técnicos para o `pdf_generator.py`", self.styles["Heading2"])))
        story.append(Paragraph("O módulo `pdf_generator.py` pode ser aprimorado para incorporar esses princípios de design:", self.styles["BodyText"])))
        story.append(Paragraph("\u2022 \u00a0**Templates de Layout:** Criar diferentes templates de layout para seções específicas (capa, sumário, perfil do avatar, insights de marketing, etc.). Isso permitiria uma maior flexibilidade e profissionalismo no design.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Incorporação de Imagens Geradas:** A descrição visual do avatar gerada pelo Gemini Pro pode ser usada como prompt para uma ferramenta de geração de imagem (como DALL-E, Midjourney ou Stable Diffusion). As imagens resultantes seriam então incorporadas ao PDF, tornando o avatar tangível. O ARQV30 já tem um placeholder para `generate_avatar_image`, que pode ser expandido para integrar uma API de geração de imagem real.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Gráficos Dinâmicos:** Utilizar bibliotecas Python como Matplotlib ou Plotly para gerar gráficos a partir dos dados de métricas e insights, e então incorporar esses gráficos como imagens no PDF.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Estilos Personalizados:** Expandir o uso de `ParagraphStyle` e `TableStyle` no ReportLab para criar estilos mais sofisticados para títulos, subtítulos, corpo de texto, listas e tabelas. Isso inclui controle sobre cores, fontes, espaçamento e alinhamento.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Cores e Paletas:** Definir uma paleta de cores coesa usando `HexColor` e aplicá-la consistentemente em todo o documento.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Sumário e Links Internos:** Implementar a geração automática de um sumário com links clicáveis para as seções do relatório, melhorando a experiência do usuário.", self.styles["ListText"])))
        story.append(Paragraph("\u2022 \u00a0**Cabeçalhos e Rodapés:** Personalizar cabeçalhos e rodapés com o título do relatório, número da página e, talvez, o logo do ARQV30 ou do cliente.", self.styles["ListText"])))
        story.append(PageBreak())

        # Conclusion
        story.append(Paragraph("7. Conclusão e Próximos Passos", self.styles["Heading1"])))
        story.append(Paragraph("O ARQV30 representa um avanço significativo na compreensão do público-alvo através da \"Arqueologia de Avatar\" impulsionada por IA. Sua capacidade de extrair insights profundos, construir narrativas envolventes e gerar descrições visuais detalhadas o posiciona como uma ferramenta estratégica valiosa para qualquer empresa que busque uma conexão mais autêntica e eficaz com seus clientes.", self.styles["BodyText"])))
        story.append(Paragraph("Para maximizar seu impacto e \"surpreender o cliente\", os próximos passos devem focar em:", self.styles["BodyText"])))
        story.append(Paragraph("1. \u00a0**Aprimoramento Contínuo da Análise de IA:** Refinar os prompts do Gemini Pro e explorar novas dimensões de análise (sentimento, gatilhos, cenários de interação).", self.styles["ListText"])))
        story.append(Paragraph("2. \u00a0**Expansão da Análise de Concorrentes:** Transformar o placeholder atual em uma funcionalidade robusta que forneça insights competitivos detalhados.", self.styles["ListText"])))
        story.append(Paragraph("3. \u00a0**Integração com Ferramentas de Geração de Imagem:** Conectar a descrição visual do avatar a APIs de geração de imagem para criar representações visuais automáticas.", self.styles["ListText"])))
        story.append(Paragraph("4. \u00a0**Design Profissional do PDF:** Implementar os princípios de design e aprimoramentos técnicos no `pdf_generator.py` para criar documentos de apresentação visualmente deslumbrantes e altamente informativos.", self.styles["ListText"])))
        story.append(Paragraph("5. \u00a0**Visualização de Dados Interativa:** Desenvolver dashboards e gráficos que permitam aos usuários explorar os insights do avatar de forma dinâmica.", self.styles["ListText"])))
        story.append(Paragraph("Ao seguir estas diretrizes, o ARQV30 não apenas atenderá, mas superará as expectativas, entregando um valor inestimável na compreensão e engajamento do público-alvo. O potencial de \"surpreender\" o cliente reside na profundidade dos insights, na clareza da apresentação e na acionabilidade das recomendações, tudo isso impulsionado pela inteligência artificial de ponta.", self.styles["BodyText"])))

        try:
            doc.build(story, onAndAfterPage=self._add_header_and_footer)
            logger.info(f"Relatório PDF \'{filename}\' gerado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar o relatório PDF: {e}")
            return False

@pdf_bp.route("/generate", methods=["POST"])
def generate_pdf():
    data = request.json
    report_data = data.get("report_data")
    user_id = data.get("user_id")

    if not report_data or not user_id:
        return jsonify({"error": "Report data and user ID are required"}), 400

    try:
        generator = PDFReportGenerator()
        filename = f"relatorio_arqueologia_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        success = generator.generate_pdf_report(report_data, filename)

        if success:
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({"error": "Falha ao gerar o relatório PDF."}), 500
    except Exception as e:
        logger.error(f"Erro na rota de geração de PDF: {e}")
        return jsonify({"error": str(e)}), 500






