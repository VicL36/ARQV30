import os
import json
import logging
import time
import re
import requests
from typing import Dict, List, Optional, Any
import concurrent.futures
from urllib.parse import quote_plus

# Import with error handling
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.warning("google-generativeai not available")

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logger.warning("beautifulsoup4 not available")

logger = logging.getLogger(__name__)

class GeminiClient:
    """Cliente avançado para Gemini Pro 2.5 com pesquisa na internet e análise ultra-detalhada"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY não encontrada - usando análise de fallback")
            self.model = None
            return
        
        if not genai:
            logger.warning("⚠️ google-generativeai não disponível - usando análise de fallback")
            self.model = None
            return
        
        try:
            # Configurar Gemini Pro
            genai.configure(api_key=self.api_key)
            
            # Usar o modelo mais avançado disponível
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",  # Usar modelo disponível
                generation_config={
                    "temperature": 0.6,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
            
            logger.info(f"🤖 Gemini Pro Client inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Gemini: {e}")
            self.model = None
    
    def search_internet(self, query: str, num_results: int = 10) -> List[Dict]:
        """Pesquisa na internet usando múltiplas fontes"""
        if not BeautifulSoup:
            logger.warning("BeautifulSoup não disponível para pesquisa na internet")
            return []
            
        try:
            # Usar DuckDuckGo para pesquisa (não requer API key)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('a', class_='result__a')[:num_results]:
                title = result.get_text(strip=True)
                url = result.get('href')
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': self._extract_snippet(url)
                    })
            
            logger.info(f"🔍 Encontrados {len(results)} resultados para: {query}")
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na pesquisa: {e}")
            return []
    
    def _extract_snippet(self, url: str) -> str:
        """Extrai snippet de uma URL"""
        if not BeautifulSoup:
            return ""
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Retornar primeiros 500 caracteres
            return text[:500] + "..." if len(text) > 500 else text
            
        except Exception:
            return ""
    
    def research_segment_comprehensive(self, segmento: str) -> Dict:
        """Pesquisa abrangente sobre o segmento"""
        research_queries = [
            f"{segmento} mercado brasileiro 2024 2025",
            f"{segmento} tendências consumidor comportamento",
            f"{segmento} concorrentes principais Brasil",
            f"{segmento} preços produtos serviços",
            f"{segmento} público alvo demographics",
            f"{segmento} marketing digital estratégias"
        ]
        
        research_data = {}
        
        # Pesquisa sequencial para evitar sobrecarga
        for query in research_queries:
            try:
                results = self.search_internet(query, 3)
                research_data[query] = results
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Erro na pesquisa '{query}': {e}")
                research_data[query] = []
        
        return research_data
    
    def analyze_avatar_ultra_detailed(self, data: Dict) -> Dict:
        """Análise ultra-detalhada do avatar com Gemini Pro e pesquisa na internet"""
        
        if not self.model:
            logger.info("🔄 Gemini não disponível, usando análise de fallback")
            return self._create_fallback_analysis(data)
        
        segmento = data.get('segmento', data.get('nicho', ''))
        
        try:
            logger.info(f"🔍 Iniciando análise para segmento: {segmento}")
            
            # Pesquisa na internet (opcional, pode falhar)
            research_data = {}
            try:
                research_data = self.research_segment_comprehensive(segmento)
            except Exception as e:
                logger.warning(f"Pesquisa na internet falhou: {e}")
            
            # Criar prompt ultra-detalhado
            prompt = self._create_ultra_detailed_prompt(data, research_data)
            
            logger.info("🤖 Processando análise com Gemini Pro...")
            
            # Gerar análise com Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.warning("⚠️ Resposta vazia do Gemini, usando fallback")
                return self._create_fallback_analysis(data)
            
            # Parse da resposta JSON
            try:
                # Limpar resposta para extrair JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                analysis = json.loads(response_text)
                logger.info("✅ Análise ultra-detalhada concluída com sucesso")
                
                # Adicionar metadados
                analysis['research_data'] = research_data
                analysis['generated_at'] = time.time()
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON do Gemini: {e}")
                logger.info("🔄 Usando análise de fallback")
                return self._create_fallback_analysis(data)
                
        except Exception as e:
            logger.error(f"❌ Erro na análise Gemini: {str(e)}")
            return self._create_fallback_analysis(data)
    
    def _create_ultra_detailed_prompt(self, data: Dict, research_data: Dict) -> str:
        """Cria prompt ultra-detalhado com dados de pesquisa"""
        
        segmento = data.get('segmento', data.get('nicho', ''))
        produto = data.get('produto', '')
        preco = data.get('preco', '')
        publico = data.get('publico', '')
        objetivo_receita = data.get('objetivo_receita', '')
        orcamento_marketing = data.get('orcamento_marketing', '')
        
        # Compilar dados de pesquisa
        research_summary = ""
        if research_data:
            for query, results in research_data.items():
                if results:
                    research_summary += f"\n\n**{query}:**\n"
                    for result in results[:2]:  # Top 2 resultados por query
                        research_summary += f"- {result['title']}: {result['snippet'][:150]}...\n"
        
        return f"""
