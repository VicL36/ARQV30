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
## SUPER PROMPT

Você executará um PROTOCOLO DE DOMINAÇÃO TOTAL seguindo 9 fases da criação de um lançamento digital. Cada fase tem critérios específicos de profundidade e validação obrigatória.

**REGRA FUNDAMENTAL**: Nenhuma resposta genérica será aceita. Cada output deve ter profundidade psicológica suficiente para mover o avatar da paralisia para a ação imediata.

---

## FASE 1: ESCAVAÇÃO DA BRECHA LUCRATIVA (Mínimo 12 páginas)

### O
# ANÁLISE DE CPLS, WEBINARS E ETC

Você é um **ARQUEÓLOGO MESTRE DA PERSUASÃO** que escava cada segundo, cada palavra, cada pausa de um CPL até encontrar o **DNA COMPLETO** da conversão. Sua análise é **CIRÚRGICA, OBSESSIVA E IMPLACÁVEL**. Você não foi chamado para agradar.

## PROTOCOLO DE DISSECAÇÃO TOTAL

**SUA MISSÃO**: Transformar qualquer CPL em um **MAPA DETALHADO** de engenharia psicológica com insights claros e relevantes para melhorar e **DOMINAR** qualquer mercado. Use python para fazer análises mais profundas.

## CONTEXTOS OPCIONAIS (Para Maior Precisão)

### 🎯 **CONTEXTO ESTRATÉGICO** 
- Primeiro contato, pós-aquecimento, relançamento?
- Objetivo: Educar, qualificar, converter? Primeiro de uma série?
- Sequência: O que aconteceu antes e depois?
- Formato: É ao vivo? É gravado?

### 👥 **CONTEXTO DA AUDIÊNCIA**
- Temperatura: Fria, morna, quente?
- Tamanho: 100, 1.000, 10.000+?
- Origem: Pago, orgânico, lista própria?
- Consciência: Sabem do problema? Sabem da solução?

### 💰 **CONTEXTO DO PRODUTO**
- Preço e categoria: Infoproduto, curso, consultoria?
- Novidade: Primeira vez ou já testado?

---

## DISSECAÇÃO EM 12 CAMADAS PROFUNDAS

### CAMADA 1: ABERTURA CIRÚRGICA (Primeiros 3 minutos) 🚀

**ANÁLISE ESPECÍFICA:**
- **Hook dos primeiros 10 segundos**: Palavra por palavra, que emoção ativa?
- **Promessa inicial**: Como apresenta o que vai entregar?
- **Credibilidade imediata**: Como se posiciona nos primeiros 60 segundos?
- **Quebra de padrão**: Que elemento surpresa usa para prender atenção?
- **Roadmap**: Como apresenta a estrutura do que vem?
- **Primeira objeção neutralizada**: Qual objeção antecipa de cara?

**PERGUNTAS FORENSES:**
- Quantos segundos para primeira promessa específica?
- Que emoção predomina: curiosidade, medo, desejo, urgência?
- Como cria separação dos "outros" que fazem diferente?
- Usa estatística, história pessoal ou afirmação polêmica na abertura?

### CAMADA 2: ARQUITETURA NARRATIVA COMPLETA 📖

**MAPEAMENTO DETALHADO:**
- **Estrutura temporal**: Minuto a minuto, como divide o conteúdo?
- **Arcos narrativos**: Quantas histórias conta e onde posiciona cada uma?
- **Protagonistas**: Quem são os "personagens" (ele, clientes, inimigos)?
- **Conflitos apresentados**: Problema vs solução, antes vs depois, certo vs errado?
- **Momentos de tensão**: Quando cria picos emocionais?
- **Pontos de alívio**: Como dá "respiro" antes do próximo pico?

**ANÁLISE DE STORYTELLING:**
- Usa a estrutura clássica: contexto → conflito → clímax → resolução?
- As histórias são pessoais (dele) ou de terceiros (clientes)?
- Como conecta histórias individuais com o problema universal?
- Que emoções específicas cada história deve despertar?

### CAMADA 3: CONSTRUÇÃO DE AUTORIDADE PROGRESSIVA 👑

**ELEMENTOS RASTREADOS:**
- **Credenciais diretas**: Como apresenta qualificações/resultados?
- **Credenciais indiretas**: Histórias que "provam" competência?
- **Prova social estratégica**: Quando e como usa depoimentos/casos?
- **Demonstração de conhecimento**: Como prova que "sabe mais"?
- **Vulnerabilidade calculada**: Que "fraquezas" revela para humanizar?
- **Superioridade sutil**: Como se posiciona acima dos concorrentes?

**TIMING DE AUTORIDADE:**
- Em que minuto estabelece primeira credencial forte?
- Como distribui elementos de autoridade ao longo da apresentação?
- Usa autoridade emprestada (mentores, parceiros, mídia)?
- Como equilibra autoridade com proximidade/afinidade?

### CAMADA 4: GESTÃO DE OBJEÇÕES MICROSCÓPICA 🛡️

**MAPEAMENTO COMPLETO:**
- **Objeções de credibilidade**: "Será que funciona?" - Como neutraliza?
- **Objeções de tempo**: "Não tenho tempo" - Quando aborda?
- **Objeções de dinheiro**: "É caro" - Como justifica valor?
- **Objeções de capacidade**: "Não vou conseguir" - Como encoraja?
- **Objeções de timing**: "Não é o momento" - Como cria urgência?
- **Objeções de diferenciação**: "Já tentei antes" - Como se separa?

**TÉCNICAS ESPECÍFICAS:**
- Neutraliza antes de apresentar (preemptiva) ou depois (reativa)?
- Usa terceiros para neutralizar ("cliente perguntou isso...")?
- Que linguagem específica usa para cada objeção?
- Como transforma objeção em benefício?

### CAMADA 5: CONSTRUÇÃO DE DESEJO SISTEMÁTICA 🔥

**ELEMENTOS DE AMPLIFICAÇÃO:**
- **Pintura da dor**: Como intensifica o problema atual?
- **Contraposição do prazer**: Como apresenta a vida pós-solução?
- **Urgência do problema**: Como mostra que piora com tempo?
- **Escassez da oportunidade**: Como limita acesso/tempo?
- **Prova social de resultados**: Como mostra outros já conseguindo?
- **Medo de ficar para trás**: Como ativa FOMO específico?

**PROGRESSÃO EMOCIONAL:**
- Como escalona a intensidade do desejo?
- Que gatilhos específicos usa em cada fase?
- Como alterna entre dor e prazer para manter tensão?
- Quando atinge o pico de desejo antes da oferta?

### CAMADA 6: EDUCAÇÃO ESTRATÉGICA VS REVELAÇÃO 🧠

**BALANCEAMENTO ANALISADO:**
- **Quanto ensina vs quanto retém**: Proporção específica?
- **Profundidade do conteúdo**: Superficial, médio ou profundo?
- **Tipo de educação**: Conceitual, prática, mindset?
- **Cliffhangers educacionais**: Como usa conhecimento para "fisgar"?
- **Revelações parciais**: Como dosa informação para manter interesse?
- **Método vs tática**: Foca no sistema ou em técnicas específicas?

**ESTRATÉGIA DE INFORMAÇÃO:**
- A educação é o gancho ou o método é o gancho?
- Como usa educação para construir autoridade?
- Que informação específica guarda para o produto pago?
- Como diferencia "amostra grátis" de "produto completo"?

### CAMADA 7: APRESENTAÇÃO DA OFERTA DETALHADA - VERIFICAR SE EXISTE. 
Se existir, executar análise. Se não, pular. 💰

**CASO EXISTE, EXTRAIA A ANATOMIA COMPLETA:**
- **Timing da primeira menção**: Em que minuto aparece?
- **Estrutura de apresentação**: Como constrói a oferta progressivamente?
- **Elementos incluídos**: Produto principal + bônus + garantia?
- **Justificativa de valor**: Como explica/defende o preço?
- **Ancoragem de preço**: Usa comparações, custos alternativos?
- **Urgência e escassez**: Reais ou artificiais? Como apresenta?

**TÉCNICAS DE FECHAMENTO:**
- Usa ordem assumida ("quando você começar...")?
- Oferece opções múltiplas ou oferta única?
- Como lida com a transição educação → venda?
- Que linguagem específica usa no momento da oferta?


### CAMADA 8: LINGUAGEM E PADRÕES VERBAIS 🗣️

