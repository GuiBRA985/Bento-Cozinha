"""
Módulo de banco de dados - SQLite para começar
Depois migra para PostgreSQL no Render
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cozinha.db')

def get_connection():
    """Retorna conexão com o banco SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria as tabelas se não existirem"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            estado TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de estoque
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nome TEXT,
            quantidade REAL,
            unidade TEXT DEFAULT 'un',
            validade DATE,
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de notas fiscais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            arquivo TEXT,
            data_compra DATE,
            total REAL,
            itens TEXT, -- JSON
            processada BOOLEAN DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de receitas favoritas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receitas_favoritas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nome_receita TEXT,
            data_salva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def salvar_estoque(usuario_id, itens):
    """Salva itens no estoque do usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for item in itens:
        cursor.execute('''
            INSERT INTO estoque (usuario_id, nome, quantidade, unidade, validade)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            usuario_id,
            item['nome'],
            item.get('quantidade', 1),
            item.get('unidade', 'un'),
            item.get('validade', None)
        ))
    
    conn.commit()
    conn.close()

def buscar_estoque(usuario_id):
    """Retorna todo o estoque do usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM estoque WHERE usuario_id = ?', (usuario_id,))
    resultados = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in resultados]

def limpar_estoque(usuario_id):
    """Remove todos os itens do estoque"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM estoque WHERE usuario_id = ?', (usuario_id,))
    conn.commit()
    conn.close()

# Inicializa o banco ao importar
init_db()
