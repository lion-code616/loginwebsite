import os

if os.path.exists("usuarios.db"):
    os.remove("usuarios.db")
    print("Base de datos eliminada")