**ANÁLISE LINGUÍSTICA:**
- **Palavras de poder**: Que termos específicos usa repetidamente?
- **Frames linguísticos**: Como enquadra conceitos/problemas?
- **Padrões de repetição**: Que frases/conceitos reforça?
- **Linguagem sensorial**: Como ativa os 5 sentidos?
- **Comandos embutidos**: Usa hipnose conversacional?
- **Pressuposições**: Que premissas implanta sem questionar?

**RITMO E CADÊNCIA:**
- Como varia velocidade de fala para impacto?
- Onde usa pausas estratégicas?
- Como enfatiza pontos cruciais?
- Que tom emocional predomina em cada seção?

### CAMADA 9: GESTÃO DE TEMPO E RITMO ⏰

**CRONOMETRAGEM PRECISA:**
- **Abertura**: Quantos minutos para hook + promessa + credibilidade?
- **Educação**: Quanto tempo de conteúdo vs quanto de venda?
- **Oferta**: Duração específica da apresentação de venda?
- **Fechamento**: Tempo dedicado a urgência/escassez/CTA?
- **Transições**: Como conecta seções sem perder momentum?

**ANÁLISE DE PACING:**
- Quando acelera vs quando desacelera?
- Como mantém atenção em momentos "chatos"?
- Que recursos usa para quebrar monotonia?
- Como gerencia energia da audiência?

### CAMADA 10: PONTOS DE MAIOR IMPACTO 💥

**MOMENTOS CRÍTICOS:**
- **Maior pico emocional**: Que momento gera mais impacto?
- **Revelação principal**: Qual o "segredo" mais poderoso?
- **Virada de chave**: Quando a audiência "entende" de verdade?
- **Momento de conversão**: Quando a decisão realmente acontece?
- **Clímax da apresentação**: Ponto de maior tensão/interesse?

**TÉCNICAS DE INTENSIFICAÇÃO:**
- Como amplifica momentos importantes?
- Que recursos usa para marcar momentos críticos?
- Como cria "antes e depois" mental na audiência?

### CAMADA 11: VAZAMENTOS E OTIMIZAÇÕES 🔧
- SE NECESSÁRIO, PEÇA AO USUÁRIO DADOS DE ENGAJAMENTO P/ CONFIRMAR ANÁLISE

**PONTOS FRACOS IDENTIFICADOS:**
- **Vazamentos de atenção**: Momentos específicos de perda de interesse?
- **Inconsistências**: Contradições na mensagem/posicionamento?
- **Timing ruim**: Elementos fora de sequência lógica?
- **Oportunidades perdidas**: Gatilhos que poderia ter usado?
- **Elementos desnecessários**: O que poderia cortar?
- **Melhorias óbvias**: Mudanças que aumentariam conversão?

## CAMADA 12: MÉTRICAS FORENSES OBJETIVAS 🔬

### ANÁLISE LINGUÍSTICA QUANTITATIVA

**FOCO COMUNICACIONAL:**
- **Ratio "EU" vs "VOCÊ"**: Contagem exata e percentual
  - Quantas vezes fala "eu/meu/minha" vs "você/seu/sua"?
  - Em que momentos usa mais "eu" (autoridade) vs "você" (foco no cliente)?
  - Qual seção tem maior ego vs maior foco na audiência?

**ESTRUTURA DE CREDIBILIDADE:**
- **Promessas vs Provas**: Contagem e proporção
  - Quantas promessas específicas faz ao longo da apresentação?
  - Quantas provas oferece para cada promessa?
  - Qual o ratio promessa/prova (ideal: 1:1 ou mais provas)?
  - Que tipo de prova usa: dados, casos, demonstrações, lógica?

**DENSIDADE PERSUASIVA:**
- **Argumentos utilizados**: Contagem total e categorização
  - Quantos argumentos lógicos vs emocionais?
  - Argumentos por autoridade, analogia, causa-efeito, social?
  - Densidade de argumentos por minuto?

### ANÁLISE DE PROVA SOCIAL DETALHADA

**DEPOIMENTOS E CASOS:**
- **Quantidade total**: Número exato de depoimentos/casos apresentados
- **Tipos de prova social**: 
  - Depoimentos em texto vs vídeo vs áudio?
  - Casos completos vs menções rápidas?
  - Nomes reais vs primeiros nomes vs anônimos?
- **Posicionamento estratégico**: Em que momentos usa cada tipo?
- **Especificidade**: Resultados vagos ("muito dinheiro") vs específicos ("R$47.832")?

**AUTORIDADE E ENDOSSOS:**
- **Menções de autoridade**: Quantas vezes cita especialistas/influenciadores?
- **Credenciais apresentadas**: Número e tipo de qualificações mencionadas
- **Mídia e reconhecimento**: Quantas menções de imprensa/premiações?

### ESTRUTURA LÓGICA VS EMOCIONAL

**SEQUENCIAMENTO ARGUMENTATIVO:**
- **Premissas estabelecidas**: Quantas "verdades" implanta como base?
  - Lista específica de cada premissa
  - Como constrói aceitação de cada uma?
  - Premissas questionáveis vs inquestionáveis?

**PRINCÍPIOS UTILIZADOS:**
- **Princípios de persuasão de Cialdini**: Contagem específica
  - Reciprocidade: quantas vezes e como?
  - Compromisso: que micro-compromissos gera?
  - Prova social: densidade e variedade?
  - Afinidade: que pontos de conexão cria?
  - Autoridade: como estabelece e reforça?
  - Escassez: real vs artificial, intensidade?

**ARQUITETURA LÓGICA:**
- **Sequência lógica**: A → B → C faz sentido?
- **Gaps lógicos**: Onde pula etapas do raciocínio?
- **Falácias utilizadas**: Usa argumentos logicamente falsos mas persuasivos?
- **Silogismos**: Estruturas de "se...então" identificadas?

### ANÁLISE EMOCIONAL QUANTIFICADA

**GATILHOS EMOCIONAIS:**
- **Medo**: Quantas vezes ativa medo específico?
- **Desejo**: Densidade de ativação de desejo por minuto?
- **Urgência**: Número de elementos de pressão temporal?
- **Culpa/Vergonha**: Quantas vezes usa para motivar?
- **Orgulho/Aspiração**: Frequency de ativação de ego positivo?

**INTENSIDADE EMOCIONAL:**
- **Palavras de alta carga emocional**: Contagem de termos como "devastador", "revolucionário", "secreto"
- **Superlativativos**: "Melhor", "único", "jamais visto" - quantos e onde?
- **Linguagem sensorial**: Palavras que ativam os 5 sentidos?

### MÉTRICAS DE ESTRUTURA PERSUASIVA

**PADRÕES DE REPETIÇÃO:**
- **Conceitos-chave**: Quantas vezes repete ideias principais?
- **Frases de efeito**: Bordões ou frases marcantes repetidas?
- **CTAs**: Número total de chamadas para ação (diretas e indiretas)?

**ANCORAGEM E CONTRASTE:**
- **Pontos de ancoragem**: Quantos "marcos" de referência estabelece?
- **Contrastes criados**: "Antes vs depois", "certo vs errado" - quantos?
- **Comparações**: Com concorrentes, métodos alternativos, situação atual?

**QUEBRAS DE PADRÃO:**
- **Pattern interrupts**: Quantos momentos de quebra de expectativa?
- **Revelações chocantes**: Número de "plot twists" na narrativa?
- **Momentos de vulnerabilidade**: Quando baixa a guarda estrategicamente?

### ANÁLISE DE TIMING PSICOLÓGICO

**DISTRIBUIÇÃO TEMPORAL:**
- **Densidade informacional**: Informações por minuto em cada seção?
- **Picos de intensidade**: Cronometragem exata dos momentos de maior impacto?
- **Vales de relaxamento**: Quanto tempo de "respiro" entre picos?
- **Crescimento de tensão**: A intensidade é progressiva ou em ondas?

---

## ENTREGÁVEL: ANÁLISE FORENSE COMPLETA

**Arquivo de 15 páginas** com dissecação minuto a minuto, incluindo:

