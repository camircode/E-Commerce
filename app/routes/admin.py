import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from db import ejecutar_consulta, obtener_conexion
from routes.auth import admin_requerido
from config import Configuracion

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_requerido
def panel():
    """Panel de administración con estadísticas"""
    # Estadísticas de ventas
    ventas_totales = ejecutar_consulta(
        "SELECT COALESCE(SUM(total), 0) as total_ventas, COUNT(*) as total_pedidos FROM pedidos WHERE estado = 'pagado'",
        obtener_uno=True
    )

    total_usuarios = ejecutar_consulta(
        "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'cliente'",
        obtener_uno=True
    )

    total_productos = ejecutar_consulta(
        "SELECT COUNT(*) as total FROM productos WHERE activo = 1",
        obtener_uno=True
    )

    productos_bajo_stock = ejecutar_consulta(
        "SELECT COUNT(*) as total FROM productos WHERE stock <= 5 AND activo = 1",
        obtener_uno=True
    )

    # Pedidos recientes
    pedidos_recientes = ejecutar_consulta(
        """SELECT p.*, u.nombre as usuario_nombre 
           FROM pedidos p JOIN usuarios u ON p.usuario_id = u.id 
           ORDER BY p.fecha DESC LIMIT 10""",
        obtener_todos=True
    ) or []

    # Productos más vendidos
    productos_top = ejecutar_consulta(
        """SELECT pr.nombre, SUM(dp.cantidad) as total_vendido, SUM(dp.subtotal) as total_ingresos
           FROM detalle_pedido dp 
           JOIN productos pr ON dp.producto_id = pr.id
           JOIN pedidos pe ON dp.pedido_id = pe.id
           WHERE pe.estado = 'pagado'
           GROUP BY pr.id, pr.nombre
           ORDER BY total_vendido DESC LIMIT 5""",
        obtener_todos=True
    ) or []

    # Ventas por mes (últimos 6 meses)
    ventas_mensuales = ejecutar_consulta(
        """SELECT DATE_FORMAT(fecha, '%%Y-%%m') as mes, 
           COALESCE(SUM(total), 0) as total_ventas, 
           COUNT(*) as total_pedidos
           FROM pedidos WHERE estado = 'pagado'
           GROUP BY DATE_FORMAT(fecha, '%%Y-%%m')
           ORDER BY mes DESC LIMIT 6""",
        obtener_todos=True
    ) or []

    return render_template('admin/panel.html',
                           ventas_totales=ventas_totales,
                           total_usuarios=total_usuarios,
                           total_productos=total_productos,
                           productos_bajo_stock=productos_bajo_stock,
                           pedidos_recientes=pedidos_recientes,
                           productos_top=productos_top,
                           ventas_mensuales=ventas_mensuales)


@admin_bp.route('/productos')
@admin_requerido
def listar_productos():
    """Lista todos los productos para administración"""
    productos = ejecutar_consulta(
        """SELECT p.*, c.nombre as categoria_nombre 
           FROM productos p 
           LEFT JOIN categorias c ON p.categoria_id = c.id 
           ORDER BY p.fecha_creacion DESC""",
        obtener_todos=True
    ) or []

    return render_template('admin/productos.html', productos=productos)


def archivo_permitido(nombre_archivo):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in Configuracion.EXTENSIONES_PERMITIDAS


