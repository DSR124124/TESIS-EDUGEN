// Editor de Formato de Texto
// Herramientas para formateo de texto en el editor

console.log('📝 Iniciando módulo de formato de texto...');

// Namespace para evitar conflictos
window.TextFormatTools = {
    // Función para ejecutar comandos de formato
    execCmd: function(command, showUI) {
        console.log('🎨 Ejecutando comando de formato:', command);
        
        // Preservar posición del cursor durante la ejecución del comando
        this.preserveCursorPosition(() => {
            document.execCommand(command, showUI, showUI ? prompt('Ingresa el valor:', '') : null);
        });
        
        // Actualizar contador de palabras de forma segura
        setTimeout(() => {
            this.updateWordCountSafely();
            this.preventAutoScroll();
        }, 10);
        
        console.log('✅ Comando ejecutado sin mover cursor');
    },

    // Crear herramientas de formato
    createFormatToolbar: function(parent) {
        console.log('Creando herramientas de formato...');
        
        const formatGroup = document.createElement('div');
        formatGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
        
        const formatLabel = document.createElement('div');
        formatLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
        formatLabel.textContent = 'Formato de texto:';
        formatGroup.appendChild(formatLabel);
        
        const columnsContainer = document.createElement('div');
        columnsContainer.className = 'text-format-tools';
        columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; width: 100%; padding: 5px;';
        formatGroup.appendChild(columnsContainer);
        
        const formatButtons = [
            { title: 'Texto en Negrita', subtitle: 'Resaltar importante', icon: 'fas fa-bold', action: () => this.execCmd('bold') },
            { title: 'Texto en Cursiva', subtitle: 'Enfatizar contenido', icon: 'fas fa-italic', action: () => this.execCmd('italic') },
            { title: 'Texto Subrayado', subtitle: 'Destacar información', icon: 'fas fa-underline', action: () => this.execCmd('underline') },
            { title: 'Texto Tachado', subtitle: 'Marcar eliminado', icon: 'fas fa-strikethrough', action: () => this.execCmd('strikethrough') },
            { title: 'Lista con Viñetas', subtitle: 'Puntos y elementos', icon: 'fas fa-list-ul', action: () => this.execCmd('insertUnorderedList') },
            { title: 'Lista Numerada', subtitle: 'Pasos ordenados', icon: 'fas fa-list-ol', action: () => this.execCmd('insertOrderedList') },
            { title: 'Aumentar Sangría', subtitle: 'Mover a la derecha', icon: 'fas fa-indent', action: () => this.execCmd('indent') },
            { title: 'Reducir Sangría', subtitle: 'Mover a la izquierda', icon: 'fas fa-outdent', action: () => this.execCmd('outdent') },
            { title: 'Texto Superior', subtitle: 'Exponentes (x²)', icon: 'fas fa-superscript', action: () => this.execCmd('superscript') },
            { title: 'Texto Inferior', subtitle: 'Subíndices (H₂O)', icon: 'fas fa-subscript', action: () => this.execCmd('subscript') },
            { title: 'Centrar Texto', subtitle: 'Alinear al centro', icon: 'fas fa-align-center', action: () => this.execCmd('justifyCenter') },
            { title: 'Color de Texto', subtitle: 'Cambiar color', icon: 'fas fa-palette', action: () => this.promptTextColor() }
        ];
        
        formatButtons.forEach(btn => {
            const button = this.createToolButton(btn);
            columnsContainer.appendChild(button);
        });
        
        parent.appendChild(formatGroup);
        console.log('Herramientas de formato creadas exitosamente');
    },

    // Crear botón de herramienta
    createToolButton: function(btnData) {
        const button = document.createElement('button');
        button.className = 'btn btn-sm text-format-tool-btn';
        button.title = `${btnData.title} - ${btnData.subtitle}`;
        button.style.cssText = `
            width: 100%; 
            min-height: 65px; 
            padding: 8px 6px; 
            font-size: 10px; 
            border: 1px solid #0046CC; 
            background: linear-gradient(135deg, #0046CC 0%, #0056E0 100%); 
            color: white;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            cursor: pointer;
            margin: 2px 0;
            gap: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        `;
        
        // Crear contenedor principal
        const content = document.createElement('div');
        content.style.cssText = 'display: flex; flex-direction: column; align-items: center; gap: 4px; text-align: center; width: 100%;';
        
        // Icono
        const icon = document.createElement('i');
        icon.className = btnData.icon;
        icon.style.cssText = 'font-size: 16px; margin: 0;';
        
        // Título principal
        const title = document.createElement('div');
        title.textContent = btnData.title;
        title.style.cssText = 'font-weight: 600; font-size: 9px; line-height: 1.1; margin: 0;';
        
        // Subtítulo
        const subtitle = document.createElement('div');
        subtitle.textContent = btnData.subtitle;
        subtitle.style.cssText = 'font-size: 8px; opacity: 0.85; line-height: 1; margin: 0; font-weight: 400;';
        
        content.appendChild(icon);
        content.appendChild(title);
        content.appendChild(subtitle);
        button.appendChild(content);
        
        // Agregar efecto hover
        button.addEventListener('mouseenter', () => {
            button.style.background = 'linear-gradient(135deg, #003399 0%, #004ACC 100%)';
            button.style.transform = 'translateY(-2px) scale(1.02)';
            button.style.boxShadow = '0 4px 15px rgba(0,70,204,0.3)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.background = 'linear-gradient(135deg, #0046CC 0%, #0056E0 100%)';
            button.style.transform = 'translateY(0) scale(1)';
            button.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Efecto visual de clic
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = '';
            }, 100);
            
            // Ejecutar acción
            if (btnData.action) {
                btnData.action();
            }
        });
        
        return button;
    },

    // Función para seleccionar color de texto
    promptTextColor: function() {
        const color = prompt('Ingresa el color (hex, ej: #ff0000):');
        if (color) {
            this.preserveCursorPosition(() => {
                document.execCommand('foreColor', false, color);
            });
        }
    },

    // Función para preservar posición del cursor
    preserveCursorPosition: function(callback) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            callback();
            selection.removeAllRanges();
            selection.addRange(range);
        } else {
            callback();
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
            console.error('Error al actualizar contador de palabras:', error);
        }
    },

    // Inicializar módulo
    init: function() {
        console.log('✅ Módulo de formato de texto inicializado');
        
        // Agregar estilos CSS para botones de formato
        this.addTextFormatStyles();
    },

    // Agregar estilos CSS para formato de texto
    addTextFormatStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* Estilos para botones de formato de texto */
            .text-format-tool-btn {
                word-wrap: break-word;
                text-align: center !important;
                white-space: normal !important;
            }
            
            /* Estilos para panel de formato de texto */
            .text-format-tools {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
                padding: 5px;
            }
            
            /* Responsive para botones de formato */
            @media (max-width: 768px) {
                .text-format-tools {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            @media (max-width: 480px) {
                .text-format-tools {
                    grid-template-columns: 1fr;
                }
                
                .text-format-tool-btn {
                    min-height: 55px;
                    font-size: 9px;
                }
            }
        `;
        document.head.appendChild(style);
    }
};

// Auto-inicializar si el DOM está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.TextFormatTools.init();
    });
} else {
    window.TextFormatTools.init();
} 