import sqlite3, os

conexion = sqlite3.connect("usuarios.db")
cursor = conexion.cursor()

#Mostrar todos los usuarios
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()
print("Usuarios actuales: ")

for u in usuarios:
    print(u)

conexion.close()