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

# Import with error handling
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

try:
    from services.gemini_client import GeminiClient
except ImportError:
    GeminiClient = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analysis_bp = Blueprint("analysis", __name__)

# Configure Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Cliente Supabase configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Supabase: {e}")

# Initialize Gemini client
gemini_client = None
if GeminiClient:
    try:
        gemini_client = GeminiClient()
        logger.info("✅ Cliente Gemini configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Gemini: {e}")
        gemini_client = None

# Cache para respostas da API Gemini
@lru_cache(maxsize=128)
def get_gemini_response_cached(prompt: str, temperature: float = 0.7, max_tokens: int = 1500):
    return gemini_client.generate_text(prompt, temperature, max_tokens)

@analysis_bp.route("/archeology", methods=["POST"])
def archeology_analysis():
    data = request.json
    user_id = data.get("user_id")
    text_input = data.get("text_input")
    image_input = data.get("image_input")

    if not user_id or not (text_input or image_input):
        return jsonify({"error": "User ID and either text or image input are required"}), 400

    try:
        # Step 1: Initial analysis with Gemini
        prompt_initial = f"""Análise inicial de texto/imagem para arqueologia de avatar. Identifique elementos chave, contexto cultural, período aproximado e possíveis significados. \n\nEntrada: {text_input or image_input}"""
        initial_analysis = get_gemini_response_cached(prompt_initial)

        # Step 2: Deep dive into cultural context
        prompt_cultural = f"""Com base na análise inicial: {initial_analysis}, aprofunde no contexto cultural. Inclua informações sobre rituais, crenças, organização social e artefatos relevantes. \n\nEntrada: {text_input or image_input}"""
        cultural_context = get_gemini_response_cached(prompt_cultural)

        # Step 3: Identify archetypes and symbols
        prompt_archetypes = f"""Com base na análise inicial: {initial_analysis} e contexto cultural: {cultural_context}, identifique arquétipos, símbolos e suas interpretações. \n\nEntrada: {text_input or image_input}"""
        archetypes_symbols = get_gemini_response_cached(prompt_archetypes)

        # Step 4: Behavioral patterns and psychological insights
        prompt_behavioral = f"""Com base na análise inicial: {initial_analysis}, contexto cultural: {cultural_context} e arquétipos/símbolos: {archetypes_symbols}, descreva padrões comportamentais e insights psicológicos do avatar. \n\nEntrada: {text_input or image_input}"""
        behavioral_patterns = get_gemini_response_cached(prompt_behavioral)

        # Step 5: Narrative construction and avatar story
        prompt_narrative = f"""Com base em todas as análises anteriores: \nAnálise Inicial: {initial_analysis}\nContexto Cultural: {cultural_context}\nArquétipos e Símbolos: {archetypes_symbols}\nPadrões Comportamentais: {behavioral_patterns}\n\nCrie uma narrativa envolvente e detalhada para o avatar, incluindo sua história, motivações, desafios e evolução. \n\nEntrada: {text_input or image_input}"""
        avatar_narrative = get_gemini_response_cached(prompt_narrative)

        # Step 6: Generate visual description for avatar
        prompt_visual = f"""Com base na narrativa do avatar: {avatar_narrative}, crie uma descrição visual detalhada para a geração de uma imagem. Inclua elementos como vestimenta, ambiente, expressões faciais, cores e estilo artístico. \n\nEntrada: {text_input or image_input}"""
        visual_description = get_gemini_response_cached(prompt_visual)

        # Step 7: Generate marketing insights
        prompt_marketing = f"""Com base em todas as análises do avatar: \nAnálise Inicial: {initial_analysis}\nContexto Cultural: {cultural_context}\nArquétipos e Símbolos: {archetypes_symbols}\nPadrões Comportamentais: {behavioral_patterns}\nNarrativa do Avatar: {avatar_narrative}\nDescrição Visual: {visual_description}\n\nCrie insights de marketing acionáveis para atingir este avatar. Inclua canais de comunicação, mensagens-chave, produtos/serviços relevantes e estratégias de engajamento. \n\nEntrada: {text_input or image_input}"""
        marketing_insights = get_gemini_response_cached(prompt_marketing)

        # Step 8: Generate competitor analysis (placeholder for now)
        prompt_competitor = f"""Com base nos insights de marketing: {marketing_insights}, identifique potenciais concorrentes e suas estratégias. \n\nEntrada: {text_input or image_input}"""
        competitor_analysis = get_gemini_response_cached(prompt_competitor)

        # Save results to Supabase
        response, count = supabase.table("archeology_results").insert({
            "user_id": user_id,
            "text_input": text_input,
            "image_input": image_input,
            "initial_analysis": initial_analysis,
            "cultural_context": cultural_context,
            "archetypes_symbols": archetypes_symbols,
            "behavioral_patterns": behavioral_patterns,
            "avatar_narrative": avatar_narrative,
            "visual_description": visual_description,
            "marketing_insights": marketing_insights,
            "competitor_analysis": competitor_analysis,
            "created_at": datetime.now().isoformat()
        }).execute()

        return jsonify({
            "message": "Análise de arqueologia de avatar concluída com sucesso!",
            "results": {
                "initial_analysis": initial_analysis,
                "cultural_context": cultural_context,
                "archetypes_symbols": archetypes_symbols,
                "behavioral_patterns": behavioral_patterns,
                "avatar_narrative": avatar_narrative,
                "visual_description": visual_description,
                "marketing_insights": marketing_insights,
                "competitor_analysis": competitor_analysis
            }
        }), 200

    except Exception as e:
        logger.error(f"Erro na análise de arqueologia de avatar: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/history/<user_id>", methods=["GET"])
