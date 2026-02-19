import mysql.connector
from mysql.connector import Error
from config import Configuracion


def obtener_conexion():
    """Obtiene una conexión a la base de datos MySQL"""
    try:
        conexion = mysql.connector.connect(
            host=Configuracion.DB_HOST,
            port=Configuracion.DB_PORT,
            user=Configuracion.DB_USER,
            password=Configuracion.DB_PASSWORD,
            database=Configuracion.DB_NAME,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def ejecutar_consulta(consulta, parametros=None, obtener_uno=False, obtener_todos=False, obtener_id=False):
    """
    Ejecuta una consulta preparada de forma segura (anti-SQL injection).
    
    Args:
        consulta: La consulta SQL con placeholders %s
        parametros: Tupla con los parámetros
        obtener_uno: Si True, retorna un solo registro
        obtener_todos: Si True, retorna todos los registros
        obtener_id: Si True, retorna el ID del último registro insertado
    
    Returns:
        Resultado de la consulta según los parámetros
    """
    conexion = obtener_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(consulta, parametros or ())
        
        if obtener_uno:
            resultado = cursor.fetchone()
            return resultado
        elif obtener_todos:
            resultado = cursor.fetchall()
            return resultado
        elif obtener_id:
            conexion.commit()
            return cursor.lastrowid
        else:
            conexion.commit()
            return cursor.rowcount
    except Error as e:
        print(f"Error en la consulta: {e}")
        conexion.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
