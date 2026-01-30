from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno desde .env (Solo en desarrollo local)
# override=False significa que NO reemplaza variables ya existentes del sistema
load_dotenv(override=False)

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
# DEBUG: Imprimir todas las variables relacionadas con MySQL
print("[DEBUG] === Environment Variables ===")
print(f"[DEBUG] MYSQL_URL = {os.environ.get('MYSQL_URL', 'NOT SET')}")
print(f"[DEBUG] DATABASE_URL = {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"[DEBUG] MYSQLHOST = {os.environ.get('MYSQLHOST', 'NOT SET')}")
print(f"[DEBUG] DB_HOST = {os.environ.get('DB_HOST', 'NOT SET')}")
print("[DEBUG] ================================")

mysql_url = os.environ.get("MYSQL_URL") or os.environ.get("DATABASE_URL")

if mysql_url:
    # Produccion: usar URL de Railway
    db_uri = mysql_url
    if db_uri.startswith('mysql://'):
        db_uri = db_uri.replace('mysql://', 'mysql+pymysql://', 1)
    # Agregar charset para compatibilidad con MySQL 8
    if '?' not in db_uri:
        db_uri += '?charset=utf8mb4'
    else:
        db_uri += '&charset=utf8mb4'
    print(f"[INFO] Using MySQL URL from environment")
else:
    # Local: construir desde variables individuales
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "gamer_store")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    db_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"[INFO] Using local database: {DB_HOST}")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')

# --- CONFIGURACIÓN DE SEGURIDAD AVANZADA ---
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# --- CONFIGURACIÓN DE CORREO (MICROSERVICIO) ---
EMAIL_SERVICE_URL = os.environ.get('EMAIL_SERVICE_URL')

def send_email_microservice(to_email, subject, html_content):
    if not EMAIL_SERVICE_URL:
        print("[WARNING] EMAIL_SERVICE_URL not configured. Email not sent.")
        return
    
    try:
        response = requests.post(f"{EMAIL_SERVICE_URL}/send-email", json={
            "to": to_email,
            "subject": subject,
            "html": html_content
        }, timeout=5)
        
        if response.status_code == 200:
            print(f"[INFO] Email sent to {to_email}")
        else:
            print(f"[ERROR] Failed to send email: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception sending email: {e}")

# DEBUG: Verificar configuración de correo
print("[DEBUG] === Mail Configuration ===")
print(f"[DEBUG] MAIL_SERVER = {app.config['MAIL_SERVER']}")
print(f"[DEBUG] MAIL_PORT = {app.config['MAIL_PORT']}")
print(f"[DEBUG] MAIL_USE_TLS = {app.config['MAIL_USE_TLS']}")
print(f"[DEBUG] MAIL_USERNAME = {app.config['MAIL_USERNAME']}")
print(f"[DEBUG] MAIL_PASSWORD = {'SET' if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
print(f"[DEBUG] MAIL_DEFAULT_SENDER = {app.config['MAIL_DEFAULT_SENDER']}")
print("[DEBUG] ================================")

db = SQLAlchemy(app)
# mail = Mail(app) # Reemplazado por microservicio
csrf = CSRFProtect(app)  # Protección CSRF
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Límites globales
)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Serializador para tokens de recuperación
s = URLSafeTimedSerializer(app.secret_key)

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=10)
    image_url = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='purchases')

# --- SEED DATA ---
def seed_database():
    # Base de datos comienza vacía - agrega productos desde el panel admin
    pass

# --- ROUTES ---
@app.route('/')
def index():
    featured = Product.query.limit(3).all()
    return render_template('index.html', featured=featured)

