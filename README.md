# 🎓 Sistema Educativo - EduGen

Un sistema integral de gestión educativa desarrollado en Django con funcionalidades avanzadas de IA para la generación de contenido educativo.

## 🚀 Características Principales


### 📚 Gestión Académica
- **Gestión de Estudiantes**: Perfiles completos, historiales académicos
- **Gestión de Profesores**: Asignación de materias y seguimiento
- **Secciones y Grados**: Organización jerárquica de estudiantes
- **Inscripciones**: Sistema automatizado de matrículas

### 🤖 Generación de Contenido con IA
- **DeepSeek AI Integration**: Generación automática de contenido educativo
- **Contenido Interactivo**: Actividades, exámenes y material didáctico
- **Personalización**: Adaptación del contenido según el nivel educativo

### 📁 Portafolios Digitales
- **Portafolios de Estudiantes**: Seguimiento del progreso académico
- **Gestión de Temas**: Organización temática del contenido
- **Materiales Educativos**: Repositorio centralizado de recursos

### 🏫 Gestión Institucional
- **Multi-institución**: Soporte para múltiples instituciones educativas
- **Configuraciones Personalizadas**: Temas, colores y configuraciones específicas
- **Panel de Director**: Dashboard ejecutivo con métricas clave

### 📊 Analytics y Reportes
- **Métricas de Uso**: Seguimiento del engagement estudiantil
- **Progreso Académico**: Análisis del rendimiento por estudiante
- **Reportes Institucionales**: Estadísticas y KPIs educativos

### 🔐 Autenticación Avanzada
- **Google OAuth**: Inicio de sesión con cuentas institucionales
- **Roles y Permisos**: Sistema granular de acceso
- **Seguridad**: Protección de datos estudiantiles

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2+**: Framework web principal
- **Django REST Framework**: API RESTful
- **PostgreSQL**: Base de datos principal (producción)
- **SQLite**: Base de datos local (desarrollo)

### Frontend
- **Bootstrap 5**: Framework CSS
- **Django Crispy Forms**: Formularios mejorados
- **TinyMCE**: Editor WYSIWYG
- **GrapesJS**: Constructor visual de páginas

### Integraciones
- **DeepSeek API**: Inteligencia artificial
- **Google OAuth2**: Autenticación social
- **Azure Storage**: Almacenamiento en la nube
- **SCORM**: Estándares e-learning

### DevOps
- **Azure App Service**: Hosting en la nube
- **GitHub Actions**: CI/CD automático
- **Gunicorn**: Servidor WSGI
- **WhiteNoise**: Archivos estáticos

## 🔧 Instalación y Configuración

### Prerrequisitos
- Python 3.11+
- Git
- PostgreSQL (para producción)

### Instalación Local

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd sistema-educativo
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate     # Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar servidor:**
   ```bash
   python manage.py runserver
   ```

## 🌐 Despliegue en Azure

### Variables de Entorno Requeridas
```env
SECRET_KEY=tu-clave-secreta-django
DATABASE_URL=postgresql://usuario:password@host:5432/database
ALLOWED_HOSTS=tu-dominio.azurewebsites.net
DEEPSEEK_API_KEY=tu-api-key-deepseek
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=tu-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=tu-google-client-secret
```

### Configuración de Azure
1. **Azure App Service**: Plan Basic B1
2. **PostgreSQL Flexible Server**: Standard_B1ms
3. **GitHub Actions**: Despliegue automático
4. **SSL/TLS**: Certificado automático

## 📁 Estructura del Proyecto

```
sistema-educativo/
├── apps/                          # Aplicaciones Django
│   ├── accounts/                  # Gestión de usuarios
│   ├── academic/                  # Sistema académico
│   ├── ai_content_generator/      # Generación IA
│   ├── analytics/                 # Métricas y reportes
│   ├── content/                   # Gestión de contenido
│   ├── dashboard/                 # Panel principal
│   ├── director/                  # Panel directivo
│   ├── institutions/              # Gestión institucional
│   ├── portfolios/                # Portafolios digitales
│   └── scorm_packager/           # Empaquetado SCORM
├── config/                        # Configuraciones
│   ├── settings/                  # Settings por ambiente
│   ├── urls.py                    # URLs principales
│   └── wsgi.py                    # WSGI config
├── static/                        # Archivos estáticos
├── templates/                     # Plantillas HTML
├── media/                         # Archivos subidos
├── .github/workflows/             # GitHub Actions
├── requirements.txt               # Dependencias Python
├── requirements-azure.txt         # Dependencias Azure
└── manage.py                      # CLI Django
```

## 🎯 Funcionalidades por Rol

### 👨‍🎓 Estudiante
- Ver portafolio personal
- Acceder a materiales de estudio
- Realizar actividades interactivas
- Seguir progreso académico

### 👨‍🏫 Profesor
- Crear contenido educativo con IA
- Gestionar estudiantes asignados
- Generar reportes de progreso
- Administrar materiales de clase

### 👨‍💼 Director
- Dashboard ejecutivo
- Gestión institucional
- Reportes analíticos
- Configuración del sistema

### 👨‍💻 Administrador
- Gestión completa del sistema
- Configuración de usuarios
- Mantenimiento de datos
- Configuración de integraciones

## 🔐 Seguridad y Privacidad

- **Protección de Datos**: Cumplimiento con estándares educativos
- **Autenticación Segura**: OAuth2 y sessions cifradas
- **Permisos Granulares**: Control de acceso por rol
- **Backup Automático**: Respaldo regular de datos
- **SSL/TLS**: Comunicación cifrada

## 📈 Métricas y Analytics

### KPIs Principales
- Engagement estudiantil
- Progreso académico por materia
- Uso de contenido generado por IA
- Tiempo de sesión promedio
- Completitud de portafolios

### Reportes Disponibles
- Rendimiento por estudiante
- Estadísticas institucionales
- Uso de la plataforma
- Efectividad del contenido IA

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o consultas:
- **Issues**: Abrir un issue en GitHub
- **Documentación**: Ver la wiki del proyecto
- **Contacto**: [tu-email@dominio.com]

## 🗺️ Roadmap

### Próximas Funcionalidades
- [ ] Integración con LMS externos
- [ ] App móvil nativa
- [ ] Videoconferencias integradas
- [ ] Gamificación del aprendizaje
- [ ] Reportes avanzados con ML
- [ ] Integración con calendarios
- [ ] Sistema de notificaciones push
- [ ] Evaluaciones automáticas con IA

---

Desarrollado con ❤️ para la educación del futuro 