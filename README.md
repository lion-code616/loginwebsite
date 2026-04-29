# 🚀 Mi App Flask

Aplicación web desarrollada con Flask que incluye autenticación, gestión de archivos, panel administrativo y una Pokédex usando una API externa.

---

## 🧩 Funcionalidades

### 🔐 Autenticación

* Login de usuarios con contraseñas encriptadas
* Protección CSRF en formularios
* Bloqueo temporal tras múltiples intentos fallidos

### 📊 Dashboard

* Interfaz principal del sistema
* Sidebar de navegación
* Modo oscuro 🌙

### 📂 Gestión de archivos

* Subida de archivos (múltiples)
* Visualización de archivos
* Descarga de archivos
* Eliminación (solo admin)

### 👨‍💼 Panel de administrador

* Visualización de usuarios
* Gestión de tickets
* Asignación de contraseñas

### 🧾 Sistema de tickets

* Solicitud de recuperación de contraseña
* Resolución por administrador

### 🎮 Pokédex

* Búsqueda de Pokémon por nombre
* Generación aleatoria 🎲
* Visualización de stats, tipos e imagen

---

## 🛠️ Tecnologías utilizadas

* Python (Flask)
* SQLite
* HTML + Jinja2
* Bootstrap 5
* JavaScript
* PokéAPI

---

## 🔒 Seguridad

* Protección CSRF (`Flask-WTF`)
* Hash de contraseñas
* Validación de archivos
* Control de roles (admin / usuario)

---

## 📁 Estructura del proyecto

```id="n5k1q8"
project/
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   ├── admin.html
│   ├── archivos.html
│   ├── asignar_contrasena.html
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── pokemon.html
│   ├── ticket.html
│   └── upload.html
│
├── check_db.py
├── crear_db.py
├── limpiar_db.py
├── Virtual_Env.py
├── Virtual_Env.pyproj
├── Virtual Env.slnx
├── requirements.txt
├── .gitignore
```

---

## ⚙️ Instalación

1. Clonar repositorio:

```id="1m6y0p"
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

2. Crear entorno virtual:

```id="n94m5n"
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```id="jhe5v0"
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```id="ks9b0h"
python Virtual_Env.py
```

---

## 👤 Usuarios de prueba

| Usuario | Contraseña | Rol     |
| ------- | ---------- | ------- |
| admin   | 1234       | admin   |
| isidro  | 2345       | usuario |
| angel   | 2026       | usuario |

---

## 🚧 Próximas mejoras

* CRUD completo de mensajes (chat entre usuarios)
* API REST
* Mejoras visuales
* Notificaciones
* Deploy en servidor

---

## 📌 Notas

Proyecto realizado como práctica para aprender desarrollo web con Flask, manejo de bases de datos, seguridad básica e integración de APIs.

---

## 💪 Autor

Ángel León
