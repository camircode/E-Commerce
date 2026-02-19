from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for, flash
from db import ejecutar_consulta
from routes.auth import login_requerido

carrito_bp = Blueprint('carrito', __name__)


@carrito_bp.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    """Agrega un producto al carrito via AJAX"""
    datos = request.get_json()
    producto_id = datos.get('producto_id')
    cantidad = datos.get('cantidad', 1)

    if not producto_id:
        return jsonify({'exito': False, 'mensaje': 'Producto no especificado'}), 400

    # Verificar que el producto existe y tiene stock
    producto = ejecutar_consulta(
        "SELECT id, nombre, precio, stock, imagen FROM productos WHERE id = %s AND activo = 1",
        (producto_id,),
        obtener_uno=True
    )

    if not producto:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado'}), 404

    if producto['stock'] < cantidad:
        return jsonify({'exito': False, 'mensaje': f'Stock insuficiente. Solo quedan {producto["stock"]} unidades.'}), 400

    # Inicializar carrito en sesión si no existe
    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']
    str_id = str(producto_id)

    if str_id in carrito:
        nueva_cantidad = carrito[str_id]['cantidad'] + cantidad
        if nueva_cantidad > producto['stock']:
            return jsonify({'exito': False, 'mensaje': f'No puedes agregar más. Stock disponible: {producto["stock"]}'}), 400
        carrito[str_id]['cantidad'] = nueva_cantidad
    else:
        carrito[str_id] = {
            'producto_id': producto['id'],
            'nombre': producto['nombre'],
            'precio': float(producto['precio']),
            'imagen': producto['imagen'],
            'cantidad': cantidad
        }

    session['carrito'] = carrito
    session.modified = True

    # Calcular total de artículos en el carrito
    total_articulos = sum(item['cantidad'] for item in carrito.values())

    return jsonify({
        'exito': True,
        'mensaje': f'"{producto["nombre"]}" agregado al carrito',
        'total_articulos': total_articulos
    })


@carrito_bp.route('/api/carrito/actualizar', methods=['POST'])
def actualizar_carrito():
    """Actualiza la cantidad de un producto en el carrito via AJAX"""
    datos = request.get_json()
    producto_id = str(datos.get('producto_id'))
    cantidad = datos.get('cantidad', 1)

    if 'carrito' not in session or producto_id not in session['carrito']:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado en el carrito'}), 404

    if cantidad <= 0:
        del session['carrito'][producto_id]
        session.modified = True
        carrito = session.get('carrito', {})
        total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
        total_articulos = sum(item['cantidad'] for item in carrito.values())
        return jsonify({'exito': True, 'mensaje': 'Producto eliminado del carrito', 'total': total, 'total_articulos': total_articulos})

    # Verificar stock
    producto = ejecutar_consulta(
        "SELECT stock FROM productos WHERE id = %s",
        (int(producto_id),),
        obtener_uno=True
    )

    if producto and cantidad > producto['stock']:
        return jsonify({'exito': False, 'mensaje': f'Stock insuficiente. Disponible: {producto["stock"]}'}), 400

    session['carrito'][producto_id]['cantidad'] = cantidad
    session.modified = True

    carrito = session['carrito']
    subtotal = carrito[producto_id]['precio'] * cantidad
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    total_articulos = sum(item['cantidad'] for item in carrito.values())

    return jsonify({
        'exito': True,
        'subtotal': subtotal,
        'total': total,
        'total_articulos': total_articulos
    })


@carrito_bp.route('/api/carrito/eliminar', methods=['POST'])
def eliminar_del_carrito():
    """Elimina un producto del carrito via AJAX"""
    datos = request.get_json()
    producto_id = str(datos.get('producto_id'))

    if 'carrito' not in session or producto_id not in session['carrito']:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado en el carrito'}), 404

    del session['carrito'][producto_id]
    session.modified = True

    carrito = session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    total_articulos = sum(item['cantidad'] for item in carrito.values())

    return jsonify({
        'exito': True,
        'mensaje': 'Producto eliminado del carrito',
        'total': total,
        'total_articulos': total_articulos
    })


@carrito_bp.route('/carrito')
def ver_carrito():
    """Página del carrito de compras"""
    carrito = session.get('carrito', {})
    items = []
    total = 0

    for str_id, item in carrito.items():
        subtotal = item['precio'] * item['cantidad']
        items.append({**item, 'subtotal': subtotal})
        total += subtotal

    return render_template('carrito.html', items=items, total=total)


@carrito_bp.route('/api/carrito/cantidad')
def cantidad_carrito():
    """Devuelve la cantidad total de artículos en el carrito (para el badge)"""
    carrito = session.get('carrito', {})
    total_articulos = sum(item['cantidad'] for item in carrito.values())
    return jsonify({'total_articulos': total_articulos})
