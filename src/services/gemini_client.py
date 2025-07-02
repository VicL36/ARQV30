import os
import json
import logging
import time
import re
import requests
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from bs4 import BeautifulSoup
import concurrent.futures
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class GeminiClient:
    """Cliente avançado para Gemini Pro 2.5 com pesquisa na internet e análise ultra-detalhada"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY não encontrada - usando análise de fallback")
            self.client = None
            return
        
        try:
            # Configurar Gemini Pro 2.5
            genai.configure(api_key=self.api_key)
            
            # Usar o modelo mais avançado disponível
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 0.6,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 18192,
                    "response_mime_type": "application/json"
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
            
            logger.info(f"🤖 Gemini Pro 2.5 Client inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Gemini: {e}")
            self.client = None
    
    def search_internet(self, query: str, num_results: int = 10) -> List[Dict]:
        """Pesquisa na internet usando múltiplas fontes"""
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
            f"{segmento} mercado brasileiro 2023 2025",
            f"{segmento} tendências consumidor comportamento",
            f"{segmento} concorrentes principais Brasil",
            f"{segmento} preços produtos serviços",
            f"{segmento} público alvo demographics",
            f"{segmento} marketing digital estratégias",
            f"{segmento} palavras chave SEO",
            f"{segmento} influenciadores autoridades",
            f"{segmento} problemas dores clientes",
            f"{segmento} oportunidades negócio"
        ]
        
        research_data = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_query = {
                executor.submit(self.search_internet, query, 5): query 
                for query in research_queries
            }
            
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    results = future.result()
                    research_data[query] = results
                except Exception as e:
                    logger.warning(f"Erro na pesquisa '{query}': {e}")
                    research_data[query] = []
        
        return research_data
    
    def analyze_avatar_ultra_detailed(self, data: Dict) -> Dict:
        """Análise ultra-detalhada do avatar com Gemini Pro 2.5 e pesquisa na internet"""
        
        if not self.model:
            logger.info("🔄 Gemini não disponível, usando análise de fallback")
            return self._create_fallback_analysis(data)
        
        segmento = data.get('segmento', data.get('nicho', ''))
        
        try:
            logger.info(f"🔍 Iniciando pesquisa abrangente para segmento: {segmento}")
            
            # Pesquisa abrangente na internet
            research_data = self.research_segment_comprehensive(segmento)
            
            # Criar prompt ultra-detalhado com dados da pesquisa
            prompt = self._create_ultra_detailed_prompt(data, research_data)
            
            logger.info("🤖 Processando análise com Gemini Pro 2.5...")
            
            # Gerar análise com Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.warning("⚠️ Resposta vazia do Gemini, usando fallback")
                return self._create_fallback_analysis(data)
            
            # Parse da resposta JSON
            try:
                analysis = json.loads(response.text)
                logger.info("✅ Análise ultra-detalhada concluída com sucesso")
                
                # Adicionar dados de pesquisa à análise
                analysis['research_data'] = research_data
                analysis['generated_at'] = time.time()
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON do Gemini: {e}")
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
        for query, results in research_data.items():
            if results:
                research_summary += f"\n\n**{query}:**\n"
                for result in results[:3]:  # Top 3 resultados por query
                    research_summary += f"- {result['title']}: {result['snippet'][:200]}...\n"
        
        return f"""
Você é um consultor sênior especializado em arqueologia de avatar e análise de mercado no Brasil, com acesso a dados de pesquisa em tempo real.

DADOS DO PRODUTO/SERVIÇO:
- Segmento: {segmento}
- Produto: {produto}
- Preço: R$ {preco}
- Público: {publico}
- Objetivo de Receita: R$ {objetivo_receita}
- Orçamento Marketing: R$ {orcamento_marketing}

DADOS DE PESQUISA NA INTERNET (2023-2025):
{research_summary}

Com base nos dados de pesquisa atualizados e sua expertise, crie uma análise ULTRA-DETALHADA do avatar ideal para este segmento no mercado brasileiro.

IMPORTANTE: Use os dados de pesquisa para validar e enriquecer sua análise. Seja específico, use números reais quando possível, e foque em insights acionáveis.

Retorne APENAS um JSON válido com esta estrutura:

