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
