import sqlite3
import os
from werkzeug.security import generate_password_hash

base_dir = os.path.dirname(os.path.abspath(__file__))

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    db_path = os.path.join(base_dir, 'cupcakes.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def atualizar_banco():
    """Adiciona campo de imagem aos produtos existentes"""
    try:
        conn = get_db_connection()
        
        # Verifica se a coluna imagem já existe
        colunas = conn.execute("PRAGMA table_info(produtos)").fetchall()
        coluna_existe = any(coluna[1] == 'imagem' for coluna in colunas)
        
        if not coluna_existe:
            print("🔄 Adicionando coluna 'imagem' à tabela produtos...")
            conn.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
            conn.commit()
            print("✅ Coluna 'imagem' adicionada com sucesso!")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")

def atualizar_banco_pedidos():
    """Adiciona campo de metodo_pagamento aos pedidos existentes"""
    try:
        conn = get_db_connection()
        
        # Verifica se a coluna metodo_pagamento já existe
        colunas = conn.execute("PRAGMA table_info(orders)").fetchall()
        coluna_existe = any(coluna[1] == 'metodo_pagamento' for coluna in colunas)
        
        if not coluna_existe:
            print("🔄 Adicionando coluna 'metodo_pagamento' à tabela orders...")
            conn.execute("ALTER TABLE orders ADD COLUMN metodo_pagamento TEXT DEFAULT 'cartao'")
            conn.commit()
            print("✅ Coluna 'metodo_pagamento' adicionada com sucesso!")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de pedidos: {e}")

def atualizar_banco_enderecos():
    """Adiciona campos de endereço aos usuários existentes"""
    try:
        conn = get_db_connection()
        
        # Lista de campos de endereço a serem adicionados
        campos_endereco = [
            'estado', 'cidade', 'bairro', 'rua', 'numero', 'cep'
        ]
        
        for campo in campos_endereco:
            # Verifica se a coluna já existe
            colunas = conn.execute("PRAGMA table_info(users)").fetchall()
            coluna_existe = any(coluna[1] == campo for coluna in colunas)
            
            if not coluna_existe:
                print(f"🔄 Adicionando coluna '{campo}' à tabela users...")
                conn.execute(f"ALTER TABLE users ADD COLUMN {campo} TEXT")
                print(f"✅ Coluna '{campo}' adicionada com sucesso!")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao atualizar banco com endereços: {e}")

def atualizar_banco_entrega():
    """Adiciona campo de forma_entrega aos pedidos existentes - CORREÇÃO DEFINITIVA"""
    try:
        conn = get_db_connection()
        
        # Verifica se a coluna forma_entrega já existe
        colunas = conn.execute("PRAGMA table_info(orders)").fetchall()
        coluna_existe = any(coluna[1] == 'forma_entrega' for coluna in colunas)
        
        if not coluna_existe:
            print("🔄 Adicionando coluna 'forma_entrega' à tabela orders...")
            conn.execute("ALTER TABLE orders ADD COLUMN forma_entrega TEXT DEFAULT 'delivery'")
            conn.commit()
            print("✅ Coluna 'forma_entrega' adicionada com sucesso!")
        else:
            print("✅ Coluna 'forma_entrega' já existe na tabela orders")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de entrega: {e}")

def corrigir_sequencia_usuarios_automatico():
    """Corrige automaticamente a sequência de IDs SEMPRE"""
    try:
        conn = get_db_connection()
        
        # 🔽 CORREÇÃO DEFINITIVA - FORÇA A SEQUÊNCIA
        # Primeiro busca o máximo ID atual
        result = conn.execute("SELECT MAX(id) as max_id FROM users").fetchone()
        max_id = result['max_id'] if result and result['max_id'] is not None else 0
        
        # 🔽 MÉTODO CONFIÁVEL: Recria a tabela se necessário
        conn.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('users', ?)", (max_id,))
        
        conn.commit()
        
        # Verifica se a correção funcionou
        next_seq = conn.execute("SELECT seq FROM sqlite_sequence WHERE name='users'").fetchone()
        if next_seq:
            print(f"✅ Sequência de users garantida. Próximo ID: {next_seq['seq'] + 1}")
        else:
            print("⚠️  Aviso: Sequência não encontrada, mas tabela funciona normalmente")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico na sequência: {e}")
        # Mesmo com erro, a aplicação continua funcionando
        return False

def verificar_e_criar_coluna_forma_entrega():
    """Função específica para verificar e criar a coluna forma_entrega"""
    try:
        conn = get_db_connection()
        
        # Verifica se a coluna existe
        colunas = conn.execute("PRAGMA table_info(orders)").fetchall()
        coluna_existe = any(coluna[1] == 'forma_entrega' for coluna in colunas)
        
        if not coluna_existe:
            print("🚨 COLUNA FORMA_ENTREGA NÃO ENCONTRADA! CRIANDO...")
            conn.execute("ALTER TABLE orders ADD COLUMN forma_entrega TEXT DEFAULT 'delivery'")
            conn.commit()
            print("✅ Coluna 'forma_entrega' criada com sucesso!")
        else:
            print("✅ Coluna 'forma_entrega' já existe")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao criar coluna forma_entrega: {e}")
        return False

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
            descricao TEXT,
            imagem TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            estado TEXT,
            cidade TEXT,
            bairro TEXT,
            rua TEXT,
            numero TEXT,
            cep TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de pedidos (ATUALIZADA COM FORMA_ENTREGA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_data TEXT NOT NULL,
            total_amount REAL NOT NULL,
            metodo_pagamento TEXT DEFAULT 'cartao',
            forma_entrega TEXT DEFAULT 'delivery',
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insere dados de exemplo
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos = [
            ('Cupcake de Chocolate', 8.50, 'Delicioso cupcake de chocolate com cobertura cremosa', None),
            ('Cupcake de Baunilha', 7.00, 'Cupcake de baunilha com frosting de buttercream', None),
            ('Cupcake de Morango', 9.00, 'Recheado com geléia de morango natural', None)
        ]
        cursor.executemany('INSERT INTO produtos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)', produtos)
        
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
    
    # 👇 CHAMA TODAS AS ATUALIZAÇÕES - ORDEM CRÍTICA
    print("🔄 Iniciando atualizações do banco...")
    atualizar_banco()
    atualizar_banco_pedidos()
    atualizar_banco_enderecos()
    atualizar_banco_entrega()
    corrigir_sequencia_usuarios_automatico()
    
    # 👇 VERIFICAÇÃO EXTRA PARA GARANTIR
    verificar_e_criar_coluna_forma_entrega()
    
    print(f"✅ Banco de dados criado/atualizado em: {os.path.join(base_dir, 'cupcakes.db')}")

if __name__ == '__main__':
    init_db()