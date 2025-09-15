# backend/fix_database.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

def fix_database():
    # Caminho do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'cupcakes.db')
    
    print(f"🔧 Corrigindo banco de dados: {db_path}")
    
    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verifica se a coluna is_admin existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("➕ Adicionando coluna is_admin...")
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')
            print("✅ Coluna is_admin adicionada!")
        else:
            print("ℹ️ Coluna is_admin já existe")
        
        # 2. Procura por qualquer usuário admin existente
        cursor.execute("SELECT * FROM users WHERE username = 'admin' OR email = 'admin@cupcakestore.com'")
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("🔄 Atualizando usuário existente para admin...")
            # Atualiza o usuário existente para ser admin
            cursor.execute(
                "UPDATE users SET is_admin = 1, email = 'admin@cupcakestore.com' WHERE username = 'admin' OR email = 'admin@cupcakestore.com'"
            )
            print("✅ Usuário atualizado para admin!")
        else:
            print("👤 Criando novo usuário admin...")
            # Cria novo usuário admin
            senha_hash = generate_password_hash('admin123')
            cursor.execute(
                'INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)',
                ('admin', 'admin@cupcakestore.com', senha_hash, 1)
            )
            print("✅ Usuário admin criado!")
        
        # 3. Confirma as alterações
        conn.commit()
        
        # 4. Mostra os usuários para verificar
        print("\n📋 Lista de usuários:")
        cursor.execute("SELECT id, username, email, is_admin FROM users")
        for user in cursor.fetchall():
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Admin: {user[3]}")
        
        print("\n🎉 Banco de dados corrigido com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()