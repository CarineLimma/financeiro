from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import os
from io import BytesIO
import pandas as pd
from datetime import timedelta


# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=7)


# Criação da tabela de transações recorrentes, se não existir
def criar_tabela_transacoes_recorrentes():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes_recorrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data_inicio TEXT NOT NULL,
            frequencia TEXT NOT NULL,
            repeticoes INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela_transacoes_recorrentes()

# Configurações de e-mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_SUPPRESS_SEND'] = False

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# Filtro para formatar data (ex: '2023-07-15' para '15/07/2023')
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return value

# Inicializa banco e tabelas
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()

# Decorador para exigir login
# (Removido bloco duplicado de login que causava erro de variável 'user' indefinida)

# Rota raiz redireciona para login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, senha FROM usuarios WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user[1], senha):
                session['usuario_id'] = user[0]
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Usuário ou senha incorretos.", "danger")

    return render_template('login.html')

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not nome or not email or not senha:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('register'))

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                flash('E-mail já cadastrado. Faça login ou use outro e-mail.', 'warning')
                return redirect(url_for('register'))

            senha_criptografada = generate_password_hash(senha)
            cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                           (nome, email, senha_criptografada))
            conn.commit()

        flash('Cadastro realizado com sucesso. Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
# 
# Verificação de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Criação da tabela de transações recorrentes, se não existir
def criar_tabela_transacoes_recorrentes():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes_recorrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data_inicio TEXT NOT NULL,
            frequencia TEXT NOT NULL,
            repeticoes INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar_transacao():
    if request.method == 'POST':
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        valor = float(request.form['valor'])
        categoria = request.form['categoria']
        data_inicio = request.form['data_inicio']
        frequencia = request.form['frequencia']
        repeticoes = int(request.form['repeticoes'])
        usuario_id = session['usuario_id']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transacoes_recorrentes (
                usuario_id, tipo, descricao, valor, categoria,
                data_inicio, frequencia, repeticoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usuario_id, tipo, descricao, valor, categoria,
            data_inicio, frequencia, repeticoes
        ))

        conn.commit()
        conn.close()

        flash('Transação recorrente agendada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('agendar_transacao.html')


@app.route('/dashboard')
@login_required
def dashboard():
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        flash("Usuário não autenticado.")
        return redirect(url_for('login'))

    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()

            # Nome do usuário
            cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
            resultado_nome = cursor.fetchone()
            nome = resultado_nome[0] if resultado_nome else "Usuário"

            # Total de receitas
            cursor.execute("""
                SELECT IFNULL(SUM(valor), 0) 
                FROM transacoes 
                WHERE usuario_id = ? AND tipo = 'receita'
            """, (usuario_id,))
            total_receitas = cursor.fetchone()[0]

            # Total de despesas
            cursor.execute("""
                SELECT IFNULL(SUM(valor), 0) 
                FROM transacoes 
                WHERE usuario_id = ? AND tipo = 'despesa'
            """, (usuario_id,))
            total_despesas = cursor.fetchone()[0]

            # Gráfico de categorias de despesas
            cursor.execute("""
                SELECT categoria, SUM(valor) 
                FROM transacoes
                WHERE usuario_id = ? AND tipo = 'despesa'
                GROUP BY categoria
            """, (usuario_id,))
            resultados = cursor.fetchall()

            labels_categorias = [r[0] for r in resultados]
            valores_categorias = [r[1] for r in resultados]

        return render_template('dashboard.html',
                               nome=nome,
                               total_receitas=total_receitas,
                               total_despesas=total_despesas,
                               labels_categorias=labels_categorias,
                               valores_categorias=valores_categorias)

    except Exception as e:
        flash(f"Erro ao carregar o dashboard: {str(e)}", "danger")
        return redirect(url_for('login'))
    
# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('usuario_id', None)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('login'))

# Adicionar receita
@app.route('/receita', methods=['GET', 'POST'])
@login_required
def adicionar_receita():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor_str = request.form['valor']
        data = request.form['data']
        categoria = request.form['categoria']
        usuario_id = session['usuario_id']

        # Validação do valor
        try:
            valor = float(valor_str)
        except ValueError:
            flash("Valor inválido. Digite um número válido.", "danger")
            return redirect(url_for('adicionar_receita'))

        # Validação da data
        try:
            datetime.strptime(data, '%Y-%m-%d')  # verifica se a data está no formato correto
        except ValueError:
            flash("Data inválida. Escolha uma data válida no formato correto.", "danger")
            return redirect(url_for('adicionar_receita'))

        # Inserir no banco de dados
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, tipo, descricao, valor, data, categoria)
                VALUES (?, 'receita', ?, ?, ?, ?)
            ''', (usuario_id, descricao, valor, data, categoria))
            conn.commit()

        flash('Receita adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('adicionar_receita.html')

@app.route('/despesa', methods=['GET', 'POST'])
@login_required
def adicionar_despesa():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor_str = request.form['valor']
        data = request.form['data']
        categoria = request.form['categoria']
        usuario_id = session['usuario_id']

        # Validação do valor
        try:
            valor = float(valor_str)
        except ValueError:
            flash("Valor inválido. Digite um número válido.", "danger")
            return redirect(url_for('adicionar_despesa'))

        # Validação da data
        try:
            datetime.strptime(data, '%Y-%m-%d')
        except ValueError:
            flash("Data inválida. Escolha uma data válida no formato correto.", "danger")
            return redirect(url_for('adicionar_despesa'))

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, tipo, descricao, valor, data, categoria)
                VALUES (?, 'despesa', ?, ?, ?, ?)
            ''', (usuario_id, descricao, valor, data, categoria))
            conn.commit()

        flash('Despesa adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Esta linha FALTAVA
    return render_template('adicionar_despesa.html')

# Histórico de transações
@app.route('/historico')
@login_required
def historico():
    usuario_id = session['usuario_id']

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo, descricao, valor, data, categoria FROM transacoes
            WHERE usuario_id = ? ORDER BY data DESC
        """, (usuario_id,))
        transacoes = cursor.fetchall()

        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        nome = cursor.fetchone()[0]

    return render_template('historico.html', transacoes=transacoes, nome=nome)
@app.route('/exportar_excel')
def exportar_excel():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT data, tipo, categoria, descricao, valor 
        FROM transacoes 
        WHERE usuario_id = ?
        ORDER BY data DESC
    """, (usuario_id,))
    dados = cursor.fetchall()
    conn.close()

    if not dados:
        return "Nenhuma transação encontrada para exportar."

    # Criar DataFrame
    colunas = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']
    df = pd.DataFrame(dados, columns=colunas)

    # Gerar arquivo Excel na memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transações')

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='historico_transacoes.xlsx'
    )

