from flask import Flask, render_template, session, redirect, url_for, request
import os
import sqlite3
import random
from werkzeug.security import generate_password_hash, check_password_hash  # 👈 Para criptografar senhas
from flask import flash  # 👈 Para mostrar mensagens flash
from datetime import datetime
from datetime import timedelta
try:
    from database.database import get_db_connection
except ModuleNotFoundError:
    # Se não encontrar, tenta importar do caminho relativo
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database.database import get_db_connection

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
    """Função para buscar produtos do banco de dados (AGORA SIMPLIFICADA)"""
    try:
        conn = get_db_connection()  # 👈 Usa a conexão centralizada!
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        conn.close()
        return produtos
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return []

@app.route('/')
def home():
    # 👇 OBTÉM O TERMO DE PESQUISA DA URL (se existir)
    termo_pesquisa = request.args.get('q', '').lower()
    
    # 👇 OBTÉM TODOS OS PRODUTOS
    produtos = get_produtos()
    
    # 👇 FILTRA OS PRODUTOS SE HOUVER UM TERMO DE PESQUISA
    if termo_pesquisa:
        produtos_filtrados = []
        for produto in produtos:
            # Converte para dicionário para facilitar o acesso
            produto_dict = dict(produto)
            # Verifica se o termo de pesquisa está no nome ou descrição
            if (termo_pesquisa in produto_dict['nome'].lower() or 
                termo_pesquisa in produto_dict['descricao'].lower()):
                produtos_filtrados.append(produto_dict)
        produtos_list = produtos_filtrados
    else:
        # Se não há pesquisa, mostra todos os produtos
        produtos_list = [dict(produto) for produto in produtos]
    
    # 👇 PASSA O TERMO DE PESQUISA PARA O TEMPLATE PARA MOSTRAR NO CAMPO
    return render_template('index.html', produtos=produtos_list, termo_pesquisa=termo_pesquisa)

# === NOVAS ROTAS DO CARRINHO COM SESSÕES ===
@app.route('/adicionar/<int:id_produto>')
def adicionar_carrinho(id_produto):
    """Adiciona produto ao carrinho na session"""
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    session['carrinho'].append(id_produto)
    session.modified = True
    
    # 👇 VERIFICAMOS DE ONDE A REQUISIÇÃO VEIO PARA REDIRECIONAR CORRETAMENTE
    # Se veio da página do carrinho, voltamos para o carrinho
    # Se veio de qualquer outra página, voltamos para a home
    referer = request.headers.get('Referer')
    if referer and '/carrinho' in referer:
        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('home'))

@app.route('/remover/<int:id_produto>')
def remover_carrinho(id_produto):
    """Remove produto do carrinho"""
    if 'carrinho' in session:
        if id_produto in session['carrinho']:
            session['carrinho'].remove(id_produto)
            session.modified = True
    
    # 👇 MESMA LÓGICA: Se veio do carrinho, volta para o carrinho
    referer = request.headers.get('Referer')
    if referer and '/carrinho' in referer:
        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('home'))

@app.route('/carrinho')
def carrinho():
    """Página do carrinho com produtos reais (AGORA SIMPLIFICADA)"""
    carrinho_ids = session.get('carrinho', [])
    
    if not carrinho_ids:
        return render_template('carrinho.html', produtos=[], total=0)
    
    try:
        # 👇 Usa a conexão centralizada!
        conn = get_db_connection()
        
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        
        # 👇 Note: conn.execute() instead of cursor.execute()
        produtos_carrinho = conn.execute(query, carrinho_ids).fetchall()
        conn.close()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
        # 👇 Pequena melhoria: converter para lista de dicionários
        produtos_list = [dict(produto) for produto in produtos_carrinho]
        
        total = sum(produto['preco'] * quantidades[produto['id']] for produto in produtos_list)
        
        return render_template('carrinho.html', 
                             produtos=produtos_list,
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
    """Retorna o nome do produto pelo ID (AGORA SIMPLIFICADA)"""
    try:
        # 👇 Usa a conexão centralizada!
        conn = get_db_connection()
        produto = conn.execute('SELECT nome FROM produtos WHERE id = ?', (id_produto,)).fetchone()
        conn.close()
        
        return {'nome': produto['nome'] if produto else 'Produto'}
    except Exception as e:
        return {'nome': 'Produto'}

# === NOVAS ROTAS PARA FINALIZAÇÃO DE COMPRA ===
@app.route('/finalizar-compra')
def finalizar_compra():
    """Página de confirmação de compra finalizada"""
    # Simula um ID de pedido (em um sistema real, viria do banco de dados)
    pedido_id = f"{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Calcula o total do carrinho atual
    carrinho_ids = session.get('carrinho', [])
    total = 0
    if carrinho_ids:
        conn = get_db_connection()
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        produtos_carrinho = conn.execute(query, carrinho_ids).fetchall()
        conn.close()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
        total = sum(produto['preco'] * quantidades[produto['id']] for produto in produtos_carrinho)
    
    # Limpa o carrinho após finalizar a compra
    session.pop('carrinho', None)
    
    return render_template('compra_finalizada.html', 
                         pedido_id=pedido_id,
                         data_pedido=datetime.now().strftime('%d/%m/%Y %H:%M'),
                         total=total)

@app.route('/meus-pedidos')
def meus_pedidos():
    """Página de histórico de pedidos (será implementada depois)"""
    return "Página de meus pedidos - Em construção 🚧"

# 👇 ROTA DE REGISTRO (COMPLETA)
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de cadastro"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            
            # Verifica se username ou email já existem
            user_exists = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?', 
                (username, email)
            ).fetchone()
            
            if user_exists:
                flash('Username ou email já cadastrados!', 'error')
                return render_template('register.html')
            
            # Cria hash da senha (criptografa)
            password_hash = generate_password_hash(password)
            
            # Insere novo usuário no banco
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"❌ Erro no registro: {e}")
            flash('Erro ao criar conta. Tente novamente.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

# 👇 ROTA DE LOGIN (COMPLETA)
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            
            # Busca usuário pelo email
            user = conn.execute(
                'SELECT * FROM users WHERE email = ?', 
                (email,)
            ).fetchone()
            
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                # Login bem-sucedido!
                session['user_id'] = user['id']
                session['username'] = user['username']
                session.permanent = True  # 👈 Mantém login ativo
                
                flash(f'Bem-vindo de volta, {user["username"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Email ou senha incorretos!', 'error')
                return render_template('login.html')
            
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            flash('Erro ao fazer login. Tente novamente.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

# 👇 ROTA DE LOGOUT
@app.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.clear()  # 👈 Limpa todos os dados da sessão
    flash('Você fez logout com sucesso!', 'success')
    return redirect(url_for('home'))

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