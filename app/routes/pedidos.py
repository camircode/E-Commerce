import uuid
from datetime import datetime
from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from db import ejecutar_consulta, obtener_conexion
from routes.auth import login_requerido

pedidos_bp = Blueprint('pedidos', __name__)


def generar_numero_orden():
    """Genera un número de orden único"""
    fecha = datetime.now().strftime('%Y%m%d')
    codigo = uuid.uuid4().hex[:6].upper()
    return f'ORD-{fecha}-{codigo}'


@pedidos_bp.route('/checkout', methods=['GET', 'POST'])
@login_requerido
def checkout():
    """Página de checkout para confirmar la compra"""
    carrito = session.get('carrito', {})

    if not carrito:
        flash('Tu carrito está vacío.', 'advertencia')
        return redirect(url_for('productos.catalogo'))

    if request.method == 'POST':
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()

        if not direccion or not telefono:
            flash('Por favor completa la dirección y teléfono.', 'error')
            items = []
            total = 0
            for item in carrito.values():
                subtotal = item['precio'] * item['cantidad']
                items.append({**item, 'subtotal': subtotal})
                total += subtotal
            return render_template('checkout.html', items=items, total=total)

        # Verificar stock de todos los productos
        for str_id, item in carrito.items():
            producto = ejecutar_consulta(
                "SELECT stock FROM productos WHERE id = %s",
                (item['producto_id'],),
                obtener_uno=True
            )
            if not producto or producto['stock'] < item['cantidad']:
                flash(f'Stock insuficiente para "{item["nombre"]}".', 'error')
                return redirect(url_for('carrito.ver_carrito'))

        # Calcular total
        total = sum(item['precio'] * item['cantidad'] for item in carrito.values())

        # Generar número de orden
        numero_orden = generar_numero_orden()

        # Crear pedido
        pedido_id = ejecutar_consulta(
            """INSERT INTO pedidos (usuario_id, numero_orden, total, estado, direccion_envio, telefono)
               VALUES (%s, %s, %s, 'pendiente', %s, %s)""",
            (session['usuario_id'], numero_orden, total, direccion, telefono),
            obtener_id=True
        )

        if not pedido_id:
            flash('Error al crear el pedido. Inténtalo de nuevo.', 'error')
            return redirect(url_for('carrito.ver_carrito'))

        # Insertar detalles del pedido
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            for item in carrito.values():
                subtotal = item['precio'] * item['cantidad']
                cursor.execute(
                    """INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (pedido_id, item['producto_id'], item['cantidad'], item['precio'], subtotal)
                )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            print(f"Error al insertar detalles: {e}")
            flash('Error al procesar el pedido.', 'error')
            return redirect(url_for('carrito.ver_carrito'))
        finally:
            cursor.close()
            conexion.close()

        # Redirigir a la simulación de pago
        return redirect(url_for('pedidos.pago', pedido_id=pedido_id))

    # GET: Mostrar formulario de checkout
    items = []
    total = 0
    for item in carrito.values():
        subtotal = item['precio'] * item['cantidad']
        items.append({**item, 'subtotal': subtotal})
        total += subtotal

    return render_template('checkout.html', items=items, total=total)


@pedidos_bp.route('/pago/<int:pedido_id>', methods=['GET'])
@login_requerido
def pago(pedido_id):
    """Página de simulación de pago"""
    pedido = ejecutar_consulta(
        "SELECT * FROM pedidos WHERE id = %s AND usuario_id = %s",
        (pedido_id, session['usuario_id']),
        obtener_uno=True
    )

    if not pedido:
        flash('Pedido no encontrado.', 'error')
        return redirect(url_for('pedidos.mis_pedidos'))

    if pedido['estado'] != 'pendiente':
        flash('Este pedido ya fue procesado.', 'info')
        return redirect(url_for('pedidos.mis_pedidos'))

    return render_template('pago.html', pedido=pedido)


@pedidos_bp.route('/pago/procesar', methods=['POST'])
@login_requerido
def procesar_pago():
    """Procesa la simulación de pago"""
    pedido_id = request.form.get('pedido_id', type=int)
    numero_tarjeta = request.form.get('numero_tarjeta', '').strip()
    nombre_titular = request.form.get('nombre_titular', '').strip()

    if not pedido_id or not numero_tarjeta or not nombre_titular:
        flash('Por favor completa todos los datos de pago.', 'error')
        return redirect(url_for('pedidos.pago', pedido_id=pedido_id))

    # Verificar pedido
    pedido = ejecutar_consulta(
        "SELECT * FROM pedidos WHERE id = %s AND usuario_id = %s AND estado = 'pendiente'",
        (pedido_id, session['usuario_id']),
        obtener_uno=True
    )

    if not pedido:
        flash('Pedido no encontrado o ya procesado.', 'error')
        return redirect(url_for('pedidos.mis_pedidos'))

    # Obtener detalles del pedido para actualizar stock
    detalles = ejecutar_consulta(
        "SELECT producto_id, cantidad FROM detalle_pedido WHERE pedido_id = %s",
        (pedido_id,),
        obtener_todos=True
    ) or []

    # Actualizar stock y estado del pedido
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()

        # Descontar stock
        for detalle in detalles:
            cursor.execute(
                "UPDATE productos SET stock = stock - %s WHERE id = %s AND stock >= %s",
                (detalle['cantidad'], detalle['producto_id'], detalle['cantidad'])
            )

        # Marcar pedido como pagado
        cursor.execute(
            "UPDATE pedidos SET estado = 'pagado' WHERE id = %s",
            (pedido_id,)
        )

        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print(f"Error al procesar pago: {e}")
        flash('Error al procesar el pago.', 'error')
        return redirect(url_for('pedidos.pago', pedido_id=pedido_id))
    finally:
        cursor.close()
        conexion.close()

    # Limpiar carrito
    session.pop('carrito', None)
    session.modified = True

    flash(f'¡Pago procesado exitosamente! Tu número de orden es: {pedido["numero_orden"]}', 'exito')
    return redirect(url_for('pedidos.confirmacion', pedido_id=pedido_id))


@pedidos_bp.route('/confirmacion/<int:pedido_id>')
@login_requerido
def confirmacion(pedido_id):
    """Página de confirmación de compra"""
    pedido = ejecutar_consulta(
        "SELECT * FROM pedidos WHERE id = %s AND usuario_id = %s",
        (pedido_id, session['usuario_id']),
        obtener_uno=True
    )

    detalles = ejecutar_consulta(
        """SELECT dp.*, p.nombre, p.imagen 
           FROM detalle_pedido dp 
           JOIN productos p ON dp.producto_id = p.id 
           WHERE dp.pedido_id = %s""",
        (pedido_id,),
        obtener_todos=True
    ) or []

    return render_template('confirmacion.html', pedido=pedido, detalles=detalles)


@pedidos_bp.route('/mis-pedidos')
@login_requerido
def mis_pedidos():
    """Historial de compras del usuario"""
    pedidos = ejecutar_consulta(
        """SELECT p.*, 
           (SELECT COUNT(*) FROM detalle_pedido WHERE pedido_id = p.id) as total_items
           FROM pedidos p 
           WHERE p.usuario_id = %s 
           ORDER BY p.fecha DESC""",
        (session['usuario_id'],),
        obtener_todos=True
    ) or []

    return render_template('mis_pedidos.html', pedidos=pedidos)


@pedidos_bp.route('/pedido/<int:pedido_id>')
@login_requerido
def detalle_pedido(pedido_id):
    """Detalle de un pedido específico"""
    pedido = ejecutar_consulta(
        "SELECT * FROM pedidos WHERE id = %s AND usuario_id = %s",
        (pedido_id, session['usuario_id']),
        obtener_uno=True
    )

    if not pedido:
        flash('Pedido no encontrado.', 'error')
        return redirect(url_for('pedidos.mis_pedidos'))

    detalles = ejecutar_consulta(
        """SELECT dp.*, p.nombre, p.imagen 
           FROM detalle_pedido dp 
           JOIN productos p ON dp.producto_id = p.id 
           WHERE dp.pedido_id = %s""",
        (pedido_id,),
        obtener_todos=True
    ) or []

    return render_template('detalle_pedido.html', pedido=pedido, detalles=detalles)
