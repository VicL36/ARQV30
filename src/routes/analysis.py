from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime, timedelta
import logging
import requests
import re
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from functools import lru_cache

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import with error handling
try:
    from supabase import create_client, Client
except ImportError:
    logger.warning("Supabase not available")
    create_client = None
    Client = None

try:
    from services.gemini_client import GeminiClient
except ImportError:
    logger.warning("GeminiClient not available")
    GeminiClient = None

analysis_bp = Blueprint('analysis', __name__)

# Configure Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = None

if supabase_url and supabase_key and create_client:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Cliente Supabase configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Supabase: {e}")

# Initialize Gemini client
gemini_client = None
if GeminiClient:
    try:
        gemini_client = GeminiClient()
        logger.info("✅ Cliente Gemini Pro configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Gemini: {e}")
        gemini_client = None

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_market():
    """Análise ultra-detalhada de mercado com Gemini Pro 2.5 e pesquisa na internet"""
    try:
        data = request.get_json()
        
        # Aceitar tanto 'segmento' quanto 'nicho' para compatibilidade
        segmento = data.get('segmento') or data.get('nicho')
        if not segmento:
            return jsonify({'error': 'Segmento é obrigatório'}), 400
        
        # Extract and validate form data
        analysis_data = {
            'segmento': segmento.strip(),
            'produto': data.get('produto', '').strip(),
            'descricao': data.get('descricao', '').strip(),
            'preco': data.get('preco', ''),
            'publico': data.get('publico', '').strip(),
            'concorrentes': data.get('concorrentes', '').strip(),
            'dados_adicionais': data.get('dadosAdicionais', '').strip(),
            'objetivo_receita': data.get('objetivoReceita', ''),
            'prazo_lancamento': data.get('prazoLancamento', ''),
            'orcamento_marketing': data.get('orcamentoMarketing', '')
        }
        
        # Safe numeric conversion
        def safe_float_conversion(value, default=None):
            if value is None or value == '':
                return default
            try:
                return float(str(value).replace(',', '.'))
            except (ValueError, TypeError):
                return default
        
        analysis_data['preco_float'] = safe_float_conversion(analysis_data['preco'], 997.0)
        analysis_data['objetivo_receita_float'] = safe_float_conversion(analysis_data['objetivo_receita'], 100000.0)
        analysis_data['orcamento_marketing_float'] = safe_float_conversion(analysis_data['orcamento_marketing'], 50000.0)
        
        logger.info(f"🔍 Iniciando análise ultra-detalhada para segmento: {analysis_data['segmento']}")
        
        # Save initial analysis record
        analysis_id = save_initial_analysis(analysis_data)
        
        # Generate comprehensive analysis with Gemini Pro 2.5
        if gemini_client:
            logger.info("🤖 Usando Gemini Pro 2.5 com pesquisa na internet para análise")
            analysis_result = gemini_client.analyze_avatar_ultra_detailed(analysis_data)
        else:
            logger.warning("⚠️ Gemini não disponível, usando análise de fallback")
            analysis_result = create_fallback_analysis(analysis_data)
        
        # Update analysis record with results
        if supabase and analysis_id:
            update_analysis_record(analysis_id, analysis_result)
            analysis_result['analysis_id'] = analysis_id
        
        logger.info("✅ Análise ultra-detalhada concluída com sucesso")
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