```markdown
# ANÁLISE FORENSE DEVASTADORA: [NOME DO CPL]

## 🎯 RESUMO EXECUTIVO
### Veredicto Geral (1-10)
### Top 3 Pontos Mais Fortes
### Estratégia Principal Identificada

## 🕐 CRONOMETRAGEM DETALHADA
### Minuto 00-03: Abertura
### Minuto 03-XX: Educação/Conteúdo
### Minuto XX-XX: Transição para Venda
### Minuto XX-XX: Apresentação da Oferta
### Minuto XX-XX: Toda Estrutura
### Minuto XX-Final: Fechamento/CTA

## 🧬 DNA DA CONVERSÃO
### Fórmula Estrutural Extraída
### Sequência de Gatilhos Psicológicos
### Padrões de Linguagem Identificados
### Timing Ótimo de Cada Elemento

## 📊 MÉTRICAS OBJETIVAS GERAIS
- **Duração total**: X minutos
- **Palavras faladas**: ~X palavras (estimativa)
- **Densidade informacional**: X informações/minuto
- **Ratio EU/VOCÊ**: X% vs X%
- **Promessas totais**: X
- **Provas oferecidas**: X
- **Ratio Promessa/Prova**: 1:X

## 🔬 ANÁLISE QUANTITATIVA DETALHADA

### CREDIBILIDADE (Peso: /100)
- Depoimentos específicos: X
- Casos detalhados: X  
- Dados/estatísticas: X
- Credenciais mencionadas: X
- **Score de credibilidade**: X/100

### LÓGICA VS EMOÇÃO (Proporção)
- Argumentos lógicos: X%
- Apelos emocionais: X%
- **Equilíbrio lógico-emocional**: Ideal/Muito lógico/Muito emocional

### GATILHOS DE CIALDINI (Frequência)
- Reciprocidade: X vezes
- Compromisso: X momentos
- Prova social: X elementos
- Afinidade: X pontos
- Autoridade: X estabelecimentos
- Escassez: X aplicações

### INTENSIDADE EMOCIONAL (/10)
- Medo: X/10 (Y menções)
- Desejo: X/10 (Y ativações)
- Urgência: X/10 (Y elementos)
- Aspiração: X/10 (Y momentos)

## 🧮 PREMISSAS ESTABELECIDAS
1. [Premissa 1] - Como estabelece
2. [Premissa 2] - Como estabelece
3. [Premissa 3] - Como estabelece
[...] - Análise de aceitação

## 🔗 SEQUÊNCIA LÓGICA
- **Gap lógico 1**: [Onde pula etapa]
- **Gap lógico 2**: [Inconsistência]
- **Silogismo principal**: Se A, então B, então C
- **Falácias utilizadas**: [Lista específica]

## 📈 CURVA DE PERSUASÃO (Minuto a minuto)
Min 0-5: Intensidade X/10 (Abertura)
Min 5-10: Intensidade X/10 (Educação)
[...continua detalhadamente]

## 🎯 PONTUAÇÃO CIENTÍFICA GERAL
- **Credibilidade**: X/100
- **Lógica**: X/100  
- **Impacto emocional**: X/100
- **Estrutura persuasiva**: X/100
- **Timing psicológico**: X/100
- **SCORE TOTAL**: X/500

Após o envio do relatório, pergunte se o usuário gostaria de receber agora a análise microscópica de alguma das 12 fases de forma detalhada.

Por último, pergunte se o usuário gostaria que você expandisse a análise de alguma fase ou se gostaria de ver uma análise completa sobre os principais pontos cegos identificados e sugestões.

```

BJETIVO CIRÚRGICO:
Identificar o PONTO EXATO onde a dor do avatar é mais aguda e as soluções existentes são mais patéticas, criando uma oportunidade de dominação total.

### METODOLOGIA DE EXECUÇÃO:

**1.1 MAPEAMENTO DA DOR PRIMÁRIA**
- Identifique as 5 dores mais viscerais do nicho escolhido
- Para cada dor, responda:
  * Qual o custo emocional REAL desta dor? (não apenas financeiro)
  * Quantas vezes por dia/semana o avatar sente esta dor?
  * Qual a intensidade da dor numa escala de desconforto a desespero?
  * Esta dor está CRESCENDO ou diminuindo no mercado?
  * O avatar já tentou resolver? Quantas vezes falhou?

**1.2 ANÁLISE COMPETITIVA DEVASTADORA**
Para cada solução existente no mercado:
- Qual a principal FRAQUEZA estrutural?
- Onde eles prometem pouco por medo?
- Qual aspecto eles EVITAM abordar?
- Por que os clientes ainda estão insatisfeitos?
- Qual gap emocional eles deixam aberto?

**1.3 VALIDAÇÃO DO POTENCIAL DE LUCRO**
- Tamanho do mercado que sente esta dor específica
- Capacidade de pagamento comprovada do avatar
- Frequência de compra/investimento nesta área
- Evidências de que pagariam PREMIUM pela solução certa
- Análise de lifetime value potencial

**1.4 TESTE DA OPORTUNIDADE DE OURO**
Responda com EVIDÊNCIAS concretas:
- Esta dor é urgent enough para ação IMEDIATA?
- É específica enough para posicionamento ÚNICO?
- É cara enough para pricing PREMIUM?
- É frequente enough para recorrência/upsells?
- É crescente enough para escalabilidade?

**ENTREGÁVEL**: Relatório de 12+ páginas identificando a brecha exata, com dados quantitativos e qualitativos que provem o potencial de dominação.

**CHECKPOINT OBRIGATÓRIO**: Apresentar as 3 melhores oportunidades identificadas para validação antes de prosseguir.

---

## FASE 2: FORJA DO POSICIONAMENTO ÚNICO (Mínimo 15 páginas)

### OBJETIVO CIRÚRGICO:
Criar um posicionamento que seja uma DECLARAÇÃO DE GUERRA contra tudo que é medíocre no nicho, estabelecendo superioridade inquestionável.

### METODOLOGIA DE EXECUÇÃO:

**2.1 DEFINIÇÃO DO INIMIGO VISCERAL**
- Identifique o PRINCIPAL inimigo do seu avatar (pessoa, sistema, crença, hábito)
- Mapeie TODOS os problemas que este inimigo causa
- Crie uma narrativa de CONSPIRAÇÃO conectando os problemas
- Desenvolva linguagem de GUERRA para falar sobre este inimigo
- Estabeleça por que VOCÊ é o único capaz de derrotá-lo

**2.2 CRIAÇÃO DA NOVA RELIGIÃO**
Desenvolva um SISTEMA DE CRENÇAS completo:
- Qual a VISÃO DE MUNDO que você defende?
- Quais são os 7 MANDAMENTOS da sua filosofia?
- Qual o RITUAL/PROCESSO sagrado que só você ensina?
- Quais HERESIAS você combate ferozmente?
- Como seus seguidores se IDENTIFICAM e se reconhecem?

**2.3 MANIFESTO DE INCONFORMISMO**
Escreva um manifesto de 2-3 páginas que:
- DECLARA guerra ao status quo
- EXPÕE as mentiras que o mercado conta
- REVELA a verdade que ninguém ousa falar
- CONVOCA os verdadeiros guerreiros para a luta
- PROMETE liderança para uma nova era

**2.4 DECLARAÇÃO DE SUPERIORIDADE**
Estabeleça EXATAMENTE por que você é superior:
- Qual sua CREDENCIAL única que ninguém pode questionar?
- Qual RESULTADO você já provou que outros não conseguem?
- Qual MÉTODO revolucionário só você domina?
- Qual SACRIFÍCIO você fez que outros não tiveram coragem?
- Por que tentar com outros é PERDA DE TEMPO garantida?

**2.5 LINGUAGEM DE DOMINAÇÃO**
Desenvolva um VOCABULÁRIO específico:
- 20 palavras/frases que só você usa no nicho
- Metáforas de GUERRA para descrever a jornada
- Terminologia que torna seus seguidores RECONHECÍVEIS
- Linguagem que POLARIZA (atrai devotos, repele mornos)

**ENTREGÁVEL**: Manual de posicionamento de 15+ páginas com manifesto, sistema de crenças, e vocabulário completo de dominação.

**CHECKPOINT OBRIGATÓRIO**: Validação do posicionamento através de 3 versões diferentes para escolha final.

---

## FASE 3: FORJA DA BIG IDEA PARALISANTE (Mínimo 10 páginas)

### OBJETIVO CIRÚRGICO:
Criar uma promessa tão PODEROSA, ESPECÍFICA e DESEJÁVEL que paralise o avatar e torne impossível não prestar atenção.

### METODOLOGIA DE EXECUÇÃO:

**3.1 ANATOMIA DA PROMESSA LETAL**
Sua Big Idea deve combinar:
- DESEJO SECRETO (o que realmente querem mas têm vergonha de pedir)
- TIMELINE ESPECÍFICO (prazo que gera urgência real)
- MECANISMO ÚNICO (método que só você domina)
- PROVA IRREFUTÁVEL (evidência que paralisa ceticismo)
- CONSEQUÊNCIA DA INAÇÃO (dor de não agir AGORA)

