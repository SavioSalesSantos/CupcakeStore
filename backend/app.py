from flask import Flask, render_template, session, redirect, url_for, request, flash
import os
import sqlite3
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps  

try:
    from database.database import get_db_connection
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database.database import get_db_connection

# Obtém o caminho absoluto para as pastas frontend
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, '..', 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

# 🔐 Chave secreta para sessions
app.secret_key = 'sua_chave_secreta_super_segura_aqui_2024'
app.permanent_session_lifetime = timedelta(days=7)

# =============================================
# FUNÇÃO PARA VERIFICAR ADMIN NO TEMPLATE 
# =============================================
@app.context_processor
def utility_processor():
    def check_is_admin():
        """Verifica se o usuário logado é admin"""
        if 'user_id' not in session:
            return False
        try:
            conn = get_db_connection()
            user = conn.execute(
                'SELECT is_admin FROM users WHERE id = ?', 
                (session['user_id'],)
            ).fetchone()
            conn.close()
            return user and user['is_admin'] == 1
        except:
            return False
    return dict(is_admin=check_is_admin)

# =============================================
# 👇 FUNÇÕES DE ADMIN - CORRIGIDAS
# =============================================

def is_admin():
    """Verifica se o usuário logado é administrador"""
    if 'user_id' not in session:
        return False
    
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT is_admin FROM users WHERE id = ?', 
            (session['user_id'],)
        ).fetchone()
        conn.close()
        
        return user and user['is_admin'] == 1
    except Exception as e:
        print(f"❌ Erro ao verificar admin: {e}")
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('Acesso restrito a administradores!', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================
# 👇 ROTAS EXISTENTES 
# =============================================

def get_produtos():
    """Função para buscar produtos do banco de dados"""
    try:
        conn = get_db_connection()
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        conn.close()
        return produtos
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return []

@app.route('/')
def home():
    termo_pesquisa = request.args.get('q', '').lower()
    produtos = get_produtos()
    
    if termo_pesquisa:
        produtos_filtrados = []
        for produto in produtos:
            produto_dict = dict(produto)
            if (termo_pesquisa in produto_dict['nome'].lower() or 
                termo_pesquisa in produto_dict['descricao'].lower()):
                produtos_filtrados.append(produto_dict)
        produtos_list = produtos_filtrados
    else:
        produtos_list = [dict(produto) for produto in produtos]
    
    return render_template('index.html', produtos=produtos_list, termo_pesquisa=termo_pesquisa)

# === ROTAS DO CARRINHO ===
@app.route('/adicionar/<int:id_produto>')
def adicionar_carrinho(id_produto):
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    session['carrinho'].append(id_produto)
    session.modified = True
    
    referer = request.headers.get('Referer')
    if referer and '/carrinho' in referer:
        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('home'))

@app.route('/remover/<int:id_produto>')
def remover_carrinho(id_produto):
    if 'carrinho' in session:
        if id_produto in session['carrinho']:
            session['carrinho'].remove(id_produto)
            session.modified = True
    
    referer = request.headers.get('Referer')
    if referer and '/carrinho' in referer:
        return redirect(url_for('carrinho'))
    else:
        return redirect(url_for('home'))

@app.route('/carrinho')
def carrinho():
    carrinho_ids = session.get('carrinho', [])
    
    if not carrinho_ids:
        return render_template('carrinho.html', produtos=[], total=0)
    
    try:
        conn = get_db_connection()
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        produtos_carrinho = conn.execute(query, carrinho_ids).fetchall()
        conn.close()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
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
    session.pop('carrinho', None)
    return redirect(url_for('carrinho'))

@app.route('/get-contador-carrinho')
def get_contador_carrinho():
    carrinho_ids = session.get('carrinho', [])
    return {'quantidade': len(carrinho_ids)}

@app.route('/get-nome-produto/<int:id_produto>')
def get_nome_produto(id_produto):
    try:
        conn = get_db_connection()
        produto = conn.execute('SELECT nome FROM produtos WHERE id = ?', (id_produto,)).fetchone()
        conn.close()
        return {'nome': produto['nome'] if produto else 'Produto'}
    except Exception as e:
        return {'nome': 'Produto'}

# === ROTAS DE AUTENTICAÇÃO ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            user_exists = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?', 
                (username, email)
            ).fetchone()
            
            if user_exists:
                flash('Username ou email já cadastrados!', 'error')
                return render_template('register.html')
            
            password_hash = generate_password_hash(password)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM users WHERE email = ?', 
                (email,)
            ).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = bool(user['is_admin'])  # 👈 ADICIONE ESTA LINHA
                session.permanent = True
                
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

@app.route('/logout')
def logout():
    session.clear()
    flash('Você fez logout com sucesso!', 'success')
    return redirect(url_for('home'))

