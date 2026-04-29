from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os, socket, platform, random, string, datetime, requests, random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import CSRFProtect
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # clave segura para sesiones
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = 'uploads'
csrf = CSRFProtect(app)

# Token para acceso al panel admin
ADMIN_TOKEN = os.urandom(16).hex()
print(f"Admin token: {ADMIN_TOKEN}")

# Archivos permitidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Lista de número de intentos
intentos = {}
bloqueados = {}

# Crear carpeta uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ----------------- LOGIN -----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = ""

    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")

        if not usuario or not clave:
            mensaje = "Todos los campos son obligatorios"
            return render_template("login.html", mensaje=mensaje)

        # Inicializar intentos
        if usuario not in intentos:
            intentos[usuario] = 0

        # Verificar si está bloqueado
        if usuario in bloqueados:
            tiempo_restante = bloqueados[usuario] - datetime.datetime.now()

            if tiempo_restante.total_seconds() > 0:
                minutos = int(tiempo_restante.total_seconds() // 60)
                segundos = int(tiempo_restante.total_seconds() % 60)
                mensaje = f"Cuenta bloqueada. Intenta en {minutos}m {segundos}s"
                return render_template("login.html", mensaje=mensaje)
            else:
                # desbloquear automáticamente
                bloqueados.pop(usuario)
                intentos[usuario] = 0

        try:
            conexion = sqlite3.connect("usuarios.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT clave FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()
        except Exception as e:
            mensaje = "Error interno del servidor"
            print("ERROR:", e)
            return render_template("login.html", mensaje=mensaje)
        finally:
            conexion.close()

        # usuario no existe
        if resultado is None:
            mensaje = "Usuario no existe"

        # contraseña incorrecta
        elif not check_password_hash(resultado[0], clave):
            intentos[usuario] += 1

            if intentos[usuario] >= 3:
                # bloquear por 3 minutos
                bloqueados[usuario] = datetime.datetime.now() + timedelta(minutes=3)
                mensaje = "Cuenta bloqueada por 3 minutos"
            else:
                mensaje = f"Contraseña incorrecta ({intentos[usuario]}/3)"

        # login correcto
        else:
            intentos[usuario] = 0
            bloqueados.pop(usuario, None)

            session["usuario"] = usuario

            with open("logs.txt", "a") as f:
                f.write(f"{datetime.datetime.now()} - LOGIN OK: {usuario}\n")

            return redirect(url_for("dashboard"))

    return render_template("login.html", mensaje=mensaje)

# ----------------- DASHBOARD -----------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    sistema = platform.system()

    # Obtener rol
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (usuario,))
    usuario_rol = cursor.fetchone()[0]
    conexion.close()

    mensaje_usuario = None
    mensaje_archivo = None

    if request.method == "POST":

        # ---------------- MENSAJE ----------------
        mensaje_usuario = request.form.get("mensaje")

        # ---------------- ARCHIVOS ----------------
        if 'archivo' in request.files:
            archivos = request.files.getlist("archivo")

            subidos = []
            errores = []

            for archivo in archivos:
                if archivo.filename == '':
                    continue

                if archivo_permitido(archivo.filename):
                    nombre_seguro = f"{random.randint(1000,9999)}_{secure_filename(archivo.filename)}"
                    ruta_destino = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
                    archivo.save(ruta_destino)
                    subidos.append(archivo.filename)
                else:
                    errores.append(archivo.filename)

            # Mensaje final bonito
            if subidos:
                mensaje_archivo = f"Subidos: {', '.join(subidos)}"
            if errores:
                mensaje_archivo = (mensaje_archivo or "") + f" | No permitidos: {', '.join(errores)}"

    return render_template("dashboard.html",
                           usuario=usuario,
                           usuario_rol=usuario_rol,
                           admin_token=ADMIN_TOKEN,
                           ip=ip,
                           sistema=sistema,
                           mensaje_usuario=mensaje_usuario,
                           mensaje_archivo=mensaje_archivo)

# ----------------- LOGOUT -----------------

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# ----------------- VER / ELIMINAR ARCHIVOS -----------------

import datetime

@app.route("/archivos")
def ver_archivos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]

    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (usuario,))
    rol = cursor.fetchone()[0]
    conexion.close()

    lista_archivos = []

    for nombre in os.listdir(app.config['UPLOAD_FOLDER']):
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre)

        tamaño = os.path.getsize(ruta) / 1024  # KB
        fecha = datetime.datetime.fromtimestamp(os.path.getmtime(ruta))

        lista_archivos.append({
            "nombre": nombre,
            "tamano": round(tamaño, 2),
            "fecha": fecha.strftime("%d/%m/%Y %H:%M")
        })

    return render_template("archivos.html",
                           archivos=lista_archivos,
                           usuario=session["usuario"],
                           usuario_rol=rol,
                           admin_token=ADMIN_TOKEN,
                           ip=socket.gethostbyname(socket.gethostname()),
                           sistema=platform.system())

@app.route("/eliminar/<nombre>", methods = ["POST"])
def eliminar_archivo(nombre):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (session["usuario"],))
    rol = cursor.fetchone()[0]
    conexion.close()

    if rol != "admin":
        return "Acceso denegado", 403

    nombre_seguro = secure_filename(nombre)
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)

    if os.path.exists(ruta):
        os.remove(ruta)

    return redirect(url_for("ver_archivos"))

# --------- DESCARGAR ARCHIVOS ------------

