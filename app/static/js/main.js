/* ============================================
   TiendaOnline - JavaScript Principal
   ============================================ */

/**
 * Agrega un producto al carrito usando AJAX (Fetch API)
 * @param {number} productoId - ID del producto
 * @param {number} cantidad - Cantidad a agregar (por defecto 1)
 */
function agregarAlCarrito(productoId, cantidad = 1) {
    fetch('/api/carrito/agregar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            producto_id: productoId,
            cantidad: cantidad
        })
    })
        .then(respuesta => respuesta.json())
        .then(datos => {
            if (datos.exito) {
                // Actualizar badge del carrito
                actualizarBadge(datos.total_articulos);
                // Mostrar notificación
                mostrarToast(datos.mensaje, 'exito');
            } else {
                mostrarToast(datos.mensaje, 'error');
            }
        })
        .catch(error => {
            console.error('Error al agregar al carrito:', error);
            mostrarToast('Error de conexión. Inténtalo de nuevo.', 'error');
        });
}

/**
 * Actualiza el badge del carrito en la barra de navegación
 * @param {number} cantidad - Total de artículos en el carrito
 */
function actualizarBadge(cantidad) {
    const badge = document.getElementById('badgeCarrito');
    if (badge) {
        badge.textContent = cantidad;
        if (cantidad > 0) {
            badge.style.display = 'inline-block';
            // Animación de pulso
            badge.style.animation = 'none';
            badge.offsetHeight; // Forzar reflow
            badge.style.animation = 'pulsoBadge 0.3s ease';
        } else {
            badge.style.display = 'none';
        }
    }
}

/**
 * Muestra una notificación tipo toast
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo: 'exito', 'error', 'info'
 */
function mostrarToast(mensaje, tipo = 'info') {
    // Eliminar toast anterior si existe
    const toastAnterior = document.querySelector('.toast-carrito');
    if (toastAnterior) {
        toastAnterior.remove();
    }

    // Crear elemento toast
    const toast = document.createElement('div');
    toast.className = 'toast-carrito';

    let icono = 'bi-info-circle';
    let colorBorde = 'rgba(108, 92, 231, 0.3)';

    if (tipo === 'exito') {
        icono = 'bi-check-circle-fill';
        colorBorde = 'rgba(0, 184, 148, 0.3)';
    } else if (tipo === 'error') {
        icono = 'bi-exclamation-circle-fill';
        colorBorde = 'rgba(225, 112, 85, 0.3)';
    }

    toast.style.borderColor = colorBorde;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.8rem;">
            <i class="bi ${icono}" style="font-size: 1.3rem; color: ${tipo === 'exito' ? '#00b894' : tipo === 'error' ? '#e17055' : '#6c5ce7'};"></i>
            <span>${mensaje}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: var(--color-texto-claro); cursor: pointer; margin-left: 0.5rem;">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>
    `;

    document.body.appendChild(toast);
    toast.style.display = 'block';

    // Auto ocultar después de 3 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Animación CSS para el badge (inyectada dinámicamente)
const estiloAnimacion = document.createElement('style');
estiloAnimacion.textContent = `
    @keyframes pulsoBadge {
        0% { transform: translate(25%, -25%) scale(1); }
        50% { transform: translate(25%, -25%) scale(1.4); }
        100% { transform: translate(25%, -25%) scale(1); }
    }
`;
document.head.appendChild(estiloAnimacion);

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    // Ocultar badge si es 0
    const badge = document.getElementById('badgeCarrito');
    if (badge && parseInt(badge.textContent) === 0) {
        badge.style.display = 'none';
    }

    // Auto-cerrar alertas después de 5 segundos
    const alertas = document.querySelectorAll('.alert-dismissible');
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            const botonCerrar = alerta.querySelector('.btn-close');
            if (botonCerrar) botonCerrar.click();
        }, 5000);
    });
});
