# 📊 Diagrama Entidad-Relación — TiendaOnline

## Diagrama ER

```mermaid
erDiagram
    CATEGORIAS ||--o{ PRODUCTOS : "tiene"
    USUARIOS ||--o{ PEDIDOS : "realiza"
    PEDIDOS ||--|{ DETALLE_PEDIDO : "contiene"
    PRODUCTOS ||--o{ DETALLE_PEDIDO : "aparece en"

    CATEGORIAS {
        INT id PK
        VARCHAR nombre
        TEXT descripcion
    }

    USUARIOS {
        INT id PK
        VARCHAR nombre
        VARCHAR email UK
        VARCHAR password
        ENUM rol "admin | cliente"
        DATETIME fecha_registro
    }

    PRODUCTOS {
        INT id PK
        VARCHAR nombre
        TEXT descripcion
        DECIMAL precio
        INT stock
        VARCHAR imagen
        INT categoria_id FK
        TINYINT activo
        DATETIME fecha_creacion
    }

    PEDIDOS {
        INT id PK
        INT usuario_id FK
        VARCHAR numero_orden UK
        DECIMAL total
        ENUM estado "pendiente | pagado | enviado | entregado | cancelado"
        TEXT direccion_envio
        VARCHAR telefono
        DATETIME fecha
    }

    DETALLE_PEDIDO {
        INT id PK
        INT pedido_id FK
        INT producto_id FK
        INT cantidad
        DECIMAL precio_unitario
        DECIMAL subtotal
    }
```

## Relaciones

| Relación | Tipo | Descripción | Regla de Eliminación |
|----------|------|-------------|---------------------|
| categorias → productos | 1:N | Una categoría tiene muchos productos | ON DELETE SET NULL |
| usuarios → pedidos | 1:N | Un usuario tiene muchos pedidos | ON DELETE CASCADE |
| pedidos → detalle_pedido | 1:N | Un pedido tiene muchas líneas de detalle | ON DELETE CASCADE |
| productos → detalle_pedido | 1:N | Un producto aparece en muchos detalles | ON DELETE CASCADE |

## Índices

```mermaid
graph LR
    A["idx_productos_categoria"] --> B["productos.categoria_id"]
    C["idx_productos_precio"] --> D["productos.precio"]
    E["idx_pedidos_usuario"] --> F["pedidos.usuario_id"]
    G["idx_pedidos_fecha"] --> H["pedidos.fecha"]
    I["idx_detalle_pedido"] --> J["detalle_pedido.pedido_id"]
```

## Estados de Pedido

```mermaid
stateDiagram-v2
    [*] --> pendiente
    pendiente --> pagado : Pago exitoso
    pagado --> enviado : Admin envía
    enviado --> entregado : Entrega confirmada
    pendiente --> cancelado : Cancelar
    pagado --> cancelado : Cancelar
```

## Roles de Usuario

| Rol | Acceso |
|-----|--------|
| `cliente` | Catálogo, carrito, compras, historial |
| `admin` | Todo lo anterior + panel de administración |
