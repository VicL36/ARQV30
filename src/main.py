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
app = Flask(__name__, static_folder='static')
CORS(app)

# Configurar o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(analysis_bp, url_prefix='/analysis')
app.register_blueprint(pdf_bp, url_prefix='/pdf')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))


