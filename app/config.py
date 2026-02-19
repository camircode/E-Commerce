import os

class Configuracion:
    """Configuración de la aplicación Flask"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'clave_secreta_por_defecto')
    
    # Configuración de la base de datos
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('MYSQL_USER', 'ecommerce_user')
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'ecommerce_pass_2025')
    DB_NAME = os.environ.get('MYSQL_DATABASE', 'ecommerce_db')
    
    # Configuración de uploads
    CARPETA_UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENIDO = 16 * 1024 * 1024  # 16 MB máximo
