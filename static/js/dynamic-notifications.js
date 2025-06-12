/**
 * Sistema Dinámico de Notificaciones Flotantes
 * Complementa las notificaciones estáticas de Django con notificaciones en tiempo real
 */

(function() {
    'use strict';
    
    // Configuración del sistema
    const NOTIFICATION_CONFIG = {
        container: '#notification-container',
        duration: {
            success: 4000,
            info: 5000,
            warning: 6000,
            error: 8000
        },
        maxNotifications: 5,
        animation: {
            enter: 'slideInRight',
            exit: 'slideOutRight'
        },
        position: {
            top: '80px',
            right: '20px'
        }
    };
    
    // Estado de las notificaciones
    let notificationQueue = [];
    let activeNotifications = [];
    let notificationCounter = 0;
    
    /**
     * Crear elemento de notificación
     */
    function createNotificationElement(type, title, message, duration) {
        const id = `notification-${++notificationCounter}`;
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const colorMap = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = 'dynamic-notification';
        notification.setAttribute('data-type', type);
        notification.setAttribute('data-duration', duration);
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <div class="notification-icon">
                        <i class="${iconMap[type]}" style="color: ${colorMap[type]}"></i>
                    </div>
                    <div class="notification-title">${title}</div>
                    <button class="notification-close" onclick="DynamicNotifications.close('${id}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="notification-message">${message}</div>
                <div class="notification-progress">
                    <div class="progress-bar" style="background-color: ${colorMap[type]}"></div>
                </div>
            </div>
        `;
        
        return notification;
    }
    
    /**
     * Aplicar estilos CSS dinámicamente
     */
    function applyStyles() {
        if (document.getElementById('dynamic-notifications-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'dynamic-notifications-styles';
        styles.textContent = `
            .dynamic-notification {
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                margin-bottom: 12px;
                min-width: 320px;
                max-width: 400px;
                overflow: hidden;
                position: relative;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
                border: 1px solid rgba(0, 0, 0, 0.05);
                backdrop-filter: blur(10px);
                pointer-events: auto;
            }
            
            .dynamic-notification.show {
                transform: translateX(0);
                opacity: 1;
            }
            
            .dynamic-notification.hide {
                transform: translateX(100%);
                opacity: 0;
                margin-bottom: 0;
                max-height: 0;
                padding: 0;
            }
            
            .notification-content {
                padding: 16px;
                position: relative;
            }
            
            .notification-header {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .notification-icon {
                font-size: 1.2rem;
                margin-right: 12px;
                flex-shrink: 0;
            }
            
            .notification-title {
                font-weight: 600;
                font-size: 0.95rem;
                color: #2c3e50;
                flex: 1;
                line-height: 1.3;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: #95a5a6;
                cursor: pointer;
                padding: 4px;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
                flex-shrink: 0;
            }
            
            .notification-close:hover {
                background: rgba(0, 0, 0, 0.05);
                color: #2c3e50;
            }
            
            .notification-message {
                color: #5a6c7d;
                font-size: 0.9rem;
                line-height: 1.4;
                margin-bottom: 12px;
                word-wrap: break-word;
            }
            
            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: rgba(0, 0, 0, 0.05);
            }
            
            .progress-bar {
                height: 100%;
                width: 100%;
                transform-origin: left;
                transition: transform linear;
            }
            
            /* Tipos específicos */
            .dynamic-notification[data-type="success"] {
                border-left: 4px solid #28a745;
                background: linear-gradient(135deg, #ffffff, #f8fff9);
            }
            
            .dynamic-notification[data-type="error"] {
                border-left: 4px solid #dc3545;
                background: linear-gradient(135deg, #ffffff, #fff8f8);
            }
            
            .dynamic-notification[data-type="warning"] {
                border-left: 4px solid #ffc107;
                background: linear-gradient(135deg, #ffffff, #fffef8);
            }
            
            .dynamic-notification[data-type="info"] {
                border-left: 4px solid #17a2b8;
                background: linear-gradient(135deg, #ffffff, #f8fcfd);
            }
            
            /* Efectos hover */
            .dynamic-notification:hover {
                transform: translateX(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            }
            
            .dynamic-notification:hover .progress-bar {
                animation-play-state: paused;
            }
            
            /* Animaciones */
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .dynamic-notification {
                    min-width: 280px;
                    max-width: calc(100vw - 40px);
                }
            }
            
            @media (max-width: 480px) {
                .dynamic-notification {
                    min-width: auto;
                    margin-bottom: 8px;
                }
                
                .notification-content {
                    padding: 12px;
                }
                
                .notification-title {
                    font-size: 0.9rem;
                }
                
                .notification-message {
                    font-size: 0.85rem;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Mostrar notificación
     */
    function showNotification(type, title, message, duration = null) {
        // Usar duración por defecto si no se especifica
        if (!duration) {
            duration = NOTIFICATION_CONFIG.duration[type] || NOTIFICATION_CONFIG.duration.info;
        }
        
        const container = document.querySelector(NOTIFICATION_CONFIG.container);
        if (!container) {
            console.warn('Contenedor de notificaciones no encontrado');
            return;
        }
        
        // Limitar número de notificaciones activas
        if (activeNotifications.length >= NOTIFICATION_CONFIG.maxNotifications) {
            // Remover la más antigua
            closeNotification(activeNotifications[0].id);
        }
        
        // Crear elemento de notificación
        const notification = createNotificationElement(type, title, message, duration);
        const notificationData = {
            id: notification.id,
            element: notification,
            timeout: null,
            duration: duration
        };
        
        // Agregar al contenedor
        container.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => {
            notification.classList.add('show');
        }, 50);
        
        // Configurar progreso visual
        const progressBar = notification.querySelector('.progress-bar');
        if (progressBar && duration > 0) {
            progressBar.style.transition = `transform ${duration}ms linear`;
            setTimeout(() => {
                progressBar.style.transform = 'scaleX(0)';
            }, 100);
        }
        
        // Auto-cerrar después de la duración especificada
        if (duration > 0) {
            notificationData.timeout = setTimeout(() => {
                closeNotification(notification.id);
            }, duration);
        }
        
        // Agregar a la lista de notificaciones activas
        activeNotifications.push(notificationData);
        
        console.log(`📢 Notificación ${type}: ${title} - ${message}`);
        return notification.id;
    }
    
    /**
     * Cerrar notificación específica
     */
    function closeNotification(notificationId) {
        const index = activeNotifications.findIndex(n => n.id === notificationId);
        if (index === -1) return;
        
        const notificationData = activeNotifications[index];
        const element = notificationData.element;
        
        // Cancelar timeout si existe
        if (notificationData.timeout) {
            clearTimeout(notificationData.timeout);
        }
        
        // Aplicar animación de salida
        element.classList.remove('show');
        element.classList.add('hide');
        
        // Remover del DOM después de la animación
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 400);
        
        // Remover de la lista de activas
        activeNotifications.splice(index, 1);
    }
    
    /**
     * Cerrar todas las notificaciones
     */
    function closeAll() {
        const ids = activeNotifications.map(n => n.id);
        ids.forEach(id => closeNotification(id));
    }
    
    /**
     * Métodos de conveniencia para diferentes tipos
     */
    const Methods = {
        success: (title, message, duration) => showNotification('success', title, message, duration),
        error: (title, message, duration) => showNotification('error', title, message, duration),
        warning: (title, message, duration) => showNotification('warning', title, message, duration),
        info: (title, message, duration) => showNotification('info', title, message, duration),
        close: closeNotification,
        closeAll: closeAll,
        show: showNotification
    };
    
    /**
     * API Pública
     */
    window.DynamicNotifications = Methods;
    
    /**
     * Alias globales para facilidad de uso
     */
    window.notify = Methods;
    window.showSuccess = Methods.success;
    window.showError = Methods.error;
    window.showWarning = Methods.warning;
    window.showInfo = Methods.info;
    
    /**
     * Integración con eventos del sistema
     */
    function setupSystemIntegration() {
        // Escuchar eventos personalizados
        document.addEventListener('system:notification', (event) => {
            const { type, title, message, duration } = event.detail;
            showNotification(type, title, message, duration);
        });
        
        // Integración con fetch para errores de red
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args)
                .catch(error => {
                    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                        showNotification('error', 'Error de Conexión', 'No se pudo conectar con el servidor. Verifique su conexión a internet.');
                    }
                    throw error;
                });
        };
        
        // Manejar errores de JavaScript no capturados
        window.addEventListener('error', (event) => {
            // Solo mostrar errores que no sean de extensiones
            if (!event.filename.includes('extension') && 
                !event.message.includes('Script error') &&
                !event.message.includes('ResizeObserver')) {
                showNotification('error', 'Error Inesperado', 'Se ha producido un error en la aplicación. Por favor, recargue la página.');
            }
        });
    }
    
    /**
     * Inicialización
     */
    function init() {
        // Aplicar estilos
        applyStyles();
        
        // Configurar integración con el sistema
        setupSystemIntegration();
        
        // Verificar si existe el contenedor de notificaciones
        let container = document.querySelector(NOTIFICATION_CONFIG.container);
        if (!container) {
            // Crear contenedor si no existe
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed';
            container.style.cssText = `
                top: ${NOTIFICATION_CONFIG.position.top};
                right: ${NOTIFICATION_CONFIG.position.right};
                z-index: 10050;
                max-width: 400px;
                pointer-events: auto;
            `;
            
            document.body.appendChild(container);
        }
        
        console.log('🔔 Sistema de Notificaciones Dinámicas inicializado');
    }
    
    /**
     * Auto-inicialización cuando el DOM esté listo
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})(); 