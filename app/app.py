import time
import bcrypt
from flask import Flask, render_template, session
from datetime import timedelta
from config import Configuracion
from db import ejecutar_consulta, obtener_conexion

# Importar blueprints
from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.pedidos import pedidos_bp
from routes.admin import admin_bp


def inicializar_admin():
    """Crea el usuario administrador si no existe con contraseña encriptada"""
    # Esperar a que la base de datos esté lista
    intentos = 0
    while intentos < 30:
        conexion = obtener_conexion()
        if conexion:
            conexion.close()
            break
        print(f"Esperando conexión a la base de datos... intento {intentos + 1}")
        time.sleep(2)
        intentos += 1

    # Verificar si el admin ya existe
    admin = ejecutar_consulta(
        "SELECT id FROM usuarios WHERE email = %s",
        ('admin@tienda.com',),
        obtener_uno=True
    )

    if not admin:
        # Crear admin con contraseña encriptada con bcrypt
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        ejecutar_consulta(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, 'admin')",
            ('Administrador', 'admin@tienda.com', password_hash.decode('utf-8'))
        )
        print("✓ Usuario administrador creado exitosamente.")
    else:
        print("✓ Usuario administrador ya existe")


def crear_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    app.secret_key = Configuracion.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Configuracion.MAX_CONTENIDO
    app.permanent_session_lifetime = timedelta(hours=24)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(admin_bp)

    # Contexto global para templates
    @app.context_processor
    def contexto_global():
        carrito = session.get('carrito', {})
        total_carrito = sum(item['cantidad'] for item in carrito.values())
        categorias_nav = ejecutar_consulta(
            "SELECT * FROM categorias ORDER BY nombre",
            obtener_todos=True
        ) or []
        return {
            'total_carrito': total_carrito,
            'categorias_nav': categorias_nav
        }

    # Ruta principal
    @app.route('/', endpoint='principal.inicio')
    def inicio():
        """Página de inicio dinámica"""
        productos_destacados = ejecutar_consulta(
            "SELECT * FROM productos WHERE activo = 1 ORDER BY fecha_creacion DESC LIMIT 8",
            obtener_todos=True
        ) or []

        categorias = ejecutar_consulta(
            "SELECT c.*, COUNT(p.id) as total_productos FROM categorias c LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = 1 GROUP BY c.id ORDER BY c.nombre",
            obtener_todos=True
        ) or []

        return render_template('inicio.html', productos=productos_destacados, categorias=categorias)

    # Manejo de errores
    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def error_servidor(e):
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    app = crear_app()
    inicializar_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
