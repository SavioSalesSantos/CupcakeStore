import sqlite3
import os
from werkzeug.security import generate_password_hash  # 👈 Import para criptografia

# 👇 DEFINIMOS base_dir FORA das funções para poder usar em qualquer lugar
base_dir = os.path.dirname(os.path.abspath(__file__))

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    db_path = os.path.join(base_dir, 'cupcakes.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com todas as tabelas necessárias."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            descricao TEXT
        )
    ''')
    
    # Tabela de usuários (ATUALIZADA com campo is_admin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_data TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insere dados de exemplo
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos = [
            ('Cupcake de Chocolate', 8.50, 'Delicioso cupcake de chocolate com cobertura cremosa'),
            ('Cupcake de Baunilha', 7.00, 'Cupcake de baunilha com frosting de buttercream'),
            ('Cupcake de Morango', 9.00, 'Recheado com geléia de morango natural')
        ]
        cursor.executemany('INSERT INTO produtos (nome, preco, descricao) VALUES (?, ?, ?)', produtos)
        
        # 👇 USUÁRIO ADMIN DE TESTE
        senha_hash = generate_password_hash('admin123')
        cursor.execute('INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)', 
                      ('admin', 'admin@cupcakestore.com', senha_hash, 1))
        
        # 👇 USUÁRIO NORMAL DE TESTE
        senha_hash = generate_password_hash('teste123')
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      ('cliente_teste', 'teste@email.com', senha_hash))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Banco de dados criado/atualizado em: {os.path.join(base_dir, 'cupcakes.db')}")

if __name__ == '__main__':
    init_db()