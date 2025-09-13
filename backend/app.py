from flask import Flask, render_template
import os
import sqlite3 

# Obtém o caminho absoluto para as pastas frontend
base_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta backend/
frontend_dir = os.path.join(base_dir, '..', 'frontend')

template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

def get_produtos():
    """Função para buscar produtos do banco de dados"""
    try:
        # Conecta ao banco na pasta database/
        db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos')
        produtos = cursor.fetchall()
        conn.close()
        
        return produtos
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return []

@app.route('/')
def home():
    produtos = get_produtos()
    return render_template('index.html', produtos=produtos)

# === NOVA ROTA DO CARRINHO (ADICIONE ISSO) ===
@app.route('/carrinho')
def carrinho():
    """Página do carrinho de compras"""
    try:
        # Busca os detalhes dos produtos no carrinho
        db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Simula produtos no carrinho (IDs 1, 2, 3)
        cursor.execute('SELECT * FROM produtos WHERE id IN (1, 2, 3)')
        produtos_carrinho = cursor.fetchall()
        conn.close()
        
        total = sum(produto[2] for produto in produtos_carrinho)
        
        return render_template('carrinho.html', 
                             produtos=produtos_carrinho, 
                             total=total)
    except Exception as e:
        print(f"❌ Erro no carrinho: {e}")
        return render_template('carrinho.html', produtos=[], total=0)
# === FIM DA NOVA ROTA ===

if __name__ == '__main__':
    print(f"📁 Templates path: {template_dir}")
    print(f"📁 Static path: {static_dir}")
    print(f"✅ Template exists: {os.path.exists(template_dir)}")
    print(f"✅ Static exists: {os.path.exists(static_dir)}")
    
    db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
    print(f"✅ Database exists: {os.path.exists(db_path)}")
    
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True)