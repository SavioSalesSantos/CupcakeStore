# =============================================
# 👇 IMPORTS (todas as importações)
# =============================================
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database import get_db_connection, init_db, atualizar_banco, atualizar_banco_pedidos
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
import os
import sqlite3
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename 
import uuid  
from PIL import Image  
import io 

try:
    from database.database import get_db_connection
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database.database import get_db_connection

# =============================================
# 👇 CONFIGURAÇÃO DO FLASK
# =============================================
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, '..', 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

# =============================================
# 👇 CONFIGURAÇÕES DE UPLOAD
# =============================================

app.config['UPLOAD_FOLDER'] = os.path.join(static_dir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =============================================
# 🔐 Chave secreta para sessions
# =============================================

app.secret_key = 'sua_chave_secreta_super_segura_aqui_2024'
app.permanent_session_lifetime = timedelta(days=7)

# =============================================
# 👇 FUNÇÕES DE ADMIN
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
# 👇 FUNÇÕES DE MASTER
# =============================================

def is_master_account(user_id):
    """Verifica se o usuário é a conta master"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT email FROM users WHERE id = ?', 
            (user_id,)
        ).fetchone()
        conn.close()
        
        return user and user['email'] == 'saviosales@cupcakestore.com'
    except Exception as e:
        print(f"❌ Erro ao verificar conta master: {e}")
        return False
    
# =============================================
# 👇 filtro personalizado para parse de JSON
# =============================================

@app.template_filter('parse_json')
def parse_json_filter(data):
    try:
        if isinstance(data, str):
            return json.loads(data)
        return data
    except:
        return data

# =============================================
# 👇 ROTAS PRINCIPAIS
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
    pagina = request.args.get('pagina', 1, type=int)
    produtos_por_pagina = 8

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
    
    # Calcular paginação
    total_produtos = len(produtos_list)
    total_paginas = (total_produtos + produtos_por_pagina - 1) // produtos_por_pagina
    inicio = (pagina - 1) * produtos_por_pagina
    fim = inicio + produtos_por_pagina
    produtos_paginados = produtos_list[inicio:fim]
    
    return render_template('index.html', 
                         produtos=produtos_paginados, 
                         termo_pesquisa=termo_pesquisa,
                         pagina=pagina,
                         total_paginas=total_paginas,
                         total_produtos=total_produtos)

# =============================================
# 👇 ROTAS DO CARRINHO  
# =============================================

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

#============================================
# 👇 ROTAS DE AUTENTICAÇÃO
#============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # 👇 NOVOS CAMPOS DE ENDEREÇO
        estado = request.form['estado']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        numero = request.form['numero']
        cep = request.form['cep']
        
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
            
            # 👇 INSERT ATUALIZADO COM ENDEREÇO
            conn.execute(
                '''INSERT INTO users (username, email, password, estado, cidade, bairro, rua, numero, cep) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, email, password_hash, estado, cidade, bairro, rua, numero, cep)
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
                session['is_admin'] = bool(user['is_admin'])
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

@app.route('/meu-usuario', methods=['GET', 'POST'])
def meu_usuario():
    """Página para o usuário editar seus próprios dados"""
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página!', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = get_db_connection()

        # 👇 VERIFICA SE É UM CANCELAMENTO
        if request.method == 'POST' and 'cancelar' in request.form:
            flash('Alterações canceladas com sucesso!', 'success')
            return redirect(url_for('meu_usuario'))

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # 👇 NOVOS CAMPOS DE ENDEREÇO
            estado = request.form['estado']
            cidade = request.form['cidade']
            bairro = request.form['bairro']
            rua = request.form['rua']
            numero = request.form['numero']
            cep = request.form['cep']
            
            # Atualiza os dados básicos e endereço
            conn.execute(
                '''UPDATE users SET username = ?, email = ?, estado = ?, cidade = ?, bairro = ?, rua = ?, numero = ?, cep = ? 
                WHERE id = ?''',
                (username, email, estado, cidade, bairro, rua, numero, cep, user_id)
            )
            
            # Atualiza a senha se fornecida
            if password:
                password_hash = generate_password_hash(password)
                conn.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (password_hash, user_id)
                )
            
            conn.commit()
            conn.close()
            
            session['username'] = username
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('meu_usuario'))
        
        else:
            usuario = conn.execute(
                'SELECT * FROM users WHERE id = ?', 
                (user_id,)
            ).fetchone()
            conn.close()
            
            if usuario:
                return render_template('meu_usuario.html', usuario=usuario)
            else:
                flash('Usuário não encontrado!', 'error')
                return redirect(url_for('home'))
                
    except Exception as e:
        print(f"❌ Erro ao editar usuário: {e}")
        flash('Erro ao editar usuário.', 'error')
        return redirect(url_for('home'))

# =============================================
# 👇 ROTAS DE PEDIDOS
# =============================================

def usuario_tem_endereco(user_id):
    """Verifica se o usuário tem endereço cadastrado"""
    try:
        conn = get_db_connection()
        usuario = conn.execute(
            'SELECT estado, cidade, bairro, rua, numero, cep FROM users WHERE id = ?', 
            (user_id,)
        ).fetchone()
        conn.close()
        
        if usuario:
            # Verifica se todos os campos obrigatórios estão preenchidos
            return (usuario['estado'] and usuario['cidade'] and usuario['bairro'] 
                    and usuario['rua'] and usuario['numero'] and usuario['cep'])
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar endereço: {e}")
        return False

@app.route('/finalizar-compra')
def finalizar_compra():
    """Página de confirmação de compra finalizada - VERSÃO CORRIGIDA"""
    metodo_pagamento = request.args.get('metodo', 'cartao')
    forma_entrega = request.args.get('entrega', 'delivery')

    print(f"🔧 Iniciando finalização de compra - Método: {metodo_pagamento}, Entrega: {forma_entrega}")

    if 'user_id' not in session:
        flash('Você precisa fazer login para finalizar a compra!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # 👇 VERIFICA SE O USUÁRIO TEM ENDEREÇO CADASTRADO (APENAS PARA DELIVERY)
    if forma_entrega == 'delivery' and not usuario_tem_endereco(user_id):
        flash('Para entrega delivery, cadastre um endereço para entrega!', 'error')
        return redirect(url_for('meu_usuario'))
    
    carrinho_ids = session.get('carrinho', [])
    
    if not carrinho_ids:
        flash('Seu carrinho está vazio!', 'error')
        return redirect(url_for('carrinho'))
    
    try:
        # 👇 VERIFICAR PRIMEIRO SE A COLUNA EXISTE
        from database.database import verificar_e_criar_coluna_forma_entrega
        verificar_e_criar_coluna_forma_entrega()
        
        conn = get_db_connection()
        placeholders = ','.join('?' * len(carrinho_ids))
        query = f'SELECT * FROM produtos WHERE id IN ({placeholders})'
        produtos_carrinho = conn.execute(query, carrinho_ids).fetchall()
        
        quantidades = {}
        for id_produto in carrinho_ids:
            quantidades[id_produto] = quantidades.get(id_produto, 0) + 1
        
        itens_pedido = []
        for produto in produtos_carrinho:
            produto_dict = dict(produto)
            itens_pedido.append({
                'id': produto_dict['id'],
                'nome': produto_dict['nome'],
                'preco': produto_dict['preco'],
                'quantidade': quantidades[produto_dict['id']]
            })
        
        total = sum(produto['preco'] * quantidades[produto['id']] for produto in produtos_carrinho)
        
        # Prepara os dados do pedido
        pedido_data = {
            'itens': itens_pedido,
            'metodo_pagamento': metodo_pagamento,
            'forma_entrega': forma_entrega
        }
        
        print(f"📦 Inserindo pedido no banco - User: {user_id}, Total: {total}")
        
        # 👇 INSERE NO BANCO COM TRATAMENTO DE ERRO MELHORADO
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO orders (user_id, order_data, total_amount, metodo_pagamento, forma_entrega) VALUES (?, ?, ?, ?, ?)',
                (user_id, json.dumps(pedido_data), total, metodo_pagamento, forma_entrega)
            )
            conn.commit()
            
            # Obtém o ID do pedido recém-inserido
            pedido_id = cursor.lastrowid
            print(f"✅ Pedido inserido com sucesso! ID: {pedido_id}")
            
        except sqlite3.OperationalError as e:
            if "no such column: forma_entrega" in str(e):
                print("🚨 ERRO: Coluna forma_entrega não existe! Criando...")
                # Tenta criar a coluna e inserir novamente
                conn.execute("ALTER TABLE orders ADD COLUMN forma_entrega TEXT DEFAULT 'delivery'")
                conn.commit()
                print("✅ Coluna forma_entrega criada!")
                
                # Tenta inserir novamente
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO orders (user_id, order_data, total_amount, metodo_pagamento, forma_entrega) VALUES (?, ?, ?, ?, ?)',
                    (user_id, json.dumps(pedido_data), total, metodo_pagamento, forma_entrega)
                )
                conn.commit()
                pedido_id = cursor.lastrowid
                print(f"✅ Pedido inserido após correção! ID: {pedido_id}")
            else:
                raise e
        
        conn.close()
        
        # Limpa o carrinho
        session.pop('carrinho', None)
        print("🛒 Carrinho limpo da sessão")
        
        # 🔽 CORREÇÃO: Formatação simples do ID (apenas # + número)
        pedido_id_exibicao = f"{pedido_id}"
        
        print(f"🎉 Compra finalizada com sucesso! Redirecionando para página de confirmação")
        
        # Renderiza a página de confirmação
        return render_template('compra_finalizada.html', 
                             pedido_id=pedido_id_exibicao,
                             data_pedido=datetime.now().strftime('%d/%m/%Y %H:%M'),
                             total=total,
                             metodo_pagamento=metodo_pagamento,
                             forma_entrega=forma_entrega,
                             itens_pedido=itens_pedido)
                             
    except Exception as e:
        print(f"❌ Erro ao finalizar compra: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Converte para lista de dicionários e processa os dados JSON
        pedidos_processados = []
        for pedido in pedidos:
            pedido_dict = dict(pedido)
            try:
                # Tenta converter a string JSON para objeto Python
                dados_pedido = json.loads(pedido_dict['order_data'])
                
                # Verifica se é a estrutura nova (com 'itens') ou antiga
                if isinstance(dados_pedido, dict) and 'itens' in dados_pedido:
                    pedido_dict['itens'] = dados_pedido['itens']
                else:
                    # Estrutura antiga - trata como lista direta de itens
                    pedido_dict['itens'] = dados_pedido
                    
            except Exception as e:
                print(f"❌ Erro ao processar pedido {pedido_dict['id']}: {e}")
                pedido_dict['itens'] = []
                
            pedidos_processados.append(pedido_dict)
        
        return render_template('meus_pedidos.html', pedidos=pedidos_processados)
        
    except Exception as e:
        print(f"❌ Erro ao carregar pedidos: {e}")
        flash('Erro ao carregar seus pedidos.', 'error')
        return redirect(url_for('home'))
    
@app.route('/admin/usuario/<int:user_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_editar_usuario(user_id):
    """Edita um usuário"""
    try:
        # Impede edição da conta master por outros usuários
        if is_master_account(user_id) and not is_master_account(session['user_id']):
            flash('Não pode editar a conta master!', 'error')
            return redirect(url_for('admin_usuarios'))
        
        conn = get_db_connection()

        # 👇 VERIFICA SE É UM CANCELAMENTO
        if request.method == 'POST' and 'cancelar' in request.form:
            flash('Alterações canceladas com sucesso!', 'success')
            return redirect(url_for('admin_editar_usuario', user_id=user_id))

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            is_admin = request.form.get('is_admin', 0)
            
            # 👇 NOVOS CAMPOS DE ENDEREÇO
            estado = request.form['estado']
            cidade = request.form['cidade']
            bairro = request.form['bairro']
            rua = request.form['rua']
            numero = request.form['numero']
            cep = request.form['cep']
            
            # Se for a conta master, força is_admin = 1
            if is_master_account(user_id):
                is_admin = 1
            
            # Atualiza os dados básicos
            if is_master_account(user_id):
                # Conta master - não atualiza email
                conn.execute(
                    'UPDATE users SET username = ? WHERE id = ?',
                    (username, user_id)
                )
            else:
                conn.execute(
                    '''UPDATE users SET username = ?, email = ?, is_admin = ?, estado = ?, cidade = ?, bairro = ?, rua = ?, numero = ?, cep = ? 
                    WHERE id = ?''',
                    (username, email, is_admin, estado, cidade, bairro, rua, numero, cep, user_id)
                )
            
            # Atualiza a senha se fornecida
            if password:
                password_hash = generate_password_hash(password)
                conn.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (password_hash, user_id)
                )
            
            conn.commit()
            conn.close()
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('admin_usuarios'))
        
        else:
            # Modo visualização - busca os dados do usuário
            usuario = conn.execute(
                'SELECT * FROM users WHERE id = ?', 
                (user_id,)
            ).fetchone()
            conn.close()
            
            if usuario:
                return render_template('admin/editar_usuario.html', usuario=usuario)
            else:
                flash('Usuário não encontrado!', 'error')
                return redirect(url_for('admin_usuarios'))
                
    except Exception as e:
        print(f"❌ Erro ao editar usuário: {e}")
        flash('Erro ao editar usuário.', 'error')
        return redirect(url_for('admin_usuarios'))
    
@app.route('/admin/pedidos/excluir-todos', methods=['POST'])
@admin_required
def admin_excluir_todos_pedidos():
    """Exclui todos os pedidos do sistema"""
    try:
        conn = get_db_connection()
        
        
        # Busca o valor total de todos os pedidos para mostrar na mensagem
        total_pedidos = conn.execute("SELECT COUNT(*) as count, SUM(total_amount) as total FROM orders").fetchone()
        count_pedidos = total_pedidos['count'] if total_pedidos else 0
        valor_total = total_pedidos['total'] if total_pedidos and total_pedidos['total'] else 0
        
        # Exclui todos os pedidos
        conn.execute('DELETE FROM orders')
        conn.commit()
        conn.close()
        
        flash(f'Todos os pedidos foram excluídos! ({count_pedidos} pedidos, R$ {valor_total:.2f})', 'success')
        return jsonify({
            'success': True, 
            'message': f'{count_pedidos} pedidos excluídos',
            'valor_total': valor_total
        })
        
    except Exception as e:
        print(f"❌ Erro ao excluir todos os pedidos: {e}")
        flash('Erro ao excluir todos os pedidos', 'error')
        return jsonify({'success': False, 'message': 'Erro ao excluir pedidos'})
    
@app.route('/admin/pedidos/reset-numeracao', methods=['POST'])
@admin_required
def admin_reset_numeracao_pedidos():
    """Reseta a numeração dos pedidos (sequência de IDs)"""
    try:
        conn = get_db_connection()
        
        # Busca o maior ID atual para mostrar na mensagem
        max_id = conn.execute("SELECT MAX(id) as max_id FROM orders").fetchone()
        current_max = max_id['max_id'] if max_id and max_id['max_id'] else 0
        
        # Reseta a sequência SQLite
        conn.execute("DELETE FROM sqlite_sequence WHERE name='orders'")
        conn.commit()
        conn.close()
        
        flash(f'Numeração de pedidos resetada com sucesso! Próximo pedido começará do ID 1 (anterior: {current_max}).', 'success')
        return jsonify({'success': True, 'message': 'Numeração resetada com sucesso!'})
        
    except Exception as e:
        print(f"❌ Erro ao resetar numeração: {e}")
        flash('Erro ao resetar numeração.', 'error')
        return jsonify({'success': False, 'message': 'Erro ao resetar numeração'})
    

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
    """Gerenciamento de pedidos com filtros"""
    try:
        status_filter = request.args.get('status', 'todos')
        
        conn = get_db_connection()
        
        if status_filter == 'todos':
            pedidos = conn.execute('''
                SELECT o.*, u.username 
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            ''').fetchall()
        else:
            pedidos = conn.execute('''
                SELECT o.*, u.username 
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                WHERE o.status = ?
                ORDER BY o.created_at DESC
            ''', (status_filter,)).fetchall()
        
        # Contagem por status para estatísticas
        contagem_status = conn.execute('''
            SELECT status, COUNT(*) as count 
            FROM orders 
            GROUP BY status
        ''').fetchall()
        
        conn.close()
        
        print(f"📦 Pedidos encontrados: {len(pedidos)}")
        
        # Converte os pedidos para dicionários e processa o JSON
        pedidos_processados = []
        for pedido in pedidos:
            try:
                pedido_dict = dict(pedido)
                print(f"🔍 Processando pedido {pedido_dict['id']}")
                print(f"   Dados order_data: {pedido_dict['order_data']}")
                
                # Converte a string JSON para objeto Python
                pedido_dict['itens'] = json.loads(pedido_dict['order_data'])
                print(f"   Itens convertidos: {pedido_dict['itens']}")
                
                pedidos_processados.append(pedido_dict)
            except Exception as e:
                print(f"❌ ERRO no pedido {pedido_dict.get('id', 'unknown')}: {e}")
                print(f"   Dados problemáticos: {pedido_dict}")
                # Skip pedidos com erro
                continue
        
        print(f"✅ Pedidos processados com sucesso: {len(pedidos_processados)}")
        
        return render_template('admin/pedidos.html', 
                             pedidos=pedidos_processados,
                             contagem_status=contagem_status,
                             status_filter=status_filter)
                             
    except Exception as e:
        print(f"❌ Erro ao carregar pedidos: {e}")
        import traceback
        traceback.print_exc()
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
    
def corrigir_sequencia_usuarios():
    """Corrige a sequência de IDs da tabela users"""
    try:
        conn = get_db_connection()
        
        # Busca o maior ID atual
        max_id = conn.execute("SELECT MAX(id) as max_id FROM users").fetchone()['max_id']
        
        if max_id is not None:
            # Atualiza a sequência SQLite
            conn.execute("DELETE FROM sqlite_sequence WHERE name='users'")
            conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('users', ?)", (max_id,))
            conn.commit()
            print(f"✅ Sequência de users corrigida. Próximo ID: {max_id + 1}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao corrigir sequência de users: {e}")

# Chame esta função após a inicialização do banco
def init_db():
    """Inicializa o banco de dados com todas as tabelas necessárias."""
    # ... (código existente) ...
    
    # 👇 CHAMA AS ATUALIZAÇÕES
    atualizar_banco()
    atualizar_banco_pedidos()
    corrigir_sequencia_usuarios()  # 👈 ADICIONE ESTA LINHA
    
    print(f"✅ Banco de dados criado/atualizado em: {os.path.join(base_dir, 'cupcakes.db')}")

@app.route('/admin/pedido/<int:pedido_id>/status', methods=['POST'])
@admin_required
def atualizar_status_pedido(pedido_id):
    """Atualiza o status de um pedido - AGORA COM FLASH MESSAGES"""
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
        
        # 🔽 AGORA RETORNA REDIRECT EM VEZ DE JSON
        flash('Status atualizado com sucesso!', 'success')
        return jsonify({'success': True, 'redirect': True})
        
    except Exception as e:
        print(f"❌ Erro ao atualizar status: {e}")
        flash('Erro ao atualizar status', 'error')
        return jsonify({'success': False, 'redirect': True})
    
@app.route('/admin/pedido/<int:pedido_id>/excluir', methods=['POST'])
@admin_required
def admin_excluir_pedido(pedido_id):
    """Exclui um pedido completamente do sistema"""
    try:
        conn = get_db_connection()
        
        # Primeiro busca o pedido para obter o valor total
        pedido = conn.execute(
            'SELECT total_amount FROM orders WHERE id = ?', 
            (pedido_id,)
        ).fetchone()
        
        if not pedido:
            flash('Pedido não encontrado!', 'error')
            return jsonify({'success': False, 'message': 'Pedido não encontrado!'})
        
        # Exclui o pedido
        conn.execute('DELETE FROM orders WHERE id = ?', (pedido_id,))
        conn.commit()
        conn.close()
        
        # 🔥 AGORA USA FLASH E JSON JUNTOS
        flash(f'Pedido #{pedido_id} excluído com sucesso! Valor removido: R$ {pedido["total_amount"]:.2f}', 'success')
        
        return jsonify({
            'success': True, 
            'message': 'Pedido excluído com sucesso!',
            'valor_removido': pedido['total_amount'],
            'pedido_id': pedido_id
        })
        
    except Exception as e:
        print(f"❌ Erro ao excluir pedido: {e}")
        flash('Erro ao excluir pedido', 'error')
        return jsonify({'success': False, 'message': 'Erro ao excluir pedido'})

@app.route('/admin/usuario/<int:user_id>/admin', methods=['POST'])
@admin_required
def toggle_admin_usuario(user_id):
    """Torna um usuário admin ou remove permissões"""
    try:
        # Impede alteração da conta master
        if is_master_account(user_id):
            return jsonify({'success': False, 'message': 'Não pode alterar permissões da conta master!'})
        
        data = request.get_json()
        is_admin = data.get('is_admin')
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET is_admin = ? WHERE id = ?',
            (is_admin, user_id)
        )
        conn.commit()
        conn.close()

         # 🔽 MENSAGEM FLASH PARA CONFIRMAÇÃO
        flash('As permissões do usuário foram atualizadas com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Erro ao atualizar permissões: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar permissões'})

# =============================================
# 👇 NOVAS ROTAS PARA GERENCIAMENTO DE PRODUTOS
# =============================================

@app.route('/admin/produto/adicionar', methods=['POST'])
@admin_required
def admin_adicionar_produto():
    """Adiciona um novo produto com imagem"""
    try:
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        
        print(f"📝 Dados do formulário: {nome}, {preco}, {descricao}")
        
        # Processar upload da imagem
        imagem_path = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            print(f"📁 Arquivo recebido: {file.filename}")
            
            if file and file.filename != '' and allowed_file(file.filename):
                print("✅ Arquivo válido")
                
                # Gera nome único para a imagem
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                # 🔽 CORREÇÃO: Usar barras normais independente do sistema operacional
                imagem_path = f"uploads/{unique_filename}"
                
                print(f"📂 Caminho da imagem: {imagem_path}")
                
                # Cria o caminho completo para salvar
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                print(f"📂 Caminho completo: {full_path}")
                
                # Garante que o diretório existe
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Salva a imagem
                file.save(full_path)
                print("✅ Imagem salva com sucesso")
                
                # Tenta redimensionar
                try:
                    img = Image.open(full_path)
                    img.thumbnail((500, 500))
                    img.save(full_path)
                    print("✅ Imagem redimensionada")
                except Exception as e:
                    print(f"⚠️ Erro ao redimensionar: {e}")
            else:
                print("❌ Arquivo inválido ou não permitido")

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO produtos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)',
            (nome, preco, descricao, imagem_path)
        )
        conn.commit()
        conn.close()
        
        print("✅ Produto adicionado ao banco")
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
        
    except Exception as e:
        print(f"❌ ERRO DETALHADO ao adicionar produto: {str(e)}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        flash('Erro ao adicionar produto. Verifique os dados.', 'error')
        return redirect(url_for('admin_produtos'))

@app.route('/admin/produto/<int:id>/remover', methods=['POST'])
@admin_required
def admin_remover_produto(id):
    """Remove um produto do banco de dados"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        flash('Produto removido com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
        
    except Exception as e:
        print(f"❌ Erro ao remover produto: {e}")
        flash('Erro ao remover produto.', 'error')
        return redirect(url_for('admin_produtos'))

@app.route('/admin/produto/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_editar_produto(id):
    """Edita um produto existente com suporte a imagem"""
    try:
        conn = get_db_connection()

        # 👇 VERIFICA SE É UM CANCELAMENTO
        if request.method == 'POST' and 'cancelar' in request.form:
            flash('Alterações canceladas com sucesso!', 'success')
            return redirect(url_for('admin_editar_produto', id=id))

        if request.method == 'POST':
            nome = request.form['nome']
            preco = float(request.form['preco'])
            descricao = request.form['descricao']
            remover_imagem = request.form.get('remover_imagem') == '1'
            
            # 🔽 VERIFICAR SE DEVE REMOVER A IMAGEM ATUAL
            if remover_imagem:
                # Busca a imagem atual para remover o arquivo
                produto_atual = conn.execute('SELECT imagem FROM produtos WHERE id = ?', (id,)).fetchone()
                if produto_atual and produto_atual['imagem']:
                    # Extrai apenas o nome do arquivo do caminho
                    filename = os.path.basename(produto_atual['imagem'])
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                # Define como None no banco
                imagem_path = None
            
            # Processar upload da nova imagem (se não estiver removendo)
            elif 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    # 🔽 CORREÇÃO: Usar barras normais
                    imagem_path = f"uploads/{unique_filename}"
                    
                    full_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(full_path)
                    
                    # Remove imagem antiga se existir
                    produto_antigo = conn.execute('SELECT imagem FROM produtos WHERE id = ?', (id,)).fetchone()
                    if produto_antigo and produto_antigo['imagem']:
                        # Extrai apenas o nome do arquivo do caminho antigo
                        old_filename = os.path.basename(produto_antigo['imagem'])
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                else:
                    # Se não enviou nova imagem, mantém a atual
                    produto_atual = conn.execute('SELECT imagem FROM produtos WHERE id = ?', (id,)).fetchone()
                    imagem_path = produto_atual['imagem'] if produto_atual else None
            else:
                # Se não enviou nova imagem, mantém a atual
                produto_atual = conn.execute('SELECT imagem FROM produtos WHERE id = ?', (id,)).fetchone()
                imagem_path = produto_atual['imagem'] if produto_atual else None
            
            # Atualiza o produto
            conn.execute(
                'UPDATE produtos SET nome = ?, preco = ?, descricao = ?, imagem = ? WHERE id = ?',
                (nome, preco, descricao, imagem_path, id)
            )
            conn.commit()
            conn.close()
            
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('admin_produtos'))
        else:
            produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
            conn.close()
            
            if produto:
                return render_template('admin/editar_produto.html', produto=produto)
            else:
                flash('Produto não encontrado!', 'error')
                return redirect(url_for('admin_produtos'))
                
    except Exception as e:
        print(f"❌ Erro ao editar produto: {e}")
        flash('Erro ao editar produto.', 'error')
        return redirect(url_for('admin_produtos'))
    
# =============================================
# 👇 ROTAS NOVAS PÁGINA USUÁRIO
# =============================================    

@app.route('/admin/usuario/<int:user_id>/excluir', methods=['POST'])
@admin_required
def admin_excluir_usuario(user_id):
    """Exclui um usuário do sistema"""
    try:
        # Impede que o usuário exclua a si mesmo
        if user_id == session['user_id']:
            flash('Não pode excluir a si mesmo!', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # Impede exclusão da conta master
        if is_master_account(user_id):
            flash('Não pode excluir a conta master!', 'error')
            return redirect(url_for('admin_usuarios'))
        
        conn = get_db_connection()
        
        # Primeiro exclui os pedidos do usuário
        conn.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
        
        # Depois exclui o usuário
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        flash('Usuário excluído com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    except Exception as e:
        print(f"❌ Erro ao excluir usuário: {e}")
        flash('Erro ao excluir usuário.', 'error')
        return redirect(url_for('admin_usuarios'))
    

# =============================================
# 👇 EXECUÇÃO DO APP
# =============================================

# Adicione este código temporário no final do backend/app.py para testar
if __name__ == '__main__':
    print("🔄 Forçando atualização do banco...")
    
    # Importe e execute a função de atualização
    try:
        from database.database import atualizar_banco_enderecos
        atualizar_banco_enderecos()
        print("✅ Banco atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
    
    app.run(debug=True)