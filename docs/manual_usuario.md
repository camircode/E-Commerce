# 📗 Manual de Usuario — TiendaOnline

## Bienvenido a TiendaOnline

Esta guía te explica cómo utilizar todas las funcionalidades de la plataforma de comercio electrónico.

---

## 1. Página de Inicio

Al ingresar a la tienda (http://localhost:5000), verás:
- **Banner principal** con información destacada
- **Categorías disponibles** (Electrónica, Ropa, Hogar, Deportes, Libros)
- **Productos destacados** con imagen, nombre y precio
- **Barra de navegación** con acceso a catálogo, carrito e inicio de sesión

---

## 2. Registro de Cuenta

1. Haz clic en **"Registrarse"** en la barra de navegación
2. Completa el formulario:
   - **Nombre completo** (mínimo 3 caracteres)
   - **Correo electrónico** (formato válido)
   - **Contraseña** (mínimo 6 caracteres)
   - **Confirmar contraseña**
3. Haz clic en **"Crear Cuenta"**
4. Serás redirigido al inicio de sesión

> **Nota**: Tu contraseña se guarda encriptada de forma segura.

---

## 3. Inicio de Sesión

1. Haz clic en **"Iniciar Sesión"** en la barra de navegación
2. Ingresa tu **correo electrónico** y **contraseña**
3. Haz clic en **"Iniciar Sesión"**
4. Serás redirigido a la página de inicio

---

## 4. Navegación del Catálogo

### Buscar productos
- Usa la **barra de búsqueda** para encontrar productos por nombre o descripción
- Los resultados se muestran con paginación

### Filtrar por categoría
- Selecciona una categoría en el menú lateral del catálogo
- Solo se mostrarán productos de esa categoría

### Filtrar por precio
- Usa los **controles deslizantes** (slider) para establecer un rango de precio mínimo y máximo
- Haz clic en **"Aplicar Filtros"** para ver los resultados

---

## 5. Ver un Producto

1. Haz clic en cualquier producto del catálogo
2. Verás:
   - **Imagen del producto**
   - **Nombre y descripción detallada**
   - **Precio**
   - **Disponibilidad** (stock actual)
   - **Productos relacionados** de la misma categoría
3. Selecciona la **cantidad** deseada
4. Haz clic en **"Agregar al Carrito"**

---

## 6. Carrito de Compras

### Agregar productos
- Desde la página de detalle, haz clic en **"Agregar al Carrito"**
- El ícono del carrito en la barra de navegación muestra la cantidad total de artículos

### Ver carrito
- Haz clic en el ícono del **carrito** 🛒 en la barra de navegación
- Verás la lista de productos, cantidades y subtotales

### Modificar cantidades
- Usa los botones **+** y **−** para ajustar la cantidad
- El total se actualiza automáticamente (sin recargar la página)

### Eliminar productos
- Haz clic en el ícono de **eliminar** (🗑️) junto al producto

### Proceder a la compra
- Haz clic en **"Proceder al Checkout"**

---

## 7. Proceso de Compra

### Paso 1: Checkout
1. Verifica el **resumen de tu pedido**
2. Ingresa la **dirección de envío** completa
3. Ingresa tu **teléfono de contacto**
4. Haz clic en **"Proceder al Pago"**

### Paso 2: Pago (Simulación)
1. Verás un formulario de tarjeta con vista previa visual
2. Ingresa los datos de la tarjeta:
   - **Número de tarjeta** (16 dígitos)
   - **Nombre del titular**
   - **Fecha de expiración** (MM/AA)
   - **CVV** (3 dígitos)
3. Haz clic en **"Pagar $X.XX"**

> **Nota**: Este es un simulador de pago. No se procesan cargos reales.

### Paso 3: Confirmación
- Verás una pantalla de **confirmación exitosa** con:
  - Número de orden asignado automáticamente
  - Detalle de los productos comprados
  - Total pagado

---

## 8. Historial de Pedidos

1. Haz clic en tu **nombre de usuario** en la barra de navegación
2. Selecciona **"Mis Pedidos"**
3. Verás la lista de todos tus pedidos con:
   - Número de orden
   - Fecha de compra
   - Total
   - Estado (Pendiente, Pagado, Enviado, Entregado, Cancelado)
4. Haz clic en **"Ver Detalle"** para ver los productos de un pedido específico

---

## 9. Panel de Administración (Solo Administradores)

### Acceso
- Inicia sesión con las credenciales de administrador:
  - **Email**: admin@tienda.com
  - **Contraseña**: admin123
- Aparecerá la opción **"Admin"** en la barra de navegación

### Dashboard (Estadísticas)
- **Ventas totales**: Monto total de pedidos pagados
- **Total de pedidos**: Número de pedidos pagados
- **Clientes registrados**: Número de usuarios
- **Productos activos**: Productos disponibles en la tienda
- **Productos más vendidos**: Top 5 por ingresos
- **Pedidos recientes**: Últimos 5 pedidos
- **Ventas mensuales**: Desglose por mes

### Gestión de Productos
1. Ve a **Admin → Productos**
2. Acciones disponibles:
   - **Crear**: Haz clic en "Nuevo Producto", llena el formulario
   - **Editar**: Haz clic en el ícono de lápiz ✏️
   - **Eliminar**: Haz clic en el ícono de papelera 🗑️
3. Campos del producto:
   - Nombre, descripción, precio, stock
   - Categoría, imagen, estado (activo/inactivo)

### Gestión de Pedidos
1. Ve a **Admin → Pedidos**
2. Verás la lista de todos los pedidos de todos los clientes
3. Puedes cambiar el **estado** de cada pedido usando el selector desplegable
4. Haz clic en ✓ para guardar el cambio

---

## 10. Cerrar Sesión

1. Haz clic en tu **nombre de usuario** en la barra de navegación
2. Selecciona **"Cerrar Sesión"**
3. Serás redirigido a la página de inicio

---

## 11. Preguntas Frecuentes

**¿Es seguro ingresar mi contraseña?**
Sí, todas las contraseñas se almacenan encriptadas con bcrypt.

**¿Se cobran cargos reales en el pago?**
No, es un simulador de pago con fines académicos.

**¿Puedo cambiar mi contraseña?**
Esta funcionalidad no está disponible en la versión actual.

**¿Qué pasa si un producto se agota?**
No podrás agregarlo al carrito si el stock es insuficiente.