# === ROTAS DE PEDIDOS ===
@app.route('/finalizar-compra')
def finalizar_compra():
    """Página de confirmação de compra finalizada (AGORA SALVA NO BANCO)"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para finalizar a compra!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    carrinho_ids = session.get('carrinho', [])
    
    if not carrinho_ids:
        flash('Seu carrinho está vazio!', 'error')
        return redirect(url_for('carrinho'))
    
    try:
        conn = get_db_connection()
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        produtos_carrinho = conn.execute(query, carrinho_ids).fetchall()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
        itens_pedido = []
        for produto in produtos_carrinho:
            itens_pedido.append({
                'id': produto['id'],
                'nome': produto['nome'],
                'preco': produto['preco'],
                'quantidade': quantidades[produto['id']]
            })
        
        total = sum(produto['preco'] * quantidades[produto['id']] for produto in produtos_carrinho)
        
        conn.execute(
            'INSERT INTO orders (user_id, order_data, total_amount) VALUES (?, ?, ?)',
            (user_id, json.dumps(itens_pedido), total)
        )
        conn.commit()
        conn.close()
        
        session.pop('carrinho', None)
        pedido_id = f"{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        return render_template('compra_finalizada.html', 
                             pedido_id=pedido_id,
                             data_pedido=datetime.now().strftime('%d/%m/%Y %H:%M'),
                             total=total)
                             
    except Exception as e:
        print(f"❌ Erro ao finalizar compra: {e}")
        flash('Erro ao processar seu pedido. Tente novamente.', 'error')
        return redirect(url_for('carrinho'))

@app.route('/meus-pedidos')
def meus_pedidos():
    """Página de histórico de pedidos"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para ver seus pedidos!', 'error')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        pedidos = conn.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
            (session['user_id'],)
        ).fetchall()
        conn.close()
        
        # Converte para lista de dicionários e já processa os dados JSON
        pedidos_processados = []
        for pedido in pedidos:
            pedido_dict = dict(pedido)
            # Converte a string JSON para objeto Python aqui mesmo
            pedido_dict['itens'] = json.loads(pedido_dict['order_data'])
            pedidos_processados.append(pedido_dict)
        
        return render_template('meus_pedidos.html', pedidos=pedidos_processados)
        
    except Exception as e:
        print(f"❌ Erro ao carregar pedidos: {e}")
        flash('Erro ao carregar seus pedidos.', 'error')
        return redirect(url_for('home'))

# =============================================
# 👇 ROTAS DO PAINEL ADMIN
# =============================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Dashboard do painel administrativo"""
    try:
        conn = get_db_connection()
        
        # Estatísticas
        total_usuarios = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_pedidos = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        total_vendas = conn.execute('SELECT SUM(total_amount) FROM orders').fetchone()[0] or 0
        total_produtos = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
        
        # Pedidos recentes
        pedidos_recentes = conn.execute('''
            SELECT o.*, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            ORDER BY o.created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        return render_template('admin/dashboard.html',
                             total_usuarios=total_usuarios,
                             total_pedidos=total_pedidos,
                             total_vendas=total_vendas,
                             total_produtos=total_produtos,
                             pedidos_recentes=pedidos_recentes)
                             
    except Exception as e:
        print(f"❌ Erro no dashboard admin: {e}")
        flash('Erro ao carregar dashboard.', 'error')
        return redirect(url_for('home'))
    
# =============================================
# 👇 ROTAS COMPLETAS DO PAINEL ADMIN
# =============================================

@app.route('/admin/produtos')
@admin_required
def admin_produtos():
    """Gerenciamento de produtos"""
    try:
        conn = get_db_connection()
        produtos = conn.execute('SELECT * FROM produtos ORDER BY id DESC').fetchall()
        conn.close()
        return render_template('admin/produtos.html', produtos=produtos)
    except Exception as e:
        print(f"❌ Erro ao carregar produtos: {e}")
        flash('Erro ao carregar produtos.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    """Gerenciamento de pedidos"""
    try:
        conn = get_db_connection()
        pedidos = conn.execute('''
            SELECT o.*, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            ORDER BY o.created_at DESC
        ''').fetchall()
        conn.close()
        return render_template('admin/pedidos.html', pedidos=pedidos)
    except Exception as e:
        print(f"❌ Erro ao carregar pedidos: {e}")
        flash('Erro ao carregar pedidos.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Gerenciamento de usuários"""
    try:
        conn = get_db_connection()
        usuarios = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        conn.close()
        return render_template('admin/usuarios.html', usuarios=usuarios)
    except Exception as e:
        print(f"❌ Erro ao carregar usuários: {e}")
        flash('Erro ao carregar usuários.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/pedido/<int:pedido_id>/status', methods=['POST'])
@admin_required
def atualizar_status_pedido(pedido_id):
    """Atualiza o status de um pedido"""
    try:
        data = request.get_json()
        novo_status = data.get('status')
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (novo_status, pedido_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Status atualizado com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao atualizar status: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar status'})

@app.route('/admin/usuario/<int:user_id>/admin', methods=['POST'])
@admin_required
def toggle_admin_usuario(user_id):
    """Torna um usuário admin ou remove permissões"""
    try:
        data = request.get_json()
        is_admin = data.get('is_admin')
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET is_admin = ? WHERE id = ?',
            (is_admin, user_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Permissões atualizadas com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao atualizar permissões: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar permissões'})

# === EXECUÇÃO DO APP ===
if __name__ == '__main__':
    print(f"📁 Templates path: {template_dir}")
    print(f"📁 Static path: {static_dir}")
    print(f"✅ Template exists: {os.path.exists(template_dir)}")
    print(f"✅ Static exists: {os.path.exists(static_dir)}")
    
    db_path = os.path.join(base_dir, '..', 'database', 'cupcakes.db')
    print(f"✅ Database exists: {os.path.exists(db_path)}")
    
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True)