from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Carrega receitas
with open('data/receitas.json', 'r', encoding='utf-8') as f:
    receitas = json.load(f)

# Estoque em memória (pra teste, depois usa banco)
estoque = {}

@app.route('/api/estoque', methods=['POST'])
def adicionar_estoque():
    itens = request.json.get('itens', [])
    for item in itens:
        nome = item['nome'].lower()
        estoque[nome] = estoque.get(nome, 0) + item.get('quantidade', 1)
    return jsonify({'estoque': estoque})

@app.route('/api/receitas', methods=['GET'])
def sugerir_receitas():
    disponiveis = set(estoque.keys())
    sugestoes = []
    for r in receitas:
        necessarios = set(r['ingredientes'])
        if necessarios.issubset(disponiveis):
            sugestoes.append(r)
    return jsonify(sugestoes)

@app.route('/api/estados', methods=['GET'])
def estados_icms():
    # Links oficiais por estado (você completa)
    return jsonify({
        'SP': 'https://www.notafiscalpaulista.fazenda.sp.gov.br',
        'RJ': 'https://www.fazenda.rj.gov.br/icms',
        # ... adicione todos
    })

if __name__ == '__main__':
    app.run(debug=True)