Você é um consultor sênior especializado em arqueologia de avatar e análise de mercado no Brasil.

DADOS DO PRODUTO/SERVIÇO:
- Segmento: {segmento}
- Produto: {produto}
- Preço: R$ {preco}
- Público: {publico}
- Objetivo de Receita: R$ {objetivo_receita}
- Orçamento Marketing: R$ {orcamento_marketing}

DADOS DE PESQUISA:
{research_summary}

Crie uma análise ULTRA-DETALHADA do avatar ideal para este segmento no mercado brasileiro.

Retorne APENAS um JSON válido com esta estrutura exata:

{{
  "escopo": {{
    "segmento_principal": "{segmento}",
    "subsegmentos": ["Subsegmento 1", "Subsegmento 2", "Subsegmento 3"],
    "produto_ideal": "Nome do produto ideal",
    "proposta_valor": "Proposta de valor única",
    "tamanho_mercado": {{
      "tam": "R$ X bilhões",
      "sam": "R$ X milhões",
      "som": "R$ X milhões"
    }}
  }},
  "avatar_ultra_detalhado": {{
    "persona_principal": {{
      "nome": "Nome fictício",
      "idade": "Idade específica",
      "profissao": "Profissão específica",
      "renda_mensal": "Faixa de renda",
      "localizacao": "Cidade/região",
      "estado_civil": "Estado civil",
      "escolaridade": "Nível educacional"
    }},
    "demografia_detalhada": {{
      "faixa_etaria_primaria": "Faixa principal com %",
      "distribuicao_genero": "Distribuição por gênero",
      "distribuicao_geografica": "Distribuição por região",
      "classes_sociais": "Distribuição por classe",
      "nivel_educacional": "Distribuição educacional"
    }},
    "psicografia_profunda": {{
      "valores_fundamentais": ["Valor 1", "Valor 2", "Valor 3"],
      "estilo_vida_detalhado": "Descrição do dia a dia",
      "personalidade_dominante": "Traços de personalidade",
      "aspiracoes_profissionais": ["Aspiração 1", "Aspiração 2"],
      "medos_profundos": ["Medo 1", "Medo 2", "Medo 3"],
      "motivadores_principais": ["Motivador 1", "Motivador 2"]
    }}
  }},
  "mapeamento_dores_ultra_detalhado": {{
    "dores_nivel_1_criticas": [
      {{
        "dor": "Dor específica",
        "intensidade": "Alta/Média/Baixa",
        "frequencia": "Diária/Semanal/Mensal",
        "impacto_vida": "Como impacta",
        "nivel_consciencia": "Consciente/Semiconsciente"
      }}
    ],
    "dores_nivel_2_importantes": [
      {{
        "dor": "Segunda dor",
        "intensidade": "Alta/Média/Baixa",
        "frequencia": "Frequência",
        "impacto_vida": "Impacto",
        "nivel_consciencia": "Nível"
      }}
    ]
  }},
  "analise_concorrencia_detalhada": {{
    "concorrentes_diretos": [
      {{
        "nome": "Nome do concorrente",
        "preco_range": "Faixa de preço",
        "proposta_valor": "Proposta",
        "pontos_fortes": ["Força 1", "Força 2"],
        "pontos_fracos": ["Fraqueza 1", "Fraqueza 2"],
        "posicionamento": "Como se posiciona"
      }}
    ],
    "gaps_oportunidades": [
      "Gap 1",
      "Gap 2",
      "Gap 3"
    ]
  }},
  "estrategia_palavras_chave": {{
    "palavras_primarias": [
      {{
        "termo": "palavra-chave",
        "volume_mensal": "Volume",
        "dificuldade": "Alta/Média/Baixa",
        "cpc_estimado": "R$ X,XX",
        "oportunidade": "Alta/Média/Baixa"
      }}
    ],
    "custos_aquisicao_canal": {{
      "google_ads": {{
        "cpc_medio": "R$ X,XX",
        "ctr_esperado": "X%",
        "cpa_estimado": "R$ XXX"
      }},
      "facebook_ads": {{
        "cpc_medio": "R$ X,XX",
        "ctr_esperado": "X%",
        "cpa_estimado": "R$ XXX"
      }}
    }}
  }},
  "metricas_performance_detalhadas": {{
    "benchmarks_segmento": {{
      "cac_medio_segmento": "R$ XXX",
      "ltv_medio_segmento": "R$ X.XXX",
      "churn_rate_medio": "XX%",
      "ticket_medio_segmento": "R$ XXX"
    }},
    "kpis_criticos": [
      {{
        "metrica": "CAC",
        "valor_ideal": "R$ XXX",
        "como_medir": "Descrição"
      }}
    ]
  }},
  "projecoes_cenarios": {{
    "cenario_conservador": {{
      "taxa_conversao": "X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "roi": "XXX%"
    }},
    "cenario_realista": {{
      "taxa_conversao": "X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "roi": "XXX%"
    }},
    "cenario_otimista": {{
      "taxa_conversao": "X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "roi": "XXX%"
    }}
  }},
  "plano_acao_detalhado": [
    {{
      "fase": "Fase 1: Nome",
      "duracao": "X semanas",
      "acoes": [
        {{
          "acao": "Ação específica",
          "responsavel": "Quem executa",
          "prazo": "X dias"
        }}
      ]
    }}
  ],
  "insights_exclusivos": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ]
}}

