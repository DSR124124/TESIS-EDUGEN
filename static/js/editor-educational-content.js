// Editor de Contenido Educativo
// Herramientas específicas para crear contenido educativo

console.log('🎓 Iniciando módulo de contenido educativo...');

// Namespace para evitar conflictos
window.EducationalContentTools = {
    // Crear herramientas educativas
    createEducationalToolbar: function(parent) {
        console.log('Creando herramientas educativas...');
        
        const eduGroup = document.createElement('div');
        eduGroup.style.cssText = 'background: white; border-radius: 8px; padding: 8px 5px; margin-bottom: 10px; width: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
        
        const eduLabel = document.createElement('div');
        eduLabel.style.cssText = 'width: 100%; padding: 3px 0; margin: 0 0 5px 0; border-bottom: 1px solid #e9ecef; font-weight: bold; color: #0046CC; font-size: 13px;';
        eduLabel.textContent = 'Contenido educativo:';
        eduGroup.appendChild(eduLabel);
        
        const columnsContainer = document.createElement('div');
        columnsContainer.className = 'educational-content-tools';
        columnsContainer.style.cssText = 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; width: 100%; padding: 5px;';
        eduGroup.appendChild(columnsContainer);
        
        const eduButtons = [
            { title: 'Crear Pregunta', subtitle: 'Formular preguntas', icon: 'fas fa-question-circle', action: () => this.insertEduElement('question') },
            { title: 'Crear Respuesta', subtitle: 'Dar soluciones', icon: 'fas fa-lightbulb', action: () => this.insertEduElement('answer') },
            { title: 'Proponer Ejercicio', subtitle: 'Actividad práctica', icon: 'fas fa-pencil-alt', action: () => this.insertEduElement('exercise') },
            { title: 'Mostrar Ejemplo', subtitle: 'Demostrar conceptos', icon: 'fas fa-star', action: () => this.insertEduElement('example') },
            { title: 'Definir Concepto', subtitle: 'Explicar términos', icon: 'fas fa-book', action: () => this.insertEduElement('definition') },
            { title: 'Objetivo de Aprendizaje', subtitle: 'Meta educativa', icon: 'fas fa-bullseye', action: () => this.insertEduElement('objective') },
            { title: 'Crear Resumen', subtitle: 'Síntesis del tema', icon: 'fas fa-list-alt', action: () => this.insertEduElement('summary') },
            { title: 'Evaluación', subtitle: 'Medir conocimiento', icon: 'fas fa-clipboard-check', action: () => this.insertEduElement('evaluation') },
            { title: 'Actividad Grupal', subtitle: 'Trabajo colaborativo', icon: 'fas fa-tasks', action: () => this.insertEduElement('activity') }
        ];
        
        eduButtons.forEach(btn => {
            const button = this.createToolButton(btn);
            columnsContainer.appendChild(button);
        });
        
        parent.appendChild(eduGroup);
        console.log('Herramientas educativas creadas exitosamente');
    },

    // Crear botón de herramienta
    createToolButton: function(btnData) {
        const button = document.createElement('button');
        button.className = 'btn btn-sm educational-content-tool-btn';
        button.title = `${btnData.title} - ${btnData.subtitle}`;
        button.style.cssText = `
            width: 100%; 
            min-height: 65px; 
            padding: 8px 6px; 
            font-size: 10px; 
            border: 1px solid #17a2b8; 
            background: linear-gradient(135deg, #17a2b8 0%, #20c997 100%); 
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
            button.style.background = 'linear-gradient(135deg, #138496 0%, #1c7430 100%)';
            button.style.transform = 'translateY(-2px) scale(1.02)';
            button.style.boxShadow = '0 4px 15px rgba(23,162,184,0.3)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.background = 'linear-gradient(135deg, #17a2b8 0%, #20c997 100%)';
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

    // Insertar elementos educativos
    insertEduElement: function(type) {
        console.log(`🎓 Insertando elemento educativo: ${type}`);
        
        let eduHTML = '';
        const eduId = 'edu-' + Date.now();
        
        switch(type) {
            case 'question':
                eduHTML = `
                    <div class="educational-element question-element" id="${eduId}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(102,126,234,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-question-circle" style="font-size: 20px;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600;">Pregunta</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; min-height: 60px; border: 2px dashed rgba(255,255,255,0.3);" onclick="this.focus()">
                            Escribe aquí tu pregunta...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'answer':
                eduHTML = `
                    <div class="educational-element answer-element" id="${eduId}" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(17,153,142,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-lightbulb" style="font-size: 20px;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600;">Respuesta</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; min-height: 60px; border: 2px dashed rgba(255,255,255,0.3);" onclick="this.focus()">
                            Escribe aquí la respuesta...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'exercise':
                eduHTML = `
                    <div class="educational-element exercise-element" id="${eduId}" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(252,182,159,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-pencil-alt" style="font-size: 20px; color: #d63384;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600; color: #d63384;">Ejercicio</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.5); border-radius: 8px; padding: 15px; min-height: 80px; border: 2px dashed rgba(214,51,132,0.3);" onclick="this.focus()">
                            Describe el ejercicio que los estudiantes deben realizar...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'example':
                eduHTML = `
                    <div class="educational-element example-element" id="${eduId}" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(168,237,234,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-star" style="font-size: 20px; color: #fd7e14;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600; color: #fd7e14;">Ejemplo</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.5); border-radius: 8px; padding: 15px; min-height: 60px; border: 2px dashed rgba(253,126,20,0.3);" onclick="this.focus()">
                            Proporciona un ejemplo claro y detallado...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'definition':
                eduHTML = `
                    <div class="educational-element definition-element" id="${eduId}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(102,126,234,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-book" style="font-size: 20px;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600;">Definición</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; min-height: 60px; border: 2px dashed rgba(255,255,255,0.3);" onclick="this.focus()">
                            Define el concepto o término clave...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'objective':
                eduHTML = `
                    <div class="educational-element objective-element" id="${eduId}" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(255,154,158,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-bullseye" style="font-size: 20px; color: #e83e8c;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600; color: #e83e8c;">Objetivo de Aprendizaje</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.5); border-radius: 8px; padding: 15px; min-height: 60px; border: 2px dashed rgba(232,62,140,0.3);" onclick="this.focus()">
                            Describe qué aprenderán los estudiantes...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'summary':
                eduHTML = `
                    <div class="educational-element summary-element" id="${eduId}" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(168,237,234,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-list-alt" style="font-size: 20px; color: #20c997;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600; color: #20c997;">Resumen</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.5); border-radius: 8px; padding: 15px; min-height: 80px; border: 2px dashed rgba(32,201,151,0.3);" onclick="this.focus()">
                            Proporciona un resumen de los puntos clave...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'evaluation':
                eduHTML = `
                    <div class="educational-element evaluation-element" id="${eduId}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(102,126,234,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-clipboard-check" style="font-size: 20px;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600;">Evaluación</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; min-height: 80px; border: 2px dashed rgba(255,255,255,0.3);" onclick="this.focus()">
                            Describe cómo se evaluará el aprendizaje...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'activity':
                eduHTML = `
                    <div class="educational-element activity-element" id="${eduId}" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; border-radius: 12px; padding: 20px; margin: 20px 0; position: relative; box-shadow: 0 8px 25px rgba(252,182,159,0.3);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: rgba(255,255,255,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                <i class="fas fa-tasks" style="font-size: 20px; color: #fd7e14;"></i>
                            </div>
                            <h4 style="margin: 0; font-weight: 600; color: #fd7e14;">Actividad</h4>
                        </div>
                        <div contenteditable="true" style="background: rgba(255,255,255,0.5); border-radius: 8px; padding: 15px; min-height: 100px; border: 2px dashed rgba(253,126,20,0.3);" onclick="this.focus()">
                            Describe la actividad que realizarán los estudiantes...
                        </div>
                        <div class="edu-controls" style="position: absolute; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s;">
                            <button onclick="window.EducationalContentTools.deleteEduElement('${eduId}')" style="background: rgba(220,53,69,0.8); color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
        }
        
        this.insertContentAtCursor(eduHTML);
        
        // Configurar event listeners después de insertar
        setTimeout(() => {
            this.setupEduEventListeners(eduId);
        }, 100);
        
        console.log(`✅ Elemento educativo ${type} insertado exitosamente`);
    },

    // Configurar event listeners para elementos educativos
    setupEduEventListeners: function(eduId) {
        const eduElement = document.getElementById(eduId);
        if (!eduElement) return;
        
        // Agregar hover effects para mostrar controles
        eduElement.addEventListener('mouseenter', () => {
            const controls = eduElement.querySelector('.edu-controls');
            if (controls) {
                controls.style.opacity = '1';
            }
        });
        
        eduElement.addEventListener('mouseleave', () => {
            const controls = eduElement.querySelector('.edu-controls');
            if (controls) {
                controls.style.opacity = '0';
            }
        });
    },

    // Eliminar elemento educativo
    deleteEduElement: function(eduId) {
        const eduElement = document.getElementById(eduId);
        if (!eduElement) return;
        
        if (confirm('¿Estás seguro de que quieres eliminar este elemento educativo?')) {
            eduElement.style.transition = 'all 0.3s ease';
            eduElement.style.opacity = '0';
            eduElement.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                eduElement.remove();
                this.showNotification('Elemento educativo eliminado exitosamente');
            }, 300);
        }
    },

    // Mostrar notificación
    showNotification: function(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #17a2b8;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: bold;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    },

    // Insertar contenido en el cursor
    insertContentAtCursor: function(htmlContent) {
        console.log('📝 Insertando contenido educativo...');
        
        // Si hay una celda activa en LayoutDesignTools, insertar ahí
        if (window.LayoutDesignTools && window.LayoutDesignTools.activeCellContainer) {
            console.log('🎯 Insertando en celda activa');
            window.LayoutDesignTools.activeCellContainer.innerHTML += htmlContent;
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
        
        console.log('✅ Contenido educativo insertado exitosamente');
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
        console.log('✅ Módulo de contenido educativo inicializado');
        
        // Agregar estilos CSS para botones educativos
        this.addEducationalContentStyles();
    },

    // Agregar estilos CSS para contenido educativo
    addEducationalContentStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* Estilos para botones de contenido educativo */
            .educational-content-tool-btn {
                word-wrap: break-word;
                text-align: center !important;
                white-space: normal !important;
            }
            
            /* Estilos para panel de contenido educativo */
            .educational-content-tools {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
                padding: 5px;
            }
            
            /* Responsive para botones educativos */
            @media (max-width: 768px) {
                .educational-content-tools {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            @media (max-width: 480px) {
                .educational-content-tools {
                    grid-template-columns: 1fr;
                }
                
                .educational-content-tool-btn {
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
        window.EducationalContentTools.init();
    });
} else {
    window.EducationalContentTools.init();
} 