def get_archeology_history(user_id):
    try:
        response, count = supabase.table("archeology_results").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return jsonify(response[1]), 200
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/latest/<user_id>", methods=["GET"])
def get_latest_archeology_result(user_id):
    try:
        response, count = supabase.table("archeology_results").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        if response[1]:
            return jsonify(response[1][0]), 200
        else:
            return jsonify({"message": "Nenhum resultado encontrado para este usuário."}), 404
    except Exception as e:
        logger.error(f"Erro ao buscar último resultado de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/delete/<result_id>", methods=["DELETE"])
def delete_archeology_result(result_id):
    try:
        response, count = supabase.table("archeology_results").delete().eq("id", result_id).execute()
        if count > 0:
            return jsonify({"message": f"Resultado {result_id} excluído com sucesso."}), 200
        else:
            return jsonify({"message": "Resultado não encontrado."}), 404
    except Exception as e:
        logger.error(f"Erro ao excluir resultado de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/update/<result_id>", methods=["PUT"])
def update_archeology_result(result_id):
    data = request.json
    try:
        response, count = supabase.table("archeology_results").update(data).eq("id", result_id).execute()
        if count > 0:
            return jsonify({"message": f"Resultado {result_id} atualizado com sucesso.", "updated_data": response[1][0]}), 200
        else:
            return jsonify({"message": "Resultado não encontrado."}), 404
    except Exception as e:
        logger.error(f"Erro ao atualizar resultado de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/search", methods=["GET"])
def search_archeology_results():
    query = request.args.get("query", "")
    user_id = request.args.get("user_id")
    try:
        if user_id:
            response, count = supabase.table("archeology_results").select("*").eq("user_id", user_id).ilike("text_input", f"%{query}%").order("created_at", desc=True).execute()
        else:
            response, count = supabase.table("archeology_results").select("*").ilike("text_input", f"%{query}%").order("created_at", desc=True).execute()
        return jsonify(response[1]), 200
    except Exception as e:
        logger.error(f"Erro ao pesquisar resultados de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/filter", methods=["GET"])
def filter_archeology_results():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    user_id = request.args.get("user_id")

    try:
        query = supabase.table("archeology_results").select("*")

        if user_id:
            query = query.eq("user_id", user_id)

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            query = query.gte("created_at", start_date.isoformat())

        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str) + timedelta(days=1) - timedelta(microseconds=1) # End of the day
            query = query.lte("created_at", end_date.isoformat())

        response, count = query.order("created_at", desc=True).execute()
        return jsonify(response[1]), 200
    except Exception as e:
        logger.error(f"Erro ao filtrar resultados de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/metrics", methods=["GET"])
def get_archeology_metrics():
    user_id = request.args.get("user_id")
    try:
        query = supabase.table("archeology_results").select("created_at")
        if user_id:
            query = query.eq("user_id", user_id)
        response, count = query.execute()

        results = response[1]
        total_analyses = len(results)

        # Análises por dia
        analyses_per_day = {}
        for r in results:
            date = datetime.fromisoformat(r["created_at"]).date()
            analyses_per_day[date] = analyses_per_day.get(date, 0) + 1

        # Análises por semana (exemplo simplificado)
        analyses_per_week = {}
        for r in results:
            date = datetime.fromisoformat(r["created_at"]).date()
            # Simplificação: semana começa no domingo
            week_start = date - timedelta(days=date.weekday() + 1)
            analyses_per_week[week_start] = analyses_per_week.get(week_start, 0) + 1

        return jsonify({
            "total_analyses": total_analyses,
            "analyses_per_day": {str(k): v for k, v in analyses_per_day.items()},
            "analyses_per_week": {str(k): v for k, v in analyses_per_week.items()}
        }), 200
    except Exception as e:
        logger.error(f"Erro ao buscar métricas de arqueologia: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/generate_image", methods=["POST"])