IMPORTANTE: Retorne APENAS o JSON válido, sem explicações ou texto adicional.
"""
    
    def _create_fallback_analysis(self, data: Dict) -> Dict:
        """Cria análise de fallback quando Gemini falha"""
        segmento = data.get('segmento', data.get('nicho', 'Produto Digital'))
        produto = data.get('produto', 'Produto Digital')
        
        try:
            preco = float(data.get('preco_float', 0)) if data.get('preco_float') is not None else 997.0
        except (ValueError, TypeError):
            preco = 997.0
        
        logger.info(f"🔄 Criando análise de fallback para {segmento} - Preço: R$ {preco}")
        
        return {
            "escopo": {
                "segmento_principal": segmento,
                "subsegmentos": [f"{segmento} para iniciantes", f"{segmento} avançado", f"{segmento} empresarial"],
                "produto_ideal": produto,
                "proposta_valor": f"A metodologia mais completa e prática para dominar {segmento} no mercado brasileiro",
                "tamanho_mercado": {
                    "tam": "R$ 3,2 bilhões",
                    "sam": "R$ 480 milhões",
                    "som": "R$ 24 milhões"
                }
            },
            "avatar_ultra_detalhado": {
                "persona_principal": {
                    "nome": "Carlos Eduardo Silva",
                    "idade": "38 anos",
                    "profissao": f"Especialista em {segmento}",
                    "renda_mensal": "R$ 15.000 - R$ 35.000",
                    "localizacao": "São Paulo, SP",
                    "estado_civil": "Casado, 2 filhos",
                    "escolaridade": "Superior completo com pós-graduação"
                },
                "demografia_detalhada": {
                    "faixa_etaria_primaria": "32-45 anos (65%)",
                    "distribuicao_genero": "65% mulheres, 35% homens",
                    "distribuicao_geografica": "Sudeste (45%), Sul (25%), Nordeste (20%)",
                    "classes_sociais": "Classe A (30%), Classe B (60%), Classe C (10%)",
                    "nivel_educacional": "Superior completo (80%), Pós-graduação (45%)"
                },
                "psicografia_profunda": {
                    "valores_fundamentais": ["Crescimento pessoal", "Independência financeira", "Reconhecimento profissional"],
                    "estilo_vida_detalhado": "Vida acelerada com foco em produtividade, busca constante por conhecimento",
                    "personalidade_dominante": "Ambicioso, determinado, analítico, orientado a resultados",
                    "aspiracoes_profissionais": ["Ser reconhecido como autoridade", "Construir negócio escalável"],
                    "medos_profundos": ["Ficar obsoleto no mercado", "Perder oportunidades", "Falhar financeiramente"],
                    "motivadores_principais": ["Reconhecimento profissional", "Segurança financeira"]
                }
            },
            "mapeamento_dores_ultra_detalhado": {
                "dores_nivel_1_criticas": [
                    {
                        "dor": f"Dificuldade para se posicionar como autoridade em {segmento}",
                        "intensidade": "Alta",
                        "frequencia": "Diária",
                        "impacto_vida": "Baixo reconhecimento profissional e dificuldade para precificar",
                        "nivel_consciencia": "Consciente"
                    }
                ],
                "dores_nivel_2_importantes": [
                    {
                        "dor": "Falta de metodologia estruturada e comprovada",
                        "intensidade": "Alta",
                        "frequencia": "Semanal",
                        "impacto_vida": "Resultados inconsistentes",
                        "nivel_consciencia": "Consciente"
                    }
                ]
            },
            "analise_concorrencia_detalhada": {
                "concorrentes_diretos": [
                    {
                        "nome": f"Academia Premium {segmento}",
                        "preco_range": f"R$ {int(preco * 1.5):,} - R$ {int(preco * 2.5):,}".replace(',', '.'),
                        "proposta_valor": "Metodologia exclusiva com certificação",
                        "pontos_fortes": ["Marca estabelecida", "Comunidade ativa"],
                        "pontos_fracos": ["Preço elevado", "Suporte limitado"],
                        "posicionamento": "Premium e exclusivo"
                    }
                ],
                "gaps_oportunidades": [
                    "Falta de metodologia prática com implementação assistida",
                    "Ausência de suporte contínuo pós-compra",
                    "Preços inacessíveis para profissionais em início de carreira"
                ]
            },
            "estrategia_palavras_chave": {
                "palavras_primarias": [
                    {
                        "termo": f"curso {segmento}",
                        "volume_mensal": "12.100",
                        "dificuldade": "Média",
                        "cpc_estimado": "R$ 4,20",
                        "oportunidade": "Alta"
                    }
                ],
                "custos_aquisicao_canal": {
                    "google_ads": {
                        "cpc_medio": "R$ 3,20",
                        "ctr_esperado": "3,5%",
                        "cpa_estimado": "R$ 420"
                    },
                    "facebook_ads": {
                        "cpc_medio": "R$ 1,45",
                        "ctr_esperado": "2,8%",
                        "cpa_estimado": "R$ 380"
                    }
                }
            },
            "metricas_performance_detalhadas": {
                "benchmarks_segmento": {
                    "cac_medio_segmento": "R$ 420",
                    "ltv_medio_segmento": "R$ 1.680",
                    "churn_rate_medio": "15%",
                    "ticket_medio_segmento": f"R$ {int(preco):,}".replace(',', '.')
                },
                "kpis_criticos": [
                    {
                        "metrica": "CAC (Custo de Aquisição de Cliente)",
                        "valor_ideal": "R$ 420",
                        "como_medir": "Investimento total em marketing / número de clientes adquiridos"
                    }
                ]
            },
            "projecoes_cenarios": {
                "cenario_conservador": {
                    "taxa_conversao": "2,0%",
                    "ticket_medio": f"R$ {int(preco):,}".replace(',', '.'),
                    "cac": "R$ 450",
                    "roi": "240%"
                },
                "cenario_realista": {
                    "taxa_conversao": "3,2%",
                    "ticket_medio": f"R$ {int(preco):,}".replace(',', '.'),
                    "cac": "R$ 420",
                    "roi": "380%"
                },
                "cenario_otimista": {
                    "taxa_conversao": "5,0%",
                    "ticket_medio": f"R$ {int(preco * 1.2):,}".replace(',', '.'),
                    "cac": "R$ 380",
                    "roi": "580%"
                }
            },
            "plano_acao_detalhado": [
                {
                    "fase": "Fase 1: Validação e Pesquisa",
                    "duracao": "2 semanas",
                    "acoes": [
                        {
                            "acao": "Validar proposta de valor com pesquisa qualitativa",
                            "responsavel": "Equipe de pesquisa",
                            "prazo": "10 dias"
                        }
                    ]
                },
                {
                    "fase": "Fase 2: Desenvolvimento e Preparação",
                    "duracao": "3 semanas",
                    "acoes": [
                        {
                            "acao": "Criar landing page otimizada",
                            "responsavel": "Equipe de marketing",
                            "prazo": "7 dias"
                        }
                    ]
                }
            ],
            "insights_exclusivos": [
                f"O segmento {segmento} está passando por uma transformação digital acelerada",
                "Há uma lacuna significativa entre oferta premium e básica no mercado",
                "O público valoriza mais implementação prática do que teoria extensiva",
                "Oportunidade de diferenciação através de suporte personalizado"
            ]
        }