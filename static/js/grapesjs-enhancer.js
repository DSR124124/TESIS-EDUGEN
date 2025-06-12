// GrapesJS Enhancer - Extensión para agregar funcionalidades de diseño avanzado
// Versión 2.0.0 - Versión simplificada para solucionar problemas de visualización

console.log('Iniciando GrapesJS Enhancer v2.0.0...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando...');
    
    // Comprobar si estamos en la página de edición
    const contentEditor = document.getElementById('content-editor');
    if (!contentEditor) {
        console.log('No se encontró content-editor, saliendo...');
        return;
    }
    
    console.log('Content editor encontrado, continuando...');
    
    // Definir función execCmd globalmente si no existe
    if (typeof window.execCmd === 'undefined') {
        window.execCmd = function(command, showUI) {
            console.log('🎨 Ejecutando comando de formato:', command);
            
            // Preservar posición del cursor durante la ejecución del comando
            preserveCursorPosition(() => {
            document.execCommand(command, showUI, showUI ? prompt('Ingresa el valor:', '') : null);
            });
            
            // Actualizar contador de palabras de forma segura
            setTimeout(() => {
                updateWordCountSafely();
                preventAutoScroll();
            }, 10);
            
            console.log('✅ Comando ejecutado sin mover cursor');
        };
        console.log('Función execCmd definida globalmente con preservación de cursor');
    }
    
    // Eliminar padding del body.teacher-dashboard
    if (document.body.classList.contains('teacher-dashboard')) {
        document.body.style.padding = '0';
        console.log('Padding del body eliminado');
    }
    
    // Esperar un poco para asegurar que todo esté cargado
    setTimeout(function() {
        console.log('Ejecutando reorganización del layout...');
        reorganizeEditorLayout();
        console.log('Layout reorganizado');
        
        console.log('Creando herramientas avanzadas...');
        createAdvancedToolbar();
        console.log('Herramientas creadas');
        
        console.log('Mejorando editor...');
        enhanceEditor();
        console.log('Editor mejorado');
        
        console.log('Configurando interceptor de guardado...');
        setupCleanSaveInterceptor();
        console.log('Interceptor configurado');
        
        console.log('GrapesJS Enhancer v2.0.0 completado exitosamente');
    }, 500);
    
    // Restaurar funcionalidad de imágenes editables después de crear el editor
    setTimeout(() => {
        restoreEditableImages();
        restoreEditableFiles();
        console.log('Imágenes y archivos editables restaurados después de reorganizar layout');
    }, 500);
});

// Reorganizar el layout del editor para tener herramientas fijas a la izquierda y contenido a la derecha
function reorganizeEditorLayout() {
    console.log('Iniciando reorganización del layout...');
    
    // Obtener elementos principales
    const cardBody = document.querySelector('.card-body');
    const contentEditor = document.getElementById('content-editor');
    
    if (!cardBody || !contentEditor) {
        console.error('No se encontraron elementos necesarios:', { cardBody: !!cardBody, contentEditor: !!contentEditor });
        return;
    }
    
    console.log('Elementos principales encontrados');
    
    // Guardar el contenido actual del editor
    const editorContent = contentEditor.innerHTML;
    console.log('Contenido del editor guardado:', editorContent.length + ' caracteres');
    
    // Eliminar elementos originales si existen
    const existingToolbar = document.querySelector('.editor-toolbar');
    if (existingToolbar) {
        existingToolbar.remove();
        console.log('Barra de herramientas existente eliminada');
    }
    
    // Crear nuevo layout
    console.log('Creando nuevo layout...');
    cardBody.innerHTML = `
        <div style="display: flex; height: calc(100vh - 120px); overflow: hidden; padding: 0; margin: 0;">
            <div id="fixed-sidebar" style="width: 320px; background: #f8f9fa; border-right: 1px solid #e0e0e0; 
                 overflow-y: auto; box-shadow: 2px 0 10px rgba(0,0,0,0.05); padding: 0; margin: 0;">
                <div id="editor-toolbar-vertical" class="editor-toolbar-vertical" style="padding: 10px 5px;">
                    <h3 style="text-align: center; padding: 8px 0; margin: 0 0 10px 0; border-bottom: 2px solid #0046CC; color: #0046CC; font-size: 16px; font-weight: 600;">
                        Herramientas de Edición
                    </h3>
                </div>
            </div>
            <div style="flex: 1; padding: 20px; overflow-y: auto;">
                <div id="content-editor-container"></div>
            </div>
        </div>
    `;
    
    // Recuperar referencias a los nuevos elementos
    const contentContainer = document.getElementById('content-editor-container');
    
    // Crear nuevo editor y mantener el id original para compatibilidad
    const newEditor = document.createElement('div');
    newEditor.id = 'content-editor';
    newEditor.className = 'editor-content';
    newEditor.contentEditable = true;
    newEditor.innerHTML = editorContent;
    newEditor.style.cssText = 'min-height: 500px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: white; line-height: 1.6; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;';
    
    // Insertar el editor de contenido
    contentContainer.appendChild(newEditor);
    
    // Configurar event listeners para el nuevo editor
    newEditor.addEventListener('input', function() {
        // Actualizar contador de palabras de forma segura sin mover cursor
        setTimeout(() => {
            updateWordCountSafely();
            preventAutoScroll();
        }, 50); // Delay pequeño para evitar conflictos
    });
    
    // Restaurar funcionalidad de imágenes editables después de crear el editor
    setTimeout(() => {
        restoreEditableImages();
        restoreEditableFiles();
        console.log('Imágenes y archivos editables restaurados después de reorganizar layout');
    }, 500);
    
    console.log('Nuevo layout creado exitosamente');
}

// Crear barra de herramientas avanzada
function createAdvancedToolbar() {
    console.log('Iniciando creación de herramientas...');
    
    const editorToolbar = document.getElementById('editor-toolbar-vertical');
    if (!editorToolbar) {
        console.error('No se encontró editor-toolbar-vertical');
        return;
    }
    
    console.log('Contenedor de herramientas encontrado');
    
    // Crear botones de formato básico primero
    createFormatToolbar(editorToolbar);
    
    // Crear herramientas de diseño
    createLayoutToolbar(editorToolbar);
    
    // Crear herramientas multimedia
    createMediaToolbar(editorToolbar);
    
    // Crear herramientas educativas
    createEducationalToolbar(editorToolbar);
    
    console.log('Todas las herramientas creadas exitosamente');
}

// Crear herramientas de formato
function createFormatToolbar(parent) {
    console.log('Creando herramientas de formato...');
    
    const formatGroup = document.createElement('div');
    formatGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    
    const formatLabel = document.createElement('div');
    formatLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
    formatLabel.textContent = 'Formato de texto:';
    formatGroup.appendChild(formatLabel);
    
    const columnsContainer = document.createElement('div');
    columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; width: 100%;';
    formatGroup.appendChild(columnsContainer);
    
    const formatButtons = [
        { title: 'Negrita', icon: 'fas fa-bold', action: () => window.execCmd('bold') },
        { title: 'Cursiva', icon: 'fas fa-italic', action: () => window.execCmd('italic') },
        { title: 'Subrayado', icon: 'fas fa-underline', action: () => window.execCmd('underline') },
        { title: 'Tachado', icon: 'fas fa-strikethrough', action: () => window.execCmd('strikethrough') },
        { title: 'Lista', icon: 'fas fa-list-ul', action: () => window.execCmd('insertUnorderedList') },
        { title: 'Lista Núm.', icon: 'fas fa-list-ol', action: () => window.execCmd('insertOrderedList') }
    ];
    
    formatButtons.forEach(btnData => {
        const btn = createToolButton(btnData);
        columnsContainer.appendChild(btn);
    });
    
    parent.appendChild(formatGroup);
    console.log('Herramientas de formato creadas');
}

// Crear herramientas de diseño
function createLayoutToolbar(parent) {
    console.log('Creando herramientas de diseño...');
    
    const layoutGroup = document.createElement('div');
    layoutGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    
    const layoutLabel = document.createElement('div');
    layoutLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
    layoutLabel.textContent = 'Diseño y estructura:';
    layoutGroup.appendChild(layoutLabel);
    
    const columnsContainer = document.createElement('div');
    columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; width: 100%;';
    layoutGroup.appendChild(columnsContainer);
    
    const layoutButtons = [
        { title: '1 Columna', icon: 'fas fa-columns', action: () => insertLayout('1') },
        { title: '2 Columnas', icon: 'fas fa-columns', action: () => insertLayout('2') },
        { title: '3 Columnas', icon: 'fas fa-columns', action: () => insertLayout('3') },
        { title: '2/3 + 1/3', icon: 'fas fa-columns', action: () => insertLayout('2-1') }
    ];
    
    layoutButtons.forEach(btnData => {
        const btn = createToolButton(btnData);
        columnsContainer.appendChild(btn);
    });
    
    parent.appendChild(layoutGroup);
    console.log('Herramientas de diseño creadas');
}

// Crear herramientas multimedia
function createMediaToolbar(parent) {
    console.log('Creando herramientas multimedia...');
    
    const mediaGroup = document.createElement('div');
    mediaGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    
    const mediaLabel = document.createElement('div');
    mediaLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
    mediaLabel.textContent = 'Elementos multimedia:';
    mediaGroup.appendChild(mediaLabel);
    
    const columnsContainer = document.createElement('div');
    columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; width: 100%;';
    mediaGroup.appendChild(columnsContainer);
    
    const mediaButtons = [
        { title: 'Imagen', icon: 'fas fa-image', action: () => insertMedia('image') },
        { title: 'Video', icon: 'fas fa-video', action: () => insertMedia('video') },
        { title: 'Audio', icon: 'fas fa-volume-up', action: () => insertMedia('audio') },
        { title: 'Archivo', icon: 'fas fa-file', action: () => insertMedia('file') }
    ];
    
    mediaButtons.forEach(btnData => {
        const btn = createToolButton(btnData);
        columnsContainer.appendChild(btn);
    });
    
    parent.appendChild(mediaGroup);
    console.log('Herramientas multimedia creadas');
}

// Crear herramientas educativas
function createEducationalToolbar(parent) {
    console.log('Creando herramientas educativas...');
    
    const eduGroup = document.createElement('div');
    eduGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    
    const eduLabel = document.createElement('div');
    eduLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
    eduLabel.textContent = 'Contenido educativo:';
    eduGroup.appendChild(eduLabel);
    
    const columnsContainer = document.createElement('div');
    columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; width: 100%;';
    eduGroup.appendChild(columnsContainer);
    
    const eduButtons = [
        { title: 'IA Quiz', icon: 'fas fa-robot', action: () => generateAIQuiz() },
        { title: 'Tabla', icon: 'fas fa-table', action: () => insertEduElement('table') },
        { title: 'Tarjeta', icon: 'fas fa-sticky-note', action: () => insertEduElement('card') },
        { title: 'Línea tiempo', icon: 'fas fa-history', action: () => insertEduElement('timeline') },
        { title: 'Acordeón', icon: 'fas fa-list', action: () => insertEduElement('accordion') },
        { title: 'Nota/Aviso', icon: 'fas fa-exclamation-triangle', action: () => insertEduElement('callout') },
        { title: 'Progreso', icon: 'fas fa-chart-line', action: () => insertEduElement('progress') },
        { title: 'Pestañas', icon: 'fas fa-folder-open', action: () => insertEduElement('tabs') },
        { title: 'Lista tareas', icon: 'fas fa-tasks', action: () => insertEduElement('checklist') }
    ];
    
    eduButtons.forEach(btnData => {
        const btn = createToolButton(btnData);
        columnsContainer.appendChild(btn);
    });
    
    parent.appendChild(eduGroup);
    console.log('Herramientas educativas creadas');
}

// Función auxiliar para crear botones de herramientas
function createToolButton(btnData) {
    const button = document.createElement('button');
    button.type = 'button';
    button.style.cssText = 'padding: 5px 3px; margin: 0; border-radius: 5px; background: white; border: 1px solid #e9ecef; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; font-size: 12px; transition: all 0.2s ease; cursor: pointer;';
    button.title = btnData.title;
    
    // Configurar la acción
    button.onclick = function() {
        console.log('Ejecutando acción para:', btnData.title);
        try {
            btnData.action();
        } catch (error) {
            console.error('Error ejecutando acción:', error);
        }
    };
    
    // Añadir efecto hover
    button.onmouseover = function() {
        this.style.backgroundColor = '#f0f4ff';
        this.style.borderColor = '#0046CC';
    };
    button.onmouseout = function() {
        this.style.backgroundColor = 'white';
        this.style.borderColor = '#e9ecef';
    };
    
    // Añadir ícono
    const icon = document.createElement('i');
    icon.className = btnData.icon;
    icon.style.cssText = 'font-size: 14px; margin-bottom: 2px;';
    button.appendChild(icon);
    
    // Añadir etiqueta
    const label = document.createElement('span');
    label.style.cssText = 'font-size: 9px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;';
    label.textContent = btnData.title;
    button.appendChild(label);
    
    return button;
}

