from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# Fallback: se não achar, tenta caminho relativo
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.join(os.getcwd(), 'frontend')

print(f"📁 Servindo frontend de: {FRONTEND_DIR}")

# === ROTAS DO FRONTEND ===
@app.route('/')
def index():
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        return jsonify({'erro': str(e), 'frontend_dir': FRONTEND_DIR}), 500

@app.route('/<path:filename>')
def static_files(filename):
    try:
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception as e:
        return jsonify({'erro': f'Arquivo {filename} não encontrado'}), 404

# === RESTO DA API (mantenha o código que você já tinha) ===
# ... (todo o resto do seu app.py aqui)
