from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Diccionario de usuarios simulados
users = {
    "miguel": "1234",
    "carl": "abcd"
}

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            return redirect(url_for("welcome", username=username))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/welcome/<username>")
def welcome(username):
    return render_template("welcome.html", username=username)

if __name__ == "__main__":
    print("Iniciando servidor Flask en http://127.0.0.1:5000/")
    app.run(debug=True)