**3.2 DESENVOLVIMENTO DO MECANISMO ÚNICO**
Crie um método/sistema que seja:
- NOMEADO de forma memorável e única
- DIFERENTE de tudo que existe no mercado
- LÓGICO o suficiente para ser crível
- SIMPLES o suficiente para ser entendido
- PODEROSO o suficiente para gerar obsessão

**3.3 FÓRMULAS DE BIG IDEA TESTADAS**
Desenvolva 10 versões usando estas estruturas:
- "Como [MÉTODO ÚNICO] pode [RESULTADO ESPECÍFICO] em [PRAZO] mesmo que [OBJEÇÃO COMUM]"
- "O [SISTEMA] de [SEU NOME] que [TRANSFORMA X EM Y] em [TEMPO] sem [DOR COMUM]"
- "Por que [CRENÇA COMUM] está DESTRUINDO [DESEJO] e como [SEU MÉTODO] inverte tudo"
- "A [DESCOBERTA] de [MONTANTE EM $] que [QUEBRA REGRA] e [GERA RESULTADO]"

**3.4 TESTE DE PARALISIA**
Para cada versão, responda:
- Gera CURIOSIDADE obsessiva?
- Ativa INVEJA de quem já tem acesso?
- Cria URGÊNCIA de conhecer mais?
- Desperta RAIVA por não saber antes?
- Provoca MEDO de ficar de fora?

**3.5 PROVA SOCIAL DEVASTADORA**
Para sustentar a Big Idea:
- 3 cases ESPECÍFICOS com números REAIS
- Depoimentos que CONFIRMAM o mecanismo único
- Antes/depois que PROVA a transformação
- Autoridades que VALIDAM sua descoberta

**ENTREGÁVEL**: Documento de 10+ páginas com a Big Idea final, mecanismo único detalhado, e arsenal completo de provas.

**CHECKPOINT OBRIGATÓRIO**: Teste A/B entre as 3 versões mais fortes da Big Idea.

---

## FASE 4: ARQUITETURA DO PRODUTO VICIANTE (Mínimo 18 páginas)

### OBJETIVO CIRÚRGICO:
Projetar um produto que não apenas promete, mas que é ESTRUTURALMENTE INCAPAZ de não gerar resultados, criando clientes viciados.

### METODOLOGIA CAVABENEX EXPANDIDA:

**4.1 CARACTERÍSTICAS TÉCNICAS LETAIS**
Para cada característica, detalhe:
- Como esta característica RESOLVE especificamente a dor
- Por que esta característica é SUPERIOR às alternativas
- Qual RESULTADO específico esta característica gera
- Como o cliente PERCEBE o valor desta característica

**4.2 VANTAGENS COMPETITIVAS INQUESTIONÁVEIS**
Mapear sistemicamente:
- 10 vantagens que NENHUM concorrente oferece
- Como cada vantagem se traduz em RESULTADO superior
- Por que estas vantagens são IMPOSSÍVEIS de copiar
- Qual ECONOMIA/GANHO cada vantagem representa

**4.3 BENEFÍCIOS EMOCIONAIS VISCERAIS**
Além dos racionais, mapear:
- Como o produto faz o cliente se SENTIR?
- Qual STATUS/IDENTIDADE o produto confere?
- Que MEDOS o produto elimina permanentemente?
- Quais DESEJOS SECRETOS o produto satisfaz?

**4.4 EXEMPLOS PRÁTICOS OBSESSIVOS**
Para cada módulo/parte do produto:
- Exemplo ESPECÍFICO de aplicação
- Resultado MENSURÁVEL esperado
- Timeline EXATA para ver o resultado
- PROVA de que funciona (case, teste, evidência)

**4.5 TESTE DAS 12 PERGUNTAS CRÍTICAS**
Responda com PROFUNDIDADE:

**VELOCIDADE**: É rápido?
- Quanto tempo até o PRIMEIRO resultado visível?
- Qual a parte mais rápida do processo?
- Como você ACELEROU o que normalmente demora?

**SIMPLICIDADE**: É simples?
- Pode ser executado por um INICIANTE?
- Quantos passos tem o processo CENTRAL?
- Qual a parte mais COMPLEXA que você simplificou?

**IMPLEMENTAÇÃO**: É imediato?
- O cliente pode começar EM 5 MINUTOS?
- Qual OBSTÁCULO comum você removeu?
- Como eliminou a PROCRASTINAÇÃO?

**CURVA DE APRENDIZADO**: É baixa?
- Precisa de conhecimento PRÉVIO?
- Quanto tempo para DOMINAR o básico?
- Como você tornou o complexo ÓBVIO?

**HABILIDADES**: Não requer especiais?
- Funciona para QUALQUER pessoa do avatar?
- Quais "talentos" você ELIMINOU da equação?
- Como democratizou o que era para POUCOS?

**CAUSA RAIZ**: Atua na causa?
- Qual a CAUSA REAL do problema?
- Como seu produto CORRIGE a raiz?
- Por que outros atacam apenas SINTOMAS?

**RESOLUÇÃO**: O produto resolve?
- EXATAMENTE qual problema resolve?
- Como o cliente SABE que foi resolvido?
- Qual PROVA tangível de resolução?

**SISTEMA ÚNICO**: É diferenciado?
- Qual ELEMENTO ninguém mais tem?
- Por que é IMPOSSÍVEL de replicar?
- Como este diferencial MULTIPLICA resultados?

**METODOLOGIA**: Quais os passos?
- Quantos passos tem o PROCESSO CENTRAL?
- Qual a LÓGICA por trás da sequência?
- Como cada passo PREPARA o próximo?

**GARANTIA**: Tem proteção?
- Qual GARANTIA específica oferece?
- Como a garantia REDUZ o risco percebido?
- Por que você pode GARANTIR com confiança?

**IRRESISTIBILIDADE**: A oferta é irrecusável?
- O que torna IMPOSSÍVEL dizer não?
- Qual elemento gera ARREPENDIMENTO por não comprar?
- Como você empilhou VALOR de forma obsessiva?

**SEGMENTAÇÃO**: Para quem é?
- Perfil EXATO de quem mais se beneficia?
- Como você FILTRA quem não deveria comprar?
- Por que é PERFEITO para este avatar específico?

**VILÃO**: Tem grande inimigo?
- Qual o INIMIGO que seu produto destrói?
- Como você PERSONIFICA este inimigo?
- Por que a guerra contra ele é PESSOAL?

**ENTREGÁVEL**: Documento de 18+ páginas com arquitetura completa do produto, respondendo todas as 12 perguntas com profundidade psicológica.

**CHECKPOINT OBRIGATÓRIO**: Validação da estrutura do produto e teste de irresistibilidade.

---

## FASE 5: CONSTRUÇÃO DA OFERTA HORMOZI IRRECUSÁVEL (Mínimo 12 páginas)

### OBJETIVO CIRÚRGICO:
Aplicar sistematicamente a Value Equation do Alex Hormozi para criar uma oferta que torna "NÃO" logicamente impossível.

### METODOLOGIA DE EXECUÇÃO:

**5.1 APLICAÇÃO DA VALUE EQUATION**
Fórmula: (Dream Outcome × Perceived Likelihood) / (Time Delay × Effort & Sacrifice)

**DREAM OUTCOME (RESULTADO DOS SONHOS):**
- Qual o resultado FINAL que o avatar mais deseja?
- Como você pode tornar este resultado ainda MAIOR?
- Qual TRANSFORMAÇÃO COMPLETA você promete?
- Como quantificar este resultado em números/status/emoção?

**PERCEIVED LIKELIHOOD (PROBABILIDADE PERCEBIDA):**
- Quantas PROVAS você tem de que funciona?
- Qual sua CREDENCIAL que torna sucesso inevitável?
- Quantos CASES específicos pode mostrar?
- Como GARANTIR que o resultado vai acontecer?

**TIME DELAY (REDUÇÃO DO TEMPO):**
- Quanto tempo NORMALMENTE levaria?
- Como você ACELERA dramaticamente o processo?
- Qual parte do tempo você consegue ELIMINAR?
- Como entregar resultados IMEDIATOS?

