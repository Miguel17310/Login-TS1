from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesion'

# Diccionario de usuarios simulados con sus correos
users = {
    "miguel": {"password": "1234", "email": "miguelarturo3103@gmail.com"},
    "carl": {"password": "abcd", "email": "carl@ejemplo.com"}
}

# Lista de productos simulados
products = [
    {"id": "1", "name": "BOXY SUCCESSFUL", "price": 85.00, "image": "https://balbonistore.com/cdn/shop/files/Sintitulo-1_8653f49d-fce8-4fa8-82d3-24beeedc1e7f.jpg?v=1748365764&width=1080"},
    {"id": "2", "name": "BOXY LEGACY", "price": 85.00, "image": "https://balbonistore.com/cdn/shop/files/Sintitulo-2_e685913b-8627-438f-a701-ad3cd26e4030.jpg?v=1748365686&width=1800"},
    {"id": "3", "name": "SPV", "price": 95.00, "image": "https://balbonistore.com/cdn/shop/files/FOTO_5_390ef3f8-ab07-453e-b3f5-bc25c584bdc5.png?v=1746553416&width=1800"},
    {"id": "4", "name": "NEW 70", "price": 95.00, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_10f07dd3-3b52-40ac-a59d-cddf73483e69.png?v=1746307113&width=1800"},
    {"id": "5", "name": "DEPORT", "price": 109.00, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_9e07891e-88ac-4f65-92fb-da716fa0bd3d.png?v=1746296409&width=1800"},
    {"id": "6", "name": "TENNIS", "price": 79.00, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_e13ebf09-e000-4e0c-afc4-2ca4d3f7bb2c.png?v=1746294751&width=1800"},
    {"id": "7", "name": "TENNIS BLUE", "price": 79.00, "image": "https://balbonistore.com/cdn/shop/files/FOTO_1_b97a677d-3676-497b-a78d-38f16fdea7ae.png?v=1746295618&width=1800"},
    {"id": "8", "name": "TENNIS WHITE", "price": 79.00, "image": "https://raw.githubusercontent.com/miguelarturo-design/images/main/tennis_white.jpg"}
]

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
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    cart_count = sum(cart.values())
    return jsonify({'cart_count': cart_count})

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
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    print("Iniciando servidor Flask en http://127.0.0.1:5000/")
    app.run(debug=True)
