from flask import Blueprint, request, render_template, jsonify
from db import ejecutar_consulta

productos_bp = Blueprint('productos', __name__)


@productos_bp.route('/catalogo')
def catalogo():
    """Página del catálogo de productos con filtros"""
    # Obtener parámetros de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    categoria_id = request.args.get('categoria', '', type=str)
    precio_min = request.args.get('precio_min', 0, type=float)
    precio_max = request.args.get('precio_max', 99999, type=float)
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 12

    # Construir consulta dinámica con parámetros preparados
    consulta = "SELECT p.*, c.nombre as categoria_nombre FROM productos p LEFT JOIN categorias c ON p.categoria_id = c.id WHERE p.activo = 1"
    parametros = []

    if busqueda:
        consulta += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s)"
        parametros.extend([f'%{busqueda}%', f'%{busqueda}%'])

    if categoria_id:
        consulta += " AND p.categoria_id = %s"
        parametros.append(int(categoria_id))

    if precio_min > 0:
        consulta += " AND p.precio >= %s"
        parametros.append(precio_min)

    if precio_max < 99999:
        consulta += " AND p.precio <= %s"
        parametros.append(precio_max)

    # Contar total para paginación
    consulta_conteo = consulta.replace(
        "SELECT p.*, c.nombre as categoria_nombre",
        "SELECT COUNT(*) as total"
    )
    total_resultado = ejecutar_consulta(consulta_conteo, tuple(parametros), obtener_uno=True)
    total_productos = total_resultado['total'] if total_resultado else 0
    total_paginas = max(1, (total_productos + por_pagina - 1) // por_pagina)

    # Agregar orden y paginación
    consulta += " ORDER BY p.fecha_creacion DESC LIMIT %s OFFSET %s"
    parametros.extend([por_pagina, (pagina - 1) * por_pagina])

    productos = ejecutar_consulta(consulta, tuple(parametros), obtener_todos=True) or []

    # Obtener categorías para el filtro
    categorias = ejecutar_consulta(
        "SELECT * FROM categorias ORDER BY nombre",
        obtener_todos=True
    ) or []

    # Obtener rango de precios
    rango_precios = ejecutar_consulta(
        "SELECT MIN(precio) as min_precio, MAX(precio) as max_precio FROM productos WHERE activo = 1",
        obtener_uno=True
    )

    return render_template('catalogo.html',
                           productos=productos,
                           categorias=categorias,
                           busqueda=busqueda,
                           categoria_id=categoria_id,
                           precio_min=precio_min,
                           precio_max=precio_max,
                           pagina=pagina,
                           total_paginas=total_paginas,
                           total_productos=total_productos,
                           rango_precios=rango_precios)


@productos_bp.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    """Vista detallada de un producto"""
    producto = ejecutar_consulta(
        """SELECT p.*, c.nombre as categoria_nombre 
           FROM productos p 
           LEFT JOIN categorias c ON p.categoria_id = c.id 
           WHERE p.id = %s AND p.activo = 1""",
        (producto_id,),
        obtener_uno=True
    )

    if not producto:
        return render_template('404.html'), 404

    # Productos relacionados (misma categoría)
    relacionados = ejecutar_consulta(
        """SELECT * FROM productos 
           WHERE categoria_id = %s AND id != %s AND activo = 1 
           ORDER BY RAND() LIMIT 4""",
        (producto['categoria_id'], producto_id),
        obtener_todos=True
    ) or []

    return render_template('producto.html', producto=producto, relacionados=relacionados)


@productos_bp.route('/api/productos')
def api_productos():
    """API JSON para obtener productos (usado por AJAX)"""
    busqueda = request.args.get('busqueda', '').strip()
    categoria_id = request.args.get('categoria', '', type=str)

    consulta = "SELECT p.id, p.nombre, p.precio, p.imagen, p.stock FROM productos p WHERE p.activo = 1"
    parametros = []

    if busqueda:
        consulta += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s)"
        parametros.extend([f'%{busqueda}%', f'%{busqueda}%'])

    if categoria_id:
        consulta += " AND p.categoria_id = %s"
        parametros.append(int(categoria_id))

    consulta += " ORDER BY p.fecha_creacion DESC LIMIT 50"
    productos = ejecutar_consulta(consulta, tuple(parametros), obtener_todos=True) or []

    return jsonify(productos)
