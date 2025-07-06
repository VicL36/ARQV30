import os
import logging
import time
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .database import db
from .routes.user import user_bp
from .routes.analysis import analysis_bp
from .routes.pdf_generator import pdf_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__, static_folder='static')

# Configurar CORS para permitir todas as origens
CORS(app, origins=os.getenv('CORS_ORIGINS', '*'))

# Configuração da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-secret-key-that-should-be-changed')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(pdf_bp, url_prefix='/api')

# Configuração do banco de dados usando suas variáveis
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        # Fix connection string format if needed
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        # Configuração otimizada para Supabase com timeout aumentado
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 120,  # Increased timeout
            'pool_size': 5,      # Increased pool size
            'max_overflow': 10,  # Increased overflow
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 120,  # Increased connection timeout
                'application_name': 'UP_Lancamentos_Avatar_App',
                'keepalives_idle': 600,
                'keepalives_interval': 30,
                'keepalives_count': 3,
                'options': '-c statement_timeout=300000'  # 5 minute statement timeout
            }
        }
        
        db.init_app(app)
        
        # Teste de conexão com retry logic
        with app.app_context():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    from sqlalchemy import text
                    result = db.session.execute(text('SELECT 1'))
                    logger.info("✅ Conexão com Supabase estabelecida com sucesso!")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente... Erro: {str(e)[:100]}...")
                        time.sleep(2)  # Wait 2 seconds before retry
                    else:
                        logger.warning(f"⚠️ Conexão com banco não disponível após {max_retries} tentativas: {str(e)[:100]}...")
                        logger.info("📱 Aplicação funcionará com funcionalidades limitadas")
                        
    except Exception as e:
        logger.warning(f"⚠️ Erro na configuração do banco de dados: {str(e)[:100]}...")
        logger.info("📱 Aplicação funcionará sem persistência de dados")
else:
    logger.warning("📋 DATABASE_URL não encontrada. Executando sem funcionalidades de banco de dados.")

# Rota de health check
@app.route('/health')
def health_check():
    # Verificar status das APIs e banco
    gemini_status = 'configured' if os.getenv('GEMINI_API_KEY') else 'not_configured'
    supabase_status = 'configured' if os.getenv('SUPABASE_URL') else 'not_configured'
    database_status = 'configured' if database_url else 'not_configured'
    
    # Teste rápido de conexão com banco
    db_connection = 'disconnected'
    if database_url:
        try:
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db_connection = 'connected'
        except Exception as e:
            db_connection = f'error: {str(e)[:50]}...'
    
    return jsonify({
        'status': 'healthy',
        'message': 'UP Lançamentos - Arqueologia do Avatar com Gemini Pro 2.5',
        'services': {
            'gemini_ai': gemini_status,
            'supabase': supabase_status,
            'database': database_status,
            'db_connection': db_connection
        },
        'version': '3.1.0',
        'features': [
            'Gemini Pro 2.5 Integration',
            'Real-time Internet Research',
            'Ultra-detailed Avatar Analysis',
            'Advanced Market Intelligence',
            'Comprehensive Competitor Analysis',
            'PDF Report Generation',
            'Interactive Charts & Infographics'
        ],
        'environment_vars': {
            'DATABASE_URL': 'configured' if database_url else 'missing',
            'GEMINI_API_KEY': 'configured' if os.getenv('GEMINI_API_KEY') else 'missing',
            'SUPABASE_URL': 'configured' if os.getenv('SUPABASE_URL') else 'missing',
            'SUPABASE_SERVICE_ROLE_KEY': 'configured' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'missing'
        }
    })

# Rota para servir arquivos estáticos e SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Add database connection test endpoint
@app.route('/api/test-db')
def test_database():
    """Test database connection endpoint"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT version()'))
        version = result.fetchone()[0]
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'database_version': version
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
