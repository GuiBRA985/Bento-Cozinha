// Configuração da API
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : 'https://bento-cozinha.onrender.com';  // <-- MUDE PARA SUA URL DO RENDER DEPOIS

// ============================================
// 1. FUNÇÕES DO ESTOQUE
// ============================================

async function processarNota() {
    const fileInput = document.getElementById('notaInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('📄 Por favor, selecione uma nota fiscal primeiro!');
        return;
    }

    // Mostra loading
    const btn = document.querySelector('button[onclick="processarNota()"]');
    btn.textContent = '⏳ Processando...';
    btn.disabled = true;

    try {
        // Aqui você pode integrar com OCR
        // Por enquanto, vamos simular a extração com base no nome do arquivo
        const itens = await extrairItensSimulados(file);
        
        if (itens.length === 0) {
            alert('❌ Não foi possível extrair itens dessa nota. Tente outra.');
            btn.textContent = 'Adicionar ao Estoque';
            btn.disabled = false;
            return;
        }

        // Envia para o backend
        const response = await fetch(`${API_URL}/estoque`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ itens })
        });

        const data = await response.json();
        alert(`✅ ${data.mensagem}`);
        
        // Limpa o input
        fileInput.value = '';
        // Atualiza a lista de estoque
        await carregarEstoque();
        
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao processar a nota. Tente novamente.');
    }

    btn.textContent = 'Adicionar ao Estoque';
    btn.disabled = false;
}

async function extrairItensSimulados(file) {
    // Simulação: extrai palavras-chave do nome do arquivo
    // Em produção, use OCR real (Tesseract, Google Vision, etc.)
    
    const nomeArquivo = file.name.toLowerCase();
    
    // Lista de alimentos comuns para detectar
    const alimentos = [
        'arroz', 'feijao', 'macarrao', 'ovo', 'leite', 'carne', 'frango',
        'tomate', 'cebola', 'alho', 'batata', 'cenoura', 'alface',
        'pao', 'queijo', 'presunto', 'manteiga', 'oleo', 'acucar', 'sal',
        'cafe', 'cha', 'refrigerante', 'suco', 'agua', 'cerveja', 'vinho',
        'farinha', 'milho', 'ervilha', 'lentilha', 'grao de bico'
    ];
    
    const itens = [];
    for (const alimento of alimentos) {
        if (nomeArquivo.includes(alimento)) {
            itens.push({
                nome: alimento,
                quantidade: 1,
                validade: null
            });
        }
    }
    
    // Se não encontrou nada, usa itens padrão para demonstração
    if (itens.length === 0) {
        itens.push({ nome: 'arroz', quantidade: 2, validade: null });
        itens.push({ nome: 'ovo', quantidade: 6, validade: null });
        itens.push({ nome: 'tomate', quantidade: 3, validade: null });
    }
    
    return itens;
}

async function carregarEstoque() {
    try {
        const response = await fetch(`${API_URL}/estoque`);
        const estoque = await response.json();
        
        const container = document.getElementById('estoqueList');
        
        const itens = Object.keys(estoque);
        if (itens.length === 0) {
            container.innerHTML = '<span class="text-gray-400 text-sm">Nenhum item ainda. Adicione sua primeira nota!</span>';
            return;
        }
        
        container.innerHTML = itens.map(nome => {
            const qtd = estoque[nome].quantidade || 1;
            return `<span class="badge-estoque">${nome} ${qtd > 1 ? `×${qtd}` : ''}</span>`;
        }).join('');
        
    } catch (error) {
        console.error('Erro ao carregar estoque:', error);
    }
}

async function limparEstoque() {
    if (!confirm('🗑️ Tem certeza que deseja limpar todo o estoque?')) return;
    
    try {
        await fetch(`${API_URL}/limpar_estoque`, { method: 'POST' });
        await carregarEstoque();
        document.getElementById('receitasList').innerHTML = 
            '<p class="text-gray-400 text-center text-sm">Adicione ingredientes para ver receitas!</p>';
        alert('✅ Estoque limpo!');
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao limpar estoque.');
    }
}

// ============================================
// 2. FUNÇÕES DE RECEITAS
// ============================================

async function buscarReceitas() {
    const container = document.getElementById('receitasList');
    container.innerHTML = '<p class="text-gray-400 text-center text-sm">⏳ Buscando receitas...</p>';
    
    try {
        const response = await fetch(`${API_URL}/receitas`);
        const data = await response.json();
        
        if (data.sugestoes.length === 0) {
            container.innerHTML = `
                <div class="text-center py-6">
                    <span class="text-4xl">😅</span>
                    <p class="text-gray-500 mt-2">Nenhuma receita encontrada com seus ingredientes.</p>
                    <p class="text-gray-400 text-sm">Tente adicionar mais itens ao estoque!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = data.sugestoes.map((receita, index) => `
            <div class="receita-card bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4 border border-orange-100 hover:shadow-md transition">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-semibold text-gray-800">${receita.nome}</h3>
                        <p class="text-sm text-gray-500 mt-1">⏱️ ${receita.tempo || 20} min • ${receita.ingredientes.length} ingredientes</p>
                    </div>
                    <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">✅ Disponível</span>
                </div>
                <p class="text-sm text-gray-600 mt-2">${receita.modo_preparo || 'Modo de preparo: combine os ingredientes e cozinhe.'}</p>
                <div class="mt-2 flex flex-wrap gap-1">
                    ${receita.ingredientes.map(ing => 
                        `<span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">${ing}</span>`
                    ).join('')}
                </div>
                <button onclick="usarReceita('${receita.nome}')" class="mt-3 text-sm bg-orange-500 hover:bg-orange-600 text-white px-4 py-1.5 rounded-full transition">
                    👨‍🍳 Preparar!
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p class="text-red-500 text-center">❌ Erro ao buscar receitas.</p>';
    }
}

async function usarReceita(nomeReceita) {
    alert(`🍳 Preparando: ${nomeReceita}\n\nEssa funcionalidade vai descontar os ingredientes do estoque em breve!`);
    // Em breve: remover ingredientes do estoque após usar a receita
}

// ============================================
// 3. FUNÇÕES DE ICMS
// ============================================

async function redirecionarICMS() {
    const select = document.getElementById('estadoSelect');
    const uf = select.value;
    
    if (!uf) {
        alert('⚠️ Selecione seu estado primeiro!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/estados/${uf}`);
        const data = await response.json();
        
        if (data.link) {
            window.open(data.link, '_blank');
        } else {
            alert('❌ Link não encontrado para este estado.');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao buscar o link do estado.');
    }
}

// ============================================
// 4. INICIALIZAÇÃO
// ============================================

// Carrega estoque ao abrir a página
document.addEventListener('DOMContentLoaded', () => {
    carregarEstoque();
    
    // Evento para Enter no campo de texto (se quiser adicionar manualmente depois)
    console.log('🍳 Minha Cozinha carregada!');
});
