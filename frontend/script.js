const API = 'https://seu-app.onrender.com/api'; // muda depois

async function lerNota() {
  const file = document.getElementById('notaInput').files[0];
  if (!file) return alert('Selecione uma nota!');
  
  // Simulação: extrair itens manualmente (depois integra OCR)
  const itens = [
    { nome: 'arroz', quantidade: 1 },
    { nome: 'ovo', quantidade: 6 }
  ];
  
  const resp = await fetch(`${API}/estoque`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itens })
  });
  const data = await resp.json();
  document.getElementById('estoque').innerHTML = Object.entries(data.estoque)
    .map(([k,v]) => `<span class="badge">${k}: ${v}</span>`).join(' ');
}

async function buscarReceitas() {
  const resp = await fetch(`${API}/receitas`);
  const receitas = await resp.json();
  document.getElementById('receitas').innerHTML = receitas.map(r => 
    `<div class="p-2 bg-white shadow rounded mt-2">🍽️ ${r.nome} - ${r.tempo}min</div>`
  ).join('');
}

function redirecionarICMS() {
  const estado = document.getElementById('estadoSelect').value;
  fetch(`${API}/estados`)
    .then(r => r.json())
    .then(data => window.open(data[estado], '_blank'));
}