def generate_avatar_image():
    data = request.json
    visual_description = data.get("visual_description")
    user_id = data.get("user_id")

    if not visual_description or not user_id:
        return jsonify({"error": "Visual description and user ID are required"}), 400

    try:
        # Placeholder for actual image generation logic
        # In a real scenario, this would call an image generation API (e.g., DALL-E, Midjourney)
        # For now, we'll just return a mock URL
        mock_image_url = f"https://example.com/generated_avatar_{user_id}_{datetime.now().timestamp()}.png"

        # Update Supabase with the generated image URL
        # This assumes you have a way to link this image to a specific archeology result
        # For simplicity, we'll just add it to a new table or update an existing one
        supabase.table("generated_images").insert({
            "user_id": user_id,
            "visual_description": visual_description,
            "image_url": mock_image_url,
            "created_at": datetime.now().isoformat()
        }).execute()

        return jsonify({"message": "Image generation request received (mock).", "image_url": mock_image_url}), 200
    except Exception as e:
        logger.error(f"Erro ao gerar imagem do avatar: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/dashboard_data", methods=["GET"])
def get_dashboard_data():
    user_id = request.args.get("user_id")
    try:
        # Fetch latest archeology result
        latest_result_response, count = supabase.table("archeology_results").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        latest_result = latest_result_response[1][0] if latest_result_response[1] else None

        # Fetch metrics
        metrics_response = get_archeology_metrics().json # Assuming this returns a Flask Response object
        metrics_data = json.loads(metrics_response.data) # Parse the JSON data

        return jsonify({
            "latest_result": latest_result,
            "metrics": metrics_data
        }), 200
    except Exception as e:
        logger.error(f"Erro ao buscar dados do dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/archeology/generate_report", methods=["POST"])
def generate_report():
    data = request.json
    user_id = data.get("user_id")
    report_type = data.get("report_type", "full") # 'full' or 'summary'

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # Fetch all archeology results for the user
        results_response, count = supabase.table("archeology_results").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        all_results = results_response[1]

        if not all_results:
            return jsonify({"message": "Nenhum resultado de arqueologia encontrado para este usuário."}), 404

        report_content = ""
        if report_type == "full":
            report_content += "# Relatório Completo de Arqueologia de Avatar\n\n"
            for i, result in enumerate(all_results):
                report_content += f"## Análise {i+1} (ID: {result.get("id")})\n"
                report_content += f"Data: {result.get("created_at")}\n\n"
                report_content += f"### Análise Inicial\n{result.get("initial_analysis", "N/A")}\n\n"
                report_content += f"### Contexto Cultural\n{result.get("cultural_context", "N/A")}\n\n"
                report_content += f"### Arquétipos e Símbolos\n{result.get("archetypes_symbols", "N/A")}\n\n"
                report_content += f"### Padrões Comportamentais\n{result.get("behavioral_patterns", "N/A")}\n\n"
                report_content += f"### Narrativa do Avatar\n{result.get("avatar_narrative", "N/A")}\n\n"
                report_content += f"### Descrição Visual\n{result.get("visual_description", "N/A")}\n\n"
                report_content += f"### Insights de Marketing\n{result.get("marketing_insights", "N/A")}\n\n"
                report_content += f"### Análise de Concorrentes\n{result.get("competitor_analysis", "N/A")}\n\n---\n\n"
        elif report_type == "summary":
            report_content += "# Relatório Resumido de Arqueologia de Avatar\n\n"
            latest_result = all_results[0] # Get the most recent one
            report_content += f"## Última Análise (ID: {latest_result.get("id")})\n"
            report_content += f"Data: {latest_result.get("created_at")}\n\n"
            report_content += f"### Análise Inicial\n{latest_result.get("initial_analysis", "N/A")}\n\n"
            report_content += f"### Narrativa do Avatar (Resumo)\n{latest_result.get("avatar_narrative", "N/A")}\n\n"
            report_content += f"### Insights de Marketing (Resumo)\n{latest_result.get("marketing_insights", "N/A")}\n\n"

        # Save the report to a file (e.g., Markdown)
        report_filename = f"archeology_report_{user_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        return jsonify({"message": "Relatório gerado com sucesso!", "report_path": report_filename}), 200

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return jsonify({"error": str(e)}), 500


