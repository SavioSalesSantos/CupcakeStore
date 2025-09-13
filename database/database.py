import sqlite3
import os

def init_db():
    # O banco será criado na PRÓPRIA pasta database/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'cupcakes.db')  # Agora está na mesma pasta
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Cria tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            descricao TEXT
        )
    ''')
    
    # Insere alguns dados de exemplo
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos = [
            ('Cupcake de Chocolate', 8.50, 'Delicioso cupcake de chocolate com cobertura cremosa'),
            ('Cupcake de Baunilha', 7.00, 'Cupcake de baunilha com frosting de buttercream'),
            ('Cupcake de Morango', 9.00, 'Recheado com geléia de morango natural')
        ]
        cursor.executemany('INSERT INTO produtos (nome, preco, descricao) VALUES (?, ?, ?)', produtos)
    
    conn.commit()
    conn.close()
    print(f"✅ Banco de dados criado em: {db_path}")

if __name__ == '__main__':
    init_db()