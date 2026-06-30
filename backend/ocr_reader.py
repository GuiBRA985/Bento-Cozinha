"""
Módulo para extração de itens de notas fiscais
Por enquanto, usa simulação - depois integra com OCR real
"""

import re
import json

def extrair_itens_simulacao(texto_nota):
    """
    Função de exemplo que extrai itens de um texto simples
    Depois pode ser substituída por Tesseract/Google Vision
    """
    # Lista comum de alimentos para reconhecimento
    alimentos_comuns = [
        'arroz', 'feijão', 'macarrão', 'ovo', 'leite', 'carne', 'frango',
        'tomate', 'cebola', 'alho', 'batata', 'cenoura', 'alface',
        'pão', 'queijo', 'presunto', 'manteiga', 'óleo', 'açúcar', 'sal',
        'café', 'chá', 'refrigerante', 'suco', 'água', 'cerveja', 'vinho'
    ]
    
    itens_encontrados = []
    texto_lower = texto_nota.lower()
    
    for alimento in alimentos_comuns:
        if alimento in texto_lower:
            # Tenta encontrar quantidade (ex: "2x", "1kg", "500g")
            padrao = rf'(\d+)\s*(x|kg|g|ml|l|un|unidade)?\s*{alimento}'
            match = re.search(padrao, texto_lower)
            
            quantidade = 1
            if match:
                try:
                    quantidade = int(match.group(1))
                except:
                    quantidade = 1
            
            itens_encontrados.append({
                'nome': alimento,
                'quantidade': quantidade,
                'validade': None  # Seria extraído da nota ou perguntado ao usuário
            })
    
    return itens_encontrados

def extrair_itens_pdf(caminho_pdf):
    """Extrai itens de um arquivo PDF (placeholder)"""
    # Aqui você pode integrar com pdfplumber ou PyPDF2
    print(f"Processando PDF: {caminho_pdf}")
    return []

def extrair_itens_imagem(caminho_imagem):
    """Extrai itens de uma imagem (placeholder)"""
    # Aqui você pode integrar com Tesseract OCR
    print(f"Processando imagem: {caminho_imagem}")
    return []

if __name__ == '__main__':
    # Teste
    texto_teste = "2x arroz 5kg, 1 leite integral, 3 ovos, queijo mussarela"
    itens = extrair_itens_simulacao(texto_teste)
    print(json.dumps(itens, indent=2))