{{
  "escopo": {{
    "segmento_principal": "{segmento}",
    "subsegmentos": ["Subsegmento específico 1", "Subsegmento específico 2", "Subsegmento específico 3"],
    "produto_ideal": "Nome do produto ideal baseado na pesquisa",
    "proposta_valor": "Proposta de valor única validada pela pesquisa de mercado",
    "tamanho_mercado": {{
      "tam": "Valor em R$ bilhões baseado na pesquisa",
      "sam": "Valor em R$ milhões baseado na pesquisa",
      "som": "Valor em R$ milhões baseado na pesquisa"
    }}
  }},
  "avatar_ultra_detalhado": {{
    "persona_principal": {{
      "nome": "Nome fictício mas realista",
      "idade": "Idade específica",
      "profissao": "Profissão específica baseada na pesquisa",
      "renda_mensal": "Faixa de renda específica",
      "localizacao": "Cidade/região específica",
      "estado_civil": "Estado civil e composição familiar",
      "escolaridade": "Nível educacional específico"
    }},
    "demografia_detalhada": {{
      "faixa_etaria_primaria": "Faixa principal com percentual",
      "faixa_etaria_secundaria": "Faixa secundária com percentual",
      "distribuicao_genero": "Distribuição por gênero com percentuais",
      "distribuicao_geografica": "Distribuição por região com percentuais baseada na pesquisa",
      "classes_sociais": "Distribuição por classe social com percentuais",
      "nivel_educacional": "Distribuição educacional com percentuais",
      "situacao_profissional": "Distribuição profissional baseada na pesquisa"
    }},
    "psicografia_profunda": {{
      "valores_fundamentais": ["Valor 1", "Valor 2", "Valor 3", "Valor 4", "Valor 5"],
      "estilo_vida_detalhado": "Descrição detalhada do dia a dia baseada na pesquisa",
      "personalidade_dominante": "Traços de personalidade predominantes",
      "aspiracoes_profissionais": ["Aspiração 1", "Aspiração 2", "Aspiração 3"],
      "aspiracoes_pessoais": ["Aspiração 1", "Aspiração 2", "Aspiração 3"],
      "medos_profundos": ["Medo 1", "Medo 2", "Medo 3", "Medo 4"],
      "frustracoes_atuais": ["Frustração 1", "Frustração 2", "Frustração 3"],
      "crencas_limitantes": ["Crença 1", "Crença 2", "Crença 3"],
      "motivadores_principais": ["Motivador 1", "Motivador 2", "Motivador 3"]
    }},
    "comportamento_digital_avancado": {{
      "plataformas_primarias": ["Plataforma 1 com tempo gasto", "Plataforma 2 com tempo gasto"],
      "plataformas_secundarias": ["Plataforma 3", "Plataforma 4"],
      "horarios_pico_detalhados": {{
        "segunda_sexta": "Horários específicos",
        "fins_semana": "Horários específicos",
        "dispositivos_preferidos": ["Dispositivo 1", "Dispositivo 2"]
      }},
      "conteudo_consumido": {{
        "formatos_preferidos": ["Formato 1", "Formato 2", "Formato 3"],
        "temas_interesse": ["Tema 1", "Tema 2", "Tema 3"],
        "influenciadores_seguidos": ["Tipo de influenciador 1", "Tipo de influenciador 2"],
        "tempo_medio_consumo": "Tempo específico por sessão"
      }},
      "comportamento_compra_online": {{
        "frequencia_compras": "Frequência específica",
        "ticket_medio": "Valor médio baseado na pesquisa",
        "fatores_decisao": ["Fator 1", "Fator 2", "Fator 3"],
        "canais_preferidos": ["Canal 1", "Canal 2"]
      }}
    }}
  }},
  "mapeamento_dores_ultra_detalhado": {{
    "dores_nivel_1_criticas": [
      {{
        "dor": "Dor específica e detalhada",
        "intensidade": "Alta/Média/Baixa",
        "frequencia": "Diária/Semanal/Mensal",
        "impacto_vida": "Como impacta especificamente",
        "tentativas_solucao": ["Tentativa 1", "Tentativa 2"],
        "nivel_consciencia": "Consciente/Semiconsciente/Inconsciente"
      }}
    ],
    "dores_nivel_2_importantes": [
      {{
        "dor": "Segunda dor específica",
        "intensidade": "Alta/Média/Baixa",
        "frequencia": "Frequência específica",
        "impacto_vida": "Impacto específico",
        "tentativas_solucao": ["Tentativa 1", "Tentativa 2"],
        "nivel_consciencia": "Nível de consciência"
      }}
    ],
    "dores_nivel_3_latentes": [
      {{
        "dor": "Terceira dor específica",
        "intensidade": "Intensidade",
        "frequencia": "Frequência",
        "impacto_vida": "Impacto",
        "tentativas_solucao": ["Tentativas"],
        "nivel_consciencia": "Nível"
      }}
    ],
    "jornada_dor": {{
      "gatilho_inicial": "O que desperta a dor",
      "evolucao_dor": "Como a dor evolui",
      "ponto_insuportavel": "Quando se torna insuportável",
      "busca_solucao": "Como busca soluções"
    }}
  }},
  "analise_concorrencia_detalhada": {{
    "concorrentes_diretos": [
      {{
        "nome": "Nome real ou realista baseado na pesquisa",
        "preco_range": "Faixa de preço específica",
        "proposta_valor": "Proposta específica",
        "pontos_fortes": ["Força 1", "Força 2", "Força 3"],
        "pontos_fracos": ["Fraqueza 1", "Fraqueza 2", "Fraqueza 3"],
        "posicionamento": "Como se posiciona",
        "publico_alvo": "Público específico",
        "canais_marketing": ["Canal 1", "Canal 2"],
        "share_mercado_estimado": "Percentual estimado"
      }}
    ],
    "concorrentes_indiretos": [
      {{
        "categoria": "Categoria de solução alternativa",
        "exemplos": ["Exemplo 1", "Exemplo 2"],
        "ameaca_nivel": "Alto/Médio/Baixo"
      }}
    ],
    "gaps_oportunidades": [
      "Gap específico 1 baseado na pesquisa",
      "Gap específico 2 baseado na pesquisa",
      "Gap específico 3 baseado na pesquisa"
    ],
    "barreiras_entrada": ["Barreira 1", "Barreira 2"],
    "fatores_diferenciacao": ["Fator 1", "Fator 2", "Fator 3"]
  }},
  "inteligencia_mercado": {{
    "tendencias_crescimento": [
      {{
        "tendencia": "Tendência específica baseada na pesquisa",
        "impacto": "Alto/Médio/Baixo",
        "timeline": "Prazo específico",
        "oportunidade": "Como aproveitar"
      }}
    ],
    "tendencias_declinio": [
      {{
        "tendencia": "Tendência em declínio",
        "impacto": "Impacto específico",
        "timeline": "Prazo",
        "mitigacao": "Como mitigar"
      }}
    ],
    "sazonalidade_detalhada": {{
      "picos_demanda": ["Mês/período 1", "Mês/período 2"],
      "baixas_demanda": ["Mês/período 1", "Mês/período 2"],
      "fatores_sazonais": ["Fator 1", "Fator 2"],
      "estrategias_sazonais": ["Estratégia 1", "Estratégia 2"]
    }},
    "regulamentacoes_impactos": ["Regulamentação 1", "Regulamentação 2"],
    "tecnologias_emergentes": ["Tecnologia 1", "Tecnologia 2"]
  }},
  "estrategia_palavras_chave": {{
    "palavras_primarias": [
      {{
        "termo": "palavra-chave específica baseada na pesquisa",
        "volume_mensal": "Volume específico",
        "dificuldade": "Alta/Média/Baixa",
        "cpc_estimado": "R$ X,XX",
        "intencao_busca": "Comercial/Informacional/Navegacional",
        "oportunidade": "Alta/Média/Baixa"
      }}
    ],
    "palavras_secundarias": [
      {{
        "termo": "palavra-chave secundária",
        "volume_mensal": "Volume",
        "dificuldade": "Dificuldade",
        "cpc_estimado": "CPC",
        "intencao_busca": "Intenção",
        "oportunidade": "Oportunidade"
      }}
    ],
    "palavras_long_tail": [
      "Palavra long tail 1 específica",
      "Palavra long tail 2 específica",
      "Palavra long tail 3 específica"
    ],
    "custos_aquisicao_canal": {{
      "google_ads": {{
        "cpc_medio": "R$ X,XX",
        "cpm_medio": "R$ XX",
        "ctr_esperado": "X,X%",
        "conversao_esperada": "X,X%",
        "cpa_estimado": "R$ XXX"
      }},
      "facebook_ads": {{
        "cpc_medio": "R$ X,XX",
        "cpm_medio": "R$ XX",
        "ctr_esperado": "X,X%",
        "conversao_esperada": "X,X%",
        "cpa_estimado": "R$ XXX"
      }},
      "instagram_ads": {{
        "cpc_medio": "R$ X,XX",
        "cpm_medio": "R$ XX",
        "ctr_esperado": "X,X%",
        "conversao_esperada": "X,X%",
        "cpa_estimado": "R$ XXX"
      }},
      "youtube_ads": {{
        "cpv_medio": "R$ X,XX",
        "cpm_medio": "R$ XX",
        "view_rate": "XX%",
        "conversao_esperada": "X,X%",
        "cpa_estimado": "R$ XXX"
      }},
      "tiktok_ads": {{
        "cpc_medio": "R$ X,XX",
        "cpm_medio": "R$ XX",
        "ctr_esperado": "X,X%",
        "conversao_esperada": "X,X%",
        "cpa_estimado": "R$ XXX"
      }}
    }}
  }},
  "metricas_performance_detalhadas": {{
    "benchmarks_segmento": {{
      "cac_medio_segmento": "R$ XXX baseado na pesquisa",
      "ltv_medio_segmento": "R$ X.XXX baseado na pesquisa",
      "churn_rate_medio": "XX% baseado na pesquisa",
      "ticket_medio_segmento": "R$ XXX baseado na pesquisa"
    }},
    "funil_conversao_otimizado": {{
      "visitantes_leads": "XX% (benchmark do segmento)",
      "leads_oportunidades": "XX% (benchmark do segmento)",
      "oportunidades_vendas": "XX% (benchmark do segmento)",
      "vendas_clientes": "XX% (benchmark do segmento)"
    }},
    "kpis_criticos": [
      {{
        "metrica": "CAC (Custo de Aquisição de Cliente)",
        "valor_ideal": "R$ XXX",
        "como_medir": "Descrição específica",
        "frequencia": "Diária/Semanal/Mensal"
      }},
      {{
        "metrica": "LTV (Lifetime Value)",
        "valor_ideal": "R$ X.XXX",
        "como_medir": "Descrição específica",
        "frequencia": "Mensal/Trimestral"
      }},
      {{
        "metrica": "ROI Marketing",
        "valor_ideal": "XXX%",
        "como_medir": "Descrição específica",
        "frequencia": "Mensal"
      }}
    ]
  }},
  "voz_mercado_linguagem": {{
    "linguagem_avatar": {{
      "termos_tecnicos": ["Termo 1", "Termo 2", "Termo 3"],
      "girias_expressoes": ["Gíria 1", "Gíria 2", "Gíria 3"],
      "palavras_poder": ["Palavra 1", "Palavra 2", "Palavra 3"],
      "palavras_evitar": ["Palavra 1", "Palavra 2", "Palavra 3"]
    }},
    "objecoes_principais": [
      {{
        "objecao": "Objeção específica baseada na pesquisa",
        "frequencia": "Alta/Média/Baixa",
        "momento_surgimento": "Quando surge na jornada",
        "estrategia_contorno": "Como contornar especificamente",
        "prova_social_necessaria": "Tipo de prova social"
      }}
    ],
    "gatilhos_mentais_efetivos": [
      {{
        "gatilho": "Nome do gatilho",
        "aplicacao": "Como aplicar no segmento",
        "efetividade": "Alta/Média/Baixa",
        "exemplos": ["Exemplo 1", "Exemplo 2"]
      }}
    ],
    "tom_comunicacao": {{
      "personalidade_marca": "Personalidade ideal baseada no avatar",
      "nivel_formalidade": "Formal/Informal/Misto",
      "emocoes_despertar": ["Emoção 1", "Emoção 2", "Emoção 3"],
      "storytelling_temas": ["Tema 1", "Tema 2", "Tema 3"]
    }}
  }},
  "projecoes_cenarios": {{
    "cenario_conservador": {{
      "premissas": ["Premissa 1", "Premissa 2"],
      "taxa_conversao": "X,X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "ltv": "R$ X.XXX",
      "faturamento_mensal": "R$ XX.XXX",
      "roi": "XXX%",
      "break_even": "X meses"
    }},
    "cenario_realista": {{
      "premissas": ["Premissa 1", "Premissa 2"],
      "taxa_conversao": "X,X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "ltv": "R$ X.XXX",
      "faturamento_mensal": "R$ XX.XXX",
      "roi": "XXX%",
      "break_even": "X meses"
    }},
    "cenario_otimista": {{
      "premissas": ["Premissa 1", "Premissa 2"],
      "taxa_conversao": "X,X%",
      "ticket_medio": "R$ XXX",
      "cac": "R$ XXX",
      "ltv": "R$ X.XXX",
      "faturamento_mensal": "R$ XXX.XXX",
      "roi": "XXX%",
      "break_even": "X meses"
    }}
  }},
  "plano_acao_detalhado": [
    {{
      "fase": "Fase 1: Validação e Pesquisa",
      "duracao": "X semanas",
      "acoes": [
        {{
          "acao": "Ação específica 1",
          "responsavel": "Quem executa",
          "prazo": "X dias",
          "recursos_necessarios": ["Recurso 1", "Recurso 2"],
          "entregaveis": ["Entregável 1", "Entregável 2"],
          "metricas_sucesso": ["Métrica 1", "Métrica 2"]
        }}
      ]
    }},
    {{
      "fase": "Fase 2: Desenvolvimento e Preparação",
      "duracao": "X semanas",
      "acoes": [
        {{
          "acao": "Ação específica 2",
          "responsavel": "Quem executa",
          "prazo": "X dias",
          "recursos_necessarios": ["Recurso 1", "Recurso 2"],
          "entregaveis": ["Entregável 1", "Entregável 2"],
          "metricas_sucesso": ["Métrica 1", "Métrica 2"]
        }}
      ]
    }}
  ],
  "insights_exclusivos": [
    "Insight específico 1 baseado na pesquisa atual",
    "Insight específico 2 baseado na pesquisa atual",
    "Insight específico 3 baseado na pesquisa atual"
  ]
}}

