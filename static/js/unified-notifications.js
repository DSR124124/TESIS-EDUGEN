/**
 * Sistema Unificado de Notificaciones
 * Versión 1.0.0 - Previene duplicados y maneja un solo tipo de notificación
 */

// Variables globales para el sistema de notificaciones
let activeNotifications = new Set();
let notificationQueue = [];
let isShowingNotification = false;
let currentNotificationId = null;

// Configuración del sistema
const NOTIFICATION_CONFIG = {
    maxNotifications: 1, // Solo una notificación a la vez
    defaultDuration: 5000,
    animationDuration: 300,
    container: null
};

/**
 * Inicializar el sistema de notificaciones
 */
function initNotificationSystem() {
    console.log('Inicializando sistema unificado de notificaciones...');
    
    // Crear contenedor único si no existe
    if (!NOTIFICATION_CONFIG.container) {
        // Remover contenedores existentes primero
        const existingContainers = document.querySelectorAll('.toast-container, #toastContainer, #notificationContainer');
        existingContainers.forEach(container => {
            container.remove();
        });
        
        // Crear nuevo contenedor único
        const container = document.createElement('div');
        container.id = 'unifiedNotificationContainer';
        container.className = 'unified-notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            width: 400px;
            max-width: 90vw;
            pointer-events: none;
        `;
        
        document.body.appendChild(container);
        NOTIFICATION_CONFIG.container = container;
        
        console.log('Contenedor de notificaciones unificado creado');
    }
    
    // Limpiar notificaciones existentes
    clearAllExistingNotifications();
}

/**
 * Limpiar todas las notificaciones existentes
 */
function clearAllExistingNotifications() {
    // Limpiar toasts de Bootstrap existentes
    const existingToasts = document.querySelectorAll('.toast, .notification-toast, .modern-toast');
    existingToasts.forEach(toast => {
        try {
            // Si es un toast de Bootstrap, usar la API de Bootstrap
            if (toast.classList.contains('toast')) {
                const bsToast = bootstrap.Toast.getInstance(toast);
                if (bsToast) {
                    bsToast.dispose();
                }
            }
            toast.remove();
        } catch (error) {
            console.warn('Error al limpiar notificación existente:', error);
        }
    });
    
    // Limpiar variables de estado
    activeNotifications.clear();
    notificationQueue = [];
    isShowingNotification = false;
    currentNotificationId = null;
    
    console.log('Notificaciones existentes limpiadas');
}

/**
 * Mostrar notificación unificada
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 * @param {string} title - Título de la notificación
 * @param {string} message - Mensaje de la notificación
 * @param {number} duration - Duración en milisegundos (opcional)
 */
function showUnifiedNotification(type, title, message, duration = NOTIFICATION_CONFIG.defaultDuration) {
    console.log('Solicitando notificación:', { type, title, message });
    
    // Crear ID único para evitar duplicados
    const notificationId = `${type}-${title}-${message}`.replace(/\s+/g, '-').toLowerCase();
    
    // Verificar si ya existe una notificación idéntica
    if (activeNotifications.has(notificationId)) {
        console.log('Notificación duplicada bloqueada:', notificationId);
        return;
    }
    
    // Si ya hay una notificación mostrándose, limpiarla primero
    if (isShowingNotification && currentNotificationId) {
        hideCurrentNotification();
    }
    
    // Crear la notificación
    const notification = createNotificationElement(type, title, message, notificationId);
    
    // Marcar como activa
    activeNotifications.add(notificationId);
    isShowingNotification = true;
    currentNotificationId = notificationId;
    
    // Mostrar la notificación
    displayNotification(notification, duration);
}

/**
 * Crear elemento de notificación
 */
function createNotificationElement(type, title, message, notificationId) {
    const notification = document.createElement('div');
    notification.id = notificationId;
    notification.className = `unified-notification notification-${type}`;
    notification.style.cssText = `
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        margin-bottom: 15px;
        overflow: hidden;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: auto;
        border-left: 5px solid ${getTypeColor(type)};
    `;
    
    // Obtener icono y color según el tipo
    const { icon, bgColor, textColor } = getTypeStyles(type);
    
    notification.innerHTML = `
        <div class="notification-header" style="
            background: ${bgColor};
            color: ${textColor};
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display: flex; align-items: center;">
                <i class="${icon}" style="font-size: 18px; margin-right: 8px;"></i>
                <strong style="font-size: 14px; font-weight: 600;">${title}</strong>
            </div>
            <button onclick="hideNotification('${notificationId}')" style="
                background: none;
                border: none;
                color: ${textColor};
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background-color 0.2s;
            " onmouseover="this.style.backgroundColor='rgba(255,255,255,0.2)'" onmouseout="this.style.backgroundColor='transparent'">
                ×
            </button>
        </div>
        <div class="notification-body" style="
            padding: 16px;
            color: #333;
            font-size: 14px;
            line-height: 1.5;
        ">
            ${message}
        </div>
    `;
    
    return notification;
}

/**
 * Obtener color según el tipo
 */
function getTypeColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    return colors[type] || colors.info;
}

/**
 * Obtener estilos según el tipo
 */
function getTypeStyles(type) {
    const styles = {
        success: {
            icon: 'fas fa-check-circle',
            bgColor: '#10b981',
            textColor: 'white'
        },
        error: {
            icon: 'fas fa-times-circle',
            bgColor: '#ef4444',
            textColor: 'white'
        },
        warning: {
            icon: 'fas fa-exclamation-triangle',
            bgColor: '#f59e0b',
            textColor: 'white'
        },
        info: {
            icon: 'fas fa-info-circle',
            bgColor: '#3b82f6',
            textColor: 'white'
        }
    };
    return styles[type] || styles.info;
}

/**
 * Mostrar la notificación en pantalla
 */
function displayNotification(notification, duration) {
    const container = NOTIFICATION_CONFIG.container;
    if (!container) {
        console.error('Contenedor de notificaciones no encontrado');
        return;
    }
    
    // Agregar al contenedor
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Programar auto-ocultación
    setTimeout(() => {
        hideNotification(notification.id);
    }, duration);
    
    console.log('Notificación mostrada exitosamente');
}

/**
 * Ocultar notificación específica
 */
function hideNotification(notificationId) {
    console.log('Ocultando notificación:', notificationId);
    
    const notification = document.getElementById(notificationId);
    if (!notification) return;
    
    // Animar salida
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    
    // Limpiar después de la animación
    setTimeout(() => {
        try {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            activeNotifications.delete(notificationId);
            
            if (currentNotificationId === notificationId) {
                isShowingNotification = false;
                currentNotificationId = null;
            }
            
            console.log('Notificación eliminada:', notificationId);
        } catch (error) {
            console.error('Error al eliminar notificación:', error);
        }
    }, NOTIFICATION_CONFIG.animationDuration);
}

/**
 * Ocultar notificación actual
 */
function hideCurrentNotification() {
    if (currentNotificationId) {
        hideNotification(currentNotificationId);
    }
}

/**
 * Limpiar todas las notificaciones
 */
function clearAllNotifications() {
    console.log('Limpiando todas las notificaciones');
    
    activeNotifications.forEach(id => {
        hideNotification(id);
    });
    
    // Resetear estado
    setTimeout(() => {
        activeNotifications.clear();
        notificationQueue = [];
        isShowingNotification = false;
        currentNotificationId = null;
    }, NOTIFICATION_CONFIG.animationDuration);
}

// ============ FUNCIONES DE CONVENIENCIA ============

/**
 * Mostrar notificación de éxito
 */
function showSuccess(title, message, duration) {
    showUnifiedNotification('success', title, message, duration);
}

/**
 * Mostrar notificación de error
 */
function showError(title, message, duration) {
    showUnifiedNotification('error', title, message, duration);
}

/**
 * Mostrar notificación de advertencia
 */
function showWarning(title, message, duration) {
    showUnifiedNotification('warning', title, message, duration);
}

/**
 * Mostrar notificación de información
 */
function showInfo(title, message, duration) {
    showUnifiedNotification('info', title, message, duration);
}

// ============ COMPATIBILIDAD CON SISTEMAS EXISTENTES ============

/**
 * Función de compatibilidad para showNotification existente
 */
function showNotification(type, title, message, duration) {
    showUnifiedNotification(type, title, message, duration);
}

/**
 * Función de compatibilidad para sistemas de portfolio
 */
function showToast(message, type = 'success', duration) {
    const titles = {
        success: 'Éxito',
        error: 'Error',
        warning: 'Advertencia',
        info: 'Información'
    };
    showUnifiedNotification(type, titles[type] || 'Notificación', message, duration);
}

// ============ INICIALIZACIÓN ============

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotificationSystem);
} else {
    initNotificationSystem();
}

// Exponer funciones globalmente
window.showUnifiedNotification = showUnifiedNotification;
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.showInfo = showInfo;
window.showNotification = showNotification;
window.showToast = showToast;
window.clearAllNotifications = clearAllNotifications;
window.hideNotification = hideNotification;

console.log('Sistema unificado de notificaciones cargado exitosamente'); 