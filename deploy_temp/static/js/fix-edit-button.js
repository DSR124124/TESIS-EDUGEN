// Script para reparar el botón de editar en la página de detalle de contenido
window.onload = function() {
    console.log("Script de reparación iniciado");
    
    // Obtener referencias a los elementos necesarios
    const btnEditarAqui = document.getElementById('btnEditarAqui');
    const viewContainer = document.getElementById('view-container');
    const editorContainer = document.getElementById('editor-container');
    const contentViewer = document.getElementById('content-viewer');
    const contentEditor = document.getElementById('content-editor');
    const contentIframe = document.getElementById('content-iframe');
    const btnSaveContent = document.getElementById('btn-save-content');
    
    if (!btnEditarAqui) {
        console.error("Botón 'Editar Contenido' no encontrado");
        return;
    }
    
    if (!viewContainer || !editorContainer || !contentViewer || !contentEditor || !contentIframe) {
        console.error("Elementos necesarios para la edición no encontrados", {
            viewContainer: !!viewContainer,
            editorContainer: !!editorContainer,
            contentViewer: !!contentViewer,
            contentEditor: !!contentEditor,
            contentIframe: !!contentIframe
        });
        return;
    }
    
    console.log("Elementos necesarios encontrados, configurando evento de click");
    
    // Función para preservar estilos GrapesJS
    function preserveGrapesJSStyles(htmlContent) {
        // Verifica si el contenido ya tiene estilos
        if (htmlContent.includes('<style>') && htmlContent.includes('gjs-row')) {
            return htmlContent; // Ya tiene estilos GrapesJS
        }
        
        // Si no tiene estilos o estructura GrapesJS, intentar mantener el contenido
        // pero encapsularlo en la estructura de GrapesJS
        const defaultStyles = `
<style>
.gjs-row {
  display: flex;
  justify-content: flex-start;
  align-items: stretch;
  flex-wrap: wrap;
  padding: 10px;
  margin: 0 0 10px 0;
}

.gjs-cell {
  min-height: 75px;
  flex-grow: 1;
  flex-basis: 100%;
  padding: 0 15px;
}

@media (max-width: 768px) {
  .gjs-cell {
    flex-basis: 100%;
  }
}

.header-container {
  background-color: #4a90e2;
  border-radius: 8px 8px 0 0;
  color: white;
  padding: 25px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-title {
  font-size: 2.5em;
  margin-bottom: 10px;
  font-weight: 700;
  color: white;
}

.subtitle {
  font-size: 1.2em;
  font-weight: 400;
  margin-top: 0;
  color: rgba(255, 255, 255, 0.9);
}

.section-container {
  background-color: white;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
}

.section-title {
  font-size: 1.8em;
  color: #4a90e2;
  padding: 15px 20px;
  margin: 0;
  border-bottom: 2px solid #4a90e2;
}

.section-content {
  padding: 20px;
}

.content-block {
  margin-bottom: 15px;
}
</style>`;

        // Encapsular contenido en estructura GrapesJS
        const wrappedContent = `
${defaultStyles}
<div class="gjs-row">
  <div class="gjs-cell">
    <div class="section-container">
      <div class="section-content">
        ${htmlContent}
      </div>
    </div>
  </div>
</div>`;
        
        return wrappedContent;
    }
    
    // Limpiar eventos existentes
    const newBtn = btnEditarAqui.cloneNode(true);
    btnEditarAqui.parentNode.replaceChild(newBtn, btnEditarAqui);
    
    // Agregar nuevo manejador de evento
    newBtn.addEventListener('click', function() {
        console.log("Botón de editar clickeado");
        
        // Ocultar visor de contenido
        viewContainer.style.display = 'none';
        
        // Mostrar el editor
        editorContainer.style.display = 'block';
        
        // Cargar el contenido completo en el editor
        try {
            if (contentIframe && contentIframe.contentDocument) {
                const iframeDocument = contentIframe.contentDocument;
                let fullContent = '';
                
                // Obtener todos los elementos style del document
                const styleElements = iframeDocument.getElementsByTagName('style');
                for (let i = 0; i < styleElements.length; i++) {
                    fullContent += styleElements[i].outerHTML;
                }
                
                // Obtener el contenido del body
                if (iframeDocument.body) {
                    fullContent += iframeDocument.body.innerHTML;
                }
                
                contentEditor.innerHTML = fullContent;
            } else {
                const srcDoc = contentIframe.getAttribute('srcdoc') || '';
                contentEditor.innerHTML = srcDoc;
            }
        } catch (error) {
            console.error("Error al acceder al contenido del iframe:", error);
            contentEditor.innerHTML = contentViewer.innerHTML;
        }
        
        console.log("Editor activado correctamente");
    });
    
    // Sobrescribir el comportamiento del botón de guardado 
    if (btnSaveContent) {
        const newSaveBtn = btnSaveContent.cloneNode(true);
        btnSaveContent.parentNode.replaceChild(newSaveBtn, btnSaveContent);
        
        newSaveBtn.addEventListener('click', function() {
            const content = contentEditor.innerHTML;
            
            // Asegurar que el contenido tiene los estilos GrapesJS
            const processedContent = preserveGrapesJSStyles(content);
            
            document.getElementById('content-input').value = processedContent;
            document.getElementById('content-formatted').value = processedContent;
            document.getElementById('content-form').submit();
        });
    }
    
    console.log("Script de reparación completado");
}; 