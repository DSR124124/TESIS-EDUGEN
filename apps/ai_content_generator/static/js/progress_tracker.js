// Check if file exists and create it if not
const progressTracker = {
    requestId: null,
    progressUrl: null,
    updateInterval: 3000,  // 3 segundos entre actualizaciones
    retryCount: 0,
    maxRetries: 40,     // Máximo de reintentos (40 * 3 segundos = hasta ~2 minutos)
    statusElement: null,
    progressElement: null,
    timer: null,
    isCompleted: false,
    lastProgress: -1,
    completedCallback: null,
    consecutiveErrors: 0,
    maxConsecutiveErrors: 5,
    // NUEVO: Progreso simulado más realista
    simulatedProgress: 0,
    simulatedMax: 85, // No pasar de 85% hasta que el backend confirme (más conservador)
    simulatedDuration: 240, // 4 minutos en segundos (más realista)
    simulatedStartTime: null,
    backendProgress: 0,
    hasBackendControl: false,
    
    init: function(requestId, progressUrl, statusSelector, progressSelector, completedCallback) {
        this.requestId = requestId;
        this.progressUrl = progressUrl;
        this.statusElement = document.querySelector(statusSelector);
        this.progressElement = document.querySelector(progressSelector);
        this.completedCallback = completedCallback || function() { 
            window.location.reload();
        };
        this.updateInterval = 2000; // Verificar más frecuentemente
        this.simulatedProgress = 0;
        this.simulatedStartTime = Date.now();
        this.backendProgress = 0;
        this.hasBackendControl = false;
        this.startSimulatedProgress();
        this.startTracking();
    },
    
    startTracking: function() {
        // Hacer una primera solicitud inmediatamente
        this.checkProgress();
        
        // Configurar intervalo para actualizar regularmente
        this.timer = setInterval(() => {
            this.checkProgress();
        }, this.updateInterval);
    },
    
    stopTracking: function() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        if (this.simTimer) {
            clearInterval(this.simTimer);
            this.simTimer = null;
        }
    },
    
    checkProgress: function() {
        if (this.isCompleted) {
            this.stopTracking();
            return;
        }
        
        fetch(this.progressUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                this.updateProgress(data);
                
                // Ajustar intervalo basado en el estado
                if (data.status === 'processing') {
                    // Mantener intervalo corto mientras procesa
                    this.updateInterval = 2000; // 2 segundos
                    this.retryCount = 0; // Reiniciar contador si hay actividad
                } else if (data.status === 'pending') {
                    // Aumentar intervalo si está pendiente
                    this.updateInterval = 3000; // 3 segundos
                    this.retryCount = 0; // Reiniciar contador si hay actividad
                }
                
                // Actualizar el temporizador con el nuevo intervalo
                this.resetTimer();
            })
            .catch(error => {
                console.error('Error obteniendo progreso:', error);
                this.handleError(error);
            });
    },
    
    resetTimer: function() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = setInterval(() => {
                this.checkProgress();
            }, this.updateInterval);
        }
    },
    
    handleError: function(error) {
        this.consecutiveErrors++;
        this.retryCount++;
        
        console.warn(`Error de progreso #${this.consecutiveErrors}: ${error.message}`);
        
        if (this.consecutiveErrors >= this.maxConsecutiveErrors) {
            this.showErrorMessage('Error de conexión', 'No se puede obtener el estado de la generación. Verifica tu conexión.');
            this.stopTracking();
            return;
        }
        
        if (this.retryCount >= this.maxRetries) {
            this.showErrorMessage('Tiempo agotado', 'La generación está tardando más de lo esperado.');
            this.stopTracking();
            return;
        }
        
        // Aumentar el intervalo después de errores
        this.updateInterval = Math.min(this.updateInterval * 1.5, 10000);
    },
    
    showErrorMessage: function(title, message) {
        console.error(`${title}: ${message}`);
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-warning mt-3">
                    <strong>${title}:</strong> ${message}
                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="progressTracker.manualRetry()">
                        Reintentar
                    </button>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    },
    
    manualRetry: function() {
        // Función para reintentar manualmente
        this.consecutiveErrors = 0;
        this.retryCount = 0;
        this.updateInterval = 2000; // Reset a intervalo corto
        
        // Limpiar mensaje de error
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
        
        // Realizar un intento inmediato
        this.checkProgress();
    },
    
    startSimulatedProgress: function() {
        // Progreso simulado más conservador y realista
        if (this.simTimer) clearInterval(this.simTimer);
        this.simTimer = setInterval(() => {
            if (this.isCompleted || this.hasBackendControl) {
                clearInterval(this.simTimer);
                return;
            }
            
            const elapsed = (Date.now() - this.simulatedStartTime) / 1000;
            
            // Curva de progreso más realista:
            // - Primeros 30 segundos: 0-20% (rápido al inicio)
            // - Siguientes 60 segundos: 20-40% (medio)
            // - Siguientes 90 segundos: 40-70% (proceso principal)
            // - Últimos 60 segundos: 70-85% (finalización, más lento)
            
            let percent = 0;
            if (elapsed <= 30) {
                // Primeros 30 segundos: 0-20%
                percent = (elapsed / 30) * 20;
            } else if (elapsed <= 90) {
                // Segundos 30-90: 20-40%
                percent = 20 + ((elapsed - 30) / 60) * 20;
            } else if (elapsed <= 180) {
                // Segundos 90-180: 40-70%
                percent = 40 + ((elapsed - 90) / 90) * 30;
            } else {
                // Después de 180 segundos: 70-85% (más lento)
                percent = 70 + ((elapsed - 180) / 60) * 15;
            }
            
            percent = Math.min(this.simulatedMax, percent);
            
            // Solo actualizar si el progreso aumenta y el backend no tiene control
            if (percent > this.simulatedProgress && !this.hasBackendControl) {
                this.simulatedProgress = percent;
                if (this.progressElement) {
                    this.progressElement.style.width = percent + '%';
                    this.progressElement.setAttribute('aria-valuenow', percent);
                    
                    // Actualizar también el elemento de porcentaje si existe
                    const progressPercentage = document.getElementById('progress-percentage');
                    if (progressPercentage) {
                        progressPercentage.textContent = Math.round(percent) + '%';
                    }
                }
                this.lastProgress = percent;
            }
        }, 1000);
    },
    
    updateProgress: function(data) {
        // Solo actualizar UI para estados importantes
        const isImportantUpdate = data.status === 'completed' || data.status === 'failed' || 
                                 data.progress === 100 || data.progress === 0 ||
                                 data.status === 'cancelled';
        if (this.statusElement && isImportantUpdate) {
            this.updateStatus(data.message || data.status);
        }
        
        if (this.progressElement) {
            // Si el backend reporta progreso válido
            const newProgress = data.progress || 0;
            
            // Si el backend reporta progreso significativo, tomar control
            if (newProgress >= 10 && newProgress > this.simulatedProgress) {
                this.hasBackendControl = true;
                this.backendProgress = newProgress;
                
                // Detener progreso simulado
                if (this.simTimer) {
                    clearInterval(this.simTimer);
                    this.simTimer = null;
                }
                
                // Actualizar progreso
                this.lastProgress = newProgress;
                this.progressElement.style.width = newProgress + '%';
                this.progressElement.setAttribute('aria-valuenow', newProgress);
                
                // Actualizar también el elemento de porcentaje
                const progressPercentage = document.getElementById('progress-percentage');
                if (progressPercentage) {
                    progressPercentage.textContent = Math.round(newProgress) + '%';
                }
                
                // Si el backend llega a 100%, marcar como completado
                if (newProgress >= 100) {
                    this.isCompleted = true;
                    if (this.simTimer) clearInterval(this.simTimer);
                }
            } else if (this.hasBackendControl && newProgress > this.backendProgress) {
                // Solo actualizar si el backend ya tiene control y el progreso aumentó
                this.backendProgress = newProgress;
                this.lastProgress = newProgress;
                this.progressElement.style.width = newProgress + '%';
                this.progressElement.setAttribute('aria-valuenow', newProgress);
                
                const progressPercentage = document.getElementById('progress-percentage');
                if (progressPercentage) {
                    progressPercentage.textContent = Math.round(newProgress) + '%';
                }
                
                if (newProgress >= 100) {
                    this.isCompleted = true;
                    if (this.simTimer) clearInterval(this.simTimer);
                }
            }
        }
        
        // Verificar si debe detener el seguimiento
        if (data.status === 'completed') {
            this.handleCompletion();
        } else if (data.status === 'failed') {
            this.handleFailure(data.error || 'Error desconocido');
        } else if (data.status === 'cancelled') {
            this.handleFailure('La generación fue cancelada');
        }
    },
    
    updateStatus: function(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    },
    
    handleCompletion: function() {
        this.isCompleted = true;
        this.stopTracking();
        
        // Asegurar que el progreso esté al 100%
        if (this.progressElement) {
            this.progressElement.style.width = '100%';
            this.progressElement.setAttribute('aria-valuenow', 100);
            
            const progressPercentage = document.getElementById('progress-percentage');
            if (progressPercentage) {
                progressPercentage.textContent = '100%';
            }
        }
        
        // Ejecutar callback de completado después de una breve pausa
        setTimeout(() => {
            if (this.completedCallback) {
                this.completedCallback();
            }
        }, 1000);
    },
    
    handleFailure: function(error) {
        this.isCompleted = true;
        this.stopTracking();
        
        this.showErrorMessage('Error en la generación', error);
        
        // Opcional: ejecutar callback de fallo si existe
        if (this.failureCallback) {
            this.failureCallback(error);
        }
    }
}; 