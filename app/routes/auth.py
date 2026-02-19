from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from functools import wraps
import bcrypt
from db import ejecutar_consulta

auth_bp = Blueprint('auth', __name__)


def login_requerido(f):
    """Decorador que requiere que el usuario haya iniciado sesión"""
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'advertencia')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorador


def admin_requerido(f):
    """Decorador que requiere que el usuario sea administrador"""
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'advertencia')
            return redirect(url_for('auth.login'))
        if session.get('usuario_rol') != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'error')
            return redirect(url_for('productos.catalogo'))
        return f(*args, **kwargs)
    return decorador


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirmar_password = request.form.get('confirmar_password', '')

        # Validaciones del servidor
        errores = []
        if not nombre or len(nombre) < 3:
            errores.append('El nombre debe tener al menos 3 caracteres.')
        if not email or '@' not in email:
            errores.append('Ingresa un correo electrónico válido.')
        if not password or len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        if password != confirmar_password:
            errores.append('Las contraseñas no coinciden.')

        # Verificar si el email ya existe
        usuario_existente = ejecutar_consulta(
            "SELECT id FROM usuarios WHERE email = %s",
            (email,),
            obtener_uno=True
        )
        if usuario_existente:
            errores.append('Este correo electrónico ya está registrado.')

        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('registro.html', nombre=nombre, email=email)

        # Encriptar contraseña con bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insertar usuario
        usuario_id = ejecutar_consulta(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, password_hash.decode('utf-8')),
            obtener_id=True
        )

        if usuario_id:
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'exito')
            return redirect(url_for('auth.login'))
        else:
            flash('Error al registrar el usuario. Inténtalo de nuevo.', 'error')

    return render_template('registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html', email=email)

        # Buscar usuario con consulta preparada
        usuario = ejecutar_consulta(
            "SELECT id, nombre, email, password, rol FROM usuarios WHERE email = %s",
            (email,),
            obtener_uno=True
        )

        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario['password'].encode('utf-8')):
            # Crear sesión
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre']
            session['usuario_email'] = usuario['email']
            session['usuario_rol'] = usuario['rol']
            session.permanent = True

            flash(f'¡Bienvenido, {usuario["nombre"]}!', 'exito')

            if usuario['rol'] == 'admin':
                return redirect(url_for('admin.panel'))
            return redirect(url_for('productos.catalogo'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'error')
            return render_template('login.html', email=email)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('principal.inicio'))