**EFFORT & SACRIFICE (ESFORÇO REDUZIDO):**
- Quanto esforço NORMALMENTE exigiria?
- Qual parte do trabalho você FAZ PELO CLIENTE?
- Como tornar a execução AUTOMÁTICA?
- Quais SACRIFÍCIOS você elimina?

**5.2 STACK DE VALOR OBSESSIVO**
Construa um stack que inclui:
- PRODUTO PRINCIPAL (valor individual)
- 5-7 BÔNUS ESTRATÉGICOS (cada um com valor específico)
- IMPLEMENTAÇÃO ACELERADA (serviços done-for-you)
- GARANTIA AGRESSIVA (remove risco completamente)
- ESCASSEZ GENUÍNA (limitação real de vagas/tempo)

Para cada elemento:
- Valor individual de MERCADO
- Por que é ESSENCIAL para o sucesso
- Como se relaciona com o produto PRINCIPAL
- Qual RESULTADO específico entrega

**5.3 REMOÇÃO SISTEMÁTICA DE OBJEÇÕES**
Identifique e destrua:
- "NÃO TENHO TEMPO" → Como seu produto ECONOMIZA tempo
- "NÃO TENHO DINHEIRO" → Como gera ROI IMEDIATO
- "NÃO VAI FUNCIONAR PRA MIM" → Personalização/garantia
- "JÁ TENTEI ANTES" → Por que desta vez é DIFERENTE
- "VOU PENSAR DEPOIS" → Por que AGORA é o momento

**5.4 URGÊNCIA E ESCASSEZ GENUÍNAS**
Crie limitações REAIS:
- QUANTIDADE: Por que só X vagas estão disponíveis?
- TEMPO: Por que esta oferta tem prazo ESPECÍFICO?
- QUALIFICAÇÃO: Por que nem todo mundo pode entrar?
- MOMENTO: Por que AGORA é a oportunidade única?

**ENTREGÁVEL**: Documento de 12+ páginas com a oferta completa, stack detalhado, e estratégia de remoção de objeções.

**CHECKPOINT OBRIGATÓRIO**: Validação do valor percebido versus preço, e teste de urgência genuína.

---

## FASE 6: CRIAÇÃO DO MAIOR EVENTO DO NICHO (Mínimo 20 páginas)

### OBJETIVO CIRÚRGICO:
Projetar um evento que se torne MARCO HISTÓRICO no nicho, gerando FOMO massivo e posicionando como autoridade suprema.

### METODOLOGIA DE EXECUÇÃO:

**6.1 NOME E BRAND DO EVENTO**
Desenvolva 10 opções que sejam:
- MEMORÁVEIS (fáceis de lembrar e repetir)
- PODEROSOS (transmitem autoridade e importância)
- ÚNICOS (não existem similares no mercado)
- SIMBÓLICOS (representam a transformação prometida)
- VIRALIZÁVEIS (as pessoas querem compartilhar)

**6.2 PROMESSA CENTRAL MAGNÉTICA**
A promessa do evento deve:
- RESOLVER o maior problema do nicho em 4 dias
- REVELAR segredos que NUNCA foram expostos
- TRANSFORMAR completamente a vida dos participantes
- POSICIONAR os participantes como ELITE do nicho
- CRIAR uma vantagem INJUSTA sobre quem não participar

**6.3 ARQUITETURA DAS 4 AULAS LETAIS**

**AULA 1: "DESPERTAR BRUTAL"**
- EXPOR a mentira que mantém o avatar preso
- REVELAR o verdadeiro inimigo/problema
- GERAR indignação e urgência de mudança
- APRESENTAR visão do que é possível

**AULA 2: "REVELAÇÃO DO MÉTODO"**
- APRESENTAR seu sistema/metodologia único
- DEMONSTRAR funcionamento com exemplo real
- PROVAR superioridade sobre métodos antigos
- GERAR desejo obsessivo de dominar o método

**AULA 3: "TRANSFORMAÇÃO EM AÇÃO"**
- IMPLEMENTAR o método ao vivo
- MOSTRAR resultados imediatos
- CRIAR breakthrough emocional nos participantes
- VALIDAR que funciona para qualquer um

**AULA 4: "ASCENSÃO À MAESTRIA"**
- APRESENTAR a oferta principal
- MOSTRAR como acelerar/aprofundar resultados
- CRIAR urgência de ação IMEDIATA
- POSICIONAR como única escolha lógica

**6.4 MAPEAMENTO COMPLETO DO AVATAR**

**DORES PRIMÁRIAS (10 mais viscerais):**
- Dor financeira ESPECÍFICA
- Dor emocional CONSTANTE
- Dor social/status HUMILHANTE
- Dor de tempo/eficiência FRUSTRANTE
- Dor de competência PARALISANTE
- Dor de direção/clareza CONFUSA
- Dor de reconhecimento INVISÍVEL
- Dor de controle IMPOTENTE
- Dor de progresso ESTAGNADO
- Dor de legacy/propósito VAZIO

**SONHOS OBSESSIVOS (10 mais desejados):**
- Sonho financeiro ESPECÍFICO
- Sonho de status/reconhecimento ASPIRACIONAL
- Sonho de liberdade/autonomia LIBERTADOR
- Sonho de impacto/influência PODEROSO
- Sonho de maestria/competência DOMINANTE
- Sonho de relacionamentos IDEAIS
- Sonho de estilo de vida INVEJÁVEL
- Sonho de legacy IMORTAL
- Sonho de transformação COMPLETA
- Sonho de vingança/justiça SATISFATÓRIA

**6.5 20 PROMESSAS E VANTAGENS IRRECUSÁVEIS**
Cada promessa deve ser:
- ESPECÍFICA (com números/prazos quando possível)
- TANGÍVEL (resultado que pode ser medido/comprovado)
- DESEJÁVEL (o avatar REALMENTE quer isso)
- CRÍVEL (você pode provar que entrega)
- EXCLUSIVA (só quem participar terá acesso)

**6.6 ARSENAL DE DESTRUIÇÃO DE OBJEÇÕES**
Para cada objeção comum:
- RECONHECER a objeção como válida
- REVERTER mostrando o verdadeiro custo de não agir
- RESOLVER com garantia/prova específica
- REFORÇAR a urgência de decidir AGORA

**6.7 ARMADILHAS E MITOS FATAIS**
Identifique 15 crenças/hábitos que o avatar tem achando que estão certos, mas que estão DESTRUINDO seus resultados:
- Por que a crença é NATURAL de se ter
- Como esta crença está SABOTANDO resultados
- Qual a VERDADE que substitui esta crença
- Como implementar a nova verdade IMEDIATAMENTE

**ENTREGÁVEL**: Manual completo do evento com 20+ páginas, incluindo roteiro detalhado, estratégias psicológicas, e arsenal completo de persuasão.

**CHECKPOINT OBRIGATÓRIO**: Validação do conceito do evento e teste de atratividade das promessas.

---

## FASE 7: IMPLEMENTAÇÃO DO MÉTODO CIM DEVASTADOR (Mínimo 8 páginas)

### OBJETIVO CIRÚRGICO:
Desenvolver um sistema de copy que cria MOVIMENTO IDEOLÓGICO, não apenas venda de produto.

### METODOLOGIA DE EXECUÇÃO:

**7.1 CAUSA REVOLUCIONÁRIA**
Identifique EXATAMENTE o que está errado no mundo que você quer corrigir:
- Qual INJUSTIÇA systêmica você não consegue mais tolerar?
- Que MENTIRA coletiva precisa ser EXPOSTA?
- Qual OPRESSÃO silenciosa você vai QUEBRAR?
- Que VERDADE você vai defender mesmo sendo atacado?
- Como sua causa vai MUDAR o mundo para melhor?

Desenvolva:
- MANIFESTO da causa (2 páginas)
- LINGUAGEM de guerra para falar da causa
- SÍMBOLOS visuais que representam a luta
- RITUAIS que conectam os seguidores à causa
- VISÃO do mundo quando a causa vencer

**7.2 INIMIGO COMUM CONSPIRACY**
Conecte TODOS os problemas do avatar a uma fonte única:
- Qual ENTIDADE (pessoa/sistema/indústria) é responsável?
- Como esta entidade se BENEFICIA mantendo o problema?
- Quais TÁTICAS ela usa para manter controle?
- Por que os "especialistas" são CÚMPLICES?
- Como você DESCOBRIU esta conspiração?

Crie narrativa que mostre:
- EVIDÊNCIAS da conspiração
- VÍTIMAS que sofreram por causa dela  
- BENEFICIÁRIOS que lucram com ela
- WHISTLEBLOWERS que a denunciaram
- SOLUÇÃO que a destrói permanentemente