@app.route('/catalog')
def catalog():
    products = Product.query.all()
    return render_template('catalog.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('details.html', product=product)

@app.route('/profile')
@login_required
def profile():
    purchases = Purchase.query.filter_by(email=current_user.email).order_by(Purchase.date.desc()).all()
    return render_template('profile.html', purchases=purchases)

@app.route('/checkout/<int:product_id>')
@login_required
def checkout(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('checkout.html', product=product)

@app.route('/api/buy', methods=['POST'])
@login_required
def buy():
    data = request.json
    product = Product.query.get_or_404(data['product_id'])
    
    if product.stock <= 0:
        return jsonify({"message": "Error: Producto agotado.", "status": "error"}), 400

    new_purchase = Purchase(
        buyer_name=data['name'],
        cedula=data['cedula'],
        email=data['email'],
        phone=data.get('phone', ''),
        product_id=data['product_id'],
        total_price=data['price']
    )
    
    # Descontar Stock
    product.stock -= 1
    
    db.session.add(new_purchase)
    db.session.commit()

    # Enviar correo de confirmación de compra
    # Enviar correo de confirmación de compra
    msg_body = f"Hola {data['name']},<br><br>Gracias por su compra de: <b>{product.name}</b>.<br>Total: <b>${data['price']}</b><br>Celular de contacto: {data.get('phone', 'N/A')}<br><br>En unos momentos nos comunicaremos con usted a este número para coordinar el envío.<br><br>Atentamente,<br>El equipo de PONTE ONCE."
    send_email_microservice(data['email'], 'Confirmacion de Compra - PONTE ONCE', msg_body)

    return jsonify({"message": "Compra procesada correctamente", "status": "success"})

# --- AUTH ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Máximo 5 registros por minuto
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Enviar correo de bienvenida
        # Enviar correo de bienvenida
        msg_body = f'Hola {username},<br><br>Gracias por registrarte en nuestra tienda. ¡Esperamos que encuentres el hardware de tus sueños!<br><br>Saludos,<br>El equipo de PONTE ONCE.'
        send_email_microservice(email, 'Bienvenido a PONTE ONCE Store!', msg_body)

        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Máximo 10 intentos de login por minuto
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas.', 'error')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='email-confirm')
            link = url_for('reset_password', token=token, _external=True)
            msg = Message('Recuperacion de Contrasena', recipients=[email])
            msg.body = f'Hola {user.username},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{link}\n\nSi no fuiste tú, ignora este mensaje.'
            try:
                mail.send(msg)
                flash('Te hemos enviado un enlace de recuperación a tu correo.', 'info')
            except Exception as e:
                flash(f'Error al enviar correo: {e}', 'error')
        else:
             flash('No encontramos una cuenta con ese correo.', 'error')
    return render_template('auth/forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600) # Expira en 1 hora
    except:
        flash('El enlace es inválido o ha expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        user.set_password(password)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('login'))
        
    return render_template('auth/reset_password.html')

from functools import wraps

# --- ADMIN DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- ADMIN ROUTES ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Obtener todas las compras y todos los productos
    purchases = Purchase.query.order_by(Purchase.date.desc()).limit(10).all()
    products = Product.query.all()
    
    # --- ESTADÍSTICAS DEL DASHBOARD ---
    # Total de ventas
    total_ventas = db.session.query(func.sum(Purchase.total_price)).scalar() or 0
    
    # Número de pedidos
    total_pedidos = Purchase.query.count()
    
    # Número de productos
    total_productos = Product.query.count()
    
    # Número de usuarios
    total_usuarios = User.query.count()
    
    # Ventas hoy
    today = datetime.utcnow().date()
    ventas_hoy = db.session.query(func.sum(Purchase.total_price)).filter(
        func.date(Purchase.date) == today
    ).scalar() or 0
    
    # Pedidos hoy
    pedidos_hoy = Purchase.query.filter(
        func.date(Purchase.date) == today
    ).count()
    
    # Ventas por día (últimos 7 días)
    ventas_por_dia = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        day_total = db.session.query(func.sum(Purchase.total_price)).filter(
            func.date(Purchase.date) == day
        ).scalar() or 0
        ventas_por_dia.append({
            'fecha': day.strftime('%d/%m'),
            'total': float(day_total)
        })
    
    # Productos más vendidos
    productos_vendidos = db.session.query(
        Product.name,
        func.count(Purchase.id).label('cantidad')
    ).join(Purchase).group_by(Product.id).order_by(func.count(Purchase.id).desc()).limit(5).all()
    
    stats = {
        'total_ventas': float(total_ventas),
        'total_pedidos': total_pedidos,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'ventas_hoy': float(ventas_hoy),
        'pedidos_hoy': pedidos_hoy,
        'ventas_por_dia': ventas_por_dia,
        'productos_vendidos': [{'nombre': p[0], 'cantidad': p[1]} for p in productos_vendidos]
    }
    
    return render_template('admin/dashboard.html', purchases=purchases, products=products, stats=stats)

@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        image_url = request.form['image_url']
        description = request.form['description']
        
        new_product = Product(
            name=name, category=category, price=price, 
            stock=stock, image_url=image_url, description=description
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin/add_product.html')

@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Producto "{product_name}" eliminado.', 'success')
    return redirect(url_for('admin_dashboard'))

# --- INIT ---
# --- INIT ---
def init_db():
    """Inicializa la base de datos"""
    try:
        with app.app_context():
            print("[DEBUG] Starting db.create_all()...")
            db.create_all()
            print("[DEBUG] db.create_all() completed!")
            
            # Verificar que las tablas existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"[DEBUG] Tables in database: {tables}")
            
            seed_database()
            print("[INFO] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()

# Inicializar la base de datos al arrancar (producción y local)
init_db()

if __name__ == '__main__':
    app.run(debug=True)