# Rota para redefinir a senha com token
@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    try:
        email = serializer.loads(token, salt='senha-recuperacao', max_age=3600)
    except Exception:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for('esqueci_senha'))

    if request.method == 'POST':
        senha = request.form['senha']
        senha_confirm = request.form['senha_confirm']

        if senha != senha_confirm:
            flash("As senhas não coincidem.", "danger")
            return render_template('redefinir_senha.html')

        nova_senha = generate_password_hash(senha)

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (nova_senha, email))
                cursor.execute("DELETE FROM password_resets WHERE usuario_id = ?", (user[0],))
                conn.commit()

        flash("Senha redefinida com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('redefinir_senha.html')

# Rota para enviar e-mail para redefinir senha
@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                usuario_id = user[0]
                token = serializer.dumps(email, salt='senha-recuperacao')
                expira = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

                cursor.execute('''
                    INSERT INTO password_resets (usuario_id, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (usuario_id, token, expira))
                conn.commit()

                link = url_for('redefinir_senha', token=token, _external=True)
                msg = Message("Redefinição de senha", recipients=[email])
                msg.body = f"Clique no link para redefinir sua senha:\n\n{link}\n\nSe você não solicitou, ignore este e-mail."

                try:
                    mail.send(msg)
                    flash("E-mail de redefinição enviado! Verifique sua caixa de entrada.", "success")
                except Exception as e:
                    print(e)
                    flash("Erro ao enviar o e-mail. Tente novamente mais tarde.", "danger")
            else:
                flash("E-mail não encontrado.", "danger")

    return render_template('esqueci_senha.html')

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 