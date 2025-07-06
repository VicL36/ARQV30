import json
from flask import Blueprint, request, jsonify, render_template
import markdown2
from src.services import gemini_client
from src.database import SessionLocal
from src.models.analysis import Analysis
import logging

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyzes the given niche and returns the analysis result.
    """
    data = request.get_json()
    niche = data.get('niche')
    user_id = data.get('user_id')

    if not niche:
        return jsonify({'error': 'Niche is required'}), 400
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Prompt para a análise de nicho
        prompt = f"""
        Execute uma análise de avatar ultra-detalhada para o nicho de "{niche}".
        Siga exatamente esta estrutura de resposta JSON, sem adicionar ou remover campos e sem usar markdown no JSON:
        {{
          "analise_texto_formatado": "...",
          "escopo_ultra_detalhado": {{
            "segmento_principal": "...",
            "subsegmentos_identificados": ["...", "..."],
            "proposta_de_valor": "...",
            "tamanho_do_mercado": {{
              "tam": {{"label": "TAM", "valor": 0, "formatado": "R$ ..."}},
              "sam": {{"label": "SAM", "valor": 0, "formatado": "R$ ..."}},
              "som": {{"label": "SOM", "valor": 0, "formatado": "R$ ..."}}
            }}
          }},
          "avatar_ultra_detalhado": {{
            "persona_principal": {{
              "nome": "...",
              "idade": 0,
              "profissao": "...",
              "renda": "...",
              "localizacao": "...",
              "estado_civil": "...",
              "escolaridade": "..."
            }},
            "demografia_detalhada": {{
              "classes_sociais": [{{"name": "Classe A", "value": 0}}, {{"name": "Classe B", "value": 0}}, {{"name": "Classe C", "value": 0}}],
              "distribuicao_genero": [{{"name": "Mulheres", "value": 0}}, {{"name": "Homens", "value": 0}}],
              "distribuicao_geografica": [{{"name": "Sudeste", "value": 0}}, {{"name": "Sul", "value": 0}}, {{"name": "Nordeste", "value": 0}}, {{"name": "Centro-Oeste", "value": 0}}],
              "faixa_etaria_primaria": [{{"name": "32-45 anos", "value": 0}}, {{"name": "25-32 anos", "value": 0}}, {{"name": "Outros", "value": 100}}],
              "nivel_educacional": [{{"name": "Superior completo", "value": 0}}, {{"name": "Pós-graduação", "value": 0}}],
              "situacao_profissional": [{{"name": "Empreendedores", "value": 0}}, {{"name": "Profissionais liberais", "value": 0}}, {{"name": "Executivos", "value": 0}}]
            }}
          }},
          "psicografia_profunda": {{
            "valores_fundamentais": ["..."],
            "estilo_de_vida": "...",
            "aspiracoes_profissionais": ["..."],
            "medos_profundos": ["..."]
          }},
          "comportamento_digital": {{
            "plataformas_primarias": [{{"name": "Instagram", "time": "...", "icon": "Instagram"}}, {{"name": "LinkedIn", "time": "...", "icon": "Linkedin"}}],
            "conteudo_consumido": {{
              "formatos": ["..."],
              "temas": ["..."]
            }}
          }},
          "mapeamento_de_dores": {{
            "criticas": {{"titulo": "...", "intensidade": "...", "frequencia": "...", "impacto": "..."}},
            "importantes": {{"titulo": "...", "intensidade": "...", "frequencia": "..."}},
            "latentes": {{"titulo": "..."}}
          }},
          "analise_concorrencia": {{
            "concorrentes_diretos": [{{
              "nome": "...",
              "preco": "...",
              "proposta": "...",
              "share_mercado": 0,
              "pontos_fortes": ["..."],
              "pontos_fracos": ["..."]
            }}],
            "gaps_oportunidades": ["..."],
            "fatores_diferenciacao": ["..."]
          }},
          "inteligencia_mercado": {{
            "tendencias_crescimento": [{{"nome": "...", "impacto": "...", "timeline": "...", "oportunidade": "..."}}],
            "sazonalidade": {{"picos_demanda": ["..."], "baixas_demanda": ["..."]}},
            "tecnologias_emergentes": ["..."]
          }},
          "estrategia_palavras_chave": {{
            "palavras_chave_primarias": [{{"keyword": "...", "volume": 0, "cpc": 0.0, "competition": "..."}}],
            "palavras_long_tail": ["..."],
            "custos_plataforma": [
              {{"platform": "Facebook Ads", "cpc": 0.0, "cpm": 0, "cpa": 0}},
              {{"platform": "Google Ads", "cpc": 0.0, "cpm": 0, "cpa": 0}},
              {{"platform": "Instagram Ads", "cpc": 0.0, "cpm": 0, "cpa": 0}}
            ]
          }},
          "metricas_performance": {{
            "benchmarks_segmento": {{"cac_medio": 0, "ltv_medio": 0, "churn_rate": 0, "ticket_medio": 0}},
            "funil_conversao_otimizado": [
              {{"name": "Visitantes", "value": 10000}},
              {{"name": "Leads", "value": 0}},
              {{"name": "Oportunidades", "value": 0}},
              {{"name": "Vendas", "value": 0}}
            ],
            "kpis_criticos": [
              {{"nome": "CAC", "valor_ideal": "R$ ...", "como_medir": "...", "frequencia": "..."}},
              {{"nome": "LTV", "valor_ideal": "R$ ...", "como_medir": "...", "frequencia": "..."}},
              {{"nome": "ROI Marketing", "valor_ideal": "...%", "como_medir": "...", "frequencia": "..."}}
            ]
          }},
          "voz_mercado": {{
            "linguagem_avatar": {{"termos_tecnicos": ["..."], "palavras_poder": ["..."], "palavras_evitar": ["..."]}},
            "principais_objecoes": [{{"objecao": "...", "estrategia": "...", "frequencia": "..."}}],
            "gatilhos_mentais_efetivos": [{{"nome": "...", "aplicacao": "...", "efetividade": "..."}}]
          }},
          "projecoes_cenarios": {{
            "conservador": {{"taxa_conversao": "...", "faturamento_mensal": "R$ ...", "roi": "...", "break_even": "..."}},
            "realista": {{"taxa_conversao": "...", "faturamento_mensal": "R$ ...", "roi": "...", "break_even": "..."}},
            "otimista": {{"taxa_conversao": "...", "faturamento_mensal": "R$ ...", "roi": "...", "break_even": "..."}}
          }},
          "plano_acao_detalhado": [{{
            "fase": "...",
            "duracao": "...",
            "tarefas": [{{"nome": "...", "responsavel": "...", "prazo": "...", "recursos": "...", "metricas": "..."}}]
          }}],
          "insights_exclusivos": ["..."]
        }}
        O campo 'analise_texto_formatado' deve ser um texto longo e completo em markdown, formatado para um relatório, contendo todas as informações geradas, de forma discritiva e profissional.
        Todos os outros campos devem ser preenchidos com dados realistas e relevantes para o nicho de "{niche}".
        """
        
        gemini_response = gemini_client.generate_analysis(prompt)
        
        # Log da resposta bruta da Gemini para depuração
        logging.info(f"Gemini raw response for niche '{niche}': {gemini_response}")

        analysis_data = json.loads(gemini_response)
        
        # Salva a análise completa no banco de dados
        db = SessionLocal()
        try:
            analysis = Analysis(user_id=user_id, niche=niche, report_data=analysis_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            analysis_id = analysis.id
        finally:
            db.close()

        # Prepara a resposta para o frontend
        analysis_html = markdown2.markdown(analysis_data.get("analise_texto_formatado", "Nenhuma análise de texto foi gerada."))

        return jsonify({
            'analysis_html': analysis_html, 
            'analysis_id': analysis_id,
            'analysis_data': analysis_data  # Envia os dados brutos para o frontend
        })

    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError for niche '{niche}': {e}")
        logging.error(f"Malformed Gemini response was: {gemini_response}")
        return jsonify({'error': 'Falha ao decodificar a resposta da IA. A resposta não é um JSON válido.'}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred for niche '{niche}': {e}")
        return jsonify({'error': 'Ocorreu um erro inesperado ao processar sua solicitação.'}), 500


@analysis_bp.route('/generate_dashboard', methods=['POST'])
def generate_dashboard_route():
    """
    Generates an interactive dashboard HTML from analysis data.
    """
    analysis_data = request.get_json()
    if not analysis_data:
        return jsonify({'error': 'Analysis data is required'}), 400

    # Este prompt instrui a IA a criar um arquivo HTML autônomo.
    prompt = f"""
    **Persona:** Você é um desenvolvedor front-end especialista em HTML, CSS, e JavaScript, com foco em visualização de dados. Sua tarefa é transformar um objeto JSON de análise de mercado em um dashboard interativo, visualmente atraente, contido em um **único arquivo HTML**.

    **Objetivo Principal:** Criar um arquivo HTML completo e funcional que renderize os dados do objeto JSON fornecido em um dashboard informativo. O arquivo não deve ter dependências externas de arquivos (todo CSS e JS deve estar inline ou via CDN).

    **Tecnologias Obrigatórias:**
    * **Estilização:** Tailwind CSS (via CDN: https://cdn.tailwindcss.com)
    * **Gráficos:** Chart.js (via CDN: https://cdn.jsdelivr.net/npm/chart.js)
    * **Ícones:** Use SVGs inline do Lucide (ex: copie o código SVG de https://lucide.dev/icons/) para os ícones dos cards. Não use bibliotecas de ícones.

    **Instruções Detalhadas:**

    1.  **Estrutura do HTML:**
        * Crie um documento HTML5 padrão.
        * Inclua as CDNs do Tailwind CSS e Chart.js no `<head>`.
        * O layout do corpo (`<body>`) deve ser responsivo, usando um grid (CSS Grid ou Flexbox com classes do Tailwind) que se assemelhe a um layout de 3 colunas em telas grandes e uma única coluna em telas pequenas.
        * Implemente um modo claro e escuro, com um botão para alternar. O tema padrão deve ser escuro.

    2.  **Dados:**
        * Incorpore o objeto JSON com os dados da análise diretamente em uma tag `<script>` dentro do HTML, atribuindo-o a uma variável JavaScript: `const analysisData = {json.dumps(analysis_data, ensure_ascii=False)};`.

    3.  **Visualização dos Dados:**
        * Use os dados da variável `analysisData` para popular dinamicamente o dashboard.
        * Crie "Cards" (divs estilizadas com fundo escuro no modo padrão, cantos arredondados e sombras) para cada seção principal dos dados.
        * **Gráficos (Chart.js):**
            * Use um gráfico de pizza (doughnut) para `distribuicao_genero`.
            * Use um gráfico de barras vertical (bar) para `faixa_etaria_primaria`.
            * Configure os gráficos para terem um visual moderno e legível no tema escuro (cores das fontes, grid, etc.).
        * Renderize TODAS as outras informações do objeto JSON de forma clara e organizada dentro dos cards apropriados (Persona, Psicografia, Dores, Concorrência, Métricas, etc.), usando ícones SVG inline para ilustrar os títulos dos cards.

    4.  **Código Final:**
        * O resultado final deve ser um **único e completo arquivo HTML**.
        * O JavaScript para criar os gráficos e manipular o DOM deve estar dentro de uma tag `<script>` no final do `<body>`.
        * O código deve ser limpo e comentado. Não inclua a persona ou as instruções no código final, apenas o HTML.
    """

    try:
        dashboard_html = gemini_client.generate_analysis(prompt)
        # Limpa a resposta da IA para garantir que seja apenas HTML
        if "```html" in dashboard_html:
            dashboard_html = dashboard_html.split("```html")[1].split("```")[0]
        
        return jsonify({'dashboard_html': dashboard_html})
    except Exception as e:
        logging.error(f"An unexpected error occurred during dashboard generation: {e}")
        return jsonify({'error': 'Ocorreu um erro inesperado ao gerar o dashboard.'}), 500
