from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from dotenv import load_dotenv
import sqlite3
import datetime
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True') == 'True'
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

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
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

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

@app.route('/dashboard')
@login_required
def dashboard():
    usuario_id = session['usuario_id']

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Buscar nome do usuário
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        nome = cursor.fetchone()[0]

        # Buscar total de receitas
        cursor.execute("SELECT IFNULL(SUM(valor), 0) FROM transacoes WHERE usuario_id = ? AND tipo = 'receita'", (usuario_id,))
        total_receitas = cursor.fetchone()[0]

        # Buscar total de despesas
        cursor.execute("SELECT IFNULL(SUM(valor), 0) FROM transacoes WHERE usuario_id = ? AND tipo = 'despesa'", (usuario_id,))
        total_despesas = cursor.fetchone()[0]

        # Buscar categorias e valores das despesas (exemplo simples)
        cursor.execute("""
            SELECT categoria, SUM(valor) FROM transacoes
            WHERE usuario_id = ? AND tipo = 'despesa'
            GROUP BY categoria
        """, (usuario_id,))
        resultados = cursor.fetchall()

        labels_categorias = [r[0] for r in resultados]
        valores_categorias = [r[1] for r in resultados]

    return render_template(
        'dashboard.html',
        nome=nome,
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        labels_categorias=labels_categorias,
        valores_categorias=valores_categorias
    )

@app.route('/logout')
@login_required
def logout():
    session.pop('usuario_id', None)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('login'))

# Rota para enviar e-mail de recuperação de senha
@app.route('/esqueci-senha', methods=['GET', 'POST'])
def forgot_password():
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

                link = url_for('reset_password', token=token, _external=True)
                msg = Message("Redefinição de senha", recipients=[email])
                msg.body = f"Clique no link para redefinir sua senha:\n\n{link}\n\nSe você não solicitou, ignore este e-mail."
                mail.send(msg)

                flash("E-mail de redefinição enviado! Verifique sua caixa de entrada.", "success")
            else:
                flash("E-mail não encontrado.", "danger")

    return render_template('esqueci_senha.html')

# Rota para redefinir a senha usando o token
@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='senha-recuperacao', max_age=3600)
    except Exception:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for('forgot_password'))

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

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
