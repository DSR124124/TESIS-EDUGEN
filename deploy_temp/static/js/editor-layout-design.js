// Editor de Diseño y Estructura
// Herramientas para crear layouts, columnas y estructuras

console.log('🏗️ Iniciando módulo de diseño y estructura...');

// Namespace para evitar conflictos
window.LayoutDesignTools = {
    // Variable global para manejar columnas activas
    activeCellContainer: null,

    // Crear herramientas de diseño
    createLayoutToolbar: function(parent) {
        console.log('Creando herramientas de diseño...');
        
        const layoutGroup = document.createElement('div');
        layoutGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
        
        const layoutLabel = document.createElement('div');
        layoutLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
        layoutLabel.textContent = 'Diseño y estructura:';
        layoutGroup.appendChild(layoutLabel);
        
        const columnsContainer = document.createElement('div');
        columnsContainer.className = 'layout-design-tools';
        columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; width: 100%; padding: 5px;';
        layoutGroup.appendChild(columnsContainer);
        
        const layoutButtons = [
            { title: 'Crear 2 Columnas', subtitle: 'Dividir contenido', icon: 'fas fa-columns', action: () => this.insertLayout('2-columns') },
            { title: 'Crear 3 Columnas', subtitle: 'Tres secciones', icon: 'fas fa-th-large', action: () => this.insertLayout('3-columns') },
            { title: 'Línea Separadora', subtitle: 'Dividir secciones', icon: 'fas fa-minus', action: () => this.insertLayout('divider') },
            { title: 'Caja Informativa', subtitle: 'Destacar en azul', icon: 'fas fa-info-circle', action: () => this.insertLayout('blue-box') },
            { title: 'Caja de Consejos', subtitle: 'Destacar en verde', icon: 'fas fa-check-circle', action: () => this.insertLayout('green-box') },
            { title: 'Caja de Alerta', subtitle: 'Destacar en rojo', icon: 'fas fa-exclamation-triangle', action: () => this.insertLayout('red-box') }
        ];
        
        layoutButtons.forEach(btn => {
            const button = this.createToolButton(btn);
            columnsContainer.appendChild(button);
        });
        
        parent.appendChild(layoutGroup);
        console.log('Herramientas de diseño creadas exitosamente');
    },

    // Crear botón de herramienta
    createToolButton: function(btnData) {
        const button = document.createElement('button');
        button.className = 'btn btn-sm layout-design-tool-btn';
        button.title = `${btnData.title} - ${btnData.subtitle}`;
        button.style.cssText = `
            width: 100%; 
            min-height: 65px; 
            padding: 8px 6px; 
            font-size: 10px; 
            border: 1px solid #28a745; 
            background: linear-gradient(135deg, #28a745 0%, #34ce57 100%); 
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
            button.style.background = 'linear-gradient(135deg, #1e7e34 0%, #28a745 100%)';
            button.style.transform = 'translateY(-2px) scale(1.02)';
            button.style.boxShadow = '0 4px 15px rgba(40,167,69,0.3)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.background = 'linear-gradient(135deg, #28a745 0%, #34ce57 100%)';
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

    // Insertar layouts
    insertLayout: function(type) {
        console.log(`📐 Insertando layout: ${type}`);
        
        let layoutHTML = '';
        const layoutId = 'layout-' + Date.now();
        
        switch(type) {
            case '2-columns':
                layoutHTML = `
                    <div class="row custom-row" id="${layoutId}" style="margin: 20px 0; position: relative; border: 2px dashed #e0e0e0; padding: 10px; border-radius: 8px;">
                        <div class="row-controls" style="position: absolute; top: -15px; right: 5px; display: none; background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer; z-index: 1000;" onclick="window.LayoutDesignTools.deleteRow('${layoutId}')">
                            🗑️ Eliminar fila
                        </div>
                        <div class="col-md-6 custom-cell" contenteditable="true" style="min-height: 100px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; position: relative; background: #fafafa;" 
                             onclick="window.LayoutDesignTools.focusCell(this)">
                            <div class="cell-controls" style="position: absolute; top: -12px; right: 2px; display: none; background: #dc3545; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; z-index: 999;" onclick="event.stopPropagation(); window.LayoutDesignTools.deleteCell(this.parentElement)">
                                🗑️
                            </div>
                            <div class="cell-indicator" style="display: none; position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; pointer-events: none; z-index: 998;">
                                📍 Activa
                            </div>
                            <p>Haz clic aquí para escribir en la primera columna...</p>
                        </div>
                        <div class="col-md-6 custom-cell" contenteditable="true" style="min-height: 100px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; position: relative; background: #fafafa;" 
                             onclick="window.LayoutDesignTools.focusCell(this)">
                            <div class="cell-controls" style="position: absolute; top: -12px; right: 2px; display: none; background: #dc3545; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; z-index: 999;" onclick="event.stopPropagation(); window.LayoutDesignTools.deleteCell(this.parentElement)">
                                🗑️
                            </div>
                            <div class="cell-indicator" style="display: none; position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; pointer-events: none; z-index: 998;">
                                📍 Activa
                            </div>
                            <p>Haz clic aquí para escribir en la segunda columna...</p>
                        </div>
                    </div>
                `;
                break;
                
            case '3-columns':
                layoutHTML = `
                    <div class="row custom-row" id="${layoutId}" style="margin: 20px 0; position: relative; border: 2px dashed #e0e0e0; padding: 10px; border-radius: 8px;">
                        <div class="row-controls" style="position: absolute; top: -15px; right: 5px; display: none; background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer; z-index: 1000;" onclick="window.LayoutDesignTools.deleteRow('${layoutId}')">
                            🗑️ Eliminar fila
                        </div>
                        <div class="col-md-4 custom-cell" contenteditable="true" style="min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 5px; position: relative; background: #fafafa;" 
                             onclick="window.LayoutDesignTools.focusCell(this)">
                            <div class="cell-controls" style="position: absolute; top: -12px; right: 2px; display: none; background: #dc3545; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; z-index: 999;" onclick="event.stopPropagation(); window.LayoutDesignTools.deleteCell(this.parentElement)">
                                🗑️
                            </div>
                            <div class="cell-indicator" style="display: none; position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; pointer-events: none; z-index: 998;">
                                📍 Activa
                            </div>
                            <p>Primera columna...</p>
                        </div>
                        <div class="col-md-4 custom-cell" contenteditable="true" style="min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 5px; position: relative; background: #fafafa;" 
                             onclick="window.LayoutDesignTools.focusCell(this)">
                            <div class="cell-controls" style="position: absolute; top: -12px; right: 2px; display: none; background: #dc3545; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; z-index: 999;" onclick="event.stopPropagation(); window.LayoutDesignTools.deleteCell(this.parentElement)">
                                🗑️
                            </div>
                            <div class="cell-indicator" style="display: none; position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; pointer-events: none; z-index: 998;">
                                📍 Activa
                            </div>
                            <p>Segunda columna...</p>
                        </div>
                        <div class="col-md-4 custom-cell" contenteditable="true" style="min-height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; position: relative; background: #fafafa;" 
                             onclick="window.LayoutDesignTools.focusCell(this)">
                            <div class="cell-controls" style="position: absolute; top: -12px; right: 2px; display: none; background: #dc3545; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; cursor: pointer; z-index: 999;" onclick="event.stopPropagation(); window.LayoutDesignTools.deleteCell(this.parentElement)">
                                🗑️
                            </div>
                            <div class="cell-indicator" style="display: none; position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; pointer-events: none; z-index: 998;">
                                📍 Activa
                            </div>
                            <p>Tercera columna...</p>
                        </div>
                    </div>
                `;
                break;
                
            case 'divider':
                layoutHTML = `<hr style="margin: 30px 0; border: 2px solid #0046CC; border-radius: 2px;">`;
                break;
                
            case 'blue-box':
                layoutHTML = `
                    <div style="background: #e7f3ff; border: 2px solid #0046CC; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h4 style="color: #0046CC; margin-bottom: 10px;">💡 Información importante</h4>
                        <p>Escribe aquí tu contenido destacado...</p>
                    </div>
                `;
                break;
                
            case 'green-box':
                layoutHTML = `
                    <div style="background: #e8f5e8; border: 2px solid #28a745; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h4 style="color: #28a745; margin-bottom: 10px;">✅ Consejo útil</h4>
                        <p>Escribe aquí tu consejo o tip educativo...</p>
                    </div>
                `;
                break;
                
            case 'red-box':
                layoutHTML = `
                    <div style="background: #ffe6e6; border: 2px solid #dc3545; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h4 style="color: #dc3545; margin-bottom: 10px;">⚠️ Advertencia</h4>
                        <p>Escribe aquí información importante o de precaución...</p>
                    </div>
                `;
                break;
        }
        
        this.insertContentAtCursor(layoutHTML);
        
        // Restaurar controles después de insertar
        setTimeout(() => {
            this.setupRowHoverEffects();
        }, 100);
        
        console.log(`✅ Layout ${type} insertado exitosamente`);
    },

    // Configurar efectos hover para filas
    setupRowHoverEffects: function() {
        const rows = document.querySelectorAll('.custom-row');
        rows.forEach(row => {
            const rowControls = row.querySelector('.row-controls');
            const cellControls = row.querySelectorAll('.cell-controls');
            
            row.addEventListener('mouseenter', () => {
                if (rowControls) rowControls.style.display = 'block';
                cellControls.forEach(control => {
                    control.style.display = 'block';
                });
            });
            
            row.addEventListener('mouseleave', () => {
                if (rowControls) rowControls.style.display = 'none';
                cellControls.forEach(control => {
                    control.style.display = 'none';
                });
            });
        });
    },

    // Enfocar celda
    focusCell: function(cell) {
        console.log('🎯 Enfocando celda:', cell);
        
        // Limpiar estado activo anterior
        this.clearActiveState();
        
        // Establecer nueva celda activa
        this.activeCellContainer = cell;
        
        // Agregar estilos de celda activa
        cell.style.border = '2px solid #007bff';
        cell.style.boxShadow = '0 0 10px rgba(0,123,255,0.3)';
        cell.style.background = '#f8f9ff';
        
        // Mostrar indicador de celda activa
        const indicator = cell.querySelector('.cell-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
        
        // Enfocar la celda para edición
        cell.focus();
        
        console.log('✅ Celda enfocada exitosamente');
    },

    // Limpiar estado activo
    clearActiveState: function() {
        // Remover estilos de todas las celdas activas
        const allCells = document.querySelectorAll('.custom-cell');
        allCells.forEach(cell => {
            cell.style.border = '1px solid #ddd';
            cell.style.boxShadow = 'none';
            cell.style.background = '#fafafa';
            
            const indicator = cell.querySelector('.cell-indicator');
            if (indicator) {
                indicator.style.display = 'none';
            }
        });
        
        this.activeCellContainer = null;
    },

    // Eliminar fila
    deleteRow: function(rowId) {
        const row = document.getElementById(rowId);
        if (!row) return;
        
        if (confirm('¿Estás seguro de que quieres eliminar toda esta fila y su contenido?')) {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '0';
            row.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                row.remove();
                this.showDeletionNotification('Fila eliminada exitosamente');
            }, 300);
        }
    },

    // Eliminar celda
    deleteCell: function(cell) {
        const row = cell.closest('.custom-row');
        const cells = row.querySelectorAll('.custom-cell');
        
        if (cells.length === 1) {
            if (confirm('Esta es la última celda de la fila. ¿Quieres eliminar toda la fila?')) {
                this.deleteRow(row.id);
            }
            return;
        }
        
        if (confirm('¿Estás seguro de que quieres eliminar esta celda y su contenido?')) {
            // Redistribuir ancho de columnas
            const remainingCells = cells.length - 1;
            const newColClass = remainingCells === 1 ? 'col-md-12' : 
                               remainingCells === 2 ? 'col-md-6' : 'col-md-4';
            
            cell.style.transition = 'all 0.3s ease';
            cell.style.opacity = '0';
            cell.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                cell.remove();
                
                // Actualizar clases de las celdas restantes
                const updatedCells = row.querySelectorAll('.custom-cell');
                updatedCells.forEach(c => {
                    c.className = c.className.replace(/col-md-\d+/, newColClass);
                });
                
                this.showDeletionNotification('Celda eliminada exitosamente');
            }, 300);
        }
    },

    // Mostrar notificación de eliminación
    showDeletionNotification: function(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: bold;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    },

    // Insertar contenido en el cursor
    insertContentAtCursor: function(htmlContent) {
        console.log('📝 Insertando contenido...');
        
        // Si hay una celda activa, insertar ahí
        if (this.activeCellContainer) {
            console.log('🎯 Insertando en celda activa');
            this.activeCellContainer.innerHTML += htmlContent;
            return;
        }
        
        // Obtener contenedor del cursor
        const targetContainer = this.getCursorContainer();
        if (targetContainer) {
            console.log('📍 Insertando en contenedor del cursor');
            targetContainer.innerHTML += htmlContent;
        } else {
            console.log('📄 Insertando al final del editor');
            const editor = document.getElementById('content-editor');
            if (editor) {
                editor.innerHTML += htmlContent;
            }
        }
        
        console.log('✅ Contenido insertado exitosamente');
    },

    // Obtener contenedor del cursor
    getCursorContainer: function() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            let container = range.commonAncestorContainer;
            
            // Si es texto, obtener el elemento padre
            while (container.nodeType === Node.TEXT_NODE) {
                container = container.parentNode;
            }
            
            // Buscar si está dentro de una celda
            const cell = container.closest('.custom-cell');
            if (cell) {
                return cell;
            }
            
            // Si está dentro del editor pero no en una celda
            const editor = container.closest('#content-editor');
            if (editor) {
                return editor;
            }
        }
        
        return null;
    },

    // Inicializar módulo
    init: function() {
        console.log('✅ Módulo de diseño y estructura inicializado');
        
        // Configurar efectos hover para filas existentes
        setTimeout(() => {
            this.setupRowHoverEffects();
        }, 500);
        
        // Agregar event listener para limpiar estado activo con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearActiveState();
            }
        });
        
        // Agregar estilos CSS para botones de layout
        this.addLayoutDesignStyles();
    },

    // Agregar estilos CSS para diseño y layout
    addLayoutDesignStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* Estilos para botones de diseño y layout */
            .layout-design-tool-btn {
                word-wrap: break-word;
                text-align: center !important;
                white-space: normal !important;
            }
            
            /* Estilos para panel de diseño y layout */
            .layout-design-tools {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
                padding: 5px;
            }
            
            /* Responsive para botones de diseño */
            @media (max-width: 768px) {
                .layout-design-tools {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            @media (max-width: 480px) {
                .layout-design-tools {
                    grid-template-columns: 1fr;
                }
                
                .layout-design-tool-btn {
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
        window.LayoutDesignTools.init();
    });
} else {
    window.LayoutDesignTools.init();
} 