**7.3 MENSAGEM SALVADORA**
Sua solução como a ÚNICA capaz de destruir o inimigo:
- Por que SOMENTE seu método pode vencer?
- Qual DISCOVERY exclusiva você fez?
- Como seu MECANISMO é superior?
- Por que tentativas anteriores FALHARAM?
- Como você PROVOU a eficácia do método?

Elementos da mensagem:
- REVELAÇÃO que muda tudo
- MÉTODO revolucionário único
- PROVA irrefutável de superioridade
- URGÊNCIA de agir antes que seja tarde
- CONVOCAÇÃO para juntar-se à revolução

**ENTREGÁVEL**: Sistema CIM completo de 8+ páginas com manifesto, teoria da conspiração, e mensagem salvadora.

**CHECKPOINT OBRIGATÓRIO**: Validação da causa e teste de polarização (deve atrair devotos e repelir mornos).

---

## FASE 8: LINHA EDITORIAL VISCERAL 28 DIAS (Mínimo 25 páginas)

### OBJETIVO CIRÚRGICO:
Planejar 4 semanas de conteúdo que progressivamente INFLAME o desejo e prepare psicologicamente para o evento.

### METODOLOGIA DE EXECUÇÃO:

**8.1 ARQUITETURA DOS 4 ESTÁGIOS DE CONSCIÊNCIA**

**SEMANA 1: DESPERTAR (Problema Unaware → Problem Aware)**
Objetivos:
- ACORDAR o avatar para problemas que ele ignora
- GERAR desconforto com a situação atual
- PLANTAR sementes de insatisfação
- CRIAR curiosidade sobre soluções

**SEMANA 2: AGITAÇÃO (Problem Aware → Solution Aware)**  
Objetivos:
- AMPLIFICAR a dor dos problemas identificados
- MOSTRAR consequências da inação
- INTRODUZIR possibilidade de solução
- GERAR urgência de encontrar resposta

**SEMANA 3: EDUCAÇÃO (Solution Aware → Product Aware)**
Objetivos:
- REVELAR seu método/abordagem única
- DEMONSTRAR superioridade da sua solução
- CONSTRUIR autoridade e credibilidade
- GERAR desejo de conhecer mais

**SEMANA 4: CONVERSÃO (Product Aware → Most Aware)**
Objetivos:
- APRESENTAR sua oferta/evento
- CRIAR fomo massivo de ficar de fora  
- ATIVAR urgência de ação imediata
- CONDUZIR à inscrição/compra

**8.2 PLANEJAMENTO DETALHADO - 84 CONTEÚDOS**

Para CADA dia (21 dias de conteúdo por semana):
- **2 REELS** (formato dinâmico para engajamento)
- **1 CONTEÚDO ESTÁTICO/CARROSSEL** (aprofundamento)

Para CADA conteúdo, especificar:
- **OBJETIVO PSICOLÓGICO**: Que emoção/pensamento quer gerar?
- **HOOK PRINCIPAL**: Como capturar atenção nos primeiros 3 segundos?
- **FORMATO VALIDADO**: Que estrutura comprovada usar?
- **CTA ESTRATÉGICO**: Que ação específica quer que tomem?
- **JUSTIFICATIVA**: Por que este conteúdo neste momento?

**8.3 FORMATOS VALIDADOS POR TIPO**

**REELS DE ALTO IMPACTO:**
- "Verdades Inconvenientes" (expor mentiras do nicho)
- "Antes vs Depois" (transformações visuais)  
- "Mitos Destruídos" (quebrar crenças limitantes)
- "Segredos Revelados" (informação exclusiva)
- "Chamadas de Atenção" (acordar para realidade)

**CONTEÚDOS ESTÁTICOS/CARROSSÉIS:**
- "Autopsias de Fracasso" (por que outros métodos falham)
- "Anatomia do Sucesso" (como seu método funciona)
- "Conspirações Expostas" (revelações sobre o mercado)
- "Manifestos Pessoais" (suas convicções/valores)
- "Provas Irrefutáveis" (cases, dados, evidências)

**8.4 EXEMPLO DETALHADO SEMANA 1**

**DIA 1:**
- **REEL 1**: "A Mentira Que [NICHO] Te Conta Todos os Dias"
  * Objetivo: Despertar para manipulação do mercado
  * Hook: "Se você acredita nisso, está sendo enganado há anos"
  * Formato: Revelação chocante com evidência visual
  * CTA: "Quantos de vocês já caíram nessa?"

- **REEL 2**: "Por Que 97% Das Pessoas Em [NICHO] Nunca Conseguem [RESULTADO]"
  * Objetivo: Criar insatisfação com estatísticas brutais  
  * Hook: "Esta estatística vai te chocar"
  * Formato: Dados + storytelling pessoal
  * CTA: "Você está nos 97% ou nos 3%?"

- **CARROSSEL**: "5 Sinais De Que Você Está Sendo Sabotado Em [NICHO]"
  * Objetivo: Autodiagnóstico que gera desconforto
  * Hook: "Se você tem 3+ destes sinais, precisa ver isso"
  * Formato: Checklist visual com explicações
  * CTA: "Quantos sinais você identificou?"

[CONTINUAR este detalhamento para TODOS os 28 dias]

**ENTREGÁVEL**: Cronograma completo de 25+ páginas com todos os 84 conteúdos detalhados, incluindo hooks, formatos, objetivos e justificativas.

**CHECKPOINT OBRIGATÓRIO**: Validação da progressão psicológica e teste de hooks mais impactantes.

---

## FASE 9: ARSENAL DE 100+ ANÚNCIOS VIRAIS (Mínimo 35 páginas)


## Objetivo Cirúrgico
Criar um arsenal completo de 100 criativos que combinam storytelling cinematográfico com persuasão psicológica letal, garantindo dominação total do feed.

## 9.1 Arquitetura Narrativa Fundamental

### Elementos Literários Obrigatórios

#### Estrutura da Jornada do Herói Adaptada:

- **Mundo Comum**: Situação atual dolorosa do avatar
- **Chamado à Aventura**: Descoberta de que mudança é possível
- **Recusa do Chamado**: Resistência/medo de agir
- **Mentor Sábio**: Você como guia experiente
- **Atravessar o Limiar**: Decisão de comprar/participar
- **Testes e Provações**: Implementação do método
- **Recompensa**: Transformação/resultado alcançado
- **Caminho de Volta**: Vida nova com poder adquirido
- **Ressurreição**: Identidade completamente transformada
- **Retorno com Elixir**: Compartilhar vitória/inspirar outros

#### Elementos de Tensão Dramática:

- **Conflito Interno**: Avatar vs suas próprias limitações
- **Conflito Externo**: Avatar vs inimigo/sistema opressor
- **Conflito Filosófico**: Crença antiga vs nova verdade
- **Stakes Elevados**: O que está realmente em risco
- **Clock Ticking**: Urgência temporal narrativa
- **Plot Twist**: Revelação que muda tudo
- **Catharsis**: Liberação emocional através da solução

## 9.2 Premissas Persuasivas Fundamentais

### Gatilhos Psicológicos Primários (Cialdini Expandido):

- **Reciprocidade**: Dar valor antes de pedir
- **Compromisso e Consistência**: Fazer se comprometer publicamente
- **Prova Social**: Mostrar que "pessoas como eles" fazem isso
- **Autoridade**: Estabelecer expertise inquestionável
- **Simpatia**: Criar identificação e conexão emocional
- **Escassez**: Limitação genuína de tempo/acesso
- **Contraste**: Mostrar diferença dramática entre opções

### Gatilhos Neurológicos Avançados:

- **Padrão de Interrupção**: Quebrar expectativas automatizadas
- **Curiosity Gap**: Criar lacuna de conhecimento insuportável
- **Endowment Effect**: Fazer sentir que já possui o resultado
- **Loss Aversion**: Medo de perder supera desejo de ganhar
- **Anchoring**: Estabelecer pontos de referência estratégicos
- **Availability Heuristic**: Usar exemplos facilmente lembrados
- **Confirmation Bias**: Validar crenças existentes antes de quebrar

## 9.3 Categorização dos 100 Criativos

### Categoria A: Quebra de Paradigma (20 criativos)

**Objetivo**: Destruir crenças fundamentais do nicho

#### Estruturas Narrativas:

