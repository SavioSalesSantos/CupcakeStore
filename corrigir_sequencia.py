# corrigir_sequencia.py
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database.database import get_db_connection, corrigir_sequencia_usuarios

def forcar_correcao_sequencia():
    """Força a correção da sequência de IDs"""
    print("🔄 Forçando correção da sequência de IDs...")
    corrigir_sequencia_usuarios()
    print("✅ Correção concluída!")

if __name__ == '__main__':
    forcar_correcao_sequencia()