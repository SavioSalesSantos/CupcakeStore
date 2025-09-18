# correcao_automatica.py - Coloque na pasta raiz
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database.database import get_db_connection

def corrigir_todas_sequencias():
    """Corrige a sequência de TODAS as tabelas automaticamente"""
    try:
        conn = get_db_connection()
        
        # Lista de todas as tabelas com autoincrement
        tabelas = ['users', 'produtos', 'orders']
        
        for tabela in tabelas:
            # Busca o maior ID atual
            result = conn.execute(f"SELECT MAX(id) as max_id FROM {tabela}").fetchone()
            max_id = result['max_id'] if result['max_id'] is not None else 0
            
            # Corrige a sequência
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabela}'")
            conn.execute(f"INSERT INTO sqlite_sequence (name, seq) VALUES ('{tabela}', ?)", (max_id,))
            
            print(f"✅ Sequência de {tabela} corrigida. Próximo ID: {max_id + 1}")
        
        conn.commit()
        conn.close()
        print("🎉 Todas as sequências foram corrigidas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir sequências: {e}")
        return False

if __name__ == '__main__':
    corrigir_todas_sequencias()