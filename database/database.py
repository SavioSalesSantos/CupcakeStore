# database/database.py
import sqlite3
import os

# *** NOVO ***: Adicionamos esta função para centralizar a conexão
def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'cupcakes.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 🔥 Isso é mágico: faz as consultas virem como dicionários!
    return conn
# *** FIM DO NOVO ***

def init_db():
    # O banco será criado na PRÓPRIA pasta database/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'cupcakes.db')  # Agora está na mesma pasta
    
    # *** ALTERAÇÃO ***: Agora usamos a nova função get_db_connection() aqui dentro também!
    conn = get_db_connection() # 👈 Mudamos essa linha
    cursor = conn.cursor()
    # *** FIM DA ALTERAÇÃO ***
    
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