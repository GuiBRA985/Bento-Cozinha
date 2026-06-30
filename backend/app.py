from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === NOVO: Configuração para servir o frontend ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# Carrega receitas do arquivo JSON
RECEITAS_PATH = os.path.join(BASE_DIR, 'data', 'receitas.json')

def carregar_receitas():
    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Estoque em memória (para teste)
estoque = {}

# Links oficiais dos programas de ICMS por estado
LINKS_ICMS = {
    'SP': 'https://www.notafiscalpaulista.fazenda.sp.gov.br',
    'RJ': 'https://www.fazenda.rj.gov.br',
    'MG': 'https://www.fazenda.mg.gov.br',
    'PR': 'https://www.fazenda.pr.gov.br',
    'RS': 'https://www.sefaz.rs.gov.br',
    'SC': 'https://www.sefaz.sc.gov.br',
    'BA': 'https://www.sefaz.ba.gov.br',
    'PE': 'https://www.sefaz.pe.gov.br',
    'CE': 'https://www.sefaz.ce.gov.br',
    'DF': 'https://www.fazenda.df.gov.br',
    'GO': 'https://www.sefaz.go.gov.br',
    'ES': 'https://www.sefaz.es.gov.br',
    'AM': 'https://www.sefaz.am.gov.br',
    'PA': 'https://www.sefaz.pa.gov.br',
    'MT': 'https://www.sefaz.mt.gov.br',
    'MS': 'https://www.sefaz.ms.gov.br',
    'AL': 'https://www.sefaz.al.gov.br',
    'AP': 'https://www.sefaz.ap.gov.br',
    'MA': 'https://www.sefaz.ma.gov.br',
    'PB': 'https://www.sefaz.pb.gov.br',
    'PI': 'https://www.sefaz.pi.gov.br',
    'RN': 'https://www.sefaz.rn.gov.br',
    'RO': 'https://www.sefaz.ro.gov.br',
    'RR': 'https://www.sefaz.rr.gov.br',
    'SE': 'https://www.sefaz.se.gov.br',
    'TO': 'https://www.sefaz.to.gov.br'
}

# ============================================
# ROTA PRINCIPAL (NÚMERO 1 - Substitui a antiga)
# ============================================
@app.route('/')
def index():
    """Serve a página inicial index.html"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ============================================
# ROTA PARA ARQUIVOS ESTÁTICOS (NÚMERO 3 - A que você pediu)
# ============================================
@app.route('/<path:filename>')
def static_files(filename):
    """Serve arquivos CSS, JS e imagens da pasta frontend"""
    return send_from_directory(FRONTEND_DIR, filename)

# ============================================
# ROTAS DA API (permanecem iguais)
# ============================================
@app.route('/api/estoque', methods=['GET'])
def get_estoque():
    return jsonify(estoque)

@app.route('/api/estoque', methods=['POST'])
def adicionar_estoque():
    data = request.json
    itens = data.get('itens', [])
    
    for item in itens:
        nome = item['nome'].lower().strip()
        quantidade = item.get('quantidade', 1)
        validade = item.get('validade', None)
        
        if nome in estoque:
            estoque[nome]['quantidade'] += quantidade
        else:
            estoque[nome] = {
                'quantidade': quantidade,
                'validade': validade,
                'data_adicao': datetime.now().isoformat()
            }
    
    return jsonify({'estoque': estoque, 'mensagem': f'{len(itens)} item(ns) adicionado(s)!'})

@app.route('/api/estoque/<item>', methods=['DELETE'])
def remover_item(item):
    item = item.lower().strip()
    if item in estoque:
        del estoque[item]
        return jsonify({'mensagem': f'{item} removido do estoque!'})
    return jsonify({'erro': 'Item não encontrado'}), 404

@app.route('/api/receitas', methods=['GET'])
def sugerir_receitas():
    receitas = carregar_receitas()
    disponiveis = set(estoque.keys())
    
    sugestoes = []
    for r in receitas:
        ingredientes_necessarios = set(r['ingredientes'])
        if ingredientes_necessarios.issubset(disponiveis):
            sugestoes.append(r)
    
    sugestoes.sort(key=lambda x: len(x['ingredientes']))
    
    return jsonify({
        'sugestoes': sugestoes,
        'total': len(sugestoes),
        'estoque_atual': list(estoque.keys())
    })

@app.route('/api/receitas/parciais', methods=['GET'])
def sugerir_receitas_parciais():
    receitas = carregar_receitas()
    disponiveis = set(estoque.keys())
    
    sugestoes = []
    for r in receitas:
        necessarios = set(r['ingredientes'])
        disponiveis_para_receita = necessarios.intersection(disponiveis)
        proporcao = len(disponiveis_para_receita) / len(necessarios)
        
        if proporcao >= 0.7 and proporcao < 1.0:
            sugestoes.append({
                **r,
                'faltam': list(necessarios - disponiveis),
                'proporcao': round(proporcao * 100)
            })
    
    sugestoes.sort(key=lambda x: x['proporcao'], reverse=True)
    return jsonify(sugestoes)

@app.route('/api/estados', methods=['GET'])
def listar_estados():
    return jsonify(LINKS_ICMS)

@app.route('/api/estados/<uf>', methods=['GET'])
def link_icms(uf):
    uf = uf.upper()
    if uf in LINKS_ICMS:
        return jsonify({'uf': uf, 'link': LINKS_ICMS[uf]})
    return jsonify({'erro': 'Estado não encontrado'}), 404

@app.route('/api/limpar_estoque', methods=['POST'])
def limpar_estoque():
    estoque.clear()
    return jsonify({'mensagem': 'Estoque limpo!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
