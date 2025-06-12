/**
 * SCORM Content Fixer - Corrige duplicación de encabezados y mejora estilos
 * Se ejecuta automáticamente al cargar contenido SCORM
 */

(function() {
    'use strict';
    
    console.log('🔧 SCORM Content Fixer iniciado');
    
    // Configuración
    const CONFIG = {
        // Patrones de detección de encabezados institucionales
        headerPatterns: [
            /🎓.*INSTITUCIÓN.*EDUCATIVA/gi,
            /INSTITUCIÓN\s+EDUCATIVA/gi,
            /COLEGIO.*NACIONAL/gi,
            /CENTRO\s+EDUCATIVO/gi,
            /UNIDAD\s+EDUCATIVA/gi
        ],
        
        // Selectores de elementos que pueden contener encabezados
        headerSelectors: [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'div', 'header', 'section', 'article',
            '.header', '.titulo', '.encabezado',
            '[class*="header"]', '[class*="institucional"]'
        ],
        
        // Estilos CSS nativos importantes a preservar
        importantStyleProps: [
            'background',
            'background-image',
            'background-gradient',
            'border-radius',
            'box-shadow',
            'animation',
            'transform',
            'transition',
            'filter',
            'grid',
            'flex'
        ]
    };
    
    /**
     * Función principal que ejecuta todas las correcciones
     */
    function initSCORMFixer() {
        console.log('🚀 Iniciando correcciones SCORM...');
        
        // Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(runAllFixes, 100);
            });
        } else {
            setTimeout(runAllFixes, 100);
        }
    }
    
    /**
     * Ejecuta todas las correcciones en secuencia
     */
    function runAllFixes() {
        try {
            removeDuplicateHeaders();
            preserveNativeStyles();
            improveContentAccessibility();
            enhanceResponsiveness();
            
            console.log('✅ Todas las correcciones SCORM aplicadas exitosamente');
            
            // Observar cambios dinámicos en el contenido
            setupMutationObserver();
            
        } catch (error) {
            console.error('❌ Error aplicando correcciones SCORM:', error);
        }
    }
    
    /**
     * Elimina encabezados institucionales duplicados
     */
    function removeDuplicateHeaders() {
        console.log('🔄 Eliminando encabezados duplicados...');
        
        const allElements = document.querySelectorAll(CONFIG.headerSelectors.join(', '));
        const foundHeaders = new Map(); // Patrón -> [elementos]
        
        // Agrupar elementos por patrón de encabezado institucional
        allElements.forEach(element => {
            const text = element.textContent.trim();
            
            CONFIG.headerPatterns.forEach((pattern, index) => {
                if (pattern.test(text)) {
                    const key = `pattern_${index}`;
                    if (!foundHeaders.has(key)) {
                        foundHeaders.set(key, []);
                    }
                    foundHeaders.get(key).push(element);
                }
            });
        });
        
        // Eliminar duplicados (mantener solo el primero de cada patrón)
        let removedCount = 0;
        foundHeaders.forEach((elements, pattern) => {
            if (elements.length > 1) {
                // Mantener el primero, ocultar los demás
                elements.slice(1).forEach(element => {
                    element.style.display = 'none';
                    element.setAttribute('data-scorm-hidden', 'duplicate-header');
                    removedCount++;
                });
                
                console.log(`🗑️ Ocultados ${elements.length - 1} encabezados duplicados para patrón: ${pattern}`);
            }
        });
        
        if (removedCount > 0) {
            console.log(`✅ Total de encabezados duplicados ocultados: ${removedCount}`);
        } else {
            console.log('ℹ️ No se encontraron encabezados duplicados');
        }
    }
    
    /**
     * Preserva y restaura estilos CSS nativos importantes
     */
    function preserveNativeStyles() {
        console.log('🎨 Preservando estilos nativos...');
        
        // Buscar elementos con estilos inline importantes
        const elementsWithStyle = document.querySelectorAll('[style]');
        let preservedCount = 0;
        
        elementsWithStyle.forEach(element => {
            const currentStyle = element.getAttribute('style');
            const hasImportantStyles = CONFIG.importantStyleProps.some(prop => 
                currentStyle.toLowerCase().includes(prop)
            );
            
            if (hasImportantStyles) {
                // Agregar !important a propiedades críticas
                const preservedStyle = currentStyle
                    .split(';')
                    .map(rule => {
                        const [prop, value] = rule.split(':');
                        if (prop && value) {
                            const propName = prop.trim().toLowerCase();
                            if (CONFIG.importantStyleProps.some(important => propName.includes(important))) {
                                if (!value.includes('!important')) {
                                    return `${prop.trim()}: ${value.trim()} !important`;
                                }
                            }
                        }
                        return rule;
                    })
                    .join('; ');
                
                element.setAttribute('style', preservedStyle);
                element.setAttribute('data-scorm-preserved', 'true');
                preservedCount++;
            }
        });
        
        // Preservar variables CSS personalizadas
        preserveCSSVariables();
        
        console.log(`✅ Estilos nativos preservados en ${preservedCount} elementos`);
    }
    
    /**
     * Preserva variables CSS y propiedades custom
     */
    function preserveCSSVariables() {
        const styleSheets = Array.from(document.styleSheets);
        const customProperties = new Set();
        
        styleSheets.forEach(sheet => {
            try {
                const rules = Array.from(sheet.cssRules || sheet.rules || []);
                rules.forEach(rule => {
                    if (rule.style) {
                        for (let i = 0; i < rule.style.length; i++) {
                            const property = rule.style[i];
                            if (property.startsWith('--')) {
                                customProperties.add(property);
                            }
                        }
                    }
                });
            } catch (e) {
                // Ignorar errores de CORS en stylesheets externos
            }
        });
        
        if (customProperties.size > 0) {
            console.log(`🎨 Variables CSS encontradas: ${Array.from(customProperties).join(', ')}`);
        }
    }
    
    /**
     * Mejora la accesibilidad del contenido
     */
    function improveContentAccessibility() {
        console.log('♿ Mejorando accesibilidad...');
        
        // Agregar alt text a imágenes sin él
        const imagesWithoutAlt = document.querySelectorAll('img:not([alt])');
        imagesWithoutAlt.forEach((img, index) => {
            img.alt = `Imagen del contenido educativo ${index + 1}`;
            img.setAttribute('data-scorm-enhanced', 'alt-added');
        });
        
        // Mejorar contraste en elementos con texto pequeño
        const smallTextElements = document.querySelectorAll('small, .small, [style*="font-size: 1"], [style*="font-size:1"]');
        smallTextElements.forEach(element => {
            const computed = window.getComputedStyle(element);
            const fontSize = parseFloat(computed.fontSize);
            if (fontSize < 14) {
                element.style.fontSize = '14px';
                element.style.lineHeight = '1.5';
                element.setAttribute('data-scorm-enhanced', 'font-size-improved');
            }
        });
        
        // Mejorar tablas para responsive
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            if (!table.closest('.table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                wrapper.style.overflowX = 'auto';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
                table.setAttribute('data-scorm-enhanced', 'responsive-table');
            }
        });
        
        console.log(`✅ Accesibilidad mejorada: ${imagesWithoutAlt.length} imágenes, ${smallTextElements.length} textos pequeños, ${tables.length} tablas`);
    }
    
    /**
     * Mejora la responsividad del contenido
     */
    function enhanceResponsiveness() {
        console.log('📱 Mejorando responsividad...');
        
        // Asegurar que el contenido no se desborde
        const potentiallyWideElements = document.querySelectorAll('pre, code, table, .wide-content, [style*="width"]');
        potentiallyWideElements.forEach(element => {
            const computed = window.getComputedStyle(element);
            if (computed.width && computed.width !== 'auto') {
                element.style.maxWidth = '100%';
                element.style.overflowX = 'auto';
                element.setAttribute('data-scorm-enhanced', 'responsive-width');
            }
        });
        
        // Mejorar videos embebidos
        const videos = document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"]');
        videos.forEach(video => {
            video.style.maxWidth = '100%';
            video.style.height = 'auto';
            video.setAttribute('data-scorm-enhanced', 'responsive-video');
        });
        
        console.log(`✅ Responsividad mejorada en ${potentiallyWideElements.length + videos.length} elementos`);
    }
    
    /**
     * Configura un observador para cambios dinámicos en el DOM
     */
    function setupMutationObserver() {
        const observer = new MutationObserver(function(mutations) {
            let needsUpdate = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    needsUpdate = true;
                }
            });
            
            if (needsUpdate) {
                console.log('🔄 Contenido dinámico detectado, reaplicando correcciones...');
                setTimeout(runAllFixes, 500);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('👁️ Observador de cambios dinámicos configurado');
    }
    
    /**
     * Función de utilidad para logging con timestamp
     */
    function log(message, type = 'info') {
        const timestamp = new Date().toISOString().substr(11, 8);
        const prefix = `[SCORM Fixer ${timestamp}]`;
        
        switch (type) {
            case 'error':
                console.error(prefix, message);
                break;
            case 'warn':
                console.warn(prefix, message);
                break;
            default:
                console.log(prefix, message);
        }
    }
    
    // Inicializar cuando se carga el script
    initSCORMFixer();
    
    // Exponer funciones globalmente para debug
    window.SCORMFixer = {
        runAllFixes: runAllFixes,
        removeDuplicateHeaders: removeDuplicateHeaders,
        preserveNativeStyles: preserveNativeStyles,
        improveContentAccessibility: improveContentAccessibility,
        enhanceResponsiveness: enhanceResponsiveness
    };
    
})(); 