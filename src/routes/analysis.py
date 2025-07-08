from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime, timedelta
import logging
from supabase import create_client, Client
from services.gemini_client import GeminiClient
import requests
import re
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analysis_bp = Blueprint(\'analysis\', __name__)

# Configure Supabase
supabase_url = os.getenv(\'SUPABASE_URL\')
supabase_key = os.getenv(\'SUPABASE_SERVICE_ROLE_KEY\')
supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Cliente Supabase configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Supabase: {e}")
        supabase = None

# Initialize Gemini client
gemini_client = GeminiClient()
if gemini_client.client:
    logger.info("✅ Cliente Gemini Pro 2.5 configurado com sucesso")
else:
    logger.error("❌ Erro ao inicializar Gemini: Cliente não disponível.")

@analysis_bp.route(\"/analyze\", methods=[\"POST\"])
def analyze_market():
    """Análise ultra-detalhada de mercado com Gemini Pro 2.5 e pesquisa na internet"""
    try:
        data = request.get_json()

        # Aceitar tanto \'segmento\' quanto \'nicho\' para compatibilidade
        segmento = data.get(\'segmento\') or data.get(\'nicho\')
        if not segmento:
            return jsonify({\'error\': \'Segmento é obrigatório\'}), 400

        # Extrair dados adicionais para o prompt
        produto = data.get(\'produto\', \'Produto Digital\')
        preco = data.get(\'preco\', \'997.0\')
        publico = data.get(\'publico\', \'Empreendedores e Profissionais Liberais\')
        objetivo_receita = data.get(\'objetivo_receita\', \'100000\')
        orcamento_marketing = data.get(\'orcamento_marketing\', \'10000\')

        # Preparar os dados para o GeminiClient
        gemini_data = {
            "segmento": segmento,
            "produto": produto,
            "preco": preco,
            "publico": publico,
            "objetivo_receita": objetivo_receita,
            "orcamento_marketing": orcamento_marketing
        }

        logger.info(f"Iniciando análise para segmento: {segmento}")
        
        # Chamar o GeminiClient para gerar a análise completa
        analysis_result = gemini_client.generate_analysis(gemini_data)

        if "error" in analysis_result:
            logger.error(f"Erro na geração da análise pelo Gemini: {analysis_result[\"error\"]}")
            return jsonify({"error": analysis_result["error"]}), 500

        # Salvar a análise no Supabase
        if supabase:
            try:
                # Inserir a análise completa no Supabase
                # O Supabase tem um limite de tamanho para colunas JSONB. Se a análise for muito grande,
                # pode ser necessário armazená-la em um serviço de armazenamento de objetos (ex: S3) e salvar apenas o link.
                # Por enquanto, vamos tentar salvar diretamente e logar se houver erro de tamanho.
                response = supabase.table(\'analyses\').insert({
                    "segmento": segmento,
                    "produto": produto,
                    "analysis_data": analysis_result, # Salva o JSON completo aqui
                    "created_at": datetime.now().isoformat()
                }).execute()
                logger.info(f"Análise salva no Supabase: {response.data}")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar análise no Supabase: {e}. Pode ser devido ao tamanho do JSON.")
                # Continua mesmo que não consiga salvar no DB, para não bloquear o usuário
        else:
            logger.warning("Supabase não configurado, pulando salvamento da análise.")

        # Retornar a análise completa com todas as fases
        # Se o JSON for muito grande, jsonify pode falhar ou o cliente pode ter problemas para receber.
        # Uma alternativa seria retornar apenas um ID da análise e o cliente buscar o restante via outra rota.
        # Por enquanto, retornamos o JSON completo e monitoramos o erro 500.
        return jsonify(analysis_result), 200

    except Exception as e:
        logger.error(f"❌ Erro na rota /analyze: {e}")
        # Retorna um erro 500 genérico, mas o log terá mais detalhes.
        return jsonify({"error": "Ocorreu um erro interno no servidor ao processar a análise."}), 500

@analysis_bp.route(\"/analyses\", methods=[\"GET\"])
def get_analyses():
    """Retorna todas as análises salvas"""
    if not supabase:
        return jsonify({"error": "Supabase não configurado."}), 500
    try:
        response = supabase.table(\'analyses\').select(\'*\').order(\'created_at\', desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        logger.error(f"❌ Erro ao buscar análises no Supabase: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route(\"/analysis/<analysis_id>\", methods=[\"GET\"])
def get_analysis_by_id(analysis_id):
    """Retorna uma análise específica pelo ID"""
    if not supabase:
        return jsonify({"error": "Supabase não configurado."}), 500
    try:
        response = supabase.table(\'analyses\').select(\'*\').eq(\'id\', analysis_id).single().execute()
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "Análise não encontrada."}), 404
    except Exception as e:
        logger.error(f"❌ Erro ao buscar análise {analysis_id} no Supabase: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route(\"/analysis/<analysis_id>\", methods=[\"DELETE\"])
def delete_analysis(analysis_id):
    """Deleta uma análise específica pelo ID"""
    if not supabase:
        return jsonify({"error": "Supabase não configurado."}), 500
    try:
        response = supabase.table(\'analyses\').delete().eq(\'id\', analysis_id).execute()
        if response.data:
            return jsonify({"message": "Análise deletada com sucesso."}), 200
        else:
            return jsonify({"error": "Análise não encontrada."}), 404
    except Exception as e:
        logger.error(f"❌ Erro ao deletar análise {analysis_id} no Supabase: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route(\"/analysis/latest\", methods=[\"GET\"])
def get_latest_analysis():
    """Retorna a análise mais recente"""
    if not supabase:
        return jsonify({"error": "Supabase não configurado."}), 500
    try:
        response = supabase.table(\'analyses\').select(\'*\').order(\'created_at\', desc=True).limit(1).single().execute()
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"message": "Nenhuma análise encontrada."}), 404
    except Exception as e:
        logger.error(f"❌ Erro ao buscar a análise mais recente no Supabase: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route(\"/analysis/export-pdf/<analysis_id>\", methods=[\"GET\"])
def export_analysis_pdf(analysis_id):
    """Exporta uma análise específica para PDF"""
    if not supabase:
        return jsonify({"error": "Supabase não configurado."}), 500
    try:
        # Buscar a análise do Supabase
        response = supabase.table(\'analyses\').select(\'analysis_data\').eq(\'id\', analysis_id).single().execute()
        analysis_data = response.data.get(\'analysis_data\') if response.data else None

        if not analysis_data:
            return jsonify({"error": "Análise não encontrada para exportação."}), 404

        # Gerar o PDF (esta parte precisará ser implementada ou integrada com pdf_generator.py)
        # Por enquanto, apenas um placeholder
        pdf_path = f"/tmp/analysis_{analysis_id}.pdf"
        with open(pdf_path, "w") as f:
            f.write(json.dumps(analysis_data, indent=2))
        
        # Retornar o PDF como um arquivo para download
        return send_from_directory(directory=\"/tmp\", path=f"analysis_{analysis_id}.pdf\", as_attachment=True)

    except Exception as e:
        logger.error(f"❌ Erro ao exportar análise {analysis_id} para PDF: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route(\"/analysis/summary\", methods=[\"POST\"])
def get_analysis_summary():
    """Gera um resumo da análise para exibição rápida"""
    try:
        data = request.get_json()
        analysis_data = data.get(\'analysis_data\')

        if not analysis_data:
            return jsonify({"error": "Dados da análise não fornecidos."}), 400

        # Extrair as informações relevantes para o resumo
        # O resumo agora deve ser mais robusto para lidar com a nova estrutura de fases
        summary = {
            "titulo_analise": analysis_data.get(\'fase_1_result\', {}).get(\'fase_1_escavacao_brecha_lucrativa\', {}).get(\'melhores_oportunidades_identificadas\', ["Análise de Mercado"])[0] if analysis_data.get(\'fase_1_result\') and analysis_data.get(\'fase_1_result\').get(\'fase_1_escavacao_brecha_lucrativa\') and analysis_data.get(\'fase_1_result\').get(\'fase_1_escavacao_brecha_lucrativa\').get(\'melhores_oportunidades_identificadas\') else "Análise de Mercado",
            "resumo_executivo": analysis_data.get(\'fase_1_result\', {}).get(\'fase_1_escavacao_brecha_lucrativa\', {}).get(\'dores_primarias\', [{}])[0].get(\'dor\', \'N/A\') if analysis_data.get(\'fase_1_result\') and analysis_data.get(\'fase_1_result\').get(\'fase_1_escavacao_brecha_lucrativa\') and analysis_data.get(\'fase_1_result\').get(\'fase_1_escavacao_brecha_lucrativa\').get(\'dores_primarias\') and analysis_data.get(\'fase_1_result\').get(\'fase_1_escavacao_brecha_lucrativa\').get(\'dores_primarias\')[0] else "N/A",
            "pontos_chave": []
        }

        # Adicionar pontos chave de outras fases se existirem
        if analysis_data.get(\'fase_2_result\') and analysis_data.get(\'fase_2_result\').get(\'fase_2_forja_posicionamento_unico\'):
            summary["pontos_chave"].append(analysis_data[\'fase_2_result\'].get(\'fase_2_forja_posicionamento_unico\', {}).get(\'inimigo_principal\', \'N/A\'))
        if analysis_data.get(\'fase_3_result\') and analysis_data.get(\'fase_3_result\').get(\'fase_3_forja_big_idea_paralisante\'):
            summary["pontos_chave"].append(analysis_data[\'fase_3_result\'].get(\'fase_3_forja_big_idea_paralisante\', {}).get(\'desejo_secreto\', \'N/A\'))
        if analysis_data.get(\'fase_4_result\') and analysis_data.get(\'fase_4_result\').get(\'fase_4_arquitetura_produto_viciante\') and analysis_data.get(\'fase_4_result\').get(\'fase_4_arquitetura_produto_viciante\').get(\'caracteristicas_tecnicas_letais\') and analysis_data.get(\'fase_4_result\').get(\'fase_4_arquitetura_produto_viciante\').get(\'caracteristicas_tecnicas_letais\')[0]:
            summary["pontos_chave"].append(analysis_data[\'fase_4_result\'].get(\'fase_4_arquitetura_produto_viciante\', {}).get(\'caracteristicas_tecnicas_letais\', [{}])[0].get(\'caracteristica\', \'N/A\'))

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo da análise: {e}")
        return jsonify({"error": str(e)}), 500



