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
    logger.warning("Supabase not available")
    create_client = None
    Client = None

try:
    from services.gemini_client import GeminiClient
except ImportError:
    logger.warning("GeminiClient not available")
    GeminiClient = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
