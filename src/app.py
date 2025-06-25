import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesion'

# Diccionario de usuarios simulados con sus correos
users = {
    "miguel": {"password": "1234", "email": "miguelarturo3103@gmail.com"},
    "carl": {"password": "abcd", "email": "carl@ejemplo.com"}
}

# Lista de productos simulados con stock
products = [
    {"id": "1", "name": "BOXY SUCCESSFUL", "price": 85.00, "stock": 29, "image": "https://balbonistore.com/cdn/shop/files/Sintitulo-1_8653f49d-fce8-4fa8-82d3-24beeedc1e7f.jpg?v=1748365764&width=1080"},
    {"id": "2", "name": "BOXY LEGACY", "price": 85.00, "stock": 18, "image": "https://balbonistore.com/cdn/shop/files/Sintitulo-2_e685913b-8627-438f-a701-ad3cd26e4030.jpg?v=1748365686&width=1800"},
    {"id": "3", "name": "SPV", "price": 95.00, "stock": 23, "image": "https://balbonistore.com/cdn/shop/files/FOTO_5_390ef3f8-ab07-453e-b3f5-bc25c584bdc5.png?v=1746553416&width=1800"},
    {"id": "4", "name": "NEW 70", "price": 95.00, "stock": 25, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_10f07dd3-3b52-40ac-a59d-cddf73483e69.png?v=1746307113&width=1800"},
    {"id": "5", "name": "DEPORT", "price": 109.00, "stock": 20, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_9e07891e-88ac-4f65-92fb-da716fa0bd3d.png?v=1746296409&width=1800"},
    {"id": "6", "name": "TENNIS", "price": 79.00, "stock": 15, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_e13ebf09-e000-4e0c-afc4-2ca4d3f7bb2c.png?v=1746294751&width=1800"},
    {"id": "7", "name": "TENNIS BLUE", "price": 79.00, "stock": 27, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_b97a677d-3676-497b-a78d-38f16fdea7ae.png?v=1746295618&width=1800"}
]

# Variable para almacenar pagos pendientes de verificación
pending_payments = {}

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session['username'] = username
            session['cart'] = {}
            return redirect(url_for("welcome"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/welcome")
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template("welcome.html", username=username, products=products, cart_count=cart_count)

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        
        # Verificar si el correo corresponde al usuario miguel
        if email == "miguelarturo3103@gmail.com":
            password = users["miguel"]["password"]
            return render_template('forgot_password.html', 
                                 message=f"Tu contraseña es: {password}")
        else:
            return render_template('forgot_password.html', 
                                 message="Este correo no está asociado al usuario miguel.")
    
    return render_template('forgot_password.html')

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'username' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    # Verificar stock disponible
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    cart = session.get('cart', {})
    current_quantity = cart.get(product_id, 0)
    
    if current_quantity >= product['stock']:
        return jsonify({'error': 'Stock no disponible'}), 400
    
    cart[product_id] = current_quantity + 1
    session['cart'] = cart
    cart_count = sum(cart.values())
    return jsonify({'cart_count': cart_count, 'stock_remaining': product['stock'] - cart[product_id]})

@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'total': item_total
            })
    return render_template('cart.html', cart_items=cart_items, total=total, products=products)

# Configuración para subida de archivos
UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pay', methods=['POST'])
def pay():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    payment_method = request.form.get('payment_method')
    total = request.form.get('total')
    cart = session.get('cart', {})
    
    if not cart:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('cart'))
    
    # Verificar stock disponible antes de procesar el pago
    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if not product or quantity > product['stock']:
            flash('Algunos productos no tienen stock suficiente', 'error')
            return redirect(url_for('cart'))
    
    if payment_method == 'credit_card':
        # Procesar pago con tarjeta de crédito
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        card_name = request.form.get('card_name')
        
        # Validaciones básicas
        if not all([card_number, expiry_date, cvv, card_name]):
            flash('Por favor completa todos los campos de la tarjeta', 'error')
            return redirect(url_for('cart'))
        
        # Simular procesamiento de pago
        payment_id = str(uuid.uuid4())[:8]
        
        # Actualizar stock
        for product_id, quantity in cart.items():
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                product['stock'] -= quantity
        
        # Limpiar carrito después del pago exitoso
        session['cart'] = {}
        
        return render_template('payment_success.html', 
                             payment_method='Tarjeta de Crédito',
                             payment_id=payment_id,
                             total=total,
                             card_last_four=card_number[-4:])
    
    elif payment_method == 'qr_code':
        # Procesar pago con QR (YAPE/PLIN)
        phone_number = request.form.get('phone_number')
        
        if 'payment_proof' not in request.files:
            flash('Por favor sube la captura de pantalla del pago', 'error')
            return redirect(url_for('cart'))
        
        file = request.files['payment_proof']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('cart'))
        
        if file and allowed_file(file.filename):
            # Generar nombre único para el archivo
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Generar ID de pago
            payment_id = str(uuid.uuid4())[:8]
            
            # Guardar información del pago pendiente
            pending_payments[payment_id] = {
                'cart': cart.copy(),
                'total': total,
                'phone_number': phone_number,
                'proof_filename': unique_filename
            }
            
            # Redirigir a la página de verificación
            return render_template('payment_verification.html',
                                 payment_id=payment_id,
                                 total=total,
                                 phone_number=phone_number,
                                 proof_filename=unique_filename)
        else:
            flash('Formato de archivo no válido. Solo se permiten JPG, PNG, GIF', 'error')
            return redirect(url_for('cart'))
    
    else:
        flash('Método de pago no válido', 'error')
        return redirect(url_for('cart'))

@app.route('/verify_payment/<payment_id>', methods=['POST'])
def verify_payment(payment_id):
    if payment_id not in pending_payments:
        flash('Pago no encontrado', 'error')
        return redirect(url_for('cart'))
    
    payment_info = pending_payments[payment_id]
    
    # Actualizar stock
    for product_id, quantity in payment_info['cart'].items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product['stock'] -= quantity
    
    # Limpiar carrito después del pago exitoso
    session['cart'] = {}
    
    # Eliminar el pago pendiente
    del pending_payments[payment_id]
    
    return render_template('payment_success.html',
                         payment_method='YAPE/PLIN',
                         payment_id=payment_id,
                         total=payment_info['total'],
                         phone_number=payment_info['phone_number'],
                         proof_filename=payment_info['proof_filename'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Obtener el puerto del entorno (Azure lo proporciona) o usar 5000 como fallback
    port = int(os.environ.get('PORT', 5000))
    # En producción, escuchar en todas las interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=port, debug=True)
