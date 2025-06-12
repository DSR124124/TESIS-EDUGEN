// Editor de Elementos Multimedia
// Herramientas para insertar imágenes, videos, audio y archivos

console.log('🎬 Iniciando módulo de elementos multimedia...');

// Namespace para evitar conflictos
window.MultimediaTools = {
    // Crear herramientas multimedia
    createMediaToolbar: function(parent) {
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
            { title: 'Subir Imagen', subtitle: 'Desde mi computadora', icon: 'fas fa-image', action: () => this.insertMedia('image-local') },
            { title: 'Imagen Web', subtitle: 'Desde una URL', icon: 'fas fa-link', action: () => this.insertMedia('image-url') },
            { title: 'Subir Video', subtitle: 'Desde mi computadora', icon: 'fas fa-video', action: () => this.insertMedia('video-local') },
            { title: 'Video Web', subtitle: 'Desde una URL', icon: 'fas fa-play-circle', action: () => this.insertMedia('video-url') },
            { title: 'Subir Audio', subtitle: 'Grabación o archivo', icon: 'fas fa-microphone', action: () => this.insertMedia('audio-local') },
            { title: 'Audio Web', subtitle: 'Desde una URL', icon: 'fas fa-volume-up', action: () => this.insertMedia('audio-url') },
            { title: 'Video YouTube', subtitle: 'Enlace de YouTube', icon: 'fab fa-youtube', action: () => this.insertMedia('youtube') },
            { title: 'Documento PDF', subtitle: 'Archivo PDF', icon: 'fas fa-file-pdf', action: () => this.insertMedia('pdf') },
            { title: 'Otros Archivos', subtitle: 'Documentos varios', icon: 'fas fa-file-alt', action: () => this.insertMedia('file') }
        ];
        
        // Aplicar clase CSS para grid layout
        columnsContainer.className = 'multimedia-tools';
        
        mediaButtons.forEach(btn => {
            const button = this.createToolButton(btn);
            columnsContainer.appendChild(button);
        });
        
        parent.appendChild(mediaGroup);
        console.log('Herramientas multimedia creadas exitosamente');
    },

    // Crear botón de herramienta
    createToolButton: function(btnData) {
        const button = document.createElement('button');
        button.className = 'btn btn-sm multimedia-tool-btn';
        button.title = `${btnData.title} - ${btnData.subtitle}`;
        button.style.cssText = `
            width: 100%; 
            min-height: 65px; 
            padding: 8px 6px; 
            font-size: 10px; 
            border: 1px solid #667eea; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
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
            button.style.background = 'linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%)';
            button.style.transform = 'translateY(-2px) scale(1.02)';
            button.style.boxShadow = '0 4px 15px rgba(102,126,234,0.3)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
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

    // Insertar elementos multimedia
    insertMedia: function(type) {
        console.log(`🎥 Insertando multimedia: ${type}`);
        
        let mediaHTML = '';
        const mediaId = 'media-' + Date.now();
        
        switch(type) {
            case 'image-local':
                this.selectLocalFile(['image/*'], (file, fileData) => {
                    const fileName = file.name;
                    mediaHTML = `
                        <div class="editable-image-container" id="${mediaId}" style="position: relative; display: inline-block; margin: 10px 0; max-width: 100%; min-width: 200px;">
                            <img src="${fileData}" alt="${fileName}" class="editable-image" 
                                 style="max-width: 100%; height: auto; border: 2px solid transparent; border-radius: 8px; cursor: pointer; min-width: 200px; resize: both; overflow: hidden;" 
                                 onclick="window.MultimediaTools.selectMediaElement('${mediaId}')" 
                                 onload="window.MultimediaTools.adjustImageToColumn('${mediaId}')"
                                 draggable="true"
                                 ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')"
                                 ondragover="window.MultimediaTools.handleDragOver(event)"
                                 ondrop="window.MultimediaTools.handleDrop(event, '${mediaId}')">
                            <div class="image-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                                <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 25%</button>
                                <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'medium')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 50%</button>
                                <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 100%</button>
                                <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                                <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                                <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                            </div>
                            <div class="resize-handles">
                                <div class="resize-handle resize-nw" style="position: absolute; top: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; cursor: nw-resize; border-radius: 50%; display: none;"></div>
                                <div class="resize-handle resize-ne" style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; cursor: ne-resize; border-radius: 50%; display: none;"></div>
                                <div class="resize-handle resize-sw" style="position: absolute; bottom: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; cursor: sw-resize; border-radius: 50%; display: none;"></div>
                                <div class="resize-handle resize-se" style="position: absolute; bottom: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; cursor: se-resize; border-radius: 50%; display: none;"></div>
                            </div>
                        </div>
                    `;
                    this.insertContentAtCursor(mediaHTML);
                    setTimeout(() => {
                        this.setupMediaEventListeners(mediaId);
                        this.setupImageResizeHandles(mediaId);
                    }, 100);
                });
                return;
                
            case 'image-url':
                const imageUrl = prompt('Ingresa la URL de la imagen:');
                if (!imageUrl) return;
                
                mediaHTML = `
                    <div class="editable-image-container" id="${mediaId}" style="position: relative; display: inline-block; margin: 10px 0; max-width: 100%; min-width: 200px;">
                        <img src="${imageUrl}" alt="Imagen" class="editable-image" 
                             style="max-width: 100%; height: auto; border: 2px solid transparent; border-radius: 8px; cursor: pointer; min-width: 200px;" 
                             onclick="window.MultimediaTools.selectMediaElement('${mediaId}')" 
                             onload="window.MultimediaTools.adjustImageToColumn('${mediaId}')"
                             draggable="true"
                             ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')"
                             ondragover="window.MultimediaTools.handleDragOver(event)"
                             ondrop="window.MultimediaTools.handleDrop(event, '${mediaId}')">
                        <div class="image-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                            <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 25%</button>
                            <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'medium')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 50%</button>
                            <button onclick="window.MultimediaTools.resizeImage('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 100%</button>
                            <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                            <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                            <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                        </div>
                        <div class="resize-handles">
                            <div class="resize-handle resize-nw" style="position: absolute; top: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; cursor: nw-resize; border-radius: 50%; display: none;"></div>
                            <div class="resize-handle resize-ne" style="position: absolute; top: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; cursor: ne-resize; border-radius: 50%; display: none;"></div>
                            <div class="resize-handle resize-sw" style="position: absolute; bottom: -5px; left: -5px; width: 10px; height: 10px; background: #007bff; cursor: sw-resize; border-radius: 50%; display: none;"></div>
                            <div class="resize-handle resize-se" style="position: absolute; bottom: -5px; right: -5px; width: 10px; height: 10px; background: #007bff; cursor: se-resize; border-radius: 50%; display: none;"></div>
                        </div>
                    </div>
                `;
                break;
                
            case 'video-local':
                this.selectLocalFile(['video/*'], (file, fileData) => {
                    const fileName = file.name;
                    mediaHTML = `
                        <div class="media-container video-container" id="${mediaId}" style="position: relative; margin: 15px 0; min-width: 300px;" draggable="true" ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')">
                            <video controls style="max-width: 100%; height: auto; border-radius: 8px; min-width: 300px;" onclick="window.MultimediaTools.selectMediaElement('${mediaId}')">
                                <source src="${fileData}" type="${file.type}">
                                Tu navegador no soporta videos HTML5.
                            </video>
                            <div class="media-info" style="background: rgba(0,0,0,0.7); color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; margin-top: 5px;">
                                📹 ${fileName} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                            </div>
                            <div class="media-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                                <button onclick="window.MultimediaTools.resizeVideo('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 50%</button>
                                <button onclick="window.MultimediaTools.resizeVideo('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 100%</button>
                                <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                                <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                                <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                            </div>
                        </div>
                    `;
                    this.insertContentAtCursor(mediaHTML);
                    setTimeout(() => {
                        this.setupMediaEventListeners(mediaId);
                    }, 100);
                });
                return;
                
            case 'video-url':
                const videoUrl = prompt('Ingresa la URL del video (MP4):');
                if (!videoUrl) return;
                
                mediaHTML = `
                    <div class="media-container video-container" id="${mediaId}" style="position: relative; margin: 15px 0; min-width: 300px;" draggable="true" ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')">
                        <video controls style="max-width: 100%; height: auto; border-radius: 8px; min-width: 300px;" onclick="window.MultimediaTools.selectMediaElement('${mediaId}')">
                            <source src="${videoUrl}" type="video/mp4">
                            Tu navegador no soporta videos HTML5.
                        </video>
                        <div class="media-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                            <button onclick="window.MultimediaTools.resizeVideo('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 50%</button>
                            <button onclick="window.MultimediaTools.resizeVideo('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 100%</button>
                            <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                            <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                            <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'audio-local':
                this.selectLocalFile(['audio/*'], (file, fileData) => {
                    const fileName = file.name;
                    mediaHTML = `
                        <div class="media-container audio-container" id="${mediaId}" style="position: relative; margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; border: 1px solid #e9ecef; min-width: 300px;" draggable="true" ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">
                                    <i class="fas fa-microphone" style="color: white; font-size: 24px;"></i>
                                </div>
                                <div style="flex: 1;">
                                    <h5 style="margin: 0 0 5px 0; color: white; font-weight: 600;">🎵 Audio Local</h5>
                                    <audio controls style="width: 100%; margin-bottom: 5px;" onclick="window.MultimediaTools.selectMediaElement('${mediaId}')">
                                        <source src="${fileData}" type="${file.type}">
                                        Tu navegador no soporta audio HTML5.
                                    </audio>
                                    <small style="color: rgba(255,255,255,0.8);">${fileName} (${(file.size / 1024 / 1024).toFixed(2)} MB)</small>
                                </div>
                            </div>
                            <div class="media-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                                <button onclick="window.MultimediaTools.resizeAudio('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 Compacto</button>
                                <button onclick="window.MultimediaTools.resizeAudio('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 Extendido</button>
                                <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                                <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                                <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                            </div>
                        </div>
                    `;
                    this.insertContentAtCursor(mediaHTML);
                    setTimeout(() => {
                        this.setupMediaEventListeners(mediaId);
                    }, 100);
                });
                return;
                
            case 'audio-url':
                const audioUrl = prompt('Ingresa la URL del audio (MP3/WAV):');
                if (!audioUrl) return;
                
                mediaHTML = `
                    <div class="media-container audio-container" id="${mediaId}" style="position: relative; margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; min-width: 300px;" draggable="true" ondragstart="window.MultimediaTools.handleDragStart(event, '${mediaId}')">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-volume-up" style="color: #007bff; font-size: 20px;"></i>
                            <audio controls style="flex: 1;" onclick="window.MultimediaTools.selectMediaElement('${mediaId}')">
                                <source src="${audioUrl}" type="audio/mpeg">
                                Tu navegador no soporta audio HTML5.
                            </audio>
                        </div>
                        <div class="media-controls" style="position: absolute; top: -40px; right: 0; display: none; background: rgba(0,0,0,0.9); border-radius: 8px; padding: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                            <button onclick="window.MultimediaTools.resizeAudio('${mediaId}', 'small')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 Compacto</button>
                            <button onclick="window.MultimediaTools.resizeAudio('${mediaId}', 'large')" style="background: #007bff; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">📏 Extendido</button>
                            <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↑</button>
                            <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">↓</button>
                            <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 10px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'youtube':
                const youtubeUrl = prompt('Ingresa la URL de YouTube:');
                if (!youtubeUrl) return;
                
                let embedUrl = youtubeUrl;
                if (youtubeUrl.includes('watch?v=')) {
                    embedUrl = youtubeUrl.replace('watch?v=', 'embed/');
                } else if (youtubeUrl.includes('youtu.be/')) {
                    embedUrl = youtubeUrl.replace('youtu.be/', 'youtube.com/embed/');
                }
                
                mediaHTML = `
                    <div class="media-container" id="${mediaId}" style="position: relative; margin: 15px 0;">
                        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                            <iframe src="${embedUrl}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 8px;" allowfullscreen onclick="window.MultimediaTools.selectMediaElement('${mediaId}')"></iframe>
                        </div>
                        <div class="media-controls" style="position: absolute; top: -35px; right: 0; display: none; background: rgba(0,0,0,0.8); border-radius: 5px; padding: 5px;">
                            <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↑</button>
                            <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↓</button>
                            <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
                
            case 'file':
                // Crear input para archivo
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.style.display = 'none';
                fileInput.onchange = (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        this.handleFileUpload(file, mediaId);
                    }
                };
                document.body.appendChild(fileInput);
                fileInput.click();
                document.body.removeChild(fileInput);
                return;
                
            case 'pdf':
                const pdfUrl = prompt('Ingresa la URL del PDF:');
                if (!pdfUrl) return;
                
                mediaHTML = `
                    <div class="media-container" id="${mediaId}" style="position: relative; margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <i class="fas fa-file-pdf" style="color: #dc3545; font-size: 24px;"></i>
                            <div>
                                <h5 style="margin: 0; color: #333;">Documento PDF</h5>
                                <small style="color: #666;">Haz clic para ver el documento</small>
                            </div>
                        </div>
                        <iframe src="${pdfUrl}" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 5px;" onclick="window.MultimediaTools.selectMediaElement('${mediaId}')"></iframe>
                        <div class="media-controls" style="position: absolute; top: -35px; right: 0; display: none; background: rgba(0,0,0,0.8); border-radius: 5px; padding: 5px;">
                            <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↑</button>
                            <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↓</button>
                            <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">🗑️</button>
                        </div>
                    </div>
                `;
                break;
        }
        
        if (mediaHTML) {
            this.insertContentAtCursor(mediaHTML);
            
            // Configurar event listeners después de insertar
            setTimeout(() => {
                this.setupMediaEventListeners(mediaId);
            }, 100);
        }
        
        console.log(`✅ Multimedia ${type} insertado exitosamente`);
    },

    // Manejar subida de archivos
    handleFileUpload: function(file, mediaId) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const fileData = e.target.result;
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
            const fileExtension = fileName.split('.').pop().toLowerCase();
            
            const fileIcon = this.getFileIcon(fileExtension, file.type);
            
            const fileHTML = `
                <div class="media-container file-container" id="${mediaId}" style="position: relative; margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="font-size: 32px;">${fileIcon}</div>
                        <div style="flex: 1;">
                            <h5 style="margin: 0 0 5px 0; color: #333;">${fileName}</h5>
                            <small style="color: #666;">Tamaño: ${fileSize} MB | Tipo: ${fileExtension.toUpperCase()}</small>
                            <div style="margin-top: 8px;">
                                <button onclick="window.MultimediaTools.downloadFile('${mediaId}')" style="background: #007bff; color: white; border: none; padding: 5px 12px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 5px;">
                                    📥 Descargar
                                </button>
                                <button onclick="window.MultimediaTools.previewFile('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 5px 12px; border-radius: 4px; font-size: 12px; cursor: pointer;">
                                    👁️ Vista previa
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="media-controls" style="position: absolute; top: -35px; right: 0; display: none; background: rgba(0,0,0,0.8); border-radius: 5px; padding: 5px;">
                        <button onclick="window.MultimediaTools.moveMediaUp('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↑</button>
                        <button onclick="window.MultimediaTools.moveMediaDown('${mediaId}')" style="background: #28a745; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">↓</button>
                        <button onclick="window.MultimediaTools.deleteMediaElement('${mediaId}')" style="background: #dc3545; color: white; border: none; padding: 3px 8px; margin: 0 2px; border-radius: 3px; font-size: 11px; cursor: pointer;">🗑️</button>
                    </div>
                    <div style="display: none;" class="file-data">${fileData}</div>
                </div>
            `;
            
            this.insertContentAtCursor(fileHTML);
            
            setTimeout(() => {
                this.setupMediaEventListeners(mediaId);
            }, 100);
        };
        reader.readAsDataURL(file);
    },

    // Obtener icono de archivo
    getFileIcon: function(extension, mimeType) {
        const iconMap = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📋', 'pptx': '📋',
            'txt': '📄',
            'zip': '🗜️', 'rar': '🗜️', '7z': '🗜️',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
            'mp4': '🎥', 'avi': '🎥', 'mov': '🎥',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵'
        };
        
        return iconMap[extension] || '📎';
    },

    // Configurar event listeners para multimedia
    setupMediaEventListeners: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        // Agregar hover effects
        mediaElement.addEventListener('mouseenter', () => {
            this.showMediaControls(mediaId);
            
            // Mostrar handles de redimensionamiento para imágenes
            const handles = mediaElement.querySelectorAll('.resize-handle');
            handles.forEach(handle => handle.style.display = 'block');
        });
        
        mediaElement.addEventListener('mouseleave', () => {
            this.hideMediaControls(mediaId);
            
            // Ocultar handles de redimensionamiento
            const handles = mediaElement.querySelectorAll('.resize-handle');
            handles.forEach(handle => handle.style.display = 'none');
        });
        
        // Configurar arrastre si el elemento es draggable
        if (mediaElement.draggable) {
            mediaElement.addEventListener('dragstart', (e) => {
                this.handleDragStart(e, mediaId);
            });
            
            mediaElement.addEventListener('dragover', (e) => {
                this.handleDragOver(e);
            });
            
            mediaElement.addEventListener('drop', (e) => {
                this.handleDrop(e, mediaId);
            });
        }
        
        // Configurar selección
        const selectableElement = mediaElement.querySelector('img, video, audio');
        if (selectableElement) {
            selectableElement.addEventListener('click', () => {
                this.selectMediaElement(mediaId);
            });
        }
        
        console.log('✅ Event listeners configurados para multimedia:', mediaId);
    },

    // Mostrar controles de multimedia
    showMediaControls: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        const controls = mediaElement.querySelector('.media-controls, .image-controls');
        if (controls) {
            controls.style.display = 'block';
        }
    },

    // Ocultar controles de multimedia
    hideMediaControls: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        const controls = mediaElement.querySelector('.media-controls, .image-controls');
        if (controls) {
            controls.style.display = 'none';
        }
    },

    // Seleccionar elemento multimedia
    selectMediaElement: function(mediaId) {
        // Limpiar selecciones anteriores
        document.querySelectorAll('.media-selected').forEach(el => {
            el.classList.remove('media-selected');
            el.style.border = '';
        });
        
        const mediaElement = document.getElementById(mediaId);
        if (mediaElement) {
            mediaElement.classList.add('media-selected');
            mediaElement.style.border = '3px solid #007bff';
        }
    },

    // Eliminar elemento multimedia
    deleteMediaElement: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        if (confirm('¿Estás seguro de que quieres eliminar este elemento multimedia?')) {
            mediaElement.style.transition = 'all 0.3s ease';
            mediaElement.style.opacity = '0';
            mediaElement.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                mediaElement.remove();
                this.showNotification('Elemento multimedia eliminado exitosamente');
            }, 300);
        }
    },

    // Mover multimedia hacia arriba
    moveMediaUp: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        const previousSibling = mediaElement.previousElementSibling;
        if (previousSibling) {
            mediaElement.parentNode.insertBefore(mediaElement, previousSibling);
            this.showNotification('Elemento movido hacia arriba');
        }
    },

    // Mover multimedia hacia abajo
    moveMediaDown: function(mediaId) {
        const mediaElement = document.getElementById(mediaId);
        if (!mediaElement) return;
        
        const nextSibling = mediaElement.nextElementSibling;
        if (nextSibling) {
            mediaElement.parentNode.insertBefore(nextSibling, mediaElement);
            this.showNotification('Elemento movido hacia abajo');
        }
    },

    // Alternar tamaño de imagen (legacy - mejorada arriba)
    toggleImageSizeLegacy: function(imageId) {
        const imageContainer = document.getElementById(imageId);
        if (!imageContainer) return;
        
        const img = imageContainer.querySelector('img');
        if (!img) return;
        
        const currentWidth = img.style.maxWidth || '100%';
        if (currentWidth === '100%') {
            img.style.maxWidth = '50%';
            this.showNotification('Imagen redimensionada a 50%');
        } else if (currentWidth === '50%') {
            img.style.maxWidth = '25%';
            this.showNotification('Imagen redimensionada a 25%');
        } else {
            img.style.maxWidth = '100%';
            this.showNotification('Imagen redimensionada a 100%');
        }
    },

    // Ajustar imagen a columna
    adjustImageToColumn: function(imageId) {
        const imageContainer = document.getElementById(imageId);
        if (!imageContainer) return;
        
        const img = imageContainer.querySelector('img');
        if (!img) return;
        
        // Verificar si está dentro de una columna
        const cell = imageContainer.closest('.custom-cell');
        if (cell) {
            img.style.maxWidth = '100%';
            img.style.width = '100%';
            img.style.height = 'auto';
            console.log('🖼️ Imagen ajustada automáticamente a la columna');
        }
    },

    // Descargar archivo
    downloadFile: function(fileId) {
        const fileContainer = document.getElementById(fileId);
        if (!fileContainer) return;
        
        const fileData = fileContainer.querySelector('.file-data');
        if (!fileData) return;
        
        const dataUrl = fileData.textContent;
        const fileName = fileContainer.querySelector('h5').textContent;
        
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = fileName;
        link.click();
    },

    // Vista previa de archivo
    previewFile: function(fileId) {
        const fileContainer = document.getElementById(fileId);
        if (!fileContainer) return;
        
        const fileData = fileContainer.querySelector('.file-data');
        if (!fileData) return;
        
        const dataUrl = fileData.textContent;
        window.open(dataUrl, '_blank');
    },

    // Mostrar notificación
    showNotification: function(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ffc107;
            color: #333;
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
        console.log('📝 Insertando contenido multimedia...');
        
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
        
        console.log('✅ Contenido multimedia insertado exitosamente');
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

    // Seleccionar archivo local
    selectLocalFile: function(acceptTypes, callback) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = acceptTypes.join(',');
        fileInput.style.display = 'none';
        
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validar tamaño del archivo (máximo 50MB)
                if (file.size > 50 * 1024 * 1024) {
                    alert('El archivo es demasiado grande. El tamaño máximo es 50MB.');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (event) => {
                    callback(file, event.target.result);
                };
                reader.readAsDataURL(file);
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    },

    // Configurar handles de redimensionamiento para imágenes
    setupImageResizeHandles: function(imageId) {
        const imageContainer = document.getElementById(imageId);
        if (!imageContainer) return;
        
        const handles = imageContainer.querySelectorAll('.resize-handle');
        const img = imageContainer.querySelector('img');
        
        handles.forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const startX = e.clientX;
                const startY = e.clientY;
                const startWidth = img.offsetWidth;
                const startHeight = img.offsetHeight;
                
                const handleMouseMove = (moveEvent) => {
                    const deltaX = moveEvent.clientX - startX;
                    const deltaY = moveEvent.clientY - startY;
                    
                    let newWidth = startWidth;
                    let newHeight = startHeight;
                    
                    if (handle.classList.contains('resize-se')) {
                        newWidth = startWidth + deltaX;
                        newHeight = startHeight + deltaY;
                    } else if (handle.classList.contains('resize-sw')) {
                        newWidth = startWidth - deltaX;
                        newHeight = startHeight + deltaY;
                    } else if (handle.classList.contains('resize-ne')) {
                        newWidth = startWidth + deltaX;
                        newHeight = startHeight - deltaY;
                    } else if (handle.classList.contains('resize-nw')) {
                        newWidth = startWidth - deltaX;
                        newHeight = startHeight - deltaY;
                    }
                    
                    // Mantener proporción
                    const ratio = startWidth / startHeight;
                    newHeight = newWidth / ratio;
                    
                    // Límites mínimos y máximos
                    newWidth = Math.max(100, Math.min(800, newWidth));
                    newHeight = Math.max(75, Math.min(600, newHeight));
                    
                    img.style.width = newWidth + 'px';
                    img.style.height = newHeight + 'px';
                    imageContainer.style.width = newWidth + 'px';
                };
                
                const handleMouseUp = () => {
                    document.removeEventListener('mousemove', handleMouseMove);
                    document.removeEventListener('mouseup', handleMouseUp);
                    this.showNotification('Imagen redimensionada');
                };
                
                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
        });
        
        // Mostrar handles al seleccionar
        imageContainer.addEventListener('mouseenter', () => {
            handles.forEach(handle => handle.style.display = 'block');
        });
        
        imageContainer.addEventListener('mouseleave', () => {
            handles.forEach(handle => handle.style.display = 'none');
        });
    },

    // Redimensionar imagen por botones
    resizeImage: function(imageId, size) {
        const imageContainer = document.getElementById(imageId);
        if (!imageContainer) return;
        
        const img = imageContainer.querySelector('img');
        if (!img) return;
        
        const originalWidth = img.naturalWidth;
        const originalHeight = img.naturalHeight;
        
        let newWidth, newHeight;
        
        switch(size) {
            case 'small':
                newWidth = originalWidth * 0.25;
                newHeight = originalHeight * 0.25;
                break;
            case 'medium':
                newWidth = originalWidth * 0.5;
                newHeight = originalHeight * 0.5;
                break;
            case 'large':
                newWidth = originalWidth;
                newHeight = originalHeight;
                break;
        }
        
        img.style.width = newWidth + 'px';
        img.style.height = newHeight + 'px';
        imageContainer.style.width = newWidth + 'px';
        
        this.showNotification(`Imagen redimensionada a ${size === 'small' ? '25%' : size === 'medium' ? '50%' : '100%'}`);
    },

    // Redimensionar video
    resizeVideo: function(videoId, size) {
        const videoContainer = document.getElementById(videoId);
        if (!videoContainer) return;
        
        const video = videoContainer.querySelector('video');
        if (!video) return;
        
        switch(size) {
            case 'small':
                video.style.maxWidth = '50%';
                video.style.minWidth = '250px';
                break;
            case 'large':
                video.style.maxWidth = '100%';
                video.style.minWidth = '400px';
                break;
        }
        
        this.showNotification(`Video redimensionado a ${size === 'small' ? '50%' : '100%'}`);
    },

    // Redimensionar audio
    resizeAudio: function(audioId, size) {
        const audioContainer = document.getElementById(audioId);
        if (!audioContainer) return;
        
        switch(size) {
            case 'small':
                audioContainer.style.minWidth = '250px';
                audioContainer.style.padding = '10px';
                break;
            case 'large':
                audioContainer.style.minWidth = '400px';
                audioContainer.style.padding = '20px';
                break;
        }
        
        this.showNotification(`Audio redimensionado a ${size === 'small' ? 'compacto' : 'extendido'}`);
    },

    // Manejar inicio de arrastre
    handleDragStart: function(event, mediaId) {
        event.dataTransfer.setData('text/plain', mediaId);
        event.dataTransfer.effectAllowed = 'move';
        
        const element = document.getElementById(mediaId);
        if (element) {
            element.style.opacity = '0.5';
        }
        
        console.log('🔄 Iniciando arrastre de elemento:', mediaId);
    },

    // Manejar arrastre sobre elemento
    handleDragOver: function(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    },

    // Manejar soltar elemento
    handleDrop: function(event, targetId) {
        event.preventDefault();
        
        const draggedId = event.dataTransfer.getData('text/plain');
        if (draggedId === targetId) return;
        
        const draggedElement = document.getElementById(draggedId);
        const targetElement = document.getElementById(targetId);
        
        if (draggedElement && targetElement) {
            // Intercambiar posiciones
            const draggedParent = draggedElement.parentNode;
            const targetParent = targetElement.parentNode;
            const draggedNextSibling = draggedElement.nextSibling;
            const targetNextSibling = targetElement.nextSibling;
            
            if (draggedNextSibling) {
                targetParent.insertBefore(draggedElement, draggedNextSibling);
            } else {
                targetParent.appendChild(draggedElement);
            }
            
            if (targetNextSibling) {
                draggedParent.insertBefore(targetElement, targetNextSibling);
            } else {
                draggedParent.appendChild(targetElement);
            }
            
            draggedElement.style.opacity = '1';
            this.showNotification('Elementos intercambiados exitosamente');
        }
    },

    // Alternar tamaño de imagen (función legacy mejorada)
    toggleImageSize: function(imageId) {
        const imageContainer = document.getElementById(imageId);
        if (!imageContainer) return;
        
        const img = imageContainer.querySelector('img');
        if (!img) return;
        
        const currentWidth = img.style.width || img.style.maxWidth || '100%';
        
        if (currentWidth.includes('100%') || currentWidth === '') {
            this.resizeImage(imageId, 'medium');
        } else if (currentWidth.includes('50%')) {
            this.resizeImage(imageId, 'small');
        } else {
            this.resizeImage(imageId, 'large');
        }
    },

    // Inicializar módulo
    init: function() {
        console.log('✅ Módulo de elementos multimedia inicializado');
        
        // Agregar estilos CSS adicionales para multimedia
        this.addMultimediaStyles();
    },

    // Agregar estilos CSS para multimedia
    addMultimediaStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* Estilos para botones multimedia */
            .multimedia-tool-btn {
                word-wrap: break-word;
                text-align: center !important;
                white-space: normal !important;
            }
            
            /* Estilos para panel multimedia */
            .multimedia-tools {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
                padding: 5px;
            }
            
            /* Estilos para arrastre */
            .media-container[draggable="true"] {
                cursor: move;
                transition: opacity 0.3s ease;
            }
            
            .media-container[draggable="true"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            /* Estilos para handles de redimensionamiento */
            .resize-handle {
                z-index: 1000;
                transition: all 0.2s ease;
            }
            
            .resize-handle:hover {
                background: #0056b3 !important;
                transform: scale(1.2);
            }
            
            /* Estilos para elementos multimedia seleccionados */
            .media-selected {
                transform: scale(1.02);
                transition: transform 0.3s ease;
            }
            
            /* Estilos para contenedores de audio */
            .audio-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 8px 25px rgba(102,126,234,0.3);
            }
            
            /* Animaciones para controles */
            .media-controls button {
                transition: all 0.2s ease;
            }
            
            .media-controls button:hover {
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            
            /* Indicador de carga */
            .media-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100px;
                background: #f8f9fa;
                border-radius: 8px;
                color: #6c757d;
            }
            
            /* Responsive para botones multimedia */
            @media (max-width: 768px) {
                .multimedia-tools {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            @media (max-width: 480px) {
                .multimedia-tools {
                    grid-template-columns: 1fr;
                }
                
                .multimedia-tool-btn {
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
        window.MultimediaTools.init();
    });
} else {
    window.MultimediaTools.init();
} 