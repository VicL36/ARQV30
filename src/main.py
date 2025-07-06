import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client

# Blueprints
from routes.user import user_bp
from routes.analysis import analysis_bp
from routes.pdf_generator import pdf_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=\'static\', static_url_path=\'/static\')
CORS(app) # Enable CORS for all routes

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
    # Fallback for local development if .env is not used
    # SUPABASE_URL = "YOUR_SUPABASE_URL"
    # SUPABASE_KEY = "YOUR_SUPABASE_KEY"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Conectado ao Supabase com sucesso.")
except Exception as e:
    logger.error(f"Erro ao conectar ao Supabase: {e}")

# Register Blueprints
app.register_blueprint(user_bp, url_prefix=\'/api/user\')
app.register_blueprint(analysis_bp, url_prefix=\'/api/archeology\') # Corrected prefix
app.register_blueprint(pdf_bp, url_prefix=\'/api/pdf\')

@app.route(\'/\')
def index():
    return send_from_directory(app.static_folder, \'index.html\')

@app.route(\'/health\')
def health_check():
    return jsonify({"status": "ok", "message": "ARQV30 API is running!"}), 200

if __name__ == \'__main__\':
    app.run(debug=True, host=\'0.0.0.0\', port=5000)