INSTRUÇÕES CRÍTICAS:
1. Use APENAS dados reais e atualizados da pesquisa na internet
2. Seja extremamente específico em números, percentuais e valores
3. Substitua TODOS os placeholders por dados reais
4. Base todas as projeções nos dados de pesquisa e preço informado
5. Foque em insights acionáveis e práticos para o mercado brasileiro
6. Use a pesquisa para validar e enriquecer cada seção da análise
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
                    "faixa_etaria_secundaria": "25-32 anos (25%)",
                    "distribuicao_genero": "65% mulheres, 35% homens",
                    "distribuicao_geografica": "Sudeste (45%), Sul (25%), Nordeste (20%), Centro-Oeste (10%)",
                    "classes_sociais": "Classe A (30%), Classe B (60%), Classe C (10%)",
                    "nivel_educacional": "Superior completo (80%), Pós-graduação (45%)",
                    "situacao_profissional": "Empreendedores (40%), Profissionais liberais (35%), Executivos (25%)"
                },
                "psicografia_profunda": {
                    "valores_fundamentais": ["Crescimento pessoal", "Independência financeira", "Reconhecimento profissional", "Qualidade de vida", "Impacto social"],
                    "estilo_vida_detalhado": "Vida acelerada com foco em produtividade, busca constante por conhecimento, valoriza tempo de qualidade com família, investe em desenvolvimento pessoal e profissional",
                    "personalidade_dominante": "Ambicioso, determinado, analítico, orientado a resultados, perfeccionista",
                    "aspiracoes_profissionais": ["Ser reconhecido como autoridade no segmento", "Construir negócio escalável", "Ter liberdade geográfica"],
                    "aspiracoes_pessoais": ["Equilibrar vida pessoal e profissional", "Proporcionar melhor futuro para os filhos", "Viajar pelo mundo"],
                    "medos_profundos": ["Ficar obsoleto no mercado", "Perder oportunidades por indecisão", "Não conseguir escalar o negócio", "Falhar financeiramente"],
                    "frustracoes_atuais": ["Excesso de informação sem aplicação prática", "Falta de tempo para implementar estratégias", "Resultados abaixo do esperado"],
                    "crencas_limitantes": ["Preciso trabalhar mais horas para ganhar mais", "Só quem tem muito dinheiro consegue se destacar", "É muito arriscado investir em marketing"],
                    "motivadores_principais": ["Reconhecimento profissional", "Segurança financeira", "Liberdade de tempo"]
                },
                "comportamento_digital_avancado": {
                    "plataformas_primarias": ["Instagram (2h/dia)", "LinkedIn (1h/dia)"],
                    "plataformas_secundarias": ["YouTube", "WhatsApp Business"],
                    "horarios_pico_detalhados": {
                        "segunda_sexta": "6h-8h e 19h-22h",
                        "fins_semana": "9h-11h e 20h-23h",
                        "dispositivos_preferidos": ["Smartphone", "Notebook"]
                    },
                    "conteudo_consumido": {
                        "formatos_preferidos": ["Vídeos curtos", "Posts educativos", "Lives"],
                        "temas_interesse": ["Estratégias de negócio", "Cases de sucesso", "Tendências do mercado"],
                        "influenciadores_seguidos": ["Especialistas reconhecidos", "Empreendedores de sucesso"],
                        "tempo_medio_consumo": "15-20 minutos por sessão"
                    },
                    "comportamento_compra_online": {
                        "frequencia_compras": "2-3 vezes por mês",
                        "ticket_medio": f"R$ {int(preco * 0.8):,}".replace(',', '.'),
                        "fatores_decisao": ["Prova social", "Garantia", "Autoridade do vendedor"],
                        "canais_preferidos": ["Site próprio", "WhatsApp"]
                    }
                }
            },
            "mapeamento_dores_ultra_detalhado": {
                "dores_nivel_1_criticas": [
                    {
                        "dor": f"Dificuldade para se posicionar como autoridade em {segmento}",
                        "intensidade": "Alta",
                        "frequencia": "Diária",
                        "impacto_vida": "Baixo reconhecimento profissional e dificuldade para precificar adequadamente",
                        "tentativas_solucao": ["Cursos online", "Networking"],
                        "nivel_consciencia": "Consciente"
                    }
                ],
                "dores_nivel_2_importantes": [
                    {
                        "dor": "Falta de metodologia estruturada e comprovada",
                        "intensidade": "Alta",
                        "frequencia": "Semanal",
                        "impacto_vida": "Resultados inconsistentes e desperdício de recursos",
                        "tentativas_solucao": ["Consultoria", "Mentoria"],
                        "nivel_consciencia": "Consciente"
                    }
                ],
                "dores_nivel_3_latentes": [
                    {
                        "dor": "Medo de não conseguir escalar o negócio",
                        "intensidade": "Média",
                        "frequencia": "Mensal",
                        "impacto_vida": "Ansiedade e insegurança sobre o futuro",
                        "tentativas_solucao": ["Planejamento estratégico"],
                        "nivel_consciencia": "Semiconsciente"
                    }
                ],
                "jornada_dor": {
                    "gatilho_inicial": "Percepção de estagnação no crescimento profissional",
                    "evolucao_dor": "Frustração crescente com resultados abaixo do esperado",
                    "ponto_insuportavel": "Quando vê concorrentes obtendo melhores resultados",
                    "busca_solucao": "Pesquisa ativa por metodologias e especialistas"
                }
            },
            "analise_concorrencia_detalhada": {
                "concorrentes_diretos": [
                    {
                        "nome": f"Academia Premium {segmento}",
                        "preco_range": f"R$ {int(preco * 1.5):,} - R$ {int(preco * 2.5):,}".replace(',', '.'),
                        "proposta_valor": "Metodologia exclusiva com certificação",
                        "pontos_fortes": ["Marca estabelecida", "Comunidade ativa", "Conteúdo extenso"],
                        "pontos_fracos": ["Preço elevado", "Suporte limitado", "Muito teórico"],
                        "posicionamento": "Premium e exclusivo",
                        "publico_alvo": "Profissionais experientes",
                        "canais_marketing": ["Google Ads", "Parcerias"],
                        "share_mercado_estimado": "15%"
                    }
                ],
                "concorrentes_indiretos": [
                    {
                        "categoria": "Cursos gratuitos online",
                        "exemplos": ["YouTube", "Blogs especializados"],
                        "ameaca_nivel": "Médio"
                    }
                ],
                "gaps_oportunidades": [
                    "Falta de metodologia prática com implementação assistida",
                    "Ausência de suporte contínuo pós-compra",
                    "Preços inacessíveis para profissionais em início de carreira"
                ],
                "barreiras_entrada": ["Investimento em marketing", "Construção de autoridade"],
                "fatores_diferenciacao": ["Implementação prática", "Suporte personalizado", "Garantia de resultados"]
            },
            "inteligencia_mercado": {
                "tendencias_crescimento": [
                    {
                        "tendencia": "Digitalização acelerada pós-pandemia",
                        "impacto": "Alto",
                        "timeline": "2023-2026",
                        "oportunidade": "Maior demanda por soluções digitais"
                    }
                ],
                "tendencias_declinio": [
                    {
                        "tendencia": "Métodos tradicionais offline",
                        "impacto": "Médio",
                        "timeline": "2023-2025",
                        "mitigacao": "Hibridização de metodologias"
                    }
                ],
                "sazonalidade_detalhada": {
                    "picos_demanda": ["Janeiro-Março", "Setembro-Outubro"],
                    "baixas_demanda": ["Dezembro", "Julho"],
                    "fatores_sazonais": ["Início de ano", "Volta às aulas"],
                    "estrategias_sazonais": ["Campanhas de ano novo", "Promoções de volta às aulas"]
                },
                "regulamentacoes_impactos": ["LGPD", "Marco Civil da Internet"],
                "tecnologias_emergentes": ["IA Generativa", "Automação de Marketing"]
            },
            "estrategia_palavras_chave": {
                "palavras_primarias": [
                    {
                        "termo": f"curso {segmento}",
                        "volume_mensal": "12.100",
                        "dificuldade": "Média",
                        "cpc_estimado": "R$ 4,20",
                        "intencao_busca": "Comercial",
                        "oportunidade": "Alta"
                    }
                ],
                "palavras_secundarias": [
                    {
                        "termo": f"como aprender {segmento}",
                        "volume_mensal": "8.900",
                        "dificuldade": "Baixa",
                        "cpc_estimado": "R$ 2,80",
                        "intencao_busca": "Informacional",
                        "oportunidade": "Média"
                    }
                ],
                "palavras_long_tail": [
                    f"melhor curso de {segmento} online",
                    f"como se tornar especialista em {segmento}",
                    f"{segmento} para iniciantes passo a passo"
                ],
                "custos_aquisicao_canal": {
                    "google_ads": {
                        "cpc_medio": "R$ 3,20",
                        "cpm_medio": "R$ 32",
                        "ctr_esperado": "3,5%",
                        "conversao_esperada": "2,8%",
                        "cpa_estimado": "R$ 420"
                    },
                    "facebook_ads": {
                        "cpc_medio": "R$ 1,45",
                        "cpm_medio": "R$ 18",
                        "ctr_esperado": "2,8%",
                        "conversao_esperada": "2,2%",
                        "cpa_estimado": "R$ 380"
                    },
                    "instagram_ads": {
                        "cpc_medio": "R$ 1,60",
                        "cpm_medio": "R$ 20",
                        "ctr_esperado": "3,2%",
                        "conversao_esperada": "2,5%",
                        "cpa_estimado": "R$ 400"
                    },
                    "youtube_ads": {
                        "cpv_medio": "R$ 0,80",
                        "cpm_medio": "R$ 12",
                        "view_rate": "65%",
                        "conversao_esperada": "1,8%",
                        "cpa_estimado": "R$ 450"
                    },
                    "tiktok_ads": {
                        "cpc_medio": "R$ 0,60",
                        "cpm_medio": "R$ 8",
                        "ctr_esperado": "4,2%",
                        "conversao_esperada": "1,5%",
                        "cpa_estimado": "R$ 480"
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
                "funil_conversao_otimizado": {
                    "visitantes_leads": "18%",
                    "leads_oportunidades": "25%",
                    "oportunidades_vendas": "12%",
                    "vendas_clientes": "95%"
                },
                "kpis_criticos": [
                    {
                        "metrica": "CAC (Custo de Aquisição de Cliente)",
                        "valor_ideal": "R$ 420",
                        "como_medir": "Investimento total em marketing / número de clientes adquiridos",
                        "frequencia": "Semanal"
                    },
                    {
                        "metrica": "LTV (Lifetime Value)",
                        "valor_ideal": "R$ 1.680",
                        "como_medir": "Receita média por cliente x tempo médio de relacionamento",
                        "frequencia": "Mensal"
                    },
                    {
                        "metrica": "ROI Marketing",
                        "valor_ideal": "400%",
                        "como_medir": "(Receita - Investimento) / Investimento x 100",
                        "frequencia": "Mensal"
                    }
                ]
            },
            "voz_mercado_linguagem": {
                "linguagem_avatar": {
                    "termos_tecnicos": ["Metodologia", "Framework", "Sistema", "Estratégia"],
                    "girias_expressoes": ["Game changer", "Next level", "Virada de chave"],
                    "palavras_poder": ["Resultados", "Comprovado", "Exclusivo", "Garantido"],
                    "palavras_evitar": ["Fácil", "Rápido", "Milagre", "Segredo"]
                },
                "objecoes_principais": [
                    {
                        "objecao": "Não tenho tempo para mais um curso",
                        "frequencia": "Alta",
                        "momento_surgimento": "Primeira exposição à oferta",
                        "estrategia_contorno": "Mostrar metodologia de implementação em 15 minutos diários",
                        "prova_social_necessaria": "Depoimentos de pessoas ocupadas que obtiveram resultados"
                    }
                ],
                "gatilhos_mentais_efetivos": [
                    {
                        "gatilho": "Prova Social",
                        "aplicacao": "Cases de sucesso com números reais",
                        "efetividade": "Alta",
                        "exemplos": ["Depoimentos em vídeo", "Resultados mensuráveis"]
                    }
                ],
                "tom_comunicacao": {
                    "personalidade_marca": "Autoridade confiável e acessível",
                    "nivel_formalidade": "Profissional mas acessível",
                    "emocoes_despertar": ["Confiança", "Esperança", "Determinação"],
                    "storytelling_temas": ["Superação", "Transformação", "Conquista"]
                }
            },
            "projecoes_cenarios": {
                "cenario_conservador": {
                    "premissas": ["Mercado estável", "Concorrência moderada"],
                    "taxa_conversao": "2,0%",
                    "ticket_medio": f"R$ {int(preco):,}".replace(',', '.'),
                    "cac": "R$ 450",
                    "ltv": "R$ 1.500",
                    "faturamento_mensal": f"R$ {int(preco * 50):,}".replace(',', '.'),
                    "roi": "240%",
                    "break_even": "6 meses"
                },
                "cenario_realista": {
                    "premissas": ["Crescimento moderado", "Execução consistente"],
                    "taxa_conversao": "3,2%",
                    "ticket_medio": f"R$ {int(preco):,}".replace(',', '.'),
                    "cac": "R$ 420",
                    "ltv": "R$ 1.680",
                    "faturamento_mensal": f"R$ {int(preco * 80):,}".replace(',', '.'),
                    "roi": "380%",
                    "break_even": "4 meses"
                },
                "cenario_otimista": {
                    "premissas": ["Crescimento acelerado", "Execução excelente"],
                    "taxa_conversao": "5,0%",
                    "ticket_medio": f"R$ {int(preco * 1.2):,}".replace(',', '.'),
                    "cac": "R$ 380",
                    "ltv": "R$ 2.100",
                    "faturamento_mensal": f"R$ {int(preco * 150):,}".replace(',', '.'),
                    "roi": "580%",
                    "break_even": "3 meses"
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
                            "prazo": "10 dias",
                            "recursos_necessarios": ["Ferramenta de pesquisa", "Lista de contatos"],
                            "entregaveis": ["Relatório de pesquisa", "Personas validadas"],
                            "metricas_sucesso": ["50 entrevistas realizadas", "Taxa de validação > 70%"]
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
                            "prazo": "7 dias",
                            "recursos_necessarios": ["Designer", "Copywriter", "Desenvolvedor"],
                            "entregaveis": ["Landing page responsiva", "Copy otimizado"],
                            "metricas_sucesso": ["Taxa de conversão > 15%", "Tempo de carregamento < 3s"]
                        }
                    ]
                }
            ],
            "insights_exclusivos": [
                f"O segmento {segmento} está passando por uma transformação digital acelerada",
                "Há uma lacuna significativa entre oferta premium e básica no mercado",
                "O público valoriza mais implementação prática do que teoria extensiva"
            ]
        }