// Mejorar el editor con funcionalidades avanzadas
function enhanceEditor() {
    console.log('Mejorando editor...');
    
    // Añadir estilos para los elementos que se insertan dinámicamente
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .gjs-row {
            display: flex;
            justify-content: flex-start;
            align-items: stretch;
            flex-wrap: wrap;
            padding: 10px;
            margin: 0 0 10px 0;
            position: relative;
            border: 1px dashed #ddd;
        }
        
        .gjs-row:hover .row-controls {
            display: block !important;
        }
        
        .row-controls {
            position: absolute;
            top: -12px;
            right: -12px;
            z-index: 50;
            display: none;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            padding: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .row-controls button {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            width: 24px;
            height: 24px;
            cursor: pointer;
            margin: 1px;
            font-size: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .row-controls button:hover {
            background: #c82333;
            transform: scale(1.1);
        }
        
        .gjs-cell {
            min-height: 75px;
            flex-grow: 1;
            padding: 0 15px;
            position: relative;
            border: 1px dashed #eee;
            transition: all 0.3s ease;
            box-sizing: border-box;
            overflow: hidden; /* Prevenir desbordamiento */
        }
        
        .gjs-cell:hover .cell-controls {
            display: block !important;
        }
        
        .cell-controls {
            position: absolute;
            top: -10px;
            right: -10px;
            z-index: 40;
            display: none;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 6px;
            padding: 3px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .cell-controls button {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 3px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            margin: 1px;
            font-size: 10px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .cell-controls button:hover {
            background: #c82333;
            transform: scale(1.1);
        }
        
        .gjs-cell.focused {
            border: 2px solid #007bff !important;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            background-color: rgba(0, 123, 255, 0.05);
        }
        
        .gjs-row.active {
            border-color: #007bff !important;
            border-width: 2px !important;
            box-shadow: 0 0 0 1px rgba(0, 123, 255, 0.25);
        }
        
        .gjs-cell:hover {
            border-color: #007bff;
            background-color: rgba(0, 123, 255, 0.02);
        }
        
        .edu-element {
            margin: 15px 0;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #f9f9f9;
        }
        
        /* Estilos específicos para imágenes editables */
        .editable-image-container {
            position: relative;
            display: inline-block;
            margin: 15px;
            border: 2px dashed transparent;
            padding: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .editable-image-container:hover {
            border-color: #007bff !important;
        }
        
        .editable-image-container.selected {
            border-color: #007bff !important;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
        }
        
        .editable-image {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            cursor: pointer;
            display: block;
            transition: all 0.3s ease;
            user-select: none;
        }
        
        .image-controls {
            position: absolute;
            top: -10px;
            right: -10px;
            z-index: 20;
            display: none;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            padding: 5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .image-controls button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            width: 28px;
            height: 28px;
            cursor: pointer;
            margin: 2px;
            font-size: 12px;
            transition: all 0.2s ease;
        }
        
        .image-controls button:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .image-controls button.delete { background: #dc3545; }
        .image-controls button.resize { background: #28a745; }
        .image-controls button.move { background: #007bff; }
        
        .resize-handles {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
        }
        
        .resize-handle {
            position: absolute;
            width: 12px;
            height: 12px;
            background: #007bff;
            border: 2px solid white;
            border-radius: 50%;
            z-index: 15;
            pointer-events: auto;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .resize-handle:hover {
            background: #0056b3;
            transform: scale(1.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }
        
        .resize-handle.nw-resize {
            top: -6px;
            left: -6px;
            cursor: nw-resize;
        }
        
        .resize-handle.ne-resize {
            top: -6px;
            right: -6px;
            cursor: ne-resize;
        }
        
        .resize-handle.sw-resize {
            bottom: -6px;
            left: -6px;
            cursor: sw-resize;
        }
        
        .resize-handle.se-resize {
            bottom: -6px;
            right: -6px;
            cursor: se-resize;
        }
        
        .resize-handle.n-resize {
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            cursor: n-resize;
        }
        
        .resize-handle.s-resize {
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
            cursor: s-resize;
        }
        
        .resize-handle.w-resize {
            top: 50%;
            left: -6px;
            transform: translateY(-50%);
            cursor: w-resize;
        }
        
        .resize-handle.e-resize {
            top: 50%;
            right: -6px;
            transform: translateY(-50%);
            cursor: e-resize;
        }
        
        .image-info {
            position: absolute;
            bottom: -25px;
            left: 0;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            display: none;
            white-space: nowrap;
            z-index: 10;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .selection-indicator {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid #007bff;
            border-radius: 5px;
            display: none;
            pointer-events: none;
            z-index: 10;
            animation: pulse-border 2s infinite;
        }
        
        @keyframes pulse-border {
            0% {
                box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.4);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(0, 123, 255, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(0, 123, 255, 0);
            }
        }
        
        /* Mejoras para responsive */
        @media (max-width: 768px) {
            .editable-image-container {
                margin: 10px 5px;
            }
            
            .image-controls {
                top: -15px;
                right: -15px;
                padding: 8px;
            }
            
            .image-controls button {
                width: 32px;
                height: 32px;
                font-size: 14px;
            }
            
            .resize-handle {
                width: 16px;
                height: 16px;
            }
        }
        
        /* Estilos específicos para archivos editables */
        .editable-file-container {
            position: relative;
            margin: 15px 0;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: #f9f9f9;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .editable-file-container:hover {
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
        }
        
        .file-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            display: none;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 6px;
            padding: 5px;
            z-index: 10;
        }
        
        .file-controls button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            width: 30px;
            height: 30px;
            cursor: pointer;
            margin: 2px;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .file-controls button:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .file-controls button.download { background: #28a745; }
        .file-controls button.delete { background: #dc3545; }
        
        .file-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        
        .file-icon {
            font-size: 24px;
            margin-right: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .file-info h4 {
            margin: 0 0 5px 0;
            color: #333;
            font-size: 16px;
            font-weight: 600;
        }
        
        .file-meta {
            color: #666;
            font-size: 12px;
        }
        
        .file-preview {
            background: white;
            border-radius: 6px;
            padding: 15px;
            min-height: 100px;
        }
        
        .file-actions {
            margin-top: 15px;
            text-align: center;
        }
        
        .file-actions button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .file-actions button:hover {
            background: #0056b3;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }
        
        /* Estilos para previsualizaciones específicas */
        .image-preview img {
            max-width: 100%;
            max-height: 200px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .video-preview video {
            max-width: 100%;
            max-height: 200px;
            border-radius: 6px;
        }
        
        .audio-preview audio {
            width: 100%;
            max-width: 300px;
        }
        
        .text-preview pre {
            white-space: pre-wrap;
            margin: 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #333;
            max-height: 150px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        
        /* Responsive para archivos */
        @media (max-width: 768px) {
            .editable-file-container {
                margin: 10px 0;
                padding: 12px;
            }
            
            .file-controls {
                top: 5px;
                right: 5px;
                padding: 3px;
            }
            
            .file-controls button {
                width: 28px;
                height: 28px;
                font-size: 12px;
            }
            
            .file-icon {
                font-size: 20px;
                margin-right: 8px;
            }
            
            .file-info h4 {
                font-size: 14px;
            }
            
            .file-meta {
                font-size: 11px;
            }
        }
        
        /* Estilos para contenedores de multimedia responsivos */
        .responsive-media-container {
            max-width: 100%;
            box-sizing: border-box;
        }
        
        .responsive-media {
            max-width: 100% !important;
            height: auto !important;
            box-sizing: border-box;
        }
        
        /* Mejoras para celdas que contienen multimedia */
        .gjs-cell {
            min-height: 75px;
            flex-grow: 1;
            padding: 0 15px;
            position: relative;
            border: 1px dashed #eee;
            transition: all 0.3s ease;
            box-sizing: border-box;
            overflow: hidden; /* Prevenir desbordamiento */
        }
        
        .gjs-cell > * {
            max-width: 100%;
            box-sizing: border-box;
        }
        
        /* Estilos específicos para imágenes en columnas */
        .gjs-cell .editable-image-container {
            max-width: 100% !important;
            margin: 10px auto !important;
            display: block !important;
        }
        
        .gjs-cell .editable-image {
            max-width: 100% !important;
            width: 100% !important;
            height: auto !important;
        }
        
        /* Estilos para videos responsivos */
        .gjs-cell .responsive-media-container iframe {
            max-width: 100%;
            width: 100%;
        }
        
        /* Estilos para archivos en columnas */
        .gjs-cell .file-container {
            max-width: 100% !important;
            margin: 10px auto !important;
        }
        
        /* Responsive para diferentes tamaños de columna */
        .gjs-cell[style*="width: 33"] .editable-image-container,
        .gjs-cell[style*="width: 33"] .responsive-media-container {
            margin: 5px auto;
            padding: 3px;
        }
        
        .gjs-cell[style*="width: 50"] .editable-image-container,
        .gjs-cell[style*="width: 50"] .responsive-media-container {
            margin: 8px auto;
            padding: 5px;
        }
        
        /* Mejoras para prevenir overflow */
        .gjs-row {
            display: flex;
            justify-content: flex-start;
            align-items: stretch;
            flex-wrap: wrap;
            padding: 10px;
            margin: 0 0 10px 0;
            position: relative;
            border: 1px dashed #ddd;
            overflow: hidden; /* Prevenir desbordamiento horizontal */
        }
    `;
    document.head.appendChild(styleEl);
    
    console.log('Estilos del editor añadidos (incluyendo imágenes y archivos editables)');
}

// Función para insertar layouts
function insertLayout(type) {
    console.log('Insertando layout tipo:', type);
    
    const editor = document.getElementById('content-editor');
    if (!editor) {
        console.error('Editor no encontrado');
        return;
    }
    
    const layoutId = 'layout_' + Date.now(); // ID único para el layout
    let template = '';
    
    switch(type) {
        case '1':
            template = `
                <div class="gjs-row" onclick="focusOnColumn(this)" data-layout-id="${layoutId}">
                    <!-- Controles de fila -->
                    <div class="row-controls">
                        <button onclick="event.stopPropagation(); deleteRow(this)" title="Eliminar fila completa">×</button>
                    </div>
                    
                    <div class="gjs-cell" style="width: 100%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_1">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna única - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                </div>
            `;
            break;
        case '2':
            template = `
                <div class="gjs-row" onclick="focusOnColumn(this)" data-layout-id="${layoutId}">
                    <!-- Controles de fila -->
                    <div class="row-controls">
                        <button onclick="event.stopPropagation(); deleteRow(this)" title="Eliminar fila completa">×</button>
                    </div>
                    
                    <div class="gjs-cell" style="width: 50%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_1">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna 1 - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                    <div class="gjs-cell" style="width: 50%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_2">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna 2 - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                </div>
            `;
            break;
        case '3':
            template = `
                <div class="gjs-row" onclick="focusOnColumn(this)" data-layout-id="${layoutId}">
                    <!-- Controles de fila -->
                    <div class="row-controls">
                        <button onclick="event.stopPropagation(); deleteRow(this)" title="Eliminar fila completa">×</button>
                    </div>
                    
                    <div class="gjs-cell" style="width: 33.33%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_1">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                    </div>
                        <p>Columna 1 - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                    <div class="gjs-cell" style="width: 33.33%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_2">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna 2 - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                    <div class="gjs-cell" style="width: 33.33%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_3">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna 3 - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                </div>
            `;
            break;
        case '2-1':
            template = `
                <div class="gjs-row" onclick="focusOnColumn(this)" data-layout-id="${layoutId}">
                    <!-- Controles de fila -->
                    <div class="row-controls">
                        <button onclick="event.stopPropagation(); deleteRow(this)" title="Eliminar fila completa">×</button>
                    </div>
                    
                    <div class="gjs-cell" style="width: 66.66%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_1">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna principal (2/3) - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                    <div class="gjs-cell" style="width: 33.33%;" contenteditable="true" onclick="event.stopPropagation(); focusCell(this)" data-cell-id="${layoutId}_cell_2">
                        <!-- Controles de celda -->
                        <div class="cell-controls">
                            <button onclick="event.stopPropagation(); deleteCell(this)" title="Eliminar esta columna">×</button>
                        </div>
                        <p>Columna secundaria (1/3) - Haz clic aquí para escribir o insertar multimedia</p>
                    </div>
                </div>
            `;
            break;
    }
    
    if (template) {
        insertContentAtCursor(template);
        
        // Auto-enfocar la primera celda del layout recién creado
        setTimeout(() => {
            const newRows = document.querySelectorAll('.gjs-row');
            const lastRow = newRows[newRows.length - 1];
            if (lastRow) {
                const firstCell = lastRow.querySelector('.gjs-cell');
                if (firstCell) {
                    focusCell(firstCell);
                    console.log('✅ Layout insertado y primera celda auto-enfocada');
                }
            }
        }, 100);
        
        console.log('Layout insertado exitosamente con ID:', layoutId);
    }
}

// Función para enfocar en una celda específica (MEJORADA - SIN INTERFERIR CON EDICIÓN)
function focusCell(cell) {
    console.log('🎯 Enfocando en celda:', cell);
    
    // Verificar si el usuario está editando activamente
    const selection = window.getSelection();
    const isUserEditing = selection.rangeCount > 0 && 
                         selection.getRangeAt(0).collapsed === false;
    
    if (isUserEditing) {
        console.log('👤 Usuario editando activamente, no interferir con el cursor');
        // Solo establecer como activa sin mover el cursor
        activeCellContainer = cell;
        return;
    }
    
    // Remover focus anterior de todas las celdas
    const allCells = document.querySelectorAll('.gjs-cell');
    allCells.forEach(c => {
        c.classList.remove('focused');
        c.style.boxShadow = '';
        c.style.backgroundColor = '';
    });
    
    // Remover focus de filas
    const allRows = document.querySelectorAll('.gjs-row');
    allRows.forEach(r => {
        r.classList.remove('active');
        r.style.borderColor = '#ddd';
        r.style.borderWidth = '1px';
    });
    
    // Enfocar la celda actual
    cell.classList.add('focused');
    cell.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.25)';
    cell.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
    cell.style.borderColor = '#007bff';
    cell.style.borderWidth = '2px';
    
    // Establecer como celda activa globalmente
    activeCellContainer = cell;
    
    // Solo mover el cursor si NO hay una selección activa
    const currentSelection = window.getSelection();
    if (currentSelection.rangeCount === 0 || !cell.contains(currentSelection.focusNode)) {
        // El cursor no está en esta celda, es seguro moverlo
        cell.focus();
        
        // Mover el cursor al final solo si la celda está vacía o tiene contenido placeholder
        const cellContent = cell.textContent || '';
        if (cellContent.includes('Haz clic aquí para escribir') || cellContent.trim() === '') {
            try {
                const range = document.createRange();
                const sel = window.getSelection();
                range.selectNodeContents(cell);
                range.collapse(false);
                sel.removeAllRanges();
                sel.addRange(range);
            } catch (e) {
                console.log('No se pudo posicionar el cursor:', e);
            }
        }
    }
    
    // Resaltar visualmente la fila padre
    const parentRow = cell.closest('.gjs-row');
    if (parentRow) {
        parentRow.classList.add('active');
        parentRow.style.borderColor = '#007bff';
        parentRow.style.borderWidth = '2px';
    }
    
    // Mostrar indicador visual solo si no hay edición activa
    if (!isUserEditing) {
        showCellActiveIndicator(cell);
    }
    
    console.log('✅ Celda enfocada sin interferir con la edición');
}

// Nueva función para mostrar indicador visual de celda activa
function showCellActiveIndicator(cell) {
    // Remover indicadores previos
    const existingIndicators = document.querySelectorAll('.cell-active-indicator');
    existingIndicators.forEach(indicator => indicator.remove());
    
    // Crear nuevo indicador
    const indicator = document.createElement('div');
    indicator.className = 'cell-active-indicator';
    indicator.style.cssText = `
        position: absolute;
        top: -10px;
        right: -10px;
        background: #007bff;
        color: white;
        border-radius: 12px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: bold;
        z-index: 100;
        animation: pulse 2s infinite;
        pointer-events: none;
    `;
    indicator.textContent = '📍 Activa';
    
    // Agregar animación CSS si no existe
    if (!document.querySelector('#cell-indicator-style')) {
        const style = document.createElement('style');
        style.id = 'cell-indicator-style';
        style.textContent = `
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    cell.style.position = 'relative';
    cell.appendChild(indicator);
    
    // Remover el indicador después de 3 segundos
    setTimeout(() => {
        if (indicator && indicator.parentNode) {
            indicator.remove();
        }
    }, 3000);
}

// Función para enfocar en el contenedor de columnas (MEJORADA)
function focusOnColumn(row) {
    console.log('🎯 Enfocando en fila:', row);
    
    // Limpiar foco de otras filas
    const allRows = document.querySelectorAll('.gjs-row');
    allRows.forEach(r => {
        r.classList.remove('active');
        r.style.borderColor = '#ddd';
        r.style.borderWidth = '1px';
    });
    
    // Destacar visualmente la fila
    row.classList.add('active');
    row.style.borderColor = '#007bff';
    row.style.borderWidth = '2px';
    
    // Si no hay celda activa, activar la primera celda de esta fila
    if (!activeCellContainer || !row.contains(activeCellContainer)) {
        const firstCell = row.querySelector('.gjs-cell');
        if (firstCell) {
            focusCell(firstCell);
        }
    }
}

// Función mejorada para limpiar estado al hacer clic fuera
function clearActiveState() {
    console.log('🧹 Limpiando estado activo');
    
    // Limpiar celda activa
    activeCellContainer = null;
    
    // Remover estilos de todas las celdas
    const allCells = document.querySelectorAll('.gjs-cell');
    allCells.forEach(cell => {
        cell.classList.remove('focused');
        cell.style.boxShadow = '';
        cell.style.backgroundColor = '';
        cell.style.borderColor = '#eee';
        cell.style.borderWidth = '1px';
    });
    
    // Remover estilos de todas las filas
    const allRows = document.querySelectorAll('.gjs-row');
    allRows.forEach(row => {
        row.classList.remove('active');
        row.style.borderColor = '#ddd';
        row.style.borderWidth = '1px';
    });
    
    // Remover indicadores
    const indicators = document.querySelectorAll('.cell-active-indicator');
    indicators.forEach(indicator => indicator.remove());
}

// Función para insertar elementos multimedia
function insertMedia(type) {
    console.log('Insertando media tipo:', type);
    
    const editor = document.getElementById('content-editor');
    if (!editor) {
        console.error('Editor no encontrado');
        return;
    }
    
    // Verificar si estamos en una celda y obtener su ancho máximo
    const targetContainer = getCursorContainer();
    const isInCell = targetContainer && targetContainer.classList.contains('gjs-cell');
    const maxWidth = isInCell ? 'calc(100% - 30px)' : '100%'; // Restar padding de la celda
    
    console.log('📊 Contexto de inserción:', {
        'En celda': isInCell,
        'Contenedor': targetContainer,
        'Ancho máximo': maxWidth
    });
    
    let template = '';
    
    switch(type) {
        case 'image':
            // Crear input file para cargar imagen local
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.style.display = 'none';
            
            fileInput.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    // Verificar que sea una imagen
                    if (!file.type.startsWith('image/')) {
                        alert('Por favor selecciona un archivo de imagen válido.');
                        return;
                    }
                    
                    // Leer archivo como base64
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const imageId = 'img_' + Date.now(); // ID único para la imagen
                        
                        // Calcular ancho inicial apropiado para la celda
                        const initialWidth = isInCell ? '100%' : '300px';
                        
                        // Crear imagen responsiva adaptada a columnas
                        template = `
                            <div class="editable-image-container responsive-media-container" id="container_${imageId}" 
                                 style="position: relative; display: block; margin: 10px auto; max-width: ${maxWidth}; border: 2px dashed transparent; padding: 5px; cursor: pointer; text-align: center;"
                                 data-image-id="${imageId}"
                                 data-original-src="${e.target.result}"
                                 data-file-name="${file.name}"
                                 data-file-size="${(file.size / 1024).toFixed(1)}"
                                 onclick="selectEditableImage('${imageId}')">
                                
                                <!-- Imagen principal responsiva -->
                                <img id="${imageId}" 
                                     class="editable-image responsive-media"
                                     src="${e.target.result}" 
                                     alt="Imagen cargada" 
                                     style="max-width: 100%; height: auto; border-radius: 5px; width: ${initialWidth}; cursor: pointer; display: block; transition: all 0.3s ease; user-select: none;"
                                     data-width="${isInCell ? '100%' : '300'}"
                                     data-height="auto"
                                     ondragstart="return false;">
                                
                                <!-- Controles superiores -->
                                <div class="image-controls" style="position: absolute; top: -10px; right: -10px; z-index: 20; display: none; background: rgba(0,0,0,0.8); border-radius: 8px; padding: 5px;">
                                    <button onclick="event.stopPropagation(); deleteEditableImage('${imageId}')" 
                                            style="background: #dc3545; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 14px;" 
                                            title="Eliminar imagen">×</button>
                                    <button onclick="event.stopPropagation(); moveMediaUp('container_${imageId}')" 
                                            style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover arriba">↑</button>
                                    <button onclick="event.stopPropagation(); moveMediaDown('container_${imageId}')" 
                                            style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover abajo">↓</button>
                                    <button onclick="event.stopPropagation(); moveMediaToCell('container_${imageId}')" 
                                            style="background: #28a745; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover a otra celda">📂</button>
                                    <button onclick="event.stopPropagation(); promptImageResize('${imageId}')" 
                                            style="background: #6f42c1; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Redimensionar">⚏</button>
                                    <button onclick="event.stopPropagation(); toggleImageSize('${imageId}')" 
                                            style="background: #17a2b8; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Ajustar a columna">📐</button>
                                </div>
                                
                                <!-- Handles de redimensionamiento -->
                                <div class="resize-handles" style="display: none;">
                                    <!-- Esquina superior izquierda -->
                                    <div class="resize-handle nw-resize" 
                                         style="position: absolute; top: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; border: 2px solid white; border-radius: 50%; cursor: nw-resize; z-index: 15;"
                                         onmousedown="startImageResize(event, '${imageId}', 'nw')"></div>
                                    
                                    <!-- Esquina superior derecha -->
                                    <div class="resize-handle ne-resize" 
                                         style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; border: 2px solid white; border-radius: 50%; cursor: ne-resize; z-index: 15;"
                                         onmousedown="startImageResize(event, '${imageId}', 'ne')"></div>
                                    
                                    <!-- Esquina inferior izquierda -->
                                    <div class="resize-handle sw-resize" 
                                         style="position: absolute; bottom: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; border: 2px solid white; border-radius: 50%; cursor: sw-resize; z-index: 15;"
                                         onmousedown="startImageResize(event, '${imageId}', 'sw')"></div>
                                    
                                    <!-- Esquina inferior derecha -->
                                    <div class="resize-handle se-resize" 
                                         style="position: absolute; bottom: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; border: 2px solid white; border-radius: 50%; cursor: se-resize; z-index: 15;"
                                         onmousedown="startImageResize(event, '${imageId}', 'se')"></div>
                                </div>
                                
                                <!-- Información de la imagen -->
                                <div class="image-info" style="position: absolute; bottom: -25px; left: 0; background: rgba(0,0,0,0.8); color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; display: none; white-space: nowrap;">
                                    ${file.name} (${(file.size / 1024).toFixed(1)} KB) - <span id="size_${imageId}">${initialWidth} × auto</span>
                                </div>
                                
                                <!-- Indicador de selección -->
                                <div class="selection-indicator" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; border: 2px solid #007bff; border-radius: 5px; display: none; pointer-events: none; z-index: 10;"></div>
                            </div>
                        `;
                        
                        insertContentAtCursor(template);
                        
                        // Configurar eventos después de insertar
                        setTimeout(() => {
                            setupEditableImageEvents(imageId);
                            
                            // Si está en una celda, asegurar que la imagen se adapte
                            if (isInCell) {
                                adjustImageToColumn(imageId);
                            }
                        }, 100);
                        
                        console.log('✅ Imagen responsiva insertada exitosamente:', imageId, 'En celda:', isInCell);
                    };
                    
                    reader.readAsDataURL(file);
                }
            };
            
            // Simular click en el input file
            document.body.appendChild(fileInput);
            fileInput.click();
            document.body.removeChild(fileInput);
            break;
            
        case 'video':
            const videoUrl = prompt('Ingresa la URL del video (YouTube, Vimeo, etc.):');
            if (videoUrl) {
                const videoId = 'video_' + Date.now();
                template = `
                    <div class="edu-element responsive-media-container video-container" id="${videoId}" style="margin: 15px auto; max-width: ${maxWidth}; position: relative; border: 2px dashed transparent; padding: 10px; transition: all 0.3s ease;" 
                         onmouseover="showMediaControls('${videoId}')" 
                         onmouseout="hideMediaControls('${videoId}')"
                         onclick="selectMediaElement('${videoId}')">
                        
                        <!-- Controles de posicionamiento -->
                        <div class="media-controls" id="controls_${videoId}" style="position: absolute; top: -12px; right: -12px; z-index: 50; display: none; background: rgba(0, 0, 0, 0.8); border-radius: 8px; padding: 4px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
                            <button onclick="event.stopPropagation(); deleteMediaElement('${videoId}')" 
                                    style="background: #dc3545; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 14px;" 
                                    title="Eliminar video">×</button>
                            <button onclick="event.stopPropagation(); moveMediaUp('${videoId}')" 
                                    style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover arriba">↑</button>
                            <button onclick="event.stopPropagation(); moveMediaDown('${videoId}')" 
                                    style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover abajo">↓</button>
                            <button onclick="event.stopPropagation(); moveMediaToCell('${videoId}')" 
                                    style="background: #28a745; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover a otra celda">📂</button>
                        </div>
                        
                        <!-- Contenedor del video responsivo -->
                        <div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; border-radius: 8px; overflow: hidden; background: #f0f0f0;">
                            <iframe src="${videoUrl}" 
                                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 8px;" 
                                    frameborder="0" 
                                    allowfullscreen>
                            </iframe>
                        </div>
                        
                        <!-- Información del video -->
                        <div class="media-info" style="text-align: center; margin-top: 10px; padding: 8px; background: rgba(0, 123, 255, 0.1); border-radius: 6px;">
                            <p style="margin: 0; font-size: 12px; color: #0056b3; font-weight: 500;">📹 Video integrado</p>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; word-break: break-all;">${videoUrl}</p>
                        </div>
                        
                        <!-- Indicador de selección -->
                        <div class="selection-indicator" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; border: 3px solid #007bff; border-radius: 8px; display: none; pointer-events: none; z-index: 10; animation: pulse-border 2s infinite;"></div>
                    </div>
                `;
                insertContentAtCursor(template);
                
                console.log('✅ Video con controles insertado exitosamente:', videoId, 'En celda:', isInCell);
            }
            break;
            
        case 'audio':
            const audioUrl = prompt('Ingresa la URL del audio:');
            if (audioUrl) {
                const audioId = 'audio_' + Date.now();
                template = `
                    <div class="edu-element responsive-media-container audio-container" id="${audioId}" style="margin: 15px auto; max-width: ${maxWidth}; text-align: center; position: relative; border: 2px dashed transparent; padding: 10px; transition: all 0.3s ease;" 
                         onmouseover="showMediaControls('${audioId}')" 
                         onmouseout="hideMediaControls('${audioId}')"
                         onclick="selectMediaElement('${audioId}')">
                        
                        <!-- Controles de posicionamiento -->
                        <div class="media-controls" id="controls_${audioId}" style="position: absolute; top: -12px; right: -12px; z-index: 50; display: none; background: rgba(0, 0, 0, 0.8); border-radius: 8px; padding: 4px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
                            <button onclick="event.stopPropagation(); deleteMediaElement('${audioId}')" 
                                    style="background: #dc3545; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 14px;" 
                                    title="Eliminar audio">×</button>
                            <button onclick="event.stopPropagation(); moveMediaUp('${audioId}')" 
                                    style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover arriba">↑</button>
                            <button onclick="event.stopPropagation(); moveMediaDown('${audioId}')" 
                                    style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover abajo">↓</button>
                            <button onclick="event.stopPropagation(); moveMediaToCell('${audioId}')" 
                                    style="background: #28a745; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                    title="Mover a otra celda">📂</button>
                        </div>
                        
                        <!-- Contenedor del audio -->
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                            <div style="font-size: 48px; margin-bottom: 15px; color: #6f42c1;">🎵</div>
                            <audio controls style="width: 100%; max-width: 100%; border-radius: 6px;">
                                <source src="${audioUrl}" type="audio/mpeg">
                                Tu navegador no soporta audio HTML5.
                            </audio>
                        </div>
                        
                        <!-- Información del audio -->
                        <div class="media-info" style="margin-top: 10px; padding: 8px; background: rgba(111, 66, 193, 0.1); border-radius: 6px;">
                            <p style="margin: 0; font-size: 12px; color: #6f42c1; font-weight: 500;">🎵 Archivo de audio</p>
                            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; word-break: break-all;">${audioUrl}</p>
                        </div>
                        
                        <!-- Indicador de selección -->
                        <div class="selection-indicator" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; border: 3px solid #6f42c1; border-radius: 8px; display: none; pointer-events: none; z-index: 10; animation: pulse-border 2s infinite;"></div>
                    </div>
                `;
                insertContentAtCursor(template);
                
                console.log('✅ Audio con controles insertado exitosamente:', audioId, 'En celda:', isInCell);
            }
            break;
            
        case 'file':
            // [El código de file permanece igual pero se agregará la clase responsive-media-container]
            // Crear input file para cargar archivo local con previsualización
            const fileInputForFiles = document.createElement('input');
            fileInputForFiles.type = 'file';
            fileInputForFiles.accept = '*/*'; // Aceptar todos los tipos de archivo
            fileInputForFiles.style.display = 'none';
            
            fileInputForFiles.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    // Verificar tamaño del archivo (máximo 50MB)
                    if (file.size > 50 * 1024 * 1024) {
                        alert('El archivo es demasiado grande. Máximo permitido: 50MB');
                        return;
                    }
                    
                    const fileId = 'file_' + Date.now();
                    const fileName = file.name;
                    const fileSize = (file.size / 1024).toFixed(1);
                    const fileType = file.type || 'application/octet-stream';
                    const fileExtension = fileName.split('.').pop().toLowerCase();
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        const fileData = e.target.result;
                        
                        // Generar ícono del archivo basado en extension
                        const fileIcon = getFileIcon(fileExtension, fileType);
                        
                        // Generar previsualización del archivo
                        const previewContent = generateFilePreview(file, fileData, fileType, fileExtension);
                        
                        // Crear template con el archivo responsivo
                        template = `
                            <div class="file-container edu-element responsive-media-container" 
                                 id="${fileId}" 
                                 data-file-name="${fileName}"
                                 data-file-size="${fileSize}"
                                 data-file-type="${fileType}"
                                 data-file-extension="${fileExtension}"
                                 style="position: relative; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 15px auto; background: white; cursor: pointer; transition: all 0.3s ease; max-width: ${maxWidth};"
                                 onmouseover="showFileControls('${fileId}')"
                                 onmouseout="hideFileControls('${fileId}')">
                                
                                <!-- Controles del archivo -->
                                <div class="file-controls" style="position: absolute; top: -10px; right: -10px; z-index: 20; display: none; background: rgba(0,0,0,0.8); border-radius: 8px; padding: 5px;">
                                    <button onclick="event.stopPropagation(); deleteFile('${fileId}')" 
                                            style="background: #dc3545; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 14px;" 
                                            title="Eliminar archivo">×</button>
                                    <button onclick="event.stopPropagation(); moveMediaUp('${fileId}')" 
                                            style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover arriba">↑</button>
                                    <button onclick="event.stopPropagation(); moveMediaDown('${fileId}')" 
                                            style="background: #007bff; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover abajo">↓</button>
                                    <button onclick="event.stopPropagation(); moveMediaToCell('${fileId}')" 
                                            style="background: #28a745; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Mover a otra celda">📂</button>
                                    <button onclick="downloadFile('${fileId}')" 
                                            style="background: #17a2b8; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; margin: 2px; font-size: 12px;" 
                                            title="Descargar archivo">💾</button>
                                </div>
                                
                                <!-- Información del archivo -->
                                <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                                    <div style="font-size: 48px; flex-shrink: 0;">${fileIcon}</div>
                                    <div style="flex: 1; min-width: 150px;">
                                        <h4 style="margin: 0 0 5px 0; color: #333; font-size: 16px; font-weight: 600; word-break: break-word;">${fileName}</h4>
                                        <p style="margin: 0; color: #666; font-size: 14px;">Tamaño: ${fileSize} KB</p>
                                        <p style="margin: 5px 0 0 0; color: #666; font-size: 12px;">Tipo: ${fileType}</p>
                                    </div>
                                    <button onclick="downloadFile('${fileId}')" 
                                            style="background: #007bff; color: white; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 14px; flex-shrink: 0;" 
                                            title="Descargar archivo">
                                        ⬇️ Descargar
                                    </button>
                                </div>
                                
                                <!-- Previsualización -->
                                    ${previewContent}
                                
                                <!-- Datos del archivo (ocultos) -->
                                <script type="application/json" style="display: none;">
                                    {
                                        "fileName": "${fileName}",
                                        "fileSize": "${fileSize}",
                                        "fileType": "${fileType}",
                                        "fileExtension": "${fileExtension}",
                                        "fileData": "${fileData.replace(/"/g, '\\"')}"
                                    }
                                </script>
                            </div>
                        `;
                        
                        insertContentAtCursor(template);
                        console.log('✅ Archivo responsivo insertado exitosamente:', fileId);
                    };
                    
                        reader.readAsDataURL(file);
                }
            };
            
            // Simular click en el input file
            document.body.appendChild(fileInputForFiles);
            fileInputForFiles.click();
            document.body.removeChild(fileInputForFiles);
            break;
    }
    
    console.log('Función insertMedia completada para tipo:', type);
}

// Función para insertar elementos educativos
function insertEduElement(type) {
    console.log('Insertando elemento educativo tipo:', type);
    
    const editor = document.getElementById('content-editor');
    if (!editor) {
        console.error('Editor no encontrado');
        return;
    }
    
    let template = '';
    
    switch(type) {
        case 'quiz':
            template = `
                <div class="edu-element quiz-element">
                    <h3>Cuestionario</h3>
                    <div class="quiz-question">
                        <p><strong>Pregunta 1:</strong> Escribe aquí tu pregunta</p>
                        <div class="quiz-options">
                            <p><input type="radio" name="q1"> Opción 1</p>
                            <p><input type="radio" name="q1"> Opción 2</p>
                            <p><input type="radio" name="q1"> Opción 3</p>
                            <p><input type="radio" name="q1"> Opción 4</p>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="alert('Puedes personalizar esta función')">Comprobar respuestas</button>
                </div>
            `;
            break;
        case 'table':
            template = `
                <div class="edu-element table-element">
                    <table class="table table-bordered" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f8f9fa;">
                                <th style="border: 1px solid #ddd; padding: 8px;">Encabezado 1</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">Encabezado 2</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">Encabezado 3</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 1</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 2</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 3</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 4</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 5</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">Celda 6</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
            break;
        case 'card':
            template = `
                <div class="edu-element card-element">
                    <div class="card-header" style="background-color: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd;">
                        <h3>Título de la tarjeta</h3>
                    </div>
                    <div class="card-body" style="padding: 15px;">
                        <p>Contenido de la tarjeta. Puedes añadir texto, imágenes y otros elementos aquí.</p>
                    </div>
                    <div class="card-footer" style="background-color: #f8f9fa; padding: 15px; text-align: right; border-top: 1px solid #ddd;">
                        <small>Información adicional o pie de tarjeta</small>
                    </div>
                </div>
            `;
            break;
        case 'timeline':
            template = `
                <div class="edu-element timeline-element">
                    <h3>Línea de Tiempo</h3>
                    <div class="timeline-container" style="position: relative; padding-left: 30px;">
                        <div class="timeline-item" style="margin-bottom: 20px; position: relative;">
                            <div class="timeline-marker" style="position: absolute; left: -20px; top: 0; width: 12px; height: 12px; background: #0046CC; border-radius: 50%;"></div>
                            <div class="timeline-content">
                                <h4>Evento 1</h4>
                                <span class="timeline-date" style="color: #666; font-size: 14px;">2024</span>
                                <p>Descripción del primer evento en la línea de tiempo.</p>
                            </div>
                        </div>
                        <div class="timeline-item" style="margin-bottom: 20px; position: relative;">
                            <div class="timeline-marker" style="position: absolute; left: -20px; top: 0; width: 12px; height: 12px; background: #0046CC; border-radius: 50%;"></div>
                            <div class="timeline-content">
                                <h4>Evento 2</h4>
                                <span class="timeline-date" style="color: #666; font-size: 14px;">2025</span>
                                <p>Descripción del segundo evento en la línea de tiempo.</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'accordion':
            template = `
                <div class="edu-element accordion-element">
                    <h3>Preguntas Frecuentes</h3>
                    <div class="accordion-container">
                        <div class="accordion-item" style="border: 1px solid #ddd; margin-bottom: 5px;">
                            <div class="accordion-header" style="background: #f8f9fa; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0;">¿Pregunta frecuente 1?</h4>
                                <span class="accordion-icon">+</span>
                            </div>
                            <div class="accordion-content" style="padding: 15px; display: none;">
                                <p>Respuesta detallada a la primera pregunta frecuente. Puedes editar este texto según tus necesidades.</p>
                            </div>
                        </div>
                        <div class="accordion-item" style="border: 1px solid #ddd; margin-bottom: 5px;">
                            <div class="accordion-header" style="background: #f8f9fa; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0;">¿Pregunta frecuente 2?</h4>
                                <span class="accordion-icon">+</span>
                            </div>
                            <div class="accordion-content" style="padding: 15px; display: none;">
                                <p>Respuesta detallada a la segunda pregunta frecuente. Incluye toda la información necesaria.</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'callout':
            template = `
                <div class="edu-element callout-element callout-info" style="border-left: 4px solid #17a2b8; background-color: #d1ecf1; padding: 15px;">
                    <div class="callout-header" style="display: flex; align-items: center; margin-bottom: 10px;">
                        <i class="fas fa-info-circle" style="margin-right: 8px; color: #17a2b8;"></i>
                        <strong>Información Importante</strong>
                    </div>
                    <div class="callout-content">
                        <p>Este es un bloque de información destacada. Puedes cambiar el contenido editando directamente este texto.</p>
                    </div>
                </div>
            `;
            break;
        case 'progress':
            template = `
                <div class="edu-element progress-element">
                    <h3>Progreso del Curso</h3>
                    <div class="progress-container">
                        <div class="progress-item" style="margin-bottom: 15px;">
                            <div class="progress-label" style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Módulo 1: Introducción</span>
                                <span class="progress-percentage">100%</span>
                            </div>
                            <div class="progress-bar" style="background-color: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">
                                <div class="progress-fill" style="width: 100%; height: 100%; background-color: #28a745; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        <div class="progress-item" style="margin-bottom: 15px;">
                            <div class="progress-label" style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Módulo 2: Conceptos Básicos</span>
                                <span class="progress-percentage">75%</span>
                            </div>
                            <div class="progress-bar" style="background-color: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">
                                <div class="progress-fill" style="width: 75%; height: 100%; background-color: #ffc107; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'tabs':
            template = `
                <div class="edu-element tabs-element">
                    <h3>Contenido por Pestañas</h3>
                    <div class="tabs-container">
                        <div class="tabs-nav" style="display: flex; border-bottom: 1px solid #ddd; margin-bottom: 15px;">
                            <button class="tab-button active" style="padding: 10px 20px; border: none; background: #0046CC; color: white; cursor: pointer;">Pestaña 1</button>
                            <button class="tab-button" style="padding: 10px 20px; border: none; background: #f8f9fa; color: #333; cursor: pointer;">Pestaña 2</button>
                            <button class="tab-button" style="padding: 10px 20px; border: none; background: #f8f9fa; color: #333; cursor: pointer;">Pestaña 3</button>
                        </div>
                        <div class="tabs-content">
                            <div class="tab-pane active">
                                <p>Contenido de la primera pestaña. Puedes añadir cualquier tipo de contenido aquí.</p>
                            </div>
                            <div class="tab-pane" style="display: none;">
                                <p>Contenido de la segunda pestaña. Organiza tu información en secciones.</p>
                            </div>
                            <div class="tab-pane" style="display: none;">
                                <p>Contenido de la tercera pestaña. Ideal para categorizar información.</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'checklist':
            template = `
                <div class="edu-element checklist-element">
                    <h3>Lista de Tareas</h3>
                    <div class="checklist-container">
                        <div class="checklist-item" style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                            <input type="checkbox" style="margin-right: 10px; transform: scale(1.2);">
                            <span>Tarea 1: Revisar el material de estudio</span>
                        </div>
                        <div class="checklist-item" style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                            <input type="checkbox" style="margin-right: 10px; transform: scale(1.2);">
                            <span>Tarea 2: Completar los ejercicios prácticos</span>
                        </div>
                        <div class="checklist-item" style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                            <input type="checkbox" style="margin-right: 10px; transform: scale(1.2);">
                            <span>Tarea 3: Participar en el foro de discusión</span>
                        </div>
                    </div>
                </div>
            `;
            break;
    }
    
    if (template) {
        editor.innerHTML += template;
        console.log('Elemento educativo insertado exitosamente');
    }
}

// Configurar interceptor de guardado para limpiar contenido
function setupCleanSaveInterceptor() {
    console.log('Configurando interceptor de guardado...');
    
    // Interceptar formularios de guardado
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const originalSubmit = form.onsubmit;
        form.onsubmit = function(e) {
            console.log('Interceptando envío del formulario...');
            
            const contentEditor = document.getElementById('content-editor');
            if (contentEditor) {
                // Limpiar el contenido antes de enviarlo
                const cleanedContent = cleanContentForSave(contentEditor.innerHTML);
                
                // Buscar el campo de contenido y actualizarlo
                const contentField = form.querySelector('textarea[name="content"]') || 
                                   form.querySelector('input[name="content"]') ||
                                   form.querySelector('#id_content');
                
                if (contentField) {
                    contentField.value = cleanedContent;
                    console.log('Contenido limpiado y actualizado para guardado');
                }
            }
            
            if (originalSubmit) {
                return originalSubmit.call(this, e);
            }
        };
    });
    
    console.log('Interceptor de guardado configurado');
}

// Función para limpiar contenido antes del guardado
function cleanContentForSave(content) {
    console.log('Limpiando contenido para guardado...');
    
    // Crear un elemento temporal para manipular el DOM
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = content;
    
    // Preservar las clases importantes de GrapesJS
    const elementsToPreserve = tempDiv.querySelectorAll('.gjs-row, .gjs-cell, .edu-element');
    elementsToPreserve.forEach(element => {
        // Mantener las clases pero limpiar estilos innecesarios de edición
        if (element.classList.contains('gjs-row')) {
            element.style.position = 'relative';
            element.style.margin = '0 0 10px 0';
        }
        if (element.classList.contains('gjs-cell')) {
            element.style.position = 'relative';
        }
    });
    
    // Preservar las imágenes editables y sus propiedades esenciales
    const editableImages = tempDiv.querySelectorAll('.editable-image-container');
    editableImages.forEach(container => {
        const imageId = container.getAttribute('data-image-id');
        const originalSrc = container.getAttribute('data-original-src');
        const fileName = container.getAttribute('data-file-name');
        const fileSize = container.getAttribute('data-file-size');
        
        const image = container.querySelector('.editable-image');
        if (image && imageId) {
            // Preservar dimensiones actuales en los atributos de datos
            const currentWidth = image.offsetWidth || image.style.width || image.getAttribute('data-width');
            const currentHeight = image.offsetHeight || image.style.height || image.getAttribute('data-height');
            
            if (currentWidth) {
                image.setAttribute('data-width', currentWidth.toString().replace('px', ''));
            }
            if (currentHeight) {
                image.setAttribute('data-height', currentHeight.toString().replace('px', ''));
            }
            
            // Asegurar que se mantengan los atributos de datos esenciales
            if (originalSrc) container.setAttribute('data-original-src', originalSrc);
            if (fileName) container.setAttribute('data-file-name', fileName);
            if (fileSize) container.setAttribute('data-file-size', fileSize);
            
            console.log('Preservando imagen editable:', imageId, 'Dimensiones:', currentWidth, 'x', currentHeight);
        }
        
        // Eliminar elementos temporales de edición (controles, handles, etc.)
        const elementsToRemoveFromImage = container.querySelectorAll(
            '.image-controls, .resize-handles, .image-info, .selection-indicator'
        );
        elementsToRemoveFromImage.forEach(element => {
            element.style.display = 'none'; // No los eliminamos, solo los ocultamos
        });
        
        // Limpiar estilos temporales del contenedor
        container.style.border = '2px dashed transparent';
        container.style.padding = '5px';
        container.style.margin = '15px';
    });
    
    // Preservar los archivos editables y sus propiedades esenciales
    const editableFiles = tempDiv.querySelectorAll('.editable-file-container');
    editableFiles.forEach(container => {
        const fileId = container.getAttribute('data-file-id');
        const fileName = container.getAttribute('data-file-name');
        const fileSize = container.getAttribute('data-file-size');
        const fileType = container.getAttribute('data-file-type');
        const fileData = container.getAttribute('data-file-data');
        
        if (fileId) {
            // Asegurar que se mantengan todos los atributos de datos esenciales
            if (fileName) container.setAttribute('data-file-name', fileName);
            if (fileSize) container.setAttribute('data-file-size', fileSize);
            if (fileType) container.setAttribute('data-file-type', fileType);
            if (fileData) {
                // Preservar los datos del archivo asegurándose de que estén completos
                container.setAttribute('data-file-data', fileData);
                console.log('Preservando datos del archivo:', fileId, 'Tamaño de datos:', fileData.length);
            }
            
            // Preservar eventos de hover como atributos HTML
            container.setAttribute('onmouseover', `showFileControls('${fileId}')`);
            container.setAttribute('onmouseout', `hideFileControls('${fileId}')`);
            
            console.log('Preservando archivo editable:', fileId, 'Archivo:', fileName, 'Datos presentes:', !!fileData);
        }
        
        // Ocultar controles temporales de edición pero mantener su estructura
        const fileControls = container.querySelector('.file-controls');
        if (fileControls) {
            fileControls.style.display = 'none';
            
            // Asegurar que los botones mantengan sus eventos como atributos
            const downloadButtons = fileControls.querySelectorAll('button[onclick*="downloadFile"]');
            downloadButtons.forEach(button => {
                button.setAttribute('onclick', `downloadFile('${fileId}')`);
            });
            
            const deleteButtons = fileControls.querySelectorAll('button[onclick*="deleteFile"]');
            deleteButtons.forEach(button => {
                button.setAttribute('onclick', `deleteFile('${fileId}')`);
            });
        }
        
        // Mantener botones de descarga principales
        const mainDownloadButtons = container.querySelectorAll('.file-actions button[onclick*="downloadFile"]');
        mainDownloadButtons.forEach(button => {
            button.setAttribute('onclick', `downloadFile('${fileId}')`);
        });
        
        // Limpiar estilos temporales del contenedor
        container.style.borderColor = '#e0e0e0';
        container.style.boxShadow = 'none';
    });
    
    // Eliminar elementos de ayuda visual que no deben guardarse
    const elementsToRemove = tempDiv.querySelectorAll('.row-actions, .cell-actions, .gjs-toolbar, .gjs-resizer');
    elementsToRemove.forEach(element => element.remove());
    
    // Limpiar event handlers inline que pueden causar problemas al cargar
    const elementsWithInlineEvents = tempDiv.querySelectorAll('[onclick], [onmousedown], [ondragstart]');
    elementsWithInlineEvents.forEach(element => {
        // Preservar solo los eventos esenciales para las imágenes editables
        if (element.closest('.editable-image-container')) {
            if (element.classList.contains('editable-image-container')) {
                // Preservar el evento de selección de imagen
                const imageId = element.getAttribute('data-image-id');
                if (imageId) {
                    element.setAttribute('onclick', `selectEditableImage('${imageId}')`);
                }
            } else if (element.classList.contains('resize-handle')) {
                // Preservar eventos de handles de redimensionamiento
                // (ya están configurados en el HTML)
            } else {
                // Limpiar otros eventos inline
                element.removeAttribute('onclick');
                element.removeAttribute('onmousedown');
                element.removeAttribute('ondragstart');
            }
        } else {
            // Eliminar eventos inline de elementos no relacionados con imágenes
            element.removeAttribute('onclick');
            element.removeAttribute('onmousedown');
            element.removeAttribute('ondragstart');
        }
    });
    
    console.log('Contenido limpiado exitosamente, propiedades de imágenes editables preservadas');
    return tempDiv.innerHTML;
}

// ============ FUNCIONES AVANZADAS PARA MANEJO DE IMÁGENES ============

// Variables globales para el manejo de imágenes y celdas activas
let selectedImageId = null;
let isResizing = false;
let resizeData = null;
let activeCellContainer = null; // Nueva variable para trackear la celda activa

// Configurar eventos para una imagen editable
function setupEditableImageEvents(imageId) {
    console.log('Configurando eventos para imagen:', imageId);
    
    const container = document.getElementById(`container_${imageId}`);
    const image = document.getElementById(imageId);
    
    if (!container || !image) {
        console.error('Contenedor o imagen no encontrados:', imageId);
        return;
    }
    
    // Eventos de hover para mostrar controles e información
    container.addEventListener('mouseenter', function() {
        if (!isResizing) {
            this.style.border = '2px dashed #007bff';
            this.querySelector('.image-controls').style.display = 'block';
            this.querySelector('.image-info').style.display = 'block';
        }
    });
    
    container.addEventListener('mouseleave', function() {
        if (!isResizing && selectedImageId !== imageId) {
            this.style.border = '2px dashed transparent';
            this.querySelector('.image-controls').style.display = 'none';
            this.querySelector('.image-info').style.display = 'none';
        }
    });
    
    // Configurar drag and drop entre elementos
    container.draggable = true;
    container.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', imageId);
        e.dataTransfer.effectAllowed = 'move';
    });
    
    container.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    container.addEventListener('drop', function(e) {
        e.preventDefault();
        const draggedImageId = e.dataTransfer.getData('text/plain');
        if (draggedImageId !== imageId) {
            swapImages(draggedImageId, imageId);
        }
    });
    
    console.log('Eventos configurados para imagen:', imageId);
}

// Seleccionar una imagen para edición
function selectEditableImage(imageId) {
    console.log('Seleccionando imagen:', imageId);
    
    // Deseleccionar imagen anterior
    if (selectedImageId && selectedImageId !== imageId) {
        deselectImage(selectedImageId);
    }
    
    selectedImageId = imageId;
    const container = document.getElementById(`container_${imageId}`);
    
    if (container) {
        // Mostrar indicadores de selección
        container.style.border = '2px solid #007bff';
        container.querySelector('.image-controls').style.display = 'block';
        container.querySelector('.image-info').style.display = 'block';
        container.querySelector('.selection-indicator').style.display = 'block';
        container.querySelector('.resize-handles').style.display = 'block';
        
        console.log('Imagen seleccionada:', imageId);
    }
}

// Deseleccionar una imagen
function deselectImage(imageId) {
    const container = document.getElementById(`container_${imageId}`);
    
    if (container) {
        container.style.border = '2px dashed transparent';
        container.querySelector('.image-controls').style.display = 'none';
        container.querySelector('.image-info').style.display = 'none';
        container.querySelector('.selection-indicator').style.display = 'none';
        container.querySelector('.resize-handles').style.display = 'none';
    }
}

// Iniciar redimensionamiento con handles
function startImageResize(event, imageId, direction) {
    console.log('Iniciando redimensionamiento:', imageId, direction);
    
    event.preventDefault();
    event.stopPropagation();
    
    isResizing = true;
    const image = document.getElementById(imageId);
    const container = document.getElementById(`container_${imageId}`);
    
    if (!image || !container) {
        console.error('Imagen o contenedor no encontrados:', imageId);
        return;
    }
    
    // Obtener dimensiones iniciales
    const rect = image.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    
    resizeData = {
        imageId: imageId,
        direction: direction,
        startX: event.clientX,
        startY: event.clientY,
        startWidth: rect.width,
        startHeight: rect.height,
        aspectRatio: rect.width / rect.height,
        image: image,
        container: container
    };
    
    // Añadir listeners globales
    document.addEventListener('mousemove', handleImageResize);
    document.addEventListener('mouseup', stopImageResize);
    
    // Prevenir selección de texto
    document.body.style.userSelect = 'none';
    document.body.style.cursor = getResizeCursor(direction);
    
    console.log('Redimensionamiento iniciado');
}

// Manejar redimensionamiento
function handleImageResize(event) {
    if (!isResizing || !resizeData) return;
    
    const deltaX = event.clientX - resizeData.startX;
    const deltaY = event.clientY - resizeData.startY;
    
    let newWidth = resizeData.startWidth;
    let newHeight = resizeData.startHeight;
    
    // Calcular nuevas dimensiones según la dirección
    switch(resizeData.direction) {
        case 'se': // Esquina inferior derecha
            newWidth = resizeData.startWidth + deltaX;
            newHeight = resizeData.startHeight + deltaY;
            break;
        case 'sw': // Esquina inferior izquierda
            newWidth = resizeData.startWidth - deltaX;
            newHeight = resizeData.startHeight + deltaY;
            break;
        case 'ne': // Esquina superior derecha
            newWidth = resizeData.startWidth + deltaX;
            newHeight = resizeData.startHeight - deltaY;
            break;
        case 'nw': // Esquina superior izquierda
            newWidth = resizeData.startWidth - deltaX;
            newHeight = resizeData.startHeight - deltaY;
            break;
        case 'e': // Lado derecho
            newWidth = resizeData.startWidth + deltaX;
            newHeight = newWidth / resizeData.aspectRatio;
            break;
        case 'w': // Lado izquierdo
            newWidth = resizeData.startWidth - deltaX;
            newHeight = newWidth / resizeData.aspectRatio;
            break;
        case 'n': // Lado superior
            newHeight = resizeData.startHeight - deltaY;
            newWidth = newHeight * resizeData.aspectRatio;
            break;
        case 's': // Lado inferior
            newHeight = resizeData.startHeight + deltaY;
            newWidth = newHeight * resizeData.aspectRatio;
            break;
    }
    
    // Mantener proporciones si se mantiene presionada la tecla Shift
    if (event.shiftKey) {
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            newHeight = newWidth / resizeData.aspectRatio;
        } else {
            newWidth = newHeight * resizeData.aspectRatio;
        }
    }
    
    // Aplicar límites mínimos y máximos
    newWidth = Math.max(50, Math.min(newWidth, 1200));
    newHeight = Math.max(30, Math.min(newHeight, 800));
    
    // Aplicar nuevas dimensiones
    resizeData.image.style.width = newWidth + 'px';
    resizeData.image.style.height = newHeight + 'px';
    
    // Actualizar datos almacenados
    resizeData.image.setAttribute('data-width', newWidth);
    resizeData.image.setAttribute('data-height', newHeight);
    
    // Actualizar información visual
    updateImageSizeInfo(resizeData.imageId, newWidth, newHeight);
}

// Finalizar redimensionamiento
function stopImageResize(event) {
    if (!isResizing) return;
    
    console.log('Finalizando redimensionamiento');
    
    isResizing = false;
    
    // Remover listeners globales
    document.removeEventListener('mousemove', handleImageResize);
    document.removeEventListener('mouseup', stopImageResize);
    
    // Restaurar estilos del cursor y selección
    document.body.style.userSelect = '';
    document.body.style.cursor = '';
    
    // Limpiar datos de redimensionamiento
    resizeData = null;
    
    console.log('Redimensionamiento finalizado');
}

// Obtener cursor apropiado para la dirección de redimensionamiento
function getResizeCursor(direction) {
    const cursors = {
        'nw': 'nw-resize',
        'ne': 'ne-resize',
        'sw': 'sw-resize',
        'se': 'se-resize',
        'n': 'n-resize',
        's': 's-resize',
        'e': 'e-resize',
        'w': 'w-resize'
    };
    return cursors[direction] || 'default';
}

// Actualizar información del tamaño de la imagen
function updateImageSizeInfo(imageId, width, height) {
    const sizeSpan = document.getElementById(`size_${imageId}`);
    if (sizeSpan) {
        sizeSpan.textContent = `${Math.round(width)}px × ${Math.round(height)}px`;
    }
}

// Prompt para redimensionar imagen con valores específicos
function promptImageResize(imageId) {
    console.log('Redimensionamiento por prompt:', imageId);
    
    const image = document.getElementById(imageId);
    if (!image) {
        console.error('Imagen no encontrada:', imageId);
        return;
    }
    
    const currentWidth = image.offsetWidth;
    const currentHeight = image.offsetHeight;
    
    const newWidth = prompt(`Ancho actual: ${currentWidth}px\nIngresa el nuevo ancho (en píxeles):`, currentWidth);
    if (newWidth === null) return; // Usuario canceló
    
    const newHeight = prompt(`Alto actual: ${currentHeight}px\nIngresa el nuevo alto (en píxeles, o 'auto' para mantener proporciones):`, 'auto');
    if (newHeight === null) return; // Usuario canceló
    
    // Validar y aplicar nuevas dimensiones
    const width = parseInt(newWidth);
    if (isNaN(width) || width < 10) {
        alert('Por favor ingresa un ancho válido (mínimo 10px).');
        return;
    }
    
    let height;
    if (newHeight === 'auto') {
        const aspectRatio = currentWidth / currentHeight;
        height = width / aspectRatio;
    } else {
        height = parseInt(newHeight);
        if (isNaN(height) || height < 10) {
            alert('Por favor ingresa un alto válido (mínimo 10px) o "auto".');
            return;
        }
    }
    
    // Aplicar nuevas dimensiones
    image.style.width = width + 'px';
    image.style.height = height + 'px';
    
    // Actualizar atributos de datos
    image.setAttribute('data-width', width);
    image.setAttribute('data-height', height);
    
    // Actualizar información visual
    updateImageSizeInfo(imageId, width, height);
    
    console.log('Imagen redimensionada:', imageId, width, height);
}

// Eliminar imagen editable
function deleteEditableImage(imageId) {
    console.log('Eliminando imagen:', imageId);
    
    if (confirm('¿Estás seguro de que quieres eliminar esta imagen?')) {
        const container = document.getElementById(`container_${imageId}`);
        if (container) {
            container.remove();
            
            // Limpiar estado si era la imagen seleccionada
            if (selectedImageId === imageId) {
                selectedImageId = null;
            }
            
            console.log('Imagen eliminada:', imageId);
        }
    }
}

// Mover imagen hacia arriba
function moveImageUp(containerId) {
    console.log('Moviendo imagen arriba:', containerId);
    
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const prevElement = container.previousElementSibling;
    if (prevElement) {
        container.parentNode.insertBefore(container, prevElement);
        console.log('Imagen movida arriba');
    }
}

// Mover imagen hacia abajo
function moveImageDown(containerId) {
    console.log('Moviendo imagen abajo:', containerId);
    
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const nextElement = container.nextElementSibling;
    if (nextElement) {
        container.parentNode.insertBefore(nextElement, container);
        console.log('Imagen movida abajo');
    }
}

// Intercambiar posiciones de dos imágenes
function swapImages(imageId1, imageId2) {
    console.log('Intercambiando imágenes:', imageId1, imageId2);
    
    const container1 = document.getElementById(`container_${imageId1}`);
    const container2 = document.getElementById(`container_${imageId2}`);
    
    if (!container1 || !container2) return;
    
    // Crear un marcador temporal
    const tempMarker = document.createElement('div');
    
    // Insertar marcador antes del segundo contenedor
    container2.parentNode.insertBefore(tempMarker, container2);
    
    // Mover primer contenedor al lugar del segundo
    container1.parentNode.insertBefore(container2, container1);
    
    // Mover segundo contenedor al lugar del marcador
    tempMarker.parentNode.insertBefore(container1, tempMarker);
    
    // Remover marcador temporal
    tempMarker.remove();
    
    console.log('Imágenes intercambiadas');
}

// Restaurar imágenes editables desde contenido guardado
function restoreEditableImages() {
    console.log('Restaurando imágenes editables...');
    
    const editor = document.getElementById('content-editor');
    if (!editor) return;
    
    // Buscar todas las imágenes que tienen los atributos de datos
    const editableContainers = editor.querySelectorAll('.editable-image-container');
    
    editableContainers.forEach(container => {
        const imageId = container.getAttribute('data-image-id');
        if (imageId) {
            console.log('Restaurando imagen editable:', imageId);
            
            // Agregar clase responsiva si no la tiene
            if (!container.classList.contains('responsive-media-container')) {
                container.classList.add('responsive-media-container');
            }
            
            // Configurar eventos
            setupEditableImageEvents(imageId);
            
            // Restaurar dimensiones desde los atributos de datos y aplicar responsividad
            const image = container.querySelector('.editable-image');
            if (image) {
                // Agregar clase responsiva si no la tiene
                if (!image.classList.contains('responsive-media')) {
                    image.classList.add('responsive-media');
                }
                
                const width = image.getAttribute('data-width');
                const height = image.getAttribute('data-height');
                
                // Verificar si está en una celda y ajustar automáticamente
                const parentCell = container.closest('.gjs-cell');
                if (parentCell) {
                    console.log('📐 Imagen en celda detectada, aplicando ajuste responsivo:', imageId);
                    
                    // Forzar estilos responsivos
                    container.style.maxWidth = 'calc(100% - 30px)';
                    container.style.margin = '10px auto';
                    container.style.display = 'block';
                    container.style.textAlign = 'center';
                    
                    image.style.maxWidth = '100%';
                    image.style.width = '100%';
                    image.style.height = 'auto';
                    
                    // Actualizar atributos
                    image.setAttribute('data-width', '100%');
                    image.setAttribute('data-height', 'auto');
                    
                    // Actualizar información visual
                    updateImageSizeInfo(imageId, '100%', 'auto');
                } else if (width && height) {
                    // Si no está en celda, usar dimensiones guardadas
                    updateImageSizeInfo(imageId, parseInt(width), parseInt(height));
                }
            }
        }
    });
    
    console.log('✅ Imágenes editables restauradas y ajustadas responsivamente');
}

// Deseleccionar imagen al hacer clic fuera
document.addEventListener('click', function(event) {
    // Verificar si el usuario está editando texto activamente
    const isEditingText = document.activeElement && 
                         (document.activeElement.contentEditable === 'true' || 
                          document.activeElement.tagName === 'INPUT' || 
                          document.activeElement.tagName === 'TEXTAREA');
    
    if (isEditingText) {
        console.log('👤 Usuario editando texto, no interferir con eventos de clic');
        return; // No interferir cuando el usuario está editando
    }
    
    // Manejar selección de imágenes
    if (selectedImageId && !event.target.closest('.editable-image-container')) {
        deselectImage(selectedImageId);
        selectedImageId = null;
    }
    
    // Manejar selección de celdas solo si no se está editando
    const clickedCell = event.target.closest('.gjs-cell');
    const clickedRow = event.target.closest('.gjs-row');
    const clickedEditor = event.target.closest('#content-editor');
    
    // Verificar si el clic fue en un control de interfaz (botones, etc.)
    const isControlElement = event.target.closest('button, .image-controls, .cell-controls, .row-controls, .editor-toolbar-vertical');
    
    if (isControlElement) {
        console.log('🎛️ Clic en elemento de control, procesando normalmente');
        return; // Permitir que los controles funcionen normalmente
    }
    
    if (clickedCell) {
        // Se hizo clic en una celda
        // Solo enfocar si no es un clic para editar texto
        const isTextEditingClick = event.target.nodeType === Node.TEXT_NODE || 
                                  (event.target.tagName && 
                                   ['P', 'SPAN', 'DIV', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(event.target.tagName));
        
        if (!isTextEditingClick) {
            event.stopPropagation();
            focusCell(clickedCell);
            console.log('🎯 Celda seleccionada por clic (no de edición):', clickedCell);
        } else {
            // Solo establecer como activa sin mover cursor
            activeCellContainer = clickedCell;
            console.log('📝 Clic para editar texto, solo estableciendo celda activa');
        }
    } else if (clickedRow && !isTextEditingClick) {
        // Se hizo clic en una fila pero no en una celda específica
        focusOnColumn(clickedRow);
        console.log('🎯 Fila seleccionada por clic:', clickedRow);
    } else if (clickedEditor) {
        // Se hizo clic en el editor pero fuera de las columnas
        if (!event.target.closest('.gjs-row') && !isTextEditingClick) {
            clearActiveState();
            console.log('🧹 Clic fuera de columnas, limpiando estado');
        }
    } else if (!event.target.closest('.editor-toolbar-vertical')) {
        // Se hizo clic completamente fuera del editor y no en la toolbar
        clearActiveState();
        console.log('🧹 Clic completamente fuera, limpiando estado');
    }
});

// Mejorar la detección de focus en celdas
document.addEventListener('focusin', function(event) {
    // Solo procesar si el elemento enfocado es una celda editable
    const focusedCell = event.target.closest('.gjs-cell');
    if (focusedCell && focusedCell !== activeCellContainer) {
        // Verificar si es un focus natural del usuario (no programático)
        const isNaturalFocus = event.target === focusedCell || 
                              focusedCell.contains(event.target);
        
        if (isNaturalFocus) {
            // Solo establecer como activa, no mover cursor
            activeCellContainer = focusedCell;
            
            // Aplicar estilos visuales sin interferir con la edición
            const allCells = document.querySelectorAll('.gjs-cell');
            allCells.forEach(c => {
                c.classList.remove('focused');
                c.style.boxShadow = '';
                c.style.backgroundColor = '';
            });
            
            focusedCell.classList.add('focused');
            focusedCell.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.25)';
            focusedCell.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
            
            console.log('🎯 Celda enfocada naturalmente por el usuario:', focusedCell);
        }
    }
});

// Función de debug mejorada
window.debugResponsiveMedia = function() {
    console.log('🔍 DEBUG MULTIMEDIA RESPONSIVO');
    
    const editor = document.getElementById('content-editor');
    if (!editor) {
        console.error('❌ Editor no encontrado');
        return;
    }
    
    const cells = editor.querySelectorAll('.gjs-cell');
    const mediaContainers = editor.querySelectorAll('.responsive-media-container');
    const images = editor.querySelectorAll('.responsive-media');
    
    console.log('📊 Estadísticas:');
    console.log('- Celdas:', cells.length);
    console.log('- Contenedores multimedia responsivos:', mediaContainers.length);
    console.log('- Elementos multimedia responsivos:', images.length);
    
    cells.forEach((cell, index) => {
        const cellMedia = cell.querySelectorAll('.responsive-media-container');
        console.log(`--- Celda ${index + 1} ---`);
        console.log('Ancho de celda:', cell.style.width);
        console.log('Elementos multimedia:', cellMedia.length);
        
        cellMedia.forEach((media, mediaIndex) => {
            console.log(`  Multimedia ${mediaIndex + 1}:`);
            console.log(`    Max-width: ${media.style.maxWidth}`);
            console.log(`    Margin: ${media.style.margin}`);
            console.log(`    Display: ${media.style.display}`);
        });
    });
    
    console.log('✅ Debug completado');
};

console.log('✅ Sistema multimedia responsivo cargado');
console.log('📱 Función de debug disponible: debugResponsiveMedia()');
console.log('🔧 El multimedia ahora se adapta automáticamente a las columnas');

// Función para insertar contenido en la posición del cursor o al final (MEJORADA)
function insertContentAtCursor(htmlContent) {
    console.log('📝 Insertando contenido...', htmlContent.substring(0, 50) + '...');
    
    // Verificar si hay una selección/cursor activo
    const selection = window.getSelection();
    const hasActiveSelection = selection.rangeCount > 0;
    
    if (hasActiveSelection) {
        const range = selection.getRangeAt(0);
        const selectedContainer = range.commonAncestorContainer;
        
        // Buscar si la selección está dentro de una celda
        let parentCell = selectedContainer.nodeType === Node.TEXT_NODE 
                        ? selectedContainer.parentElement 
                        : selectedContainer;
        
        while (parentCell && !parentCell.classList.contains('gjs-cell') && parentCell.id !== 'content-editor') {
            parentCell = parentCell.parentElement;
        }
        
        if (parentCell && parentCell.classList.contains('gjs-cell')) {
            console.log('✅ Insertando en la posición del cursor dentro de celda:', parentCell);
            
            // Insertar en la posición exacta del cursor
            try {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlContent;
                
                // Insertar cada nodo del contenido
                while (tempDiv.firstChild) {
                    range.insertNode(tempDiv.firstChild);
                }
                
                // Mover el cursor después del contenido insertado
                range.collapse(false);
                selection.removeAllRanges();
                selection.addRange(range);
                
                return;
            } catch (error) {
                console.warn('No se pudo insertar en la posición del cursor, usando método alternativo:', error);
            }
        }
    }
    
    // Método alternativo: usar contenedor detectado o celda activa
    const container = getCursorContainer();
    
    if (container && container.classList && container.classList.contains('gjs-cell')) {
        console.log('✅ Insertando contenido en celda activa:', container);
        
        // Verificar si la celda tiene contenido placeholder
        if (container.innerHTML.includes('Haz clic aquí para escribir o insertar multimedia')) {
            container.innerHTML = htmlContent;
        } else {
            // Intentar insertar en la posición actual del cursor si es posible
            const currentSelection = window.getSelection();
            if (currentSelection.rangeCount > 0 && container.contains(currentSelection.focusNode)) {
                try {
                    const range = currentSelection.getRangeAt(0);
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = htmlContent;
                    
                    while (tempDiv.firstChild) {
                        range.insertNode(tempDiv.firstChild);
                    }
                    
                    range.collapse(false);
                    currentSelection.removeAllRanges();
                    currentSelection.addRange(range);
                    
                    console.log('✅ Contenido insertado en posición del cursor');
                    return;
                } catch (error) {
                    console.warn('Inserción en cursor falló, agregando al final:', error);
                }
            }
            
            // Si no se puede insertar en cursor, agregar al final
            container.innerHTML += htmlContent;
        }
        
        // NO mover el cursor automáticamente después de insertar
        console.log('📍 Manteniendo posición del cursor después de inserción');
        
    } else {
        // Insertar al final del editor principal
        const editor = document.getElementById('content-editor');
        if (editor) {
            console.log('⚠️ Insertando contenido al final del editor (no hay celda activa)');
            editor.innerHTML += htmlContent;
        }
    }
}

// Función para preservar la posición del cursor durante actualizaciones
function preserveCursorPosition(callback) {
    const selection = window.getSelection();
    let cursorInfo = null;
    
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const container = range.commonAncestorContainer;
        
        // Guardar información del cursor
        cursorInfo = {
            container: container,
            startOffset: range.startOffset,
            endOffset: range.endOffset,
            collapsed: range.collapsed
        };
        
        console.log('💾 Guardando posición del cursor:', cursorInfo);
    }
    
    // Ejecutar el callback
    if (typeof callback === 'function') {
        callback();
    }
    
    // Restaurar posición del cursor si es posible
    if (cursorInfo && cursorInfo.container && cursorInfo.container.parentNode) {
        try {
            const newRange = document.createRange();
            newRange.setStart(cursorInfo.container, Math.min(cursorInfo.startOffset, cursorInfo.container.length || 0));
            newRange.setEnd(cursorInfo.container, Math.min(cursorInfo.endOffset, cursorInfo.container.length || 0));
            
            const newSelection = window.getSelection();
            newSelection.removeAllRanges();
            newSelection.addRange(newRange);
            
            console.log('✅ Posición del cursor restaurada');
        } catch (error) {
            console.warn('No se pudo restaurar la posición del cursor:', error);
        }
    }
}

// Función para prevenir el scroll automático al final
function preventAutoScroll() {
    const editor = document.getElementById('content-editor');
    if (!editor) return;
    
    // Guardar posición de scroll actual
    const scrollTop = editor.scrollTop;
    const scrollLeft = editor.scrollLeft;
    
    // Restaurar después de cualquier actualización
    setTimeout(() => {
        if (editor.scrollTop !== scrollTop || editor.scrollLeft !== scrollLeft) {
            editor.scrollTop = scrollTop;
            editor.scrollLeft = scrollLeft;
            console.log('📍 Posición de scroll restaurada');
        }
    }, 0);
}

// Mejorar el contador de palabras sin interferir con la edición
function updateWordCountSafely() {
    preserveCursorPosition(() => {
        const editor = document.getElementById('content-editor');
        if (editor) {
            const text = editor.innerText || '';
            const words = text.trim().split(/\s+/).filter(word => word.length > 0);
            const wordCount = document.getElementById('word-count');
            if (wordCount) {
                wordCount.textContent = words.length + ' palabras';
            }
        }
    });
}

// Función de debug para problemas de cursor
window.debugCursorIssues = function() {
    console.log('🔍 DEBUG PROBLEMAS DE CURSOR');
    
    const selection = window.getSelection();
    const editor = document.getElementById('content-editor');
    
    console.log('📊 Estado actual:');
    console.log('- Selección activa:', selection.rangeCount > 0);
    console.log('- Elemento activo:', document.activeElement);
    console.log('- Es editable:', document.activeElement ? document.activeElement.contentEditable : 'N/A');
    console.log('- Celda activa:', activeCellContainer ? activeCellContainer.id || 'Sin ID' : 'Ninguna');
    
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        console.log('- Posición del cursor:', range.startOffset, 'a', range.endOffset);
        console.log('- Contenedor del cursor:', range.commonAncestorContainer);
        console.log('- En celda:', !!range.commonAncestorContainer.closest?.('.gjs-cell'));
    }
    
    if (editor) {
        console.log('- Scroll del editor:', editor.scrollTop, editor.scrollLeft);
    }
    
    console.log('✅ Debug de cursor completado');
};

console.log('🔧 Funciones de preservación de cursor cargadas');
console.log('📍 Función de debug disponible: debugCursorIssues()');
console.log('✅ Los problemas de cursor jumping deberían estar solucionados');

// ============ FUNCIONES DE CONTROL PARA ELEMENTOS MULTIMEDIA ============

let selectedMediaId = null;

// Mostrar controles de multimedia al hacer hover
function showMediaControls(mediaId) {
    console.log('🎬 Mostrando controles para:', mediaId);
    
    const controls = document.getElementById(`controls_${mediaId}`);
    const container = document.getElementById(mediaId);
    
    if (controls) {
        controls.style.display = 'block';
    }
    
    if (container) {
        container.style.borderColor = '#007bff';
        container.style.borderStyle = 'dashed';
        container.style.borderWidth = '2px';
    }
}

// Ocultar controles de multimedia
function hideMediaControls(mediaId) {
    const controls = document.getElementById(`controls_${mediaId}`);
    const container = document.getElementById(mediaId);
    
    if (controls && selectedMediaId !== mediaId) {
        controls.style.display = 'none';
    }
    
    if (container && selectedMediaId !== mediaId) {
        container.style.borderColor = 'transparent';
    }
}

// Seleccionar elemento multimedia
function selectMediaElement(mediaId) {
    console.log('🎯 Seleccionando elemento multimedia:', mediaId);
    
    // Deseleccionar elemento anterior
    if (selectedMediaId && selectedMediaId !== mediaId) {
        deselectMediaElement(selectedMediaId);
    }
    
    selectedMediaId = mediaId;
    const container = document.getElementById(mediaId);
    const controls = document.getElementById(`controls_${mediaId}`);
    const indicator = container?.querySelector('.selection-indicator');
    
    if (container) {
        container.style.borderColor = '#007bff';
        container.style.borderStyle = 'solid';
        container.style.borderWidth = '3px';
        container.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
    }
    
    if (controls) {
        controls.style.display = 'block';
    }
    
    if (indicator) {
        indicator.style.display = 'block';
    }
    
    console.log('✅ Elemento multimedia seleccionado:', mediaId);
}

// Deseleccionar elemento multimedia
function deselectMediaElement(mediaId) {
    const container = document.getElementById(mediaId);
    const indicator = container?.querySelector('.selection-indicator');
    
    if (container) {
        container.style.borderColor = 'transparent';
        container.style.backgroundColor = 'transparent';
    }
    
    if (indicator) {
        indicator.style.display = 'none';
    }
    
    // Ocultar controles si no hay hover
    setTimeout(() => {
        const controls = document.getElementById(`controls_${mediaId}`);
        if (controls && !container?.matches(':hover')) {
            controls.style.display = 'none';
        }
    }, 100);
}

// Eliminar elemento multimedia
function deleteMediaElement(mediaId) {
    console.log('🗑️ Eliminando elemento multimedia:', mediaId);
    
    if (confirm('¿Estás seguro de que quieres eliminar este elemento multimedia?')) {
        const container = document.getElementById(mediaId);
        if (container) {
            // Animación de eliminación
            container.style.transition = 'all 0.3s ease';
            container.style.opacity = '0';
            container.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                container.remove();
                
                // Limpiar estado si era el elemento seleccionado
                if (selectedMediaId === mediaId) {
                    selectedMediaId = null;
                }
                
                console.log('✅ Elemento multimedia eliminado:', mediaId);
                showDeletionNotification('Elemento multimedia eliminado correctamente', 'success');
            }, 300);
        }
    }
}

// Mover elemento multimedia hacia arriba
function moveMediaUp(mediaId) {
    console.log('⬆️ Moviendo elemento arriba:', mediaId);
    
    const container = document.getElementById(mediaId);
    if (!container) return;
    
    const prevElement = container.previousElementSibling;
    if (prevElement) {
        container.parentNode.insertBefore(container, prevElement);
        console.log('✅ Elemento movido arriba');
        
        // Mantener selección visible
        setTimeout(() => {
            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    } else {
        console.log('⚠️ El elemento ya está al principio');
    }
}

// Mover elemento multimedia hacia abajo
function moveMediaDown(mediaId) {
    console.log('⬇️ Moviendo elemento abajo:', mediaId);
    
    const container = document.getElementById(mediaId);
    if (!container) return;
    
    const nextElement = container.nextElementSibling;
    if (nextElement) {
        container.parentNode.insertBefore(nextElement, container);
        console.log('✅ Elemento movido abajo');
        
        // Mantener selección visible
        setTimeout(() => {
            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    } else {
        console.log('⚠️ El elemento ya está al final');
    }
}

// Mover elemento multimedia a otra celda
function moveMediaToCell(mediaId) {
    console.log('📂 Iniciando movimiento entre celdas para:', mediaId);
    
    const container = document.getElementById(mediaId);
    if (!container) {
        console.error('Elemento no encontrado:', mediaId);
        return;
    }
    
    // Obtener todas las celdas disponibles
    const allCells = document.querySelectorAll('.gjs-cell');
    if (allCells.length === 0) {
        alert('No hay columnas disponibles para mover el elemento.');
        return;
    }
    
    // Crear modal para seleccionar celda de destino
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 25px;
        max-width: 500px;
        width: 90%;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    let cellOptions = '';
    allCells.forEach((cell, index) => {
        const cellContent = cell.textContent.trim().substring(0, 50);
        const isCurrentCell = cell.contains(container);
        
        if (!isCurrentCell) {
            cellOptions += `
                <div class="cell-option" onclick="moveToSelectedCell('${mediaId}', ${index})" 
                     style="padding: 12px; margin: 8px 0; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: all 0.2s ease;">
                    <strong>Columna ${index + 1}</strong>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">${cellContent || 'Columna vacía'}</p>
        </div>
            `;
        }
    });
    
    modalContent.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #0046CC; margin: 0 0 10px 0;">Mover elemento a otra columna</h3>
            <p style="color: #666; margin: 0;">Selecciona la columna de destino:</p>
        </div>
        
        <div id="cell-options">
            ${cellOptions || '<p style="text-align: center; color: #666;">No hay otras columnas disponibles</p>'}
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="closeMoveModal()" 
                    style="background: #6c757d; color: white; border: none; border-radius: 6px; padding: 10px 20px; cursor: pointer;">
                Cancelar
            </button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Añadir estilos hover para las opciones
    const style = document.createElement('style');
    style.textContent = `
        .cell-option:hover {
            border-color: #007bff !important;
            background-color: #f0f4ff !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15) !important;
        }
    `;
    document.head.appendChild(style);
    
    // Funciones globales para el modal
    window.moveToSelectedCell = function(mediaId, cellIndex) {
        const targetCell = allCells[cellIndex];
        const elementToMove = document.getElementById(mediaId);
        
        if (elementToMove && targetCell) {
            // Verificar si la celda tiene contenido placeholder
            if (targetCell.innerHTML.includes('Haz clic aquí para escribir')) {
                targetCell.innerHTML = '';
            }
            
            targetCell.appendChild(elementToMove);
            
            console.log('✅ Elemento movido a nueva celda:', mediaId);
            showDeletionNotification('Elemento movido a nueva columna correctamente', 'success');
            
            // Enfocar la celda de destino
            focusCell(targetCell);
            
            // Scroll hacia el elemento
            setTimeout(() => {
                elementToMove.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
        
        closeMoveModal();
    };
    
    window.closeMoveModal = function() {
        document.body.removeChild(modal);
        document.head.removeChild(style);
        delete window.moveToSelectedCell;
        delete window.closeMoveModal;
    };
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            window.closeMoveModal();
        }
    });
}

// Función de debug para elementos multimedia
window.debugMediaElements = function() {
    console.log('🔍 DEBUG ELEMENTOS MULTIMEDIA');
    
    const editor = document.getElementById('content-editor');
    if (!editor) {
        console.error('❌ Editor no encontrado');
            return;
        }
        
    const videos = editor.querySelectorAll('.video-container');
    const audios = editor.querySelectorAll('.audio-container');
    const files = editor.querySelectorAll('.file-container');
    const images = editor.querySelectorAll('.editable-image-container');
    
    console.log('📊 Estadísticas:');
    console.log('- Videos:', videos.length);
    console.log('- Audios:', audios.length);
    console.log('- Archivos:', files.length);
    console.log('- Imágenes:', images.length);
    console.log('- Elemento seleccionado:', selectedMediaId || 'Ninguno');
    
    const allMedia = [...videos, ...audios, ...files, ...images];
    
    allMedia.forEach((media, index) => {
        const hasControls = !!media.querySelector('.media-controls, .image-controls, .file-controls');
        const hasEvents = media.onmouseover && media.onmouseout;
        
        console.log(`--- Elemento ${index + 1} ---`);
        console.log('ID:', media.id);
        console.log('Tipo:', media.className);
        console.log('Tiene controles:', hasControls);
        console.log('Eventos configurados:', hasEvents);
    });
    
    console.log('✅ Debug completado');
};

console.log('🎬 Sistema de control multimedia cargado');
console.log('📱 Función de debug disponible: debugMediaElements()');
console.log('✅ Todos los elementos multimedia ahora tienen controles de posicionamiento y eliminación');

// Función para mostrar notificaciones de eliminación o movimiento
function showDeletionNotification(message, type = 'success') {
    console.log('📢 Mostrando notificación:', message);
    
    // Eliminar notificaciones existentes
    const existingNotifications = document.querySelectorAll('.deletion-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Crear nueva notificación
    const notification = document.createElement('div');
    notification.className = 'deletion-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 2000;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideInRight 0.3s ease-out;
        max-width: 350px;
        word-wrap: break-word;
    `;
    
    // Definir colores según el tipo
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors['success'];
    notification.textContent = message;
    
    // Agregar animación CSS si no existe
    if (!document.querySelector('#notification-animations')) {
        const style = document.createElement('style');
        style.id = 'notification-animations';
        style.textContent = `
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
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto-eliminar después de 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Mejorar la función toggleImageSize para imágenes
function toggleImageSize(imageId) {
    console.log('📐 Ajustando imagen a columna:', imageId);
    
    const image = document.getElementById(imageId);
    const container = document.getElementById(`container_${imageId}`);
    
    if (!image || !container) {
        console.error('Imagen o contenedor no encontrado:', imageId);
        return;
    }
    
    // Verificar si está en una celda
    const parentCell = container.closest('.gjs-cell');
    if (!parentCell) {
        showDeletionNotification('La imagen no está en una columna', 'warning');
        return;
    }
    
    // Calcular ancho de la celda
    const cellWidth = parentCell.offsetWidth;
    const availableWidth = Math.max(cellWidth - 40, 100); // Restar padding, mínimo 100px
    
    // Aplicar nuevo tamaño
    image.style.width = '100%';
    image.style.height = 'auto';
    image.style.maxWidth = '100%';
    
    container.style.maxWidth = 'calc(100% - 30px)';
    container.style.margin = '10px auto';
    container.style.display = 'block';
    container.style.textAlign = 'center';
    
    // Actualizar atributos
    image.setAttribute('data-width', '100%');
    image.setAttribute('data-height', 'auto');
    
    // Actualizar información visual
    updateImageSizeInfo(imageId, '100%', 'auto');
    
    showDeletionNotification('Imagen ajustada al ancho de la columna', 'success');
    console.log('✅ Imagen ajustada a columna:', imageId);
}

// Función para ajustar imagen al ancho de la columna
function adjustImageToColumn(imageId) {
    console.log('📐 Ajustando imagen a columna:', imageId);
    
    const image = document.getElementById(imageId);
    const container = document.getElementById(`container_${imageId}`);
    
    if (!image || !container) {
        console.error('Imagen o contenedor no encontrado:', imageId);
        return;
    }
    
    // Obtener la celda contenedora
    const parentCell = container.closest('.gjs-cell');
    if (!parentCell) {
        console.log('Imagen no está en una celda, manteniendo tamaño original');
        return;
    }
    
    // Calcular ancho disponible (restar padding y márgenes)
    const cellWidth = parentCell.offsetWidth;
    const availableWidth = Math.max(cellWidth - 40, 100); // Mínimo 100px
    
    console.log('📏 Ancho de celda:', cellWidth, 'Ancho disponible:', availableWidth);
    
    // Aplicar nuevo tamaño responsivo
    container.style.maxWidth = 'calc(100% - 30px)';
    container.style.margin = '10px auto';
    container.style.display = 'block';
    container.style.textAlign = 'center';
    
    image.style.maxWidth = '100%';
    image.style.width = '100%';
    image.style.height = 'auto';
    
    // Actualizar atributos de datos
    image.setAttribute('data-width', '100%');
    image.setAttribute('data-height', 'auto');
    
    // Actualizar información visual
    updateImageSizeInfo(imageId, '100%', 'auto');
    
    console.log('✅ Imagen ajustada a columna exitosamente');
}

// ============ FUNCIONES AUXILIARES PARA ARCHIVOS Y MULTIMEDIA ============

// Función para obtener el ícono de archivo basado en la extensión
function getFileIcon(extension, mimeType) {
    console.log('🔍 Determinando ícono para:', extension, mimeType);
    
    const iconMap = {
        // Imágenes
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'svg': '🖼️', 'bmp': '🖼️', 'webp': '🖼️',
        
        // Videos
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'wmv': '🎬', 'flv': '🎬', 'webm': '🎬', 'mkv': '🎬',
        
        // Audio
        'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵', 'ogg': '🎵', 'm4a': '🎵',
        
        // Documentos
        'pdf': '📄', 'doc': '📝', 'docx': '📝', 'txt': '📝', 'rtf': '📝',
        
        // Hojas de cálculo
        'xls': '📊', 'xlsx': '📊', 'csv': '📊',
        
        // Presentaciones
        'ppt': '📽️', 'pptx': '📽️',
        
        // Archivos comprimidos
        'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
        
        // Código
        'js': '🖥️', 'html': '🖥️', 'css': '🖥️', 'py': '🖥️', 'php': '🖥️', 'java': '🖥️',
        
        // Archivos de sistema
        'exe': '⚙️', 'msi': '⚙️', 'dmg': '⚙️', 'pkg': '⚙️'
    };
    
    // Verificar por extensión primero
    const icon = iconMap[extension.toLowerCase()];
    if (icon) {
        return icon;
    }
    
    // Verificar por tipo MIME si no se encontró por extensión
    if (mimeType) {
        if (mimeType.startsWith('image/')) return '🖼️';
        if (mimeType.startsWith('video/')) return '🎬';
        if (mimeType.startsWith('audio/')) return '🎵';
        if (mimeType.startsWith('text/')) return '📝';
        if (mimeType.includes('pdf')) return '📄';
        if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return '📊';
        if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📽️';
        if (mimeType.includes('zip') || mimeType.includes('compressed')) return '📦';
    }
    
    // Ícono por defecto
    return '📁';
}

// Función para generar previsualización del archivo
function generateFilePreview(file, fileData, mimeType, extension) {
    console.log('👁️ Generando previsualización para:', file.name, mimeType);
    
    let previewHtml = '';
    
    try {
        if (mimeType.startsWith('image/')) {
            // Previsualización de imagen
            previewHtml = `
                <div class="file-preview image-preview" style="margin-top: 15px;">
                    <img src="${fileData}" 
                         alt="Vista previa" 
                         style="max-width: 100%; max-height: 200px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                </div>
            `;
        } else if (mimeType.startsWith('video/')) {
            // Previsualización de video
            previewHtml = `
                <div class="file-preview video-preview" style="margin-top: 15px;">
                    <video controls style="max-width: 100%; max-height: 200px; border-radius: 6px;">
                        <source src="${fileData}" type="${mimeType}">
                        Tu navegador no soporta la reproducción de video.
                    </video>
                </div>
            `;
        } else if (mimeType.startsWith('audio/')) {
            // Previsualización de audio
            previewHtml = `
                <div class="file-preview audio-preview" style="margin-top: 15px; text-align: center;">
                    <audio controls style="width: 100%; max-width: 300px;">
                        <source src="${fileData}" type="${mimeType}">
                        Tu navegador no soporta la reproducción de audio.
                    </audio>
            </div>
        `;
        } else if (mimeType.startsWith('text/') && file.size < 1024 * 1024) { // Solo archivos de texto menores a 1MB
            // Previsualización de texto
            const reader = new FileReader();
            reader.onload = function(e) {
                const textContent = e.target.result.substring(0, 500); // Primeros 500 caracteres
                const previewElement = document.querySelector(`#file_${Date.now() - 1} .text-preview pre`);
                if (previewElement) {
                    previewElement.textContent = textContent + (e.target.result.length > 500 ? '...' : '');
                }
            };
            reader.readAsText(file);
            
            previewHtml = `
                <div class="file-preview text-preview" style="margin-top: 15px;">
                    <pre style="white-space: pre-wrap; margin: 0; font-family: 'Courier New', monospace; font-size: 12px; color: #333; max-height: 150px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff;">
                        Cargando vista previa...
                    </pre>
                        </div>
            `;
        } else {
            // Información general del archivo
            previewHtml = `
                <div class="file-preview general-preview" style="margin-top: 15px; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 6px;">
                    <div style="font-size: 32px; margin-bottom: 10px;">${getFileIcon(extension, mimeType)}</div>
                    <p style="margin: 0; color: #666; font-size: 14px;">Vista previa no disponible</p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 12px;">Tipo: ${mimeType}</p>
                    </div>
            `;
        }
    } catch (error) {
        console.warn('Error generando previsualización:', error);
        previewHtml = `
            <div class="file-preview error-preview" style="margin-top: 15px; text-align: center; padding: 20px; background: #fff3cd; border-radius: 6px; border: 1px solid #ffeaa7;">
                <p style="margin: 0; color: #856404; font-size: 14px;">⚠️ No se pudo generar la vista previa</p>
                        </div>
        `;
    }
    
    return previewHtml;
}

// Función para mostrar controles de archivo
function showFileControls(fileId) {
    console.log('📁 Mostrando controles de archivo:', fileId);
    
    const controls = document.querySelector(`#${fileId} .file-controls`);
    const container = document.getElementById(fileId);
    
    if (controls) {
        controls.style.display = 'block';
    }
    
    if (container) {
        container.style.borderColor = '#007bff';
        container.style.boxShadow = '0 4px 12px rgba(0, 123, 255, 0.15)';
    }
}

// Función para ocultar controles de archivo
function hideFileControls(fileId) {
    const controls = document.querySelector(`#${fileId} .file-controls`);
    const container = document.getElementById(fileId);
    
    if (controls) {
        controls.style.display = 'none';
    }
    
    if (container) {
        container.style.borderColor = '#e0e0e0';
        container.style.boxShadow = 'none';
    }
}

// Función para descargar archivo
function downloadFile(fileId) {
    console.log('💾 Iniciando descarga de archivo:', fileId);
    
    const container = document.getElementById(fileId);
    if (!container) {
        console.error('Contenedor de archivo no encontrado:', fileId);
        return;
    }
    
    // Buscar los datos del archivo en el script JSON
    const scriptElement = container.querySelector('script[type="application/json"]');
    if (!scriptElement) {
        console.error('Datos del archivo no encontrados:', fileId);
        showDeletionNotification('Error: Datos del archivo no encontrados', 'error');
        return;
    }
    
    try {
        const fileInfo = JSON.parse(scriptElement.textContent);
        const fileName = fileInfo.fileName;
        const fileData = fileInfo.fileData;
        
        if (!fileData) {
            console.error('Datos del archivo corruptos:', fileId);
            showDeletionNotification('Error: Datos del archivo corruptos', 'error');
            return;
        }
        
        // Crear enlace de descarga temporal
        const downloadLink = document.createElement('a');
        downloadLink.href = fileData;
        downloadLink.download = fileName || 'archivo_descargado';
        downloadLink.style.display = 'none';
        
        // Agregar al DOM, hacer clic y remover
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        console.log('✅ Descarga iniciada:', fileName);
        showDeletionNotification(`Descargando: ${fileName}`, 'success');
        
    } catch (error) {
        console.error('Error al procesar descarga:', error);
        showDeletionNotification('Error al procesar la descarga', 'error');
    }
}

// Función para eliminar archivo
function deleteFile(fileId) {
    console.log('🗑️ Eliminando archivo:', fileId);
    
    if (confirm('¿Estás seguro de que quieres eliminar este archivo?')) {
        const container = document.getElementById(fileId);
        if (container) {
            // Obtener nombre del archivo para la notificación
            const fileName = container.getAttribute('data-file-name') || 'archivo';
            
            // Animación de eliminación
            container.style.transition = 'all 0.3s ease';
            container.style.opacity = '0';
            container.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                container.remove();
                console.log('✅ Archivo eliminado:', fileId);
                showDeletionNotification(`Archivo "${fileName}" eliminado correctamente`, 'success');
            }, 300);
        }
    }
}

// Función mejorada para restaurar archivos editables
function restoreEditableFiles() {
    console.log('📁 Restaurando archivos editables...');
    
    const editor = document.getElementById('content-editor');
    if (!editor) return;
    
    // Buscar todos los archivos que tienen los atributos de datos
    const editableFiles = editor.querySelectorAll('.file-container');
    
    editableFiles.forEach(container => {
        const fileId = container.id;
        if (fileId) {
            console.log('Restaurando archivo editable:', fileId);
            
            // Asegurar que los eventos estén configurados
            container.setAttribute('onmouseover', `showFileControls('${fileId}')`);
            container.setAttribute('onmouseout', `hideFileControls('${fileId}')`);
            
            // Verificar que los botones de descarga funcionen
            const downloadButtons = container.querySelectorAll('button[onclick*="downloadFile"]');
            downloadButtons.forEach(button => {
                button.setAttribute('onclick', `downloadFile('${fileId}')`);
            });
            
            // Verificar que los botones de eliminación funcionen
            const deleteButtons = container.querySelectorAll('button[onclick*="deleteFile"]');
            deleteButtons.forEach(button => {
                button.setAttribute('onclick', `event.stopPropagation(); deleteFile('${fileId}')`);
            });
        }
    });
    
    console.log('✅ Archivos editables restaurados');
}

// Función para obtener el contenedor del cursor (mejorada)
function getCursorContainer() {
    // Primero verificar si hay una celda activa
    if (activeCellContainer) {
        console.log('🎯 Usando celda activa:', activeCellContainer);
        return activeCellContainer;
    }
    
    // Verificar selección actual
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        let container = range.commonAncestorContainer;
        
        // Si es un nodo de texto, subir al elemento padre
        if (container.nodeType === Node.TEXT_NODE) {
            container = container.parentElement;
        }
        
        // Buscar la celda más cercana
        while (container && !container.classList.contains('gjs-cell') && container.id !== 'content-editor') {
            container = container.parentElement;
        }
        
        if (container && container.classList.contains('gjs-cell')) {
            console.log('🎯 Celda detectada por cursor:', container);
            return container;
        }
    }
    
    // Usar el editor principal como fallback
    const editor = document.getElementById('content-editor');
    console.log('🎯 Usando editor principal como fallback');
    return editor;
}

console.log('🔧 Funciones auxiliares para archivos y multimedia cargadas');
console.log('📁 Sistema completo de manejo de archivos disponible');
console.log('🎯 Funciones de posicionamiento inteligente implementadas');