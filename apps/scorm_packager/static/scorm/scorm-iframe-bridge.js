/**
 * SCORM Iframe Bridge
 * Mejora la comunicación entre el contenido SCORM en iframe y la página principal
 */

(function() {
    'use strict';
    
    // Solo ejecutar si estamos dentro de un iframe
    if (window.self === window.top) return;
    
    // Variables para el seguimiento
    let progressData = {
        completion: 0,
        timeSpent: 0,
        score: 0,
        status: 'not attempted'
    };
    
    let startTime = Date.now();
    let lastActivity = Date.now();
    
    // Función para enviar datos al padre
    function sendToParent(type, data) {
        try {
            parent.postMessage({
                type: 'scorm-' + type,
                data: data
            }, '*');
        } catch (e) {
            console.log('No se pudo enviar mensaje al padre:', e);
        }
    }
    
    // Detectar cuando el contenido está listo
    function onContentReady() {
        sendToParent('ready', {
            title: document.title,
            url: window.location.href
        });
        
        // Comenzar seguimiento de actividad
        startActivityTracking();
        
        // Intentar detectar API SCORM si existe
        detectSCORMAPI();
    }
    
    // Seguimiento de actividad del usuario
    function startActivityTracking() {
        // Actualizar tiempo cada segundo
        setInterval(function() {
            progressData.timeSpent = Math.floor((Date.now() - startTime) / 1000);
            
            // Enviar actualización cada 30 segundos si hay actividad reciente
            if (Date.now() - lastActivity < 60000) {
                sendToParent('progress', progressData);
            }
        }, 30000);
        
        // Detectar actividad del usuario
        ['click', 'keydown', 'scroll', 'touchstart'].forEach(function(event) {
            document.addEventListener(event, function() {
                lastActivity = Date.now();
                
                // Actualizar progreso basado en actividad
                updateProgressByActivity();
            }, true);
        });
        
        // Detectar cambios en formularios
        document.addEventListener('change', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                lastActivity = Date.now();
                updateProgressByActivity();
            }
        });
    }
    
    // Actualizar progreso basado en actividad
    function updateProgressByActivity() {
        // Algoritmo simple para estimar progreso
        let timeProgress = Math.min(progressData.timeSpent / 300, 0.5); // 50% máximo por tiempo (5 min)
        
        // Detectar elementos de contenido completados
        let contentProgress = detectContentProgress();
        
        // Combinar ambos tipos de progreso
        progressData.completion = Math.min(Math.round((timeProgress + contentProgress) * 100), 100);
        
        // Actualizar estado
        if (progressData.completion > 0) {
            progressData.status = 'incomplete';
        }
        if (progressData.completion >= 80) {
            progressData.status = 'completed';
        }
        
        // Enviar actualización
        sendToParent('progress', progressData);
    }
    
    // Detectar progreso del contenido
    function detectContentProgress() {
        let progress = 0;
        
        try {
            // Buscar indicadores comunes de progreso
            let totalElements = 0;
            let completedElements = 0;
            
            // Formularios completados
            let forms = document.querySelectorAll('form');
            forms.forEach(function(form) {
                let inputs = form.querySelectorAll('input, select, textarea');
                if (inputs.length > 0) {
                    totalElements++;
                    let filledInputs = Array.from(inputs).filter(function(input) {
                        return input.value && input.value.trim() !== '';
                    });
                    if (filledInputs.length > inputs.length * 0.7) {
                        completedElements++;
                    }
                }
            });
            
            // Videos vistos
            let videos = document.querySelectorAll('video');
            videos.forEach(function(video) {
                totalElements++;
                if (video.currentTime > video.duration * 0.8) {
                    completedElements++;
                }
            });
            
            // Páginas visitadas (si hay navegación)
            let navLinks = document.querySelectorAll('a[href], .nav-link, .page-link');
            let visitedPages = localStorage.getItem('visitedPages');
            if (visitedPages) {
                try {
                    visitedPages = JSON.parse(visitedPages);
                    totalElements += navLinks.length;
                    completedElements += visitedPages.length;
                } catch (e) {}
            }
            
            // Calcular progreso
            if (totalElements > 0) {
                progress = completedElements / totalElements;
            }
            
        } catch (e) {
            console.log('Error detectando progreso:', e);
        }
        
        return Math.max(progress, 0.1); // Mínimo 10% por estar activo
    }
    
    // Detectar API SCORM nativa si existe
    function detectSCORMAPI() {
        // Buscar API SCORM en diferentes niveles
        let api = null;
        
        // SCORM 2004
        if (window.API_1484_11) {
            api = window.API_1484_11;
        }
        // SCORM 1.2
        else if (window.API) {
            api = window.API;
        }
        // Buscar en el padre
        else if (parent && parent.API_1484_11) {
            api = parent.API_1484_11;
        }
        else if (parent && parent.API) {
            api = parent.API;
        }
        
        if (api) {
            console.log('API SCORM detectada');
            
            // Interceptar llamadas SCORM para obtener datos
            interceptSCORMCalls(api);
        } else {
            console.log('No se detectó API SCORM, usando seguimiento manual');
        }
    }
    
    // Interceptar llamadas SCORM
    function interceptSCORMCalls(api) {
        // Guardar métodos originales
        let originalSetValue = api.SetValue || api.LMSSetValue;
        let originalGetValue = api.GetValue || api.LMSGetValue;
        
        // Interceptar SetValue
        if (originalSetValue) {
            api.SetValue = api.LMSSetValue = function(element, value) {
                // Actualizar nuestro progreso basado en valores SCORM
                updateFromSCORM(element, value);
                return originalSetValue.call(api, element, value);
            };
        }
        
        // Interceptar GetValue para logging
        if (originalGetValue) {
            api.GetValue = api.LMSGetValue = function(element) {
                let value = originalGetValue.call(api, element);
                console.log('SCORM Get:', element, '=', value);
                return value;
            };
        }
    }
    
    // Actualizar progreso desde datos SCORM
    function updateFromSCORM(element, value) {
        console.log('SCORM Set:', element, '=', value);
        
        switch (element) {
            case 'cmi.completion_status':
            case 'cmi.core.lesson_status':
                progressData.status = value;
                if (value === 'completed' || value === 'passed') {
                    progressData.completion = 100;
                }
                break;
                
            case 'cmi.progress_measure':
                progressData.completion = Math.round(parseFloat(value) * 100);
                break;
                
            case 'cmi.score.scaled':
            case 'cmi.core.score.raw':
                progressData.score = parseFloat(value);
                break;
                
            case 'cmi.session_time':
            case 'cmi.core.session_time':
                // Convertir tiempo SCORM a segundos
                progressData.timeSpent = parseSCORMTime(value);
                break;
        }
        
        // Enviar actualización
        sendToParent('progress', progressData);
    }
    
    // Parsear tiempo en formato SCORM
    function parseSCORMTime(timeStr) {
        try {
            // Formato: PT[##H][##M][##S] o ##:##:##
            if (timeStr.includes(':')) {
                let parts = timeStr.split(':');
                return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
            } else if (timeStr.startsWith('PT')) {
                let hours = timeStr.match(/(\d+)H/);
                let minutes = timeStr.match(/(\d+)M/);
                let seconds = timeStr.match(/(\d+)S/);
                
                return (hours ? parseInt(hours[1]) * 3600 : 0) +
                       (minutes ? parseInt(minutes[1]) * 60 : 0) +
                       (seconds ? parseInt(seconds[1]) : 0);
            }
        } catch (e) {
            console.log('Error parseando tiempo SCORM:', e);
        }
        return 0;
    }
    
    // Enviar datos finales al cerrar
    function onBeforeUnload() {
        progressData.timeSpent = Math.floor((Date.now() - startTime) / 1000);
        sendToParent('final', progressData);
    }
    
    // Event listeners
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onContentReady);
    } else {
        onContentReady();
    }
    
    window.addEventListener('beforeunload', onBeforeUnload);
    
    // Exportar funciones para uso manual
    window.scormBridge = {
        sendProgress: function(completion, status) {
            progressData.completion = completion;
            progressData.status = status || 'incomplete';
            sendToParent('progress', progressData);
        },
        
        setScore: function(score) {
            progressData.score = score;
            sendToParent('progress', progressData);
        },
        
        markComplete: function() {
            progressData.completion = 100;
            progressData.status = 'completed';
            sendToParent('progress', progressData);
        }
    };
    
})(); 