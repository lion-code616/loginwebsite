import sqlite3
from werkzeug.security import generate_password_hash

conexion = sqlite3.connect("usuarios.db")
cursor = conexion.cursor()

# Crear tabla usuarios con rol
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    clave TEXT NOT NULL,
    rol TEXT DEFAULT 'usuario'
)
""")

# Crear tabla tickets
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

# Insertar usuarios con hash y rol
usuarios = [
    ("admin", generate_password_hash("1234"), "admin"),
    ("isidro", generate_password_hash("mendivil"), "usuario"),
    ("angel", generate_password_hash("2026"), "usuario")  # nuevo usuario
]

for u, c, r in usuarios:
    try:
        cursor.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?)", (u, c, r))
    except sqlite3.IntegrityError:
        pass  # ignora si ya existe

conexion.commit()
conexion.close()
print("DB creada con usuarios y tickets")