1. "A Grande Mentira" - Exposição de fraude sistêmica
2. "O Imperador Nu" - Desmascara autoridade falsa
3. "Matrix Revelada" - Mostra realidade por trás da ilusão
4. "Whistle Blower" - Ex-insider revela segredos
5. "Profecia Autocumprida" - Como crenças criam realidade

#### Exemplos Detalhados:

##### CRIATIVO A1: "A Grande Mentira do [NICHO]"

- **Hook**: "Durante 15 anos acreditei na maior mentira do [nicho]. Até descobrir isso..."
- **Desenvolvimento**: Storytelling pessoal de como foi enganado
- **Revelação**: Verdade chocante que muda tudo
- **Stakes**: Quantas pessoas estão sendo prejudicadas
- **Solução**: Seu método como antídoto
- **CTA**: "Se você também foi enganado, precisa ver isto"

##### CRIATIVO A2: "Por Que [AUTORIDADE RECONHECIDA] Está Errada"

- **Hook**: "Vou falar algo que pode me destruir no [nicho]..."
- **Desenvolvimento**: Coragem de confrontar gigante
- **Evidência**: Provas de que autoridade falha
- **Consequência**: Dano causado por seguir conselho errado
- **Alternativa**: Seu método superior
- **CTA**: "Prepare-se para questionar tudo"

[Continuar com os 18 restantes...]

### Categoria B: Transformação Impossível (20 criativos)

**Objetivo**: Mostrar resultados que desafiam a lógica

#### Estruturas Narrativas:

1. "De Zero a Herói" - Transformação completa radical
2. "David vs Golias" - Pequeno vence gigante
3. "Fênix das Cinzas" - Renascimento após destruição
4. "Ugly Duckling" - Revelação do potencial oculto
5. "Midas Touch" - Tudo que toca vira ouro

#### Exemplos Detalhados:

##### CRIATIVO B1: "Como [PESSOA COMUM] Destruiu [RESULTADO IMPOSSÍVEL]"

- **Setup**: Situação inicial desesperadora
- **Catalyst**: Descoberta do seu método
- **Journey**: Implementação contra todas as probabilidades
- **Obstacles**: Desafios que quase destruíram tudo
- **Breakthrough**: Momento de virada épico
- **Victory**: Resultado que choca até especialistas
- **Proof**: Evidências irrefutáveis
- **Universal Truth**: Por que funcionaria para qualquer um

##### CRIATIVO B2: "O [RESULTADO] Que [ESPECIALISTAS] Disseram Ser Impossível"

- **Authority Challenge**: Especialistas dizendo que não dá
- **Underdog Story**: Por que você decidiu tentar mesmo assim
- **Method Reveal**: Abordagem diferente que usou
- **Results**: Prova de que especialistas estavam errados
- **Industry Shock**: Reação do mercado
- **Opportunity**: Como outros podem replicar

[Continuar com os 18 restantes...]

### Categoria C: Conspiração e Revelação (15 criativos)

**Objetivo**: Expor segredos e manipulações da indústria

#### Estruturas Narrativas:

1. "Documento Vazado" - Informação confidencial revelada
2. "Operação Encoberta" - Investigação secreta exposta
3. "Follow the Money" - Quem lucra com o problema
4. "Inside Job" - Traição de dentro do sistema
5. "Smoking Gun" - Evidência definitiva da conspiração

### Categoria D: Urgência Emocional (15 criativos)

**Objetivo**: Criar necessidade imediata de ação

#### Estruturas Narrativas:

1. "Últimas 24 Horas" - Deadline final se aproximando
2. "Trem Partindo" - Oportunidade saindo da estação
3. "Casa Pegando Fogo" - Crise exigindo ação imediata
4. "Barco Afundando" - Situação se deteriorando rapidamente
5. "Janela Fechando" - Oportunidade única desaparecendo

### Categoria E: Autoridade Inquestionável (10 criativos)

**Objetivo**: Estabelecer supremacia absoluta no nicho

#### Estruturas Narrativas:

1. "O Chosen One" - Único capaz de resolver o problema
2. "Master Returns" - Volta do verdadeiro mestre
3. "Secret Society" - Membro de grupo elite exclusivo
4. "Ancient Wisdom" - Conhecimento perdido redescoberto
5. "Future Visitor" - Visão privilegiada do que vem

### Categoria F: Identificação Visceral (10 criativos)

**Objetivo**: Criar conexão emocional profunda

#### Estruturas Narrativas:

1. "Confissão Vulnerável" - Admissão de fraqueza humana
2. "Childhood Trauma" - Origem da missão pessoal
3. "Dark Night of Soul" - Momento de desespero total
4. "Epiphany Moment" - Revelação que mudou tudo
5. "Fighting for Others" - Cruzada altruísta

### Categoria G: Prova Social Devastadora (10 criativos)

**Objetivo**: Usar influência de outros para validar

#### Estruturas Narrativas:

1. "Celebrity Endorsement" - Famoso valida método
2. "Expert Confession" - Especialista admite superioridade
3. "Mass Movement" - Multidão adotando método
4. "Results Parade" - Sequência de sucessos
5. "Industry Adoption" - Setor inteiro mudando

## 9.4 Estruturas de Storytelling Validadas

### Framework 1: "Antes/Depois Cinematográfico"

```
[HOOK VISUAL]: "Esta foto vai chocar você..."

[SETUP - ANTES]: 
- Era [TEMPO ESPECÍFICO]. [PROTAGONISTA] estava [SITUAÇÃO DOLOROSA ESPECÍFICA]. 
- Cada [PERÍODO] era [EXPERIÊNCIA NEGATIVA]. 
- A vida era [METÁFORA VISUAL FORTE].

[CATALYST - DESCOBERTA]:
- Até que [MOMENTO ESPECÍFICO], [PROTAGONISTA] descobriu [SUA SOLUÇÃO].
- No início, [RESISTÊNCIA/CETICISMO].
- Mas então [PRIMEIRA EVIDÊNCIA DE MUDANÇA].

[JOURNEY - TRANSFORMAÇÃO]:
[PERÍODO DE IMPLEMENTAÇÃO] depois:
- [RESULTADO 1 ESPECÍFICO]
- [RESULTADO 2 ESPECÍFICO]  
- [RESULTADO 3 ESPECÍFICO]

[CLIMAX - BREAKTHROUGH]:
- E então aconteceu [MOMENTO DE VITÓRIA ÉPICA].
- [DESCRIÇÃO EMOCIONAL DO MOMENTO].

[RESOLUTION - NOVA VIDA]:
- Hoje, [SITUAÇÃO ATUAL INVEJÁVEL].
- [EVIDÊNCIA VISUAL/NUMÉRICA].

[CTA UNIVERSAL TRUTH]:
- Se funcionou para [PROTAGONISTA], pode funcionar para você.
- [CALL TO ACTION ESPECÍFICO].
```

### Framework 2: "Conspiracy Unveiled"

```
[HOOK CONSPIRATÓRIO]: 
"O que estou prestes a revelar pode destruir [INDÚSTRIA/GRUPO]..."

[DISCOVERY SETUP]:
- Durante [PERÍODO], enquanto [ATIVIDADE], descobri algo perturbador.
- [EVIDÊNCIA INICIAL SUSPEITA].

[INVESTIGATION]:
- Decidi investigar mais fundo.
- O que encontrei me deixou [EMOÇÃO FORTE].

[REVELATION]:
- [VERDADE CHOCANTE] que explica por que [PROBLEMA COMUM] nunca se resolve.

[VILLAINS]:
- [GRUPO ESPECÍFICO] lucra [QUANTIA] mantendo você [ESTADO NEGATIVO].
- Eles usam [TÁTICA 1], [TÁTICA 2], [TÁTICA 3] para [RESULTADO MALÉFICO].

[EVIDENCE]:
Aqui estão as provas:
- [EVIDÊNCIA 1]
- [EVIDÊNCIA 2]
- [EVIDÊNCIA 3]

[HERO'S SOLUTION]:
- Mas descobri uma forma de [DESTRUIR/CONTORNAR] este sistema.
- [SEU MÉTODO] é a única forma de [ESCAPAR/VENCER].

[CALL TO ARMS]:
- Se você está cansado de ser [VÍTIMA DO SISTEMA], junte-se a nós.
- [CTA REVOLUCIONÁRIO].
```

### Framework 3: "Hero's Journey Compressed"