@app.route("/descargar/<nombre>")
def descargar_archivo(nombre):
    if "usuario" not in session:
        return redirect(url_for("login"))

    nombre_seguro = secure_filename(nombre)
    return send_from_directory(app.config['UPLOAD_FOLDER'], nombre_seguro, as_attachment=True)

# ------------- PREVIEW DE ARCHIVOS --------------

@app.route("/ver/<nombre>")
def ver_archivo(nombre):
    if "usuario" not in session:
        return redirect(url_for("login"))

    nombre_seguro = secure_filename(nombre)
    return send_from_directory(app.config['UPLOAD_FOLDER'], nombre_seguro)

# ----------------- TICKET OLVIDE CONTRASEÑA -----------------

@app.route("/olvide", methods=["GET", "POST"])
def olvide_contrasena():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario")
        correo = request.form.get("correo")

        conexion = sqlite3.connect("usuarios.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT usuario FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone():
            # Crear ticket sin contraseña automática
            cursor.execute("INSERT INTO tickets (usuario, correo, estado) VALUES (?, ?, 'pendiente')",
                           (usuario, correo))
            conexion.commit()
            mensaje = "Ticket creado correctamente. El admin asignará la nueva contraseña."
        else:
            mensaje = "Usuario no encontrado"
        conexion.close()
    return render_template("ticket.html", mensaje=mensaje)

# ----------------- ADMIN -----------------

@app.route("/admin/<token>")
def admin_panel(token):
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Validar token
    if token != ADMIN_TOKEN:
        return "Acceso denegado", 403

    # Validar rol
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (session["usuario"],))
    rol = cursor.fetchone()[0]
    if rol != "admin":
        conexion.close()
        return "Acceso denegado", 403

    # Traer usuarios y tickets
    cursor.execute("SELECT id, usuario, rol FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.execute("SELECT id, usuario, correo, estado, fecha FROM tickets")
    tickets = cursor.fetchall()
    conexion.close()

    return render_template("admin.html", usuarios=usuarios, tickets=tickets, admin_token=ADMIN_TOKEN)

# ----------------- ASIGNAR CONTRASEÑA -----------------

@app.route("/asignar_contrasena/<int:ticket_id>", methods=["GET", "POST"])
def asignar_contrasena(ticket_id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (session["usuario"],))
    rol = cursor.fetchone()[0]
    if rol != "admin":
        conexion.close()
        return "Acceso denegado", 403

    if request.method == "POST":
        nueva_clave = request.form.get("nueva_clave")
        if nueva_clave:
            hash_clave = generate_password_hash(nueva_clave)
            cursor.execute("SELECT usuario FROM tickets WHERE id = ?", (ticket_id,))
            usuario_ticket = cursor.fetchone()[0]
            cursor.execute("UPDATE usuarios SET clave=? WHERE usuario=?", (hash_clave, usuario_ticket))
            cursor.execute("UPDATE tickets SET estado='resuelto', nueva_clave=? WHERE id=?", (hash_clave, ticket_id))
            conexion.commit()
            conexion.close()
            return redirect(url_for("admin_panel", token=ADMIN_TOKEN))

    conexion.close()
    return render_template("asignar_contrasena.html", ticket_id=ticket_id)

# ----------------- CREAR TABLAS -----------------

def crear_tabla_y_usuarios():
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()

    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            clave TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario'
        )
    """)

    # Tabla tickets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            correo TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            nueva_clave TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    usuarios = [
        ("admin", generate_password_hash("1234"), "admin"),
        ("isidro", generate_password_hash("2345"), "usuario"),
        ("angel", generate_password_hash("2026"), "usuario")
    ]

    for u, c, r in usuarios:
        try:
            cursor.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?)", (u, c, r))
        except sqlite3.IntegrityError:
            pass

    conexion.commit()
    conexion.close()

# ----------------- POKE API -----------------------

@app.route("/pokemon", methods=["GET", "POST"])
def pokemon():
    if "usuario" not in session:
        return redirect(url_for("login"))

    data = None
    error = None

    # obtener rol (igual que dashboard)
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ?", (session["usuario"],))
    usuario_rol = cursor.fetchone()[0]
    conexion.close()

    if request.method == "POST":

        url = None

        if request.form.get("random"):
            numero = random.randint(1, 1010)
            url = f"https://pokeapi.co/api/v2/pokemon/{numero}"

        else:
            nombre = request.form.get("nombre")

            if not nombre:
                error = "Escribe un Pokémon"
                return render_template(
                    "pokemon.html",
                    data=None,
                    error=error,
                    usuario_rol=usuario_rol,
                    admin_token=ADMIN_TOKEN
                )

            url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"

        if url:
            res = requests.get(url)

            if res.status_code != 200:
                error = "Pokémon no encontrado"
            else:
                info = res.json()

                data = {
                    "nombre": info["name"],
                    "imagen": info["sprites"]["front_default"],
                    "altura": info["height"],
                    "peso": info["weight"],
                    "tipos": [t["type"]["name"] for t in info["types"]],
                    "stats": {s["stat"]["name"]: s["base_stat"] for s in info["stats"]}
                }
    return render_template("pokemon.html",
                           data=data,
                           error=error,
                           usuario=session.get("usuario"),
                           usuario_rol="admin" if session.get("usuario") == "admin" else "usuario",
                           admin_token=ADMIN_TOKEN,
                           ip=socket.gethostbyname(socket.gethostname()),
                           sistema=platform.system())

    return render_template("pokemon.html", data=data, error=error)

# ----------------- EJECUTAR -----------------

if __name__ == "__main__":
    crear_tabla_y_usuarios()
    app.run(debug=True)