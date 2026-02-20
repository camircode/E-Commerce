-- ============================================
-- E-Commerce: Script de Base de Datos
-- ============================================

CREATE DATABASE IF NOT EXISTS ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_db;

-- --------------------------------------------
-- Tabla: usuarios
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cliente') DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- --------------------------------------------
-- Tabla: categorias
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;

-- --------------------------------------------
-- Tabla: productos
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    imagen VARCHAR(255) DEFAULT 'sin_imagen.png',
    categoria_id INT,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- --------------------------------------------
-- Tabla: pedidos
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    numero_orden VARCHAR(20) NOT NULL UNIQUE,
    total DECIMAL(10, 2) NOT NULL,
    estado ENUM('pendiente', 'pagado', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
    direccion_envio TEXT,
    telefono VARCHAR(20),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------
-- Tabla: detalle_pedido
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS detalle_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------
-- Índices
-- --------------------------------------------
CREATE INDEX idx_productos_categoria ON productos(categoria_id) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_productos_precio ON productos(precio) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_pedidos_usuario ON pedidos(usuario_id) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_detalle_pedido ON detalle_pedido(pedido_id) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- El usuario administrador se crea automáticamente al iniciar la aplicación Flask
-- con contraseña encriptada con bcrypt.


-- --------------------------------------------
-- Datos iniciales: Categorías
-- --------------------------------------------
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónica', 'Dispositivos electrónicos, gadgets y accesorios tecnológicos'),
('Ropa', 'Moda y vestimenta para todas las edades'),
('Hogar', 'Artículos para el hogar y decoración'),
('Deportes', 'Equipamiento y ropa deportiva'),
('Libros', 'Libros, revistas y material de lectura') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------
-- Datos iniciales: Productos de ejemplo
-- --------------------------------------------
INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria_id) VALUES
('Laptop Pro 15"', 'Laptop de alto rendimiento con procesador de última generación, 16GB RAM, 512GB SSD', 18999.99, 15, 'laptop.png', 1),
('Audífonos Inalámbricos', 'Audífonos bluetooth con cancelación de ruido activa y batería de 30 horas', 1299.99, 50, 'audifonos.png', 1),
('Smartphone Galaxy', 'Teléfono inteligente con pantalla AMOLED 6.5", 128GB almacenamiento', 12499.99, 25, 'smartphone.png', 1),
('Camiseta Algodón Premium', 'Camiseta 100% algodón orgánico, disponible en varios colores', 499.99, 100, 'camiseta.png', 2),
('Jeans Clásicos', 'Pantalón de mezclilla corte recto, tela resistente', 899.99, 60, 'jeans.png', 2),
('Chaqueta Deportiva', 'Chaqueta impermeable ideal para actividades al aire libre', 1599.99, 30, 'chaqueta.png', 2),
('Lámpara de Escritorio LED', 'Lámpara ajustable con 3 niveles de brillo y carga USB integrada', 699.99, 40, 'lampara.png', 3),
('Set de Sábanas', 'Juego de sábanas de microfibra suave, tamaño matrimonial', 599.99, 45, 'sabanas.png', 3),
('Balón de Fútbol Pro', 'Balón oficial tamaño 5, material sintético de alta calidad', 449.99, 35, 'balon.png', 4),
('Mancuernas Ajustables', 'Set de mancuernas ajustables de 2 a 20 kg cada una', 2499.99, 20, 'mancuernas.png', 4),
('Yoga Mat Premium', 'Tapete de yoga antideslizante de 6mm de grosor', 399.99, 55, 'yoga_mat.png', 4),
('El Arte de Programar', 'Libro esencial sobre algoritmos y estructuras de datos', 349.99, 70, 'libro_programar.png', 5),
('Novela Bestseller 2025', 'La novela más vendida del año, edición especial de pasta dura', 299.99, 80, 'novela.png', 5),
('Teclado Mecánico RGB', 'Teclado mecánico con switches Cherry MX e iluminación RGB personalizable', 1899.99, 30, 'teclado.png', 1),
('Mochila Ejecutiva', 'Mochila con compartimento acolchado para laptop de hasta 17"', 799.99, 40, 'mochila.png', 3) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