def save_initial_analysis(data: Dict) -> Optional[int]:
    """Salva registro inicial da análise no Supabase"""
    if not supabase:
        logger.warning("⚠️ Supabase não configurado, pulando salvamento")
        return None
    
    try:
        analysis_record = {
            'nicho': data['segmento'],  # Manter compatibilidade com schema
            'produto': data['produto'],
            'descricao': data['descricao'],
            'preco': data['preco_float'],
            'publico': data['publico'],
            'concorrentes': data['concorrentes'],
            'dados_adicionais': data['dados_adicionais'],
            'objetivo_receita': data['objetivo_receita_float'],
            'orcamento_marketing': data['orcamento_marketing_float'],
            'prazo_lancamento': data['prazo_lancamento'],
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('analyses').insert(analysis_record).execute()
        if result.data:
            analysis_id = result.data[0]['id']
            logger.info(f"💾 Análise salva no Supabase com ID: {analysis_id}")
            return analysis_id
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar no Supabase: {str(e)}")
    
    return None

def update_analysis_record(analysis_id: int, results: Dict):
    """Atualiza registro da análise com resultados"""
    try:
        update_data = {
            'avatar_data': results.get('avatar_ultra_detalhado', {}),
            'positioning_data': results.get('escopo', {}),
            'competition_data': results.get('analise_concorrencia_detalhada', {}),
            'marketing_data': results.get('estrategia_palavras_chave', {}),
            'metrics_data': results.get('metricas_performance_detalhadas', {}),
            'funnel_data': results.get('projecoes_cenarios', {}),
            'market_intelligence': results.get('inteligencia_mercado', {}),
            'action_plan': results.get('plano_acao_detalhado', {}),
            'comprehensive_analysis': results,  # Análise completa
            'status': 'completed',
            'updated_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('analyses').update(update_data).eq('id', analysis_id).execute()
        logger.info(f"💾 Análise {analysis_id} atualizada no Supabase")
        
    except Exception as e:
        logger.warning(f"⚠️ Erro ao atualizar análise no Supabase: {str(e)}")

def create_fallback_analysis(data: Dict) -> Dict:
    """Cria análise de fallback quando Gemini falha"""
    if gemini_client:
        return gemini_client._create_fallback_analysis(data)
    
    # Fallback básico se nem o cliente Gemini estiver disponível
    segmento = data.get('segmento', 'Produto Digital')
    return {
        "escopo": {
            "segmento_principal": segmento,
            "subsegmentos": [f"{segmento} básico", f"{segmento} avançado"],
            "produto_ideal": data.get('produto', 'Produto Digital'),
            "proposta_valor": f"Solução completa para {segmento}"
        },
        "avatar_ultra_detalhado": {
            "persona_principal": {
                "nome": "Avatar Padrão",
                "idade": "35 anos",
                "profissao": f"Profissional de {segmento}",
                "renda_mensal": "R$ 10.000 - R$ 20.000",
                "localizacao": "São Paulo, SP",
                "estado_civil": "Casado",
                "escolaridade": "Superior completo"
            }
        },
        "insights_exclusivos": [
            f"Análise básica para o segmento {segmento}",
            "Recomenda-se análise mais detalhada com Gemini Pro 2.5"
        ]
    }

# Rotas existentes mantidas com adaptações para 'segmento'
@analysis_bp.route('/analyses', methods=['GET'])
def get_analyses():
    """Get list of recent analyses"""
    try:
        if not supabase:
            return jsonify({'error': 'Banco de dados não configurado'}), 500
        
        limit = request.args.get('limit', 10, type=int)
        segmento = request.args.get('segmento') or request.args.get('nicho')  # Compatibilidade
        
        query = supabase.table('analyses').select('*').order('created_at', desc=True)
        
        if segmento:
            query = query.eq('nicho', segmento)  # Campo no DB ainda é 'nicho'
        
        result = query.limit(limit).execute()
        
        return jsonify({
            'analyses': result.data,
            'count': len(result.data)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar análises: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@analysis_bp.route('/analyses/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        if not supabase:
            return jsonify({'error': 'Banco de dados não configurado'}), 500
        
        result = supabase.table('analyses').select('*').eq('id', analysis_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Análise não encontrada'}), 404
        
        analysis = result.data[0]
        
        # Retorna análise completa se disponível
        if analysis.get('comprehensive_analysis'):
            return jsonify(analysis['comprehensive_analysis'])
        
        # Fallback para estrutura antiga
        structured_analysis = {
            'id': analysis['id'],
            'segmento': analysis['nicho'],  # Mapear nicho para segmento
            'produto': analysis['produto'],
            'avatar_ultra_detalhado': analysis['avatar_data'],
            'escopo': analysis['positioning_data'],
            'analise_concorrencia_detalhada': analysis['competition_data'],
            'estrategia_palavras_chave': analysis['marketing_data'],
            'metricas_performance_detalhadas': analysis['metrics_data'],
            'projecoes_cenarios': analysis['funnel_data'],
            'inteligencia_mercado': analysis.get('market_intelligence', {}),
            'plano_acao_detalhado': analysis.get('action_plan', {}),
            'created_at': analysis['created_at'],
            'status': analysis['status']
        }
        
        return jsonify(structured_analysis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar análise: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@analysis_bp.route('/segmentos', methods=['GET'])
def get_segmentos():
    """Get list of unique segments from analyses"""
    try:
        if not supabase:
            return jsonify({'error': 'Banco de dados não configurado'}), 500
        
        result = supabase.table('analyses').select('nicho').execute()
        
        segmentos = list(set([item['nicho'] for item in result.data if item['nicho']]))
        segmentos.sort()
        
        return jsonify({
            'segmentos': segmentos,
            'count': len(segmentos)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar segmentos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Manter rota antiga para compatibilidade
@analysis_bp.route('/nichos', methods=['GET'])
def get_nichos():
    """Get list of unique niches (compatibility route)"""
    return get_segmentos()