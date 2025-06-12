// Check if file exists and create it if not
const progressTracker = {
    requestId: null,
    progressUrl: null,
    updateInterval: 3000,  // 3 segundos entre actualizaciones
    retryCount: 0,
    maxRetries: 30,     // Máximo de reintentos (30 * 3 segundos = hasta ~1.5 minutos)
    statusElement: null,
    progressElement: null,
    timer: null,
    isCompleted: false,
    lastProgress: -1,
    completedCallback: null,
    consecutiveErrors: 0,
    maxConsecutiveErrors: 5,
    // NUEVO: Progreso simulado para tiempos largos
    simulatedProgress: 0,
    simulatedMax: 95, // No pasar de 95% hasta que el backend confirme
    simulatedDuration: 300, // 5 minutos en segundos
    simulatedStartTime: null,
    
    init: function(requestId, progressUrl, statusSelector, progressSelector, completedCallback) {
        this.requestId = requestId;
        this.progressUrl = progressUrl;
        this.statusElement = document.querySelector(statusSelector);
        this.progressElement = document.querySelector(progressSelector);
        this.completedCallback = completedCallback || function() { 
            window.location.reload();
        };
        this.updateInterval = 2000;
        this.simulatedProgress = 0;
        this.simulatedStartTime = Date.now();
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
    },
    
    checkProgress: function() {
        if (this.isCompleted) {
            this.stopTracking();
            return;
        }
        
        const url = this.progressUrl.replace('REQUEST_ID', this.requestId);
        
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
            .then(response => {
                if (!response.ok) {
                    // Reset de errores consecutivos si hay respuesta (aunque sea error)
                    this.consecutiveErrors = 0;
                    
                    if (response.status === 403) {
                        throw new Error('No tienes permiso para acceder a esta solicitud');
                    } else if (response.status === 404) {
                        throw new Error('Solicitud no encontrada');
                    } else {
                        throw new Error('Error al obtener progreso: ' + response.status);
                    }
                }
                // Reset de errores consecutivos si hay respuesta ok
                this.consecutiveErrors = 0;
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
                this.retryCount++;
                this.consecutiveErrors++;
                
                // Aumentar intervalo para evitar sobrecarga
                this.updateInterval = Math.min(10000, this.updateInterval * 1.5);
                
                // Mostrar error en UI después de varios errores consecutivos
                if (this.consecutiveErrors >= this.maxConsecutiveErrors) {
                    this.updateStatus('Error de conexión: ' + error.message);
                    // Agregar botón para reintentar manualmente
                    const errorContainer = document.getElementById('error-container');
                    if (errorContainer) {
                        errorContainer.innerHTML = `
                            <div class="alert alert-warning">
                                <strong>Error de conexión:</strong> ${error.message}
                                <button class="btn btn-sm btn-outline-primary mt-2" onclick="progressTracker.manualRetry()">Reintentar ahora</button>
                            </div>
                        `;
                        errorContainer.style.display = 'block';
                    }
                }
                
                // Detener después de demasiados reintentos
                if (this.retryCount >= this.maxRetries) {
                    this.stopTracking();
                    this.handleFailure('Se agotó el tiempo de espera. Por favor, intente nuevamente.');
                } else {
                    // Actualizar el temporizador con el nuevo intervalo
                    this.resetTimer();
                }
            });
    },
    
    resetTimer: function() {
        // Reiniciar el temporizador con el nuevo intervalo
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = setInterval(() => {
                this.checkProgress();
            }, this.updateInterval);
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
        // Avanza el progreso simulado cada segundo
        if (this.simTimer) clearInterval(this.simTimer);
        this.simTimer = setInterval(() => {
            if (this.isCompleted) {
                clearInterval(this.simTimer);
                return;
            }
            const elapsed = (Date.now() - this.simulatedStartTime) / 1000;
            let percent = Math.min(this.simulatedMax, (elapsed / this.simulatedDuration) * this.simulatedMax);
            if (percent > this.simulatedProgress) {
                this.simulatedProgress = percent;
                if (this.progressElement && (!this.lastProgress || this.lastProgress < percent)) {
                    this.progressElement.style.width = percent + '%';
                    this.progressElement.setAttribute('aria-valuenow', percent);
                }
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
            // Si el backend reporta progreso, usarlo, pero nunca retroceder
            const newProgress = data.progress || 0;
            if (newProgress > this.lastProgress) {
                this.lastProgress = newProgress;
                this.progressElement.style.width = newProgress + '%';
                this.progressElement.setAttribute('aria-valuenow', newProgress);
                // Si el backend llega a 100%, marcar como completado
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
    
    updateProgressBar: function(progress) {
        if (this.progressElement) {
            const width = Math.max(5, Math.min(100, progress)); // Mínimo 5%, máximo 100%
            this.progressElement.style.width = width + '%';
            this.progressElement.setAttribute('aria-valuenow', width);
            
            // Usar colores para indicar progreso
            if (width < 20) {
                this.progressElement.classList.remove('bg-info', 'bg-warning', 'bg-success');
                this.progressElement.classList.add('bg-secondary');
            } else if (width < 50) {
                this.progressElement.classList.remove('bg-secondary', 'bg-warning', 'bg-success');
                this.progressElement.classList.add('bg-info');
            } else if (width < 100) {
                this.progressElement.classList.remove('bg-secondary', 'bg-info', 'bg-success');
                this.progressElement.classList.add('bg-warning');
            } else {
                this.progressElement.classList.remove('bg-secondary', 'bg-info', 'bg-warning');
                this.progressElement.classList.add('bg-success');
            }
        }
    },
    
    handleCompletion: function() {
        this.isCompleted = true;
        this.updateProgressBar(100);
        this.updateStatus('¡Completado con éxito!');
        this.stopTracking();
        
        // Dar tiempo para mostrar el mensaje de éxito antes de recargar
        setTimeout(() => {
            if (typeof this.completedCallback === 'function') {
                this.completedCallback();
            }
        }, 1000);
    },
    
    handleFailure: function(errorMessage) {
        this.isCompleted = true;
        this.updateProgressBar(100);
        this.progressElement.classList.remove('bg-info', 'bg-warning', 'bg-success');
        this.progressElement.classList.add('bg-danger');
        this.updateStatus('Error: ' + errorMessage);
        this.stopTracking();
        
        // Mostrar algún mensaje de error o UI para reintentar
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error en la generación:</strong> ${errorMessage}
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-danger me-2" onclick="window.location.reload()">Reintentar</button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="window.location.href='/ai/requests/'">Volver a la lista</button>
                    </div>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    }
}; 