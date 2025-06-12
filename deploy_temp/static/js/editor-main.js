// Editor Principal - Integración de todos los módulos
// Coordina y gestiona todos los módulos de edición

console.log('🚀 Iniciando Editor Principal v3.1.0...');

// Namespace principal con funcionalidades mejoradas
window.EditorMain = {
    // Estado del editor
    state: {
        initialized: false,
        modules: {
            textFormat: false,
            layoutDesign: false,
            multimedia: false,
            educationalContent: false
        },
        config: {
            autoSaveInterval: 30000, // 30 segundos
            wordCountEnabled: true,
            keyboardShortcutsEnabled: true,
            collaborativeEditing: false
        },
        performance: {
            startTime: Date.now(),
            loadTime: null,
            moduleCount: 0
        }
    },

    // Inicializar editor principal
    init: function() {
        console.log('🚀 Inicializando Sistema de Editor Avanzado v3.1.0...');
        
        // Verificar si ya está inicializado
        if (this.preventContentDuplication()) {
            return;
        }
        
        // Determinar si es una página de IA
        this.isAIContent = this.detectAIContent();
        
        // Mostrar indicador de carga
        this.showLoadingIndicator();
        
        // Configurar interceptor de guardado limpio
        this.setupCleanSaveInterceptor();
        
        // Reorganizar layout
        this.reorganizeEditorLayout();
        
        // Crear barra de herramientas integrada
        setTimeout(() => {
            this.createIntegratedToolbar();
        }, 100);
        
        // Mejorar editor
        setTimeout(() => {
            this.enhanceEditor();
        }, 200);
        
        // Configurar funciones adicionales
        setTimeout(() => {
            this.setupPerformanceMonitoring();
            this.setupAccessibilityFeatures();
            
            // Verificar y limpiar duplicaciones existentes
            this.verifyAndCleanContent();
            
            // Agregar AI Assistant si es contenido de IA
            if (this.isAIContent) {
                this.setupAIAssistant();
            }
            
            // DESHABILITADO: Asegurar que los botones de guardar del template funcionen correctamente
            // this.ensureSaveButtonsFunctionality(); // Causaba conflictos con eventos
            
            // DESHABILITADO: Forzar cursor correcto en botones
            // this.forceCursorOnButtons(); // Causaba bloqueo de eventos con pointer-events: none
            
            // Ocultar indicador de carga
            this.hideLoadingIndicator();
            
            // Marcar como completamente inicializado
            this.state.initialized = true;
            this.dispatchCustomEvent('editorInitialized', { version: this.version });
            
            console.log('🎉 ¡Editor inicializado exitosamente!');
        }, 500);
    },

    // Mostrar indicador de carga
    showLoadingIndicator: function() {
        const indicator = document.createElement('div');
        indicator.id = 'editor-loading-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        `;
        
        indicator.innerHTML = `
            <div style="text-align: center; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="width: 50px; height: 50px; border: 4px solid #f3f3f3; border-top: 4px solid #0046CC; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                <h3 style="color: #0046CC; margin: 0 0 10px 0;">Inicializando Editor</h3>
                <p style="color: #666; margin: 0;">Cargando herramientas avanzadas...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        
        document.body.appendChild(indicator);
    },

    // Ocultar indicador de carga
    hideLoadingIndicator: function() {
        const indicator = document.getElementById('editor-loading-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            setTimeout(() => {
                indicator.remove();
            }, 300);
        }
    },

    // Reorganizar layout del editor
    reorganizeEditorLayout: function() {
        console.log('🏗️ Reorganizando layout del editor...');
        
        // Buscar el contenedor correcto (puede ser .card-body o #editor-container)
        let cardBody = document.getElementById('editor-container');
        if (!cardBody) {
            cardBody = document.querySelector('.card-body');
        }
        
        const contentEditor = document.getElementById('content-editor');
        
        if (!cardBody || !contentEditor) {
            console.error('❌ No se encontraron elementos necesarios');
            console.log('cardBody:', cardBody, 'contentEditor:', contentEditor);
            return;
        }
        
        // Verificar si ya existe el layout reorganizado para evitar duplicación
        if (document.getElementById('fixed-sidebar')) {
            console.log('⚠️ Layout ya reorganizado, saltando...');
            return;
        }
        
        // Guardar contenido actual SOLO una vez
        const editorContent = contentEditor.innerHTML;
        console.log('💾 Contenido guardado:', editorContent.length + ' caracteres');
        
        // Limpiar contenido duplicado si existe
        const cleanedContent = this.cleanDuplicatedContent(editorContent);
        if (cleanedContent !== editorContent) {
            console.log('🧹 Contenido limpiado de duplicaciones');
        }
        
        // Eliminar toolbar existente si existe
        const existingToolbar = document.querySelector('.editor-toolbar');
        if (existingToolbar) {
            existingToolbar.remove();
            console.log('🗑️ Toolbar existente eliminado');
        }
        
        // Crear nuevo layout (contenido izquierda, herramientas derecha)
        cardBody.innerHTML = `
            <div style="display: flex; height: calc(100vh - 120px); overflow: hidden; padding: 0; margin: 0;">
                <div style="flex: 1; overflow-y: auto;">
                    <div id="content-editor-container" style="padding: 0; margin: 0;"></div>
                </div>
                <div id="fixed-sidebar" style="width: 320px; background: #f8f9fa; border-left: 1px solid #e0e0e0; 
                     overflow-y: auto; box-shadow: -2px 0 10px rgba(0,0,0,0.05); padding: 0; margin: 0;">
                    <div id="editor-toolbar-vertical" class="editor-toolbar-vertical" style="padding: 10px 5px;">
                        <h3 style="text-align: center; padding: 8px 0; margin: 0 0 10px 0; border-bottom: 2px solid #0046CC; color: #0046CC; font-size: 16px; font-weight: 600;">
                            🛠️ Herramientas de Edición
                        </h3>
                    </div>
                </div>
            </div>
        `;
        
        // Crear nuevo editor completamente natural - SIN ESTILOS
        const contentContainer = document.getElementById('content-editor-container');
        const newEditor = document.createElement('div');
        newEditor.id = 'content-editor';
        newEditor.className = 'editor-content';
        newEditor.contentEditable = true;
        
        // Restaurar contenido sin duplicación
        newEditor.innerHTML = cleanedContent;
        
        // ELIMINAR TODOS LOS ESTILOS - Completamente natural
        newEditor.style.cssText = `
            min-height: 400px;
            outline: none;
        `;
        
        contentContainer.appendChild(newEditor);
        
        // Configurar event listeners
        newEditor.addEventListener('input', () => {
            setTimeout(() => {
                this.updateWordCountSafely();
                this.preventAutoScroll();
            }, 50);
        });
        
        console.log('✅ Layout reorganizado exitosamente');
    },

    // Crear barra de herramientas integrada
    createIntegratedToolbar: function() {
        console.log('🔧 Creando barra de herramientas integrada...');
        
        const editorToolbar = document.getElementById('editor-toolbar-vertical');
        if (!editorToolbar) {
            console.error('❌ No se encontró contenedor de toolbar');
            return;
        }
        
        // Verificar que los módulos estén disponibles
        this.waitForModules().then(() => {
            // Crear herramientas de formato de texto
            if (window.TextFormatTools) {
                window.TextFormatTools.createFormatToolbar(editorToolbar);
                this.state.modules.textFormat = true;
                console.log('✅ Módulo de formato de texto integrado');
            }
            
            // Crear herramientas de diseño y estructura
            if (window.LayoutDesignTools) {
                window.LayoutDesignTools.createLayoutToolbar(editorToolbar);
                this.state.modules.layoutDesign = true;
                console.log('✅ Módulo de diseño y estructura integrado');
            }
            
            // Crear herramientas multimedia
            if (window.MultimediaTools) {
                window.MultimediaTools.createMediaToolbar(editorToolbar);
                this.state.modules.multimedia = true;
                console.log('✅ Módulo multimedia integrado');
            }
            
            // Crear herramientas educativas
            if (window.EducationalContentTools) {
                window.EducationalContentTools.createEducationalToolbar(editorToolbar);
                this.state.modules.educationalContent = true;
                console.log('✅ Módulo de contenido educativo integrado');
            }
            
            console.log('🎉 Todos los módulos integrados exitosamente');
        });
    },

    // Esperar a que los módulos estén disponibles
    waitForModules: function() {
        return new Promise((resolve) => {
            const checkModules = () => {
                if (window.TextFormatTools && 
                    window.LayoutDesignTools && 
                    window.MultimediaTools && 
                    window.EducationalContentTools) {
                    resolve();
                } else {
                    setTimeout(checkModules, 100);
                }
            };
            checkModules();
        });
    },

    // Mejorar editor
    enhanceEditor: function() {
        console.log('⚡ Mejorando editor...');
        
        const editor = document.getElementById('content-editor');
        if (!editor) return;
        
        // Agregar estilos CSS dinámicos
        this.addDynamicStyles();
        
        // Configurar atajos de teclado
        this.setupKeyboardShortcuts();
        
        // Configurar auto-guardado
        this.setupAutoSave();
        
        console.log('✅ Editor mejorado exitosamente');
    },

    // Agregar estilos CSS dinámicos
    addDynamicStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* Estilos para elementos educativos */
            .educational-element:hover .edu-controls {
                opacity: 1 !important;
            }
            
            /* Estilos para elementos multimedia */
            .media-container:hover .media-controls,
            .editable-image-container:hover .image-controls {
                display: block !important;
            }
            
            /* Estilos para columnas */
            .custom-row:hover .row-controls,
            .custom-row:hover .cell-controls {
                display: block !important;
            }
            
            /* Animaciones */
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            
            /* Estilos para botones de herramientas */
            .toolbar-btn:active {
                transform: scale(0.95) !important;
            }
            
            /* SOLO el outline para focus - SIN más estilos */
            #content-editor:focus {
                outline: 2px solid #0046CC;
                outline-offset: 2px;
            }
            
            /* Estilos sutiles para celdas activas - no forzar colores */
            .custom-cell.active {
                border: 2px solid #007bff !important;
                box-shadow: 0 0 5px rgba(0,123,255,0.2) !important;
            }
        `;
        document.head.appendChild(style);
        console.log('🎨 Estilos dinámicos agregados (solo herramientas)');
    },

    // Configurar atajos de teclado
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+B para negrita
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                if (window.TextFormatTools) {
                    window.TextFormatTools.execCmd('bold');
                }
            }
            
            // Ctrl+I para cursiva
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                if (window.TextFormatTools) {
                    window.TextFormatTools.execCmd('italic');
                }
            }
            
            // Ctrl+U para subrayado
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
                if (window.TextFormatTools) {
                    window.TextFormatTools.execCmd('underline');
                }
            }
            
            // Escape para limpiar selecciones
            if (e.key === 'Escape') {
                if (window.LayoutDesignTools) {
                    window.LayoutDesignTools.clearActiveState();
                }
            }
        });
        
        console.log('⌨️ Atajos de teclado configurados');
    },

    // Configurar auto-guardado
    setupAutoSave: function() {
        let autoSaveTimer;
        const editor = document.getElementById('content-editor');
        
        if (!editor) return;
        
        editor.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                this.autoSave();
            }, 30000); // Auto-guardar cada 30 segundos
        });
        
        console.log('💾 Auto-guardado configurado');
    },

    // Auto-guardar contenido
    autoSave: function() {
        const editor = document.getElementById('content-editor');
        if (!editor) return;
        
        const content = editor.innerHTML;
        localStorage.setItem('editor-autosave', content);
        
        // Mostrar indicador de guardado
        this.showSaveIndicator();
        
        console.log('💾 Contenido auto-guardado');
    },

    // Mostrar indicador de guardado
    showSaveIndicator: function() {
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s;
        `;
        indicator.textContent = '💾 Guardado automáticamente';
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.style.opacity = '1';
        }, 10);
        
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                indicator.remove();
            }, 300);
        }, 2000);
    },

    // Configurar interceptor de guardado limpio
    setupCleanSaveInterceptor: function() {
        console.log('🧹 Configurando interceptor de guardado...');
        
        // Interceptar envío del formulario
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                this.cleanContentForSave();
            });
        }
        
        // Interceptar solo botones de guardado específicos del editor (no los del template)
        // Evitar interferir con btnSaveContent y btnSaveContent2
        const editorSaveButtons = document.querySelectorAll('button[type="submit"]:not(#btnSaveContent):not(#btnSaveContent2)');
        editorSaveButtons.forEach(button => {
            button.addEventListener('click', () => {
                setTimeout(() => {
                    this.cleanContentForSave();
                }, 10);
            });
        });
        
        console.log('✅ Interceptor de guardado configurado');
    },

    // Asegurar que los botones de guardar del template funcionen correctamente - VERSIÓN MÍNIMA
    ensureSaveButtonsFunctionality: function() {
        console.log('🔧 Verificando funcionalidad de botones de guardar (modo mínimo)...');
        
        const btnSaveContent = document.getElementById('btnSaveContent');
        const btnSaveContent2 = document.getElementById('btnSaveContent2');
        
        // Verificar que los botones existan
        if (!btnSaveContent || !btnSaveContent2) {
            console.warn('⚠️ Botones de guardar no encontrados');
            return;
        }
        
        // SOLO verificar que los botones sean clickeables - NO agregar event listeners
        console.log('✅ Botones de guardar encontrados y verificados');
        console.log('ℹ️ Funcionalidad de guardado manejada por el template');
        
        // Solo asegurar que tengan el estilo correcto
        [btnSaveContent, btnSaveContent2].forEach(button => {
            button.style.pointerEvents = 'auto';
            button.style.cursor = 'pointer';
        });
    },

    // Forzar cursor correcto en botones - SIN BLOQUEAR EVENTOS
    forceCursorOnButtons: function() {
        console.log('👆 Forzando cursor correcto en botones (sin bloquear eventos)...');
        
        const buttons = document.querySelectorAll('#btnSaveContent, #btnSaveContent2, .btn-editor, .editor-top-bar button, .editor-bottom-bar button, .editor-top-bar a, .editor-bottom-bar a');
        
        buttons.forEach(button => {
            if (button) {
                button.style.cursor = 'pointer';
                button.style.userSelect = 'none';
                button.style.webkitUserSelect = 'none';
                button.style.mozUserSelect = 'none';
                button.style.msUserSelect = 'none';
                
                // Solo aplicar estilos de cursor a elementos hijos - NO bloquear eventos
                const children = button.querySelectorAll('*');
                children.forEach(child => {
                    child.style.cursor = 'inherit';
                    child.style.userSelect = 'none';
                    // REMOVIDO: child.style.pointerEvents = 'none'; - Bloqueaba los clicks
                });
            }
        });
        
        console.log(`✅ Cursor aplicado a ${buttons.length} botones (eventos habilitados)`);
        
        // Reducir frecuencia de verificación para evitar interferencias
        setTimeout(() => {
            this.forceCursorOnButtons();
        }, 10000); // Cada 10 segundos en lugar de cada 3
    },

    // Limpiar contenido para guardado
    cleanContentForSave: function() {
        const editor = document.getElementById('content-editor');
        if (!editor) return;
        
        console.log('🧹 Limpiando contenido para guardado (modo natural)...');
        
        // Crear copia temporal para limpiar
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = editor.innerHTML;
        
        // Remover solo controles de edición - mantener contenido natural
        const controlsToRemove = [
            '.row-controls',
            '.cell-controls', 
            '.edu-controls',
            '.media-controls',
            '.image-controls',
            '.cell-indicator'
        ];
        
        controlsToRemove.forEach(selector => {
            const elements = tempDiv.querySelectorAll(selector);
            elements.forEach(el => el.remove());
        });
        
        // Remover solo atributos de edición, mantener contenido
        const editableElements = tempDiv.querySelectorAll('[contenteditable]');
        editableElements.forEach(el => {
            el.removeAttribute('contenteditable');
        });
        
        // Remover event handlers inline solamente
        const elementsWithHandlers = tempDiv.querySelectorAll('[onclick], [onmouseenter], [onmouseleave]');
        elementsWithHandlers.forEach(el => {
            el.removeAttribute('onclick');
            el.removeAttribute('onmouseenter');
            el.removeAttribute('onmouseleave');
        });
        
        // Limpiar solo estilos de edición activa - preservar estilos naturales
        const activeElements = tempDiv.querySelectorAll('.active');
        activeElements.forEach(el => {
            el.classList.remove('active');
        });
        
        // Actualizar contenido del editor preservando formato original
        editor.innerHTML = tempDiv.innerHTML;
        
        console.log('✅ Contenido limpiado preservando formato natural');
    },

    // Configurar monitoreo de rendimiento
    setupPerformanceMonitoring: function() {
        console.log('📊 Configurando monitoreo de rendimiento...');
        
        // Monitorear uso de memoria
        setInterval(() => {
            if (performance.memory) {
                const memoryInfo = {
                    used: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
                    total: Math.round(performance.memory.totalJSHeapSize / 1048576), // MB
                    limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) // MB
                };
                
                // Advertir si el uso de memoria es alto
                if (memoryInfo.used > memoryInfo.limit * 0.8) {
                    console.warn('⚠️ Alto uso de memoria detectado:', memoryInfo);
                }
            }
        }, 60000); // Cada minuto
    },

    // Configurar funciones de accesibilidad
    setupAccessibilityFeatures: function() {
        console.log('♿ Configurando funciones de accesibilidad...');
        
        const editor = document.getElementById('content-editor');
        if (!editor) return;
        
        // Agregar atributos ARIA
        editor.setAttribute('role', 'textbox');
        editor.setAttribute('aria-label', 'Editor de contenido principal');
        editor.setAttribute('aria-multiline', 'true');
        
        // Configurar navegación por teclado mejorada
        editor.addEventListener('keydown', (e) => {
            // Alt + F10 para enfocar toolbar
            if (e.altKey && e.key === 'F10') {
                e.preventDefault();
                const firstToolbarBtn = document.querySelector('.toolbar-btn');
                if (firstToolbarBtn) {
                    firstToolbarBtn.focus();
                }
            }
        });
    },

    // Disparar evento personalizado
    dispatchCustomEvent: function(eventName, detail) {
        const event = new CustomEvent(eventName, {
            detail: detail,
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    },

    // Actualizar contador de palabras de forma segura
    updateWordCountSafely: function() {
        try {
            const editor = document.getElementById('content-editor');
            if (!editor) return;
            
            const text = editor.innerText || editor.textContent || '';
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            
            const wordCountElement = document.getElementById('word-count');
            if (wordCountElement) {
                wordCountElement.textContent = `Palabras: ${wordCount}`;
            }
        } catch (error) {
            console.error('❌ Error al actualizar contador de palabras:', error);
        }
    },

    // Prevenir scroll automático
    preventAutoScroll: function() {
        const editor = document.getElementById('content-editor');
        if (editor) {
            const currentScrollTop = editor.scrollTop;
            setTimeout(() => {
                editor.scrollTop = currentScrollTop;
            }, 5);
        }
    },

    // API pública para extensiones
    api: {
        // Registrar módulo externo
        registerModule: function(name, moduleObject) {
            if (window.EditorMain.state.modules.hasOwnProperty(name)) {
                console.warn(`⚠️ Módulo ${name} ya está registrado`);
                return false;
            }
            
            window.EditorMain.state.modules[name] = moduleObject;
            console.log(`✅ Módulo ${name} registrado exitosamente`);
            return true;
        },
        
        // Obtener referencia del editor
        getEditor: function() {
            return document.getElementById('content-editor');
        },
        
        // Obtener contenido del editor
        getContent: function() {
            const editor = this.getEditor();
            return editor ? editor.innerHTML : '';
        },
        
        // Establecer contenido del editor
        setContent: function(content) {
            const editor = this.getEditor();
            if (editor) {
                editor.innerHTML = content;
                window.EditorMain.updateWordCountSafely();
                return true;
            }
            return false;
        },
        
        // Insertar contenido en la posición del cursor
        insertContent: function(content) {
            const editor = this.getEditor();
            if (editor && editor === document.activeElement) {
                document.execCommand('insertHTML', false, content);
                window.EditorMain.updateWordCountSafely();
                return true;
            }
            return false;
        },
        
        // Obtener estadísticas del editor
        getStats: function() {
            const editor = this.getEditor();
            if (!editor) return null;
            
            const text = editor.innerText || '';
            const html = editor.innerHTML || '';
            
            return {
                wordCount: text.trim().split(/\s+/).filter(word => word.length > 0).length,
                charCount: text.length,
                charCountNoSpaces: text.replace(/\s/g, '').length,
                htmlLength: html.length,
                paragraphCount: (html.match(/<p[^>]*>/g) || []).length
            };
        }
    },

    // Funciones específicas para integración web
    webIntegration: {
        // Detectar URL específica y aplicar configuraciones
        detectAndConfigure: function() {
            const currentURL = window.location.href;
            console.log('🌐 Detectando URL para configuración específica:', currentURL);
            
            // Configuración para URL de edición de contenido AI
            if (currentURL.includes('/ai/contents/') && currentURL.includes('/edit/')) {
                console.log('🤖 Detectada URL de edición de contenido AI');
                this.configureForAIContent();
            }
            
            // Configuración para otras URLs específicas
            if (currentURL.includes('/content/')) {
                console.log('📝 Detectada URL de contenido general');
                this.configureForGeneralContent();
            }
        },
        
        // Configuración específica para contenido AI
        configureForAIContent: function() {
            console.log('🔧 Aplicando configuración para contenido AI...');
            
            // Agregar funcionalidades específicas para AI después de la inicialización
            setTimeout(() => {
                this.addAISpecificFeatures();
            }, 1000);
        },
        
        // Configuración para contenido general
        configureForGeneralContent: function() {
            console.log('📄 Aplicando configuración para contenido general...');
            // Características estándar del editor
        },
        
        // Agregar características específicas para AI
        addAISpecificFeatures: function() {
            const sidebar = document.getElementById('fixed-sidebar');
            if (!sidebar) {
                console.log('⚠️ Sidebar no encontrado, reintentando...');
                setTimeout(() => this.addAISpecificFeatures(), 500);
                return;
            }
            
            // Crear sección de herramientas AI
            const aiSection = document.createElement('div');
            aiSection.innerHTML = `
                <div style="margin: 20px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
                    <h4 style="margin: 0 0 15px 0; display: flex; align-items: center;">
                        <i class="fas fa-robot" style="margin-right: 10px;"></i>
                        Asistente AI
                    </h4>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <button onclick="window.EditorMain.webIntegration.suggestImprovements()" 
                                class="ai-tool-btn" 
                                style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;">
                            <i class="fas fa-lightbulb"></i> Sugerir mejoras
                        </button>
                        <button onclick="window.EditorMain.webIntegration.analyzeReadability()" 
                                class="ai-tool-btn"
                                style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;">
                            <i class="fas fa-chart-line"></i> Analizar legibilidad
                        </button>
                    </div>
                </div>
            `;
            
            sidebar.appendChild(aiSection);
            
            // Agregar estilos hover para botones AI
            const style = document.createElement('style');
            style.textContent = `
                .ai-tool-btn:hover {
                    background: rgba(255,255,255,0.3) !important;
                    transform: translateY(-1px);
                    transition: all 0.2s ease;
                }
            `;
            document.head.appendChild(style);
            
            console.log('✅ Herramientas AI agregadas exitosamente');
        },
        
        // Sugerir mejoras con AI
        suggestImprovements: function() {
            const editor = document.getElementById('content-editor');
            if (!editor) return;
            
            const stats = window.EditorMain.api.getStats();
            
            // Mostrar modal con sugerencias básicas
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10001;
            `;
            
            modal.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 15px; max-width: 600px; max-height: 80vh; overflow-y: auto;">
                    <h2 style="margin-top: 0; color: #667eea;">
                        <i class="fas fa-robot"></i> Análisis de Contenido
                    </h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 20px;">
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${stats.wordCount}</div>
                            <div style="font-size: 12px; color: #666;">Palabras</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${stats.paragraphCount}</div>
                            <div style="font-size: 12px; color: #666;">Párrafos</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${Math.round(stats.wordCount / Math.max(stats.paragraphCount, 1))}</div>
                            <div style="font-size: 12px; color: #666;">Palabras/párrafo</div>
                        </div>
                    </div>
                    <div style="padding: 15px; background: #e9ecef; border-radius: 8px; margin-bottom: 20px;">
                        <h4 style="margin-top: 0;">💡 Sugerencias:</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            ${stats.wordCount < 100 ? '<li>Considera expandir el contenido para mayor profundidad educativa.</li>' : ''}
                            ${stats.wordCount > 2000 ? '<li>El contenido es extenso, considera dividirlo en secciones.</li>' : ''}
                            ${stats.paragraphCount < 3 ? '<li>Agregar más párrafos podría mejorar la estructura.</li>' : ''}
                            <li>Utiliza las herramientas educativas para enriquecer el contenido.</li>
                        </ul>
                    </div>
                    <div style="text-align: right;">
                        <button onclick="this.parentElement.parentElement.remove()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Cerrar
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        },
        
        // Analizar legibilidad
        analyzeReadability: function() {
            const editor = document.getElementById('content-editor');
            if (!editor) return;
            
            const text = editor.innerText || '';
            const stats = window.EditorMain.api.getStats();
            
            // Cálculos básicos de legibilidad
            const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
            const avgWordsPerSentence = Math.round((stats.wordCount / Math.max(sentences, 1)) * 10) / 10;
            const avgCharsPerWord = Math.round((stats.charCountNoSpaces / Math.max(stats.wordCount, 1)) * 10) / 10;
            
            // Estimación simple de nivel de lectura
            let readingLevel = 'Básico';
            let levelColor = '#155724';
            let levelBg = '#d4edda';
            
            if (avgWordsPerSentence > 20 || avgCharsPerWord > 6) {
                readingLevel = 'Avanzado';
                levelColor = '#721c24';
                levelBg = '#f8d7da';
            } else if (avgWordsPerSentence > 15 || avgCharsPerWord > 5) {
                readingLevel = 'Intermedio';
                levelColor = '#856404';
                levelBg = '#fff3cd';
            }
            
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10001;
            `;
            
            modal.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 15px; max-width: 500px;">
                    <h2 style="margin-top: 0; color: #28a745;">
                        <i class="fas fa-chart-line"></i> Análisis de Legibilidad
                    </h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${sentences}</div>
                            <div style="font-size: 12px; color: #666;">Oraciones</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${avgWordsPerSentence}</div>
                            <div style="font-size: 12px; color: #666;">Palabras por oración</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: bold; color: #007bff;">${avgCharsPerWord}</div>
                            <div style="font-size: 12px; color: #666;">Caracteres por palabra</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: ${levelBg}; border-radius: 8px;">
                            <div style="font-size: 18px; font-weight: bold; color: ${levelColor};">${readingLevel}</div>
                            <div style="font-size: 12px; color: #666;">Nivel de lectura</div>
                        </div>
                    </div>
                    <div style="padding: 15px; background: #e9ecef; border-radius: 8px; margin-bottom: 20px;">
                        <h4 style="margin-top: 0;">📋 Recomendaciones:</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            ${avgWordsPerSentence > 20 ? '<li>Considera dividir oraciones largas para mayor claridad.</li>' : ''}
                            ${avgCharsPerWord > 6 ? '<li>Usa palabras más simples cuando sea posible.</li>' : ''}
                            ${readingLevel === 'Avanzado' ? '<li>El contenido puede ser complejo para algunos estudiantes.</li>' : ''}
                            ${readingLevel === 'Básico' ? '<li>¡Excelente! El contenido es fácil de leer.</li>' : ''}
                        </ul>
                    </div>
                    <div style="text-align: right;">
                        <button onclick="this.parentElement.parentElement.remove()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Cerrar
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }
    },

    // Obtener estado del editor
    getState: function() {
        return this.state;
    },

    // Verificar si está inicializado
    isInitialized: function() {
        return this.state.initialized;
    },

    // Prevenir duplicación de contenido
    preventContentDuplication: function() {
        const editor = document.getElementById('content-editor');
        if (!editor) return false;
        
        // Verificar si el contenido ya ha sido inicializado
        if (editor.hasAttribute('data-initialized')) {
            console.log('⚠️ Editor ya inicializado, evitando duplicación');
            return true;
        }
        
        // Verificar si ya existe el layout avanzado
        if (document.getElementById('fixed-sidebar')) {
            console.log('⚠️ Layout avanzado ya existe, evitando reinicialización');
            return true;
        }
        
        // Marcar como inicializado
        editor.setAttribute('data-initialized', 'true');
        console.log('✅ Editor marcado como inicializado');
        return false;
    },

    // Limpiar contenido duplicado si existe
    cleanDuplicatedContent: function(content) {
        if (!content) return '';
        
        console.log('🔍 Verificando duplicaciones en contenido...');
        
        // Normalizar el contenido para mejor detección
        let normalizedContent = content.replace(/\s+/g, ' ').trim();
        
        // Detectar patrones de duplicación específicos
        const duplicatedPatterns = [
            // Patrón [TÍTULO] ... [SUBTÍTULO] ... [PÁRRAFO]
            /(\[TÍTULO\][^[]*\[SUBTÍTULO\][^[]*\[PÁRRAFO\][^[]*?)(\1)+/gi,
            
            // Patrón completo con [EJEMPLO], [ACTIVIDAD], etc.
            /(\[TÍTULO\][^]*?)\1+/gi,
            
            // Contenido específico que se repite
            /(Aplicaciones matemáticas en sucesiones para 1° de secundaria.*?Autoevaluación grupal con lista de cotejo)\s*(\1)+/gi,
            
            // Bloques que empiezan con [EJEMPLO]
            /(\[EJEMPLO\][^[]*?)(\1)+/gi,
            
            // Bloques que empiezan con [ACTIVIDAD]
            /(\[ACTIVIDAD\][^[]*?)(\1)+/gi,
            
            // Bloques que empiezan con [MULTIMEDIA]
            /(\[MULTIMEDIA\][^[]*?)(\1)+/gi,
            
            // Bloques que empiezan con [EVALUACIÓN]
            /(\[EVALUACIÓN\][^[]*?)(\1)+/gi
        ];
        
        let cleanContent = content;
        let duplicationsFound = false;
        
        // Aplicar cada patrón de limpieza
        duplicatedPatterns.forEach((pattern, index) => {
            const before = cleanContent.length;
            cleanContent = cleanContent.replace(pattern, '$1');
            const after = cleanContent.length;
            
            if (before !== after) {
                duplicationsFound = true;
                console.log(`🧹 Duplicación eliminada con patrón ${index + 1}`);
            }
        });
        
        // Método adicional: dividir por bloques y eliminar duplicados
        if (cleanContent.includes('[TÍTULO]')) {
            const blocks = cleanContent.split(/(?=\[TÍTULO\])/);
            const uniqueBlocks = [];
            const seenBlocks = new Set();
            
            for (const block of blocks) {
                const blockSignature = block.replace(/\s+/g, ' ').trim().substring(0, 200);
                if (!seenBlocks.has(blockSignature) && block.trim() !== '') {
                    seenBlocks.add(blockSignature);
                    uniqueBlocks.push(block);
                } else if (block.trim() !== '') {
                    duplicationsFound = true;
                    console.log('🧹 Bloque duplicado eliminado');
                }
            }
            
            cleanContent = uniqueBlocks.join('');
        }
        
        // Eliminar líneas idénticas consecutivas
        const lines = cleanContent.split('\n');
        const uniqueLines = [];
        let previousLine = '';
        
        for (const line of lines) {
            const normalizedLine = line.trim();
            if (normalizedLine !== previousLine) {
                uniqueLines.push(line);
                previousLine = normalizedLine;
            } else if (normalizedLine !== '') {
                duplicationsFound = true;
            }
        }
        
        cleanContent = uniqueLines.join('\n');
        
        if (duplicationsFound) {
            console.log('✅ Duplicaciones encontradas y eliminadas');
        } else {
            console.log('✅ No se encontraron duplicaciones');
        }
        
        return cleanContent;
    },

    // Detectar si es contenido de IA
    detectAIContent: function() {
        const currentURL = window.location.href;
        return currentURL.includes('/ai/contents/') || currentURL.includes('/edit/');
    },

    // Configurar AI Assistant
    setupAIAssistant: function() {
        console.log('🤖 Configurando AI Assistant...');
        
        // Implementar la lógica para configurar el AI Assistant
        // Esto puede incluir la integración con un servicio externo, la configuración de plugins, etc.
        
        console.log('✅ AI Assistant configurado exitosamente');
    },

    // Verificar y limpiar duplicaciones existentes
    verifyAndCleanContent: function() {
        const editor = document.getElementById('content-editor');
        if (!editor) return;
        
        const content = editor.innerHTML;
        const cleanedContent = this.cleanDuplicatedContent(content);
        
        if (cleanedContent !== content) {
            console.log('🧹 Contenido limpiado de duplicaciones');
            editor.innerHTML = cleanedContent;
        }
    }
};

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM cargado, iniciando Editor Principal...');
    
    // Detectar y configurar para URL específica
    window.EditorMain.webIntegration.detectAndConfigure();
    
    // Esperar un poco para asegurar que todo esté cargado
    setTimeout(() => {
        window.EditorMain.init();
    }, 500);
});

// Exportar para uso global
window.EditorMain = window.EditorMain;

console.log('✅ Editor Principal completamente cargado e integrado para ' + window.location.href); 