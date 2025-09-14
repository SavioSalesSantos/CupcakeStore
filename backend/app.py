from flask import Flask, render_template, session, redirect, url_for
import os
import sqlite3
from datetime import timedelta

# Obtém o caminho absoluto para as pastas frontend
base_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta backend/
frontend_dir = os.path.join(base_dir, '..', 'frontend')

template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

# 🔐 Chave secreta para sessions
app.secret_key = 'sua_chave_secreta_super_segura_aqui_2024'
app.permanent_session_lifetime = timedelta(days=7)

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

# === NOVAS ROTAS DO CARRINHO COM SESSÕES ===
@app.route('/adicionar/<int:id_produto>')
def adicionar_carrinho(id_produto):
    """Adiciona produto ao carrinho na session"""
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    session['carrinho'].append(id_produto)
    session.modified = True
    
    return redirect(url_for('home'))

@app.route('/remover/<int:id_produto>')
def remover_carrinho(id_produto):
    """Remove produto do carrinho"""
    if 'carrinho' in session:
        if id_produto in session['carrinho']:
            session['carrinho'].remove(id_produto)
            session.modified = True
    
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    """Página do carrinho com produtos reais"""
    carrinho_ids = session.get('carrinho', [])
    
    if not carrinho_ids:
        return render_template('carrinho.html', produtos=[], total=0)
    
    try:
        db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        
        cursor.execute(query, carrinho_ids)
        produtos_carrinho = cursor.fetchall()
        conn.close()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
        total = sum(produto[2] * quantidades[produto[0]] for produto in produtos_carrinho)
        
        return render_template('carrinho.html', 
                             produtos=produtos_carrinho,
                             quantidades=quantidades,
                             total=total)
    except Exception as e:
        print(f"❌ Erro no carrinho: {e}")
        return render_template('carrinho.html', produtos=[], total=0)

@app.route('/limpar-carrinho')
def limpar_carrinho():
    """Limpa todo o carrinho"""
    session.pop('carrinho', None)
    return redirect(url_for('carrinho'))

@app.route('/get-contador-carrinho')
def get_contador_carrinho():
    """Retorna a quantidade de itens no carrinho"""
    carrinho_ids = session.get('carrinho', [])
    return {'quantidade': len(carrinho_ids)}

@app.route('/get-nome-produto/<int:id_produto>')
def get_nome_produto(id_produto):
    """Retorna o nome do produto pelo ID"""
    try:
        db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM produtos WHERE id = ?', (id_produto,))
        produto = cursor.fetchone()
        conn.close()
        
        return {'nome': produto[0] if produto else 'Produto'}
    except Exception as e:
        return {'nome': 'Produto'}

# === FIM DAS NOVAS ROTAS ===

if __name__ == '__main__':
    print(f"📁 Templates path: {template_dir}")
    print(f"📁 Static path: {static_dir}")
    print(f"✅ Template exists: {os.path.exists(template_dir)}")
    print(f"✅ Static exists: {os.path.exists(static_dir)}")
    
    db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
    print(f"✅ Database exists: {os.path.exists(db_path)}")
    
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True)

    