@admin_bp.route('/productos/crear', methods=['GET', 'POST'])
@admin_requerido
def crear_producto():
    """Crear un nuevo producto"""
    categorias = ejecutar_consulta("SELECT * FROM categorias ORDER BY nombre", obtener_todos=True) or []

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        categoria_id = request.form.get('categoria_id', type=int)
        imagen_nombre = 'sin_imagen.png'

        # Validaciones
        if not nombre:
            flash('El nombre del producto es obligatorio.', 'error')
            return render_template('admin/producto_form.html', categorias=categorias, accion='Crear')

        if precio <= 0:
            flash('El precio debe ser mayor a 0.', 'error')
            return render_template('admin/producto_form.html', categorias=categorias, accion='Crear')

        # Procesar imagen
        if 'imagen' in request.files:
            archivo = request.files['imagen']
            if archivo.filename and archivo_permitido(archivo.filename):
                imagen_nombre = secure_filename(archivo.filename)
                ruta_guardado = os.path.join(Configuracion.CARPETA_UPLOADS, imagen_nombre)
                os.makedirs(Configuracion.CARPETA_UPLOADS, exist_ok=True)
                archivo.save(ruta_guardado)

        producto_id = ejecutar_consulta(
            """INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, descripcion, precio, stock, imagen_nombre, categoria_id),
            obtener_id=True
        )

        if producto_id:
            flash('Producto creado exitosamente.', 'exito')
            return redirect(url_for('admin.listar_productos'))
        else:
            flash('Error al crear el producto.', 'error')

    return render_template('admin/producto_form.html', categorias=categorias, accion='Crear')


@admin_bp.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@admin_requerido
def editar_producto(producto_id):
    """Editar un producto existente"""
    producto = ejecutar_consulta(
        "SELECT * FROM productos WHERE id = %s", (producto_id,), obtener_uno=True
    )

    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('admin.listar_productos'))

    categorias = ejecutar_consulta("SELECT * FROM categorias ORDER BY nombre", obtener_todos=True) or []

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        categoria_id = request.form.get('categoria_id', type=int)
        activo = 1 if request.form.get('activo') else 0
        imagen_nombre = producto['imagen']

        if not nombre:
            flash('El nombre del producto es obligatorio.', 'error')
            return render_template('admin/producto_form.html', producto=producto, categorias=categorias, accion='Editar')

        # Procesar nueva imagen si se subió
        if 'imagen' in request.files:
            archivo = request.files['imagen']
            if archivo.filename and archivo_permitido(archivo.filename):
                imagen_nombre = secure_filename(archivo.filename)
                ruta_guardado = os.path.join(Configuracion.CARPETA_UPLOADS, imagen_nombre)
                os.makedirs(Configuracion.CARPETA_UPLOADS, exist_ok=True)
                archivo.save(ruta_guardado)

        filas = ejecutar_consulta(
            """UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, 
               stock = %s, imagen = %s, categoria_id = %s, activo = %s WHERE id = %s""",
            (nombre, descripcion, precio, stock, imagen_nombre, categoria_id, activo, producto_id)
        )

        if filas is not None:
            flash('Producto actualizado exitosamente.', 'exito')
            return redirect(url_for('admin.listar_productos'))
        else:
            flash('Error al actualizar el producto.', 'error')

    return render_template('admin/producto_form.html', producto=producto, categorias=categorias, accion='Editar')


@admin_bp.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
@admin_requerido
def eliminar_producto(producto_id):
    """Eliminar un producto (desactivar)"""
    ejecutar_consulta("UPDATE productos SET activo = 0 WHERE id = %s", (producto_id,))
    flash('Producto eliminado exitosamente.', 'exito')
    return redirect(url_for('admin.listar_productos'))


@admin_bp.route('/pedidos')
@admin_requerido
def listar_pedidos():
    """Lista todos los pedidos"""
    pedidos = ejecutar_consulta(
        """SELECT p.*, u.nombre as usuario_nombre, u.email as usuario_email
           FROM pedidos p JOIN usuarios u ON p.usuario_id = u.id
           ORDER BY p.fecha DESC""",
        obtener_todos=True
    ) or []

    return render_template('admin/pedidos.html', pedidos=pedidos)


@admin_bp.route('/pedidos/actualizar/<int:pedido_id>', methods=['POST'])
@admin_requerido
def actualizar_pedido(pedido_id):
    """Actualizar el estado de un pedido"""
    nuevo_estado = request.form.get('estado')
    estados_validos = ['pendiente', 'pagado', 'enviado', 'entregado', 'cancelado']

    if nuevo_estado not in estados_validos:
        flash('Estado no válido.', 'error')
        return redirect(url_for('admin.listar_pedidos'))

    ejecutar_consulta(
        "UPDATE pedidos SET estado = %s WHERE id = %s",
        (nuevo_estado, pedido_id)
    )

    flash(f'Estado del pedido actualizado a "{nuevo_estado}".', 'exito')
    return redirect(url_for('admin.listar_pedidos'))


# ============================================
# CRUD de Categorías
# ============================================

@admin_bp.route('/categorias')
@admin_requerido
def listar_categorias():
    """Lista todas las categorías para administración"""
    categorias = ejecutar_consulta(
        """SELECT c.*, COUNT(p.id) as total_productos 
           FROM categorias c 
           LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = 1 
           GROUP BY c.id 
           ORDER BY c.nombre""",
        obtener_todos=True
    ) or []

    return render_template('admin/categorias.html', categorias=categorias)


@admin_bp.route('/categorias/crear', methods=['GET', 'POST'])
@admin_requerido
def crear_categoria():
    """Crear una nueva categoría"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return render_template('admin/categoria_form.html', accion='Crear')

        # Verificar si ya existe una categoría con ese nombre
        existente = ejecutar_consulta(
            "SELECT id FROM categorias WHERE nombre = %s", (nombre,), obtener_uno=True
        )
        if existente:
            flash('Ya existe una categoría con ese nombre.', 'error')
            return render_template('admin/categoria_form.html', accion='Crear', nombre=nombre, descripcion=descripcion)

        categoria_id = ejecutar_consulta(
            "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
            (nombre, descripcion),
            obtener_id=True
        )

        if categoria_id:
            flash('Categoría creada exitosamente.', 'exito')
            return redirect(url_for('admin.listar_categorias'))
        else:
            flash('Error al crear la categoría.', 'error')

    return render_template('admin/categoria_form.html', accion='Crear')


@admin_bp.route('/categorias/editar/<int:categoria_id>', methods=['GET', 'POST'])
@admin_requerido
def editar_categoria(categoria_id):
    """Editar una categoría existente"""
    categoria = ejecutar_consulta(
        "SELECT * FROM categorias WHERE id = %s", (categoria_id,), obtener_uno=True
    )

    if not categoria:
        flash('Categoría no encontrada.', 'error')
        return redirect(url_for('admin.listar_categorias'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return render_template('admin/categoria_form.html', categoria=categoria, accion='Editar')

        # Verificar duplicado (excluyendo la categoría actual)
        existente = ejecutar_consulta(
            "SELECT id FROM categorias WHERE nombre = %s AND id != %s",
            (nombre, categoria_id), obtener_uno=True
        )
        if existente:
            flash('Ya existe otra categoría con ese nombre.', 'error')
            return render_template('admin/categoria_form.html', categoria=categoria, accion='Editar')

        filas = ejecutar_consulta(
            "UPDATE categorias SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, categoria_id)
        )

        if filas is not None:
            flash('Categoría actualizada exitosamente.', 'exito')
            return redirect(url_for('admin.listar_categorias'))
        else:
            flash('Error al actualizar la categoría.', 'error')

    return render_template('admin/categoria_form.html', categoria=categoria, accion='Editar')


@admin_bp.route('/categorias/eliminar/<int:categoria_id>', methods=['POST'])
@admin_requerido
def eliminar_categoria(categoria_id):
    """Eliminar una categoría (solo si no tiene productos asociados)"""
    productos_asociados = ejecutar_consulta(
        "SELECT COUNT(*) as total FROM productos WHERE categoria_id = %s AND activo = 1",
        (categoria_id,), obtener_uno=True
    )

    if productos_asociados and productos_asociados['total'] > 0:
        flash(f'No se puede eliminar: la categoría tiene {productos_asociados["total"]} producto(s) activo(s) asociado(s).', 'error')
        return redirect(url_for('admin.listar_categorias'))

    ejecutar_consulta("DELETE FROM categorias WHERE id = %s", (categoria_id,))
    flash('Categoría eliminada exitosamente.', 'exito')
    return redirect(url_for('admin.listar_categorias'))
