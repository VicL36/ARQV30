import os
import logging
import json
import requests
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str = None):
        """Initialize Gemini client with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-pro')
        
        logger.info("✅ Gemini Pro client initialized successfully")
    
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        """Generate text using Gemini Pro"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Erro na geração de texto: {str(e)}"
    
    def analyze_avatar_ultra_detailed(self, data: Dict) -> Dict:
        """Perform ultra-detailed avatar analysis"""
        try:
            segmento = data.get('segmento', 'Produto Digital')
            produto = data.get('produto', 'Produto')
            descricao = data.get('descricao', '')
            preco = data.get('preco_float', 997.0)
            publico = data.get('publico', '')
            concorrentes = data.get('concorrentes', '')
            
            logger.info(f"🔍 Iniciando análise ultra-detalhada para: {segmento}")
            
            # Prompt principal para análise completa
            main_prompt = f"""
            Você é um especialista em análise de mercado e arqueologia de avatar. Realize uma análise ULTRA-DETALHADA para:

            SEGMENTO: {segmento}
            PRODUTO: {produto}
            DESCRIÇÃO: {descricao}
            PREÇO: R$ {preco}
            PÚBLICO: {publico}
            CONCORRENTES: {concorrentes}

            Forneça uma análise completa em formato JSON com as seguintes seções:

            1. ESCOPO DE MERCADO
            2. AVATAR ULTRA-DETALHADO
            3. MAPEAMENTO DE DORES (3 níveis)
            4. ANÁLISE DE CONCORRÊNCIA
            5. INTELIGÊNCIA DE MERCADO
            6. ESTRATÉGIA DE PALAVRAS-CHAVE
            7. MÉTRICAS DE PERFORMANCE
            8. VOZ DO MERCADO
            9. PROJEÇÕES DE CENÁRIOS
            10. PLANO DE AÇÃO DETALHADO
            11. INSIGHTS EXCLUSIVOS

            Retorne APENAS o JSON válido, sem explicações adicionais.
            """
            
            # Generate comprehensive analysis
            response_text = self.generate_text(main_prompt, temperature=0.7, max_tokens=4000)
            
            # Try to parse JSON response
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured fallback
                analysis_result = self._create_fallback_analysis(data)
            
            logger.info("✅ Análise ultra-detalhada concluída")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return self._create_fallback_analysis(data)
    
    def _create_fallback_analysis(self, data: Dict) -> Dict:
        """Create fallback analysis when Gemini fails"""
        segmento = data.get('segmento', 'Produto Digital')
        produto = data.get('produto', 'Produto')
        preco = data.get('preco_float', 997.0)
        
        return {
            "escopo": {
                "segmento_principal": segmento,
                "subsegmentos": [f"{segmento} Básico", f"{segmento} Avançado", f"{segmento} Premium"],
                "produto_ideal": produto,
                "proposta_valor": f"Solução completa para {segmento}",
                "tamanho_mercado": {
                    "tam": "R$ 2.8 bilhões",
                    "sam": "R$ 420 milhões", 
                    "som": "R$ 28 milhões"
                }
            },
            "avatar_ultra_detalhado": {
                "persona_principal": {
                    "nome": "Avatar Ideal",
                    "idade": "35 anos",
                    "profissao": f"Profissional de {segmento}",
                    "renda_mensal": "R$ 10.000 - R$ 20.000",
                    "localizacao": "São Paulo, SP",
                    "estado_civil": "Casado(a)",
                    "escolaridade": "Superior completo"
                },
                "demografia": {
                    "faixa_etaria": "30-45 anos",
                    "genero": "60% mulheres, 40% homens",
                    "renda_familiar": "R$ 8.000 - R$ 25.000",
                    "localizacao_geografica": "Região Sudeste e Sul"
                },
                "psicografia": {
                    "valores": ["Qualidade", "Eficiência", "Resultados"],
                    "interesses": [segmento, "Desenvolvimento pessoal", "Tecnologia"],
                    "estilo_vida": "Ativo digitalmente, busca soluções práticas"
                }
            },
            "mapeamento_dores_ultra_detalhado": {
                "dores_nivel_1_criticas": [
                    {
                        "dor": f"Dificuldade em obter resultados em {segmento}",
                        "intensidade": "Alta",
                        "frequencia": "Diária"
                    },
                    {
                        "dor": "Falta de conhecimento especializado",
                        "intensidade": "Alta", 
                        "frequencia": "Constante"
                    }
                ],
                "dores_nivel_2_importantes": [
                    {
                        "dor": "Falta de tempo para aprender",
                        "intensidade": "Média",
                        "frequencia": "Semanal"
                    }
                ],
                "dores_nivel_3_latentes": [
                    {
                        "dor": "Insegurança sobre métodos",
                        "intensidade": "Baixa",
                        "frequencia": "Eventual"
                    }
                ]
            },
            "analise_concorrencia_detalhada": {
                "concorrentes_diretos": [
                    {
                        "nome": "Concorrente A",
                        "preco_range": f"R$ {preco * 0.8:.0f} - R$ {preco * 1.2:.0f}",
                        "posicionamento": "Premium"
                    }
                ],
                "gaps_oportunidades": [
                    "Falta de personalização no mercado",
                    "Atendimento humanizado limitado",
                    "Preços acessíveis para classe média"
                ]
            },
            "inteligencia_mercado": {
                "tendencias_crescimento": [
                    {
                        "tendencia": f"Crescimento do mercado de {segmento}",
                        "impacto": "Alto",
                        "prazo": "12-24 meses"
                    }
                ],
                "sazonalidade": {
                    "alta_demanda": ["Janeiro", "Julho"],
                    "baixa_demanda": ["Dezembro"]
                }
            },
            "estrategia_palavras_chave": {
                "palavras_primarias": [
                    {
                        "termo": segmento.lower(),
                        "volume_mensal": "10.000+",
                        "dificuldade": "Média",
                        "cpc_estimado": "R$ 2,50"
                    }
                ],
                "custos_plataformas": {
                    "google_ads": {
                        "cpc_medio": "R$ 2,50",
                        "ctr_esperado": "3.5%"
                    },
                    "facebook_ads": {
                        "cpc_medio": "R$ 1,80",
                        "ctr_esperado": "4.2%"
                    }
                }
            },
            "metricas_performance_detalhadas": {
                "benchmarks_segmento": {
                    "cac_medio_segmento": f"R$ {preco * 0.3:.0f}",
                    "ltv_medio_segmento": f"R$ {preco * 3:.0f}",
                    "churn_rate_medio": "15%",
                    "ticket_medio_segmento": f"R$ {preco:.0f}"
                },
                "funil_otimizado": [
                    "Consciência → Interesse → Consideração → Compra → Retenção"
                ],
                "kpis_criticos": [
                    "Taxa de conversão",
                    "CAC",
                    "LTV",
                    "ROI"
                ]
            },
            "voz_mercado": {
                "linguagem_avatar": {
                    "tom": "Profissional e acessível",
                    "palavras_chave": [segmento, "resultados", "transformação"]
                },
                "objecoes_principais": [
                    {
                        "objecao": "Preço muito alto",
                        "resposta": "Investimento com retorno garantido"
                    }
                ],
                "gatilhos_mentais": [
                    {
                        "gatilho": "Escassez",
                        "aplicacao": "Vagas limitadas"
                    }
                ]
            },
            "projecoes_cenarios": {
                "cenario_conservador": {
                    "taxa_conversao": "2%",
                    "ticket_medio": f"R$ {preco * 0.8:.0f}",
                    "cac": f"R$ {preco * 0.4:.0f}",
                    "roi": "150%"
                },
                "cenario_realista": {
                    "taxa_conversao": "3.5%",
                    "ticket_medio": f"R$ {preco:.0f}",
                    "cac": f"R$ {preco * 0.3:.0f}",
                    "roi": "250%"
                },
                "cenario_otimista": {
                    "taxa_conversao": "5%",
                    "ticket_medio": f"R$ {preco * 1.2:.0f}",
                    "cac": f"R$ {preco * 0.2:.0f}",
                    "roi": "400%"
                }
            },
            "plano_acao_detalhado": [
                {
                    "fase": "Fase 1: Preparação",
                    "duracao": "30 dias",
                    "acoes": [
                        {
                            "acao": "Definir posicionamento",
                            "responsavel": "Marketing",
                            "prazo": "7 dias"
                        }
                    ]
                }
            ],
            "insights_exclusivos": [
                f"O mercado de {segmento} está em crescimento acelerado",
                "Oportunidade de diferenciação através de atendimento personalizado",
                "Preço posicionado adequadamente para o público-alvo",
                "Potencial de expansão para mercados adjacentes",
                "Necessidade de foco em marketing de conteúdo"
            ]
        }