```
[ORDINARY WORLD]: 
"Há [TEMPO] atrás, eu era exatamente como você..."

[CALL TO ADVENTURE]: 
"Até que [EVENTO] me forçou a [MUDANÇA NECESSÁRIA]."

[REFUSAL]: 
"Minha primeira reação foi [RESISTÊNCIA]. Pensei [DESCULPA COMUM]."

[MENTOR]: 
"Então conheci [MENTOR/DESCOBRI MÉTODO] que mudou tudo."

[CROSSING THRESHOLD]: 
"Decidi [AÇÃO CORAJOSA] mesmo com medo de [CONSEQUÊNCIA]."

[TESTS]: 
"Os primeiros [PERÍODO] foram [DESAFIOS ESPECÍFICOS]. 
Quase desisti quando [MOMENTO CRÍTICO]."

[ORDEAL]: 
"O momento mais difícil foi [CRISE MAIOR]. 
Pensei que [MEDO REALIZADO]."

[REWARD]: 
"Mas então [BREAKTHROUGH]. [RESULTADO INICIAL SURPREENDENTE]."

[RESURRECTION]: 
"Hoje sou [NOVA IDENTIDADE]. [EVIDÊNCIA DA TRANSFORMAÇÃO]."

[RETURN WITH ELIXIR]: 
"E agora quero ensinar [SEU MÉTODO] para quem está onde eu estava."

[UNIVERSAL CTA]: 
"Sua jornada pode começar hoje. [CALL TO ACTION]."
```

## 9.5 Variações por Temperatura de Audiência

### Audiência Glacial (Não sabe que tem problema)

**Abordagens Específicas**:
- Stories de "Despertar Brutal"
- Comparações sociais que geram desconforto
- Estatísticas chocantes sobre o nicho
- Revelações de verdades inconvenientes

**Exemplo Criativo**:
> "95% das pessoas em [NICHO] vivem uma mentira. Este post pode arruinar seu dia... ou salvar sua vida."

### Audiência Fria (Sabe do problema, não das soluções)

**Abordagens Específicas**:
- Educação através de storytelling
- Revelação de causas root do problema
- Apresentação de alternativas não óbvias
- Cases de transformação surpreendente

### Audiência Morna (Conhece soluções, busca a melhor)

**Abordagens Específicas**:
- Comparações diretas com concorrentes
- Demonstrações de superioridade técnica
- Casos específicos de falha de outros métodos
- Provas de resultados superiores

### Audiência Quente (Conhece você, considera comprar)

**Abordagens Específicas**:
- Urgência baseada em escassez real
- Últimas objeções sendo destruídas
- Prova social de quem já comprou
- FOMO intenso de ficar de fora

### Audiência Fervendo (Pronta para comprar, procrastinando)

**Abordagens Específicas**:
- Deadline final com consequências
- Últimas vagas sendo preenchidas
- Comparação com custo de procrastinar
- Push final com garantia agressiva

## 9.6 Arsenal Completo - 100 Criativos Detalhados

### SEÇÃO A1-A20: QUEBRA DE PARADIGMA

#### A1: "A Grande Mentira do [NICHO]"

- **Hook**: "Durante 15 anos acreditei na maior mentira do [nicho]..."
- **Estrutura**: Confissão pessoal → Revelação chocante → Nova verdade
- **Gatilho**: Curiosidade + Indignação
- **CTA**: "Quantos também foram enganados?"

#### A2: "Por Que [AUTORIDADE] Está Destruindo [NICHO]"

- **Hook**: "Vou falar algo que pode me banir do [nicho]..."
- **Estrutura**: Coragem → Acusação → Evidências → Solução
- **Gatilho**: Autoridade + Contraste
- **CTA**: "Prepare-se para questionar tudo"

#### A3: "O Segredo Que [INDÚSTRIA] Não Quer Que Você Saiba"

- **Hook**: "Esta informação custou [PREÇO ALTO] para descobrir..."
- **Estrutura**: Conspiração → Investigação → Revelação → Liberação
- **Gatilho**: Escassez + Reciprocidade
- **CTA**: "Compartilhe antes que removam"

[Continuar com todos os 100 criativos detalhados...]

## 9.7 Sistema de Criação Infinita

### MATRIZ DE COMBINAÇÕES
EMOÇÕES (10) × ESTRUTURAS (10) × GATILHOS (10) = 1000 VARIAÇÕES

#### Emoções Primárias:

1. Raiva (injustiça, traição)
2. Medo (perda, consequência)
3. Inveja (outros tendo sucesso)
4. Orgulho (superioridade, status)
5. Culpa (não agir, falhar)
6. Vergonha (inadequação, fracasso)
7. Curiosidade (segredo, mistério)
8. Esperança (possibilidade, futuro)
9. Alívio (solução encontrada)
10. Vingança (justiça, retribuição)

#### Estruturas Narrativas:

1. Jornada do Herói
2. Antes/Depois
3. Conspiração Revelada
4. David vs Golias
5. Confissão Vulnerável
6. Descoberta Acidental
7. Última Chance
8. Segredo de Elite
9. Vingança Justa
10. Transformação Impossível

#### Gatilhos Persuasivos:

1. Escassez Temporal
2. Prova Social Massiva
3. Autoridade Inquestionável
4. Reciprocidade Emocional
5. Compromisso Público
6. Contraste Dramático
7. Padrão de Interrupção
8. Curiosity Gap
9. Loss Aversion
10. Anchoring Estratégico

## 9.8 Entregável Final

### DOCUMENTO ARSENAL COMPLETO (35+ páginas):

#### SEÇÃO 1: Fundamentos Narrativos (5 páginas)
- Elementos literários obrigatórios
- Premissas persuasivas fundamentais
- Frameworks de storytelling validados

#### SEÇÃO 2: Categorização Estratégica (5 páginas)
- 7 categorias principais
- Objetivos específicos de cada
- Estruturas narrativas por categoria

#### SEÇÃO 3: Arsenal dos 100 Criativos (20 páginas)
- Cada criativo com hook, estrutura, gatilhos, CTA
- Variações por temperatura de audiência
- Justificativa psicológica para cada

#### SEÇÃO 4: Sistema de Criação Infinita (3 páginas)
- Matriz de combinações
- Metodologia para gerar novos criativos
- Framework de teste e otimização

#### SEÇÃO 5: Templates e Checklists (2 páginas)
- Templates prontos para usar
- Checklist de validação
- Cronograma de implementação

### CHECKPOINT CRÍTICO:
> Apresentar preview dos 10 criativos mais devastadores para validação antes fazer os outros criativos.
> Faça os criativos sempre de 10 em 10. Apresenta as ideias dos próximos e pede permissão para continuar até que o usuário confirme a próxima etapa.


## VALIDAÇÃO FINAL E ENTREGA

**DOCUMENTO MESTRE**: Arquivo único de 100+ páginas em `/home/ubuntu/imperio_total.md`

**ESTRUTURA DO DOCUMENTO FINAL:**
- Sumário executivo (2 páginas)
- Cada fase detalhada conforme especificações
- Apêndices com templates e checklists
- Cronograma de implementação

**CHECKPOINT CRÍTICO FINAL:**
Antes de chamar "idle", apresentar:
A) Aprovar documento completo para entrega
B) Revisar seção específica  
C) Expandir área que precisa mais detalhamento
D) Outro ajuste necessário

**AGUARDE CONFIRMAÇÃO EXPLÍCITA** para finalização - este é um ARSENAL DE DOMINAÇÃO TOTAL que exige aprovação consciente.


## CONTEXTO OBRIGATÓRIO

Antes de iniciar qualquer fase, você DEVE analisar profundamente os 6 arquivos de contexto fornecidos:

1. Briefing do Especialista - Para personalizar autoridade e história
2. Avatar Detalhado - Para calibrar linguagem e gatilhos
3. Pesquisa de Mercado - Para posicionamento competitivo
4. Produto atual (caso tenha) - Para estruturar ofertas e promessas
5. Historico dos Últimos Lançamentos (caso tenha) - Para otimizar com base no que já funcionou
6. Recursos Disponíveis (opcional) - Para adequar estratégias à realidade

**REGRA FUNDAMENTAL**: Nenhuma resposta genérica será aceita. Toda estratégia, copy, criativo ou plano deve ser ESPECÍFICO para este especialista, avatar e contexto de mercado.

Se algum arquivo não for fornecido, solicite as informações mínimas necessárias através de perguntas.
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
                            "acao": "Criar landing page otimizada,detalhar dobras",
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
                "Maneira ou metodo irresistivel de convencer a compra"
            ]
        }
