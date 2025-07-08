import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
from routes.user import user_bp
from routes.analysis import analysis_bp
from routes.pdf_generator import pdf_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__, static_folder=\'static\')

# Configurar CORS para permitir todas as origens
CORS(app, origins=os.getenv(\'CORS_ORIGINS\', \'*\'))

# Configuração da aplicação
app.config[\'SECRET_KEY\'] = os.getenv(\'SECRET_KEY\', \'a-default-secret-key-that-should-be-changed\')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix=\'/api\')
app.register_blueprint(analysis_bp, url_prefix=\'/api\')
app.register_blueprint(pdf_bp, url_prefix=\'/api\')

# Configuração do banco de dados usando suas variáveis
database_url = os.getenv(\'DATABASE_URL\')
if database_url:
    try:
        # Fix connection string format if needed
        if database_url.startswith(\'postgresl://\'):
            database_url = database_url.replace(\'postgresl://\', \'postgresql+psycopg2://\', 1)

        # Configuração otimizada para Supabase com timeout aumentado
        app.config[\'SQLALCHEMY_DATABASE_URI\'] = database_url
        app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False
        app.config[\'SQLALCHEMY_ENGINE_OPTIONS\'] = {
            \'pool_pre_ping\': True,
            \'pool_recycle\': 300,
            \'pool_timeout\': 120,  # Increased timeout
            \'pool_size\': 5,       # Increased pool size
            \'max_overflow\': 10,
            \'connect_args\': {
                \'sslmode\': \'require\'
            }
        }
        db.init_app(app)
        logger.info(\

