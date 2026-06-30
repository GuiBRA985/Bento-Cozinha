from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

from flask import send_from_directory
import os

# Pega o diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__)
CORS(app)

# Carrega receitas do arquivo JSON
RECEITAS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'receitas.json')

def carregar_receitas():
    with open(RECEITAS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Estoque em memória (para teste - depois pode usar banco)
estoque = {}

# Links oficiais dos programas de ICMS por estado
LINKS_ICMS = {
    'AC': 'https://www.sefaz.ac.gov.br',
    'AL': 'https://www.sefaz.al.gov.br',
    'AP': 'https://www.sefaz.ap.gov.br',
    'AM': 'https://www.sefaz.am.gov.br',
    'BA': 'https://www.sefaz.ba.gov.br',
    'CE': 'https://www.sefaz.ce.gov.br',
    'DF': 'https://www.fazenda.df.gov.br',
    'ES': 'https://www.sefaz.es.gov.br',
    'GO': 'https://www.sefaz.go.gov.br',
    'MA': 'https://www.sefaz.ma.gov.br',
    'MT': 'https://www.sefaz.mt.gov.br',
    'MS': 'https://www.sefaz.ms.gov.br',
    'MG': 'https://www.fazenda.mg.gov.br',
    'PA': 'https://www.sefaz.pa.gov.br',
    'PB': 'https://www.sefaz.pb.gov.br',
    'PR': 'https://www.fazenda.pr.gov.br',
    'PE': 'https://www.sefaz.pe.gov.br',
    'PI': 'https://www.sefaz.pi.gov.br',
    'RJ': 'https://www.fazenda.rj.gov.br',
    'RN': 'https://www.sefaz.rn.gov.br',
    'RS': 'https://www.sefaz.rs.gov.br',
    'RO': 'https://www.sefaz.ro.gov.br',
    'RR': 'https://www.sefaz.rr.gov.br',
    'SC': 'https://www.sefaz.sc.gov.br',
    'SP': 'https://www.notafiscalpaulista.fazenda.sp.gov.br',
    'SE': 'https://www.sefaz.se.gov.br',
    'TO': 'https://www.sefaz.to.gov.br'
}

@app.route('/')
def home():
    return jsonify({'message': 'API da Cozinha Inteligente funcionando!'})

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
    
    # Filtra receitas que usam apenas o que está disponível
    sugestoes = []
    for r in receitas:
        ingredientes_necessarios = set(r['ingredientes'])
        if ingredientes_necessarios.issubset(disponiveis):
            sugestoes.append(r)
    
    # Ordena por número de ingredientes (mais simples primeiro)
    sugestoes.sort(key=lambda x: len(x['ingredientes']))
    
    return jsonify({
        'sugestoes': sugestoes,
        'total': len(sugestoes),
        'estoque_atual': list(estoque.keys())
    })

@app.route('/api/receitas/parciais', methods=['GET'])
def sugerir_receitas_parciais():
    """Sugere receitas que usam pelo menos 70% dos ingredientes disponíveis"""
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
