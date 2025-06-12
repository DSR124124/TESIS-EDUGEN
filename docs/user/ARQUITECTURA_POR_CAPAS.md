# Arquitectura por Capas del Sistema Educativo

Este documento detalla la implementación del patrón de arquitectura por capas en el sistema educativo, describiendo cada capa, sus responsabilidades, componentes principales y la forma en que se comunican entre sí.

## Visión General

El sistema educativo implementa una arquitectura de 4 capas claramente diferenciadas que promueven la separación de responsabilidades, facilitando el mantenimiento, escalabilidad y evolución del sistema.

```
┌─────────────────────────────────────────────────────────────┐
│                     Capa de Presentación                     │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      Capa de Aplicación                      │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       Capa de Dominio                        │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Capa de Infraestructura                    │
└─────────────────────────────────────────────────────────────┘
```

## Capa de Presentación

### Responsabilidad
Proporcionar interfaces de usuario, gestionar interacciones y presentar información al usuario final.

### Componentes Principales

1. **Templates Django**
   - Base de templates con herencia (base.html, base_student.html, base_teacher.html)
   - Componentes reutilizables (navbars, cards, modals)
   - Plantillas específicas para cada módulo funcional

2. **Vistas basadas en clases**
   - LoginView, LogoutView (autenticación)
   - ListView, DetailView, CreateView, UpdateView, DeleteView (operaciones CRUD)
   - Vistas especializadas por dominio (CourseView, PortfolioView, etc.)

3. **Formularios**
   - ModelForms para operaciones CRUD
   - Formularios con validación personalizada
   - Widgets personalizados para interfaces complejas

4. **Archivos estáticos**
   - CSS (Bootstrap 5 customizado)
   - JavaScript (ES6+, jQuery para algunas operaciones)
   - Imágenes y recursos visuales

5. **Componentes de interfaz especializados**
   - Editor GrapesJS para contenido WYSIWYG
   - Visualizadores de progreso de portafolios
   - Interfaces divididas para "Material de Clase" y "Material Personalizado"
   - Nuevo control de navegación con botón de usuario en la esquina superior derecha
   - Interfaz de perfil de estudiante mejorada con headers de gradiente

### Tecnologías
- HTML5/CSS3/JavaScript
- Bootstrap 5
- Django Template Language
- GrapesJS
- AJAX para operaciones asíncronas

### Implementación en archivos
- `templates/`: Todos los archivos HTML
- `static/`: Archivos CSS, JS e imágenes
- `*/forms.py`: Definiciones de formularios
- `*/views.py`: Controladores de vistas

## Capa de Aplicación

### Responsabilidad
Orquestar los flujos de trabajo, coordinar servicios y gestionar la lógica de aplicación sin contener reglas de negocio específicas.

### Componentes Principales

1. **Servicios de aplicación**
   - `OpenAIService`: Comunicación con API de OpenAI
   - `SCORMPackagerService`: Creación de paquetes SCORM
   - `PortfolioService`: Coordinación de operaciones con portafolios

2. **Tareas asíncronas**
   - `content_generation_task`: Generación de contenido en segundo plano
   - `portfolio_update_task`: Actualización programada de portafolios
   - `notification_task`: Envío de notificaciones a usuarios

3. **Coordinadores de flujos**
   - `ContentGenerationWorkflow`: Orquestación del proceso de generación
   - `EnrollmentCoordinator`: Gestión del proceso de matrícula
   - `MaterialDistributionCoordinator`: Distribución de materiales a portafolios

4. **API Views**
   - ViewSets para operaciones CRUD vía API REST
   - Serializers para transformación de datos
   - Permission classes para control de acceso

### Tecnologías
- Django Views y ViewSets
- Celery para procesamiento asíncrono
- Django REST Framework para API
- Signals de Django para comunicación entre componentes

### Implementación en archivos
- `*/services/`: Servicios de aplicación
- `*/tasks.py`: Tareas asíncronas de Celery
- `*/workflows.py`: Coordinadores de flujos complejos
- `api/views.py`: Endpoints de API REST

## Capa de Dominio

### Responsabilidad
Encapsular la lógica de negocio, reglas del dominio educativo y entidades centrales del sistema.

### Componentes Principales

1. **Modelos de dominio**
   - **Usuarios**: `CustomUser`, `Teacher`, `Student`, `Director`
   - **Académicos**: `Course`, `Grade`, `Section`, `Enrollment`
   - **Portafolios**: `StudentPortfolio`, `PortfolioTopic`, `PortfolioMaterial`
   - **Contenido**: `ContentType`, `ContentRequest`, `GeneratedContent`

2. **Servicios de dominio**
   - `PortfolioCalculationService`: Cálculo de progreso y estadísticas
   - `ContentEvaluationService`: Evaluación de calidad de contenido
   - `AcademicProgressService`: Seguimiento académico de estudiantes

3. **Validadores y reglas de negocio**
   - Validadores específicos del dominio educativo
   - Reglas para portafolios y progreso académico
   - Invariantes de dominio (restricciones y condiciones)
   - Lógica de clasificación de materiales por tipo ("Clase" o "Personalizado")

4. **Value Objects**
   - `Progress`: Objeto de valor para progreso (0-100%)
   - `MaterialType`: Enumeración para tipos de material
   - `AcademicPeriod`: Objeto para representar periodos académicos

### Tecnologías
- Models de Django
- Python para lógica de negocio
- Signals de Django para eventos de dominio
- Manager classes personalizados

### Implementación en archivos
- `*/models.py`: Definición de entidades
- `*/domain_services.py`: Servicios específicos de dominio
- `*/validators.py`: Lógica de validación
- `*/signals.py`: Eventos y reacciones del dominio

## Capa de Infraestructura

### Responsabilidad
Proporcionar capacidades técnicas para persistencia, comunicación externa, autenticación y operaciones transversales.

### Componentes Principales

1. **Persistencia**
   - ORM de Django para acceso a base de datos
   - Queries optimizadas y migrations
   - Managers personalizados para consultas complejas

2. **Integraciones externas**
   - Cliente de OpenAI API
   - Integración con Google OAuth 2.0
   - Conectores para servicios externos

3. **Infraestructura técnica**
   - Sistema de caché con Redis
   - Configuración de Celery para tareas asíncronas
   - Almacenamiento de archivos (local/S3)
   - Entorno virtual (.venv) para aislamiento de dependencias

4. **Seguridad**
  - Autenticación y autorización
   - Middleware de seguridad
   - Gestión de sesiones

### Tecnologías
- PostgreSQL (producción) / SQLite (desarrollo)
- Redis para caché y mensajería
- Django 4.2.10 con Django ORM
- Django REST Framework 3.14.0 para APIs
- Celery 5.3.6 para procesamiento asíncrono
- OpenAI 1.12.0 para generación de contenido
- Entorno virtual con Virtualenv para gestión de dependencias
- Pillow para procesamiento de imágenes
- Bibliotecas cliente para APIs externas
- Bootstrap 5 (via Crispy Forms)
- Python 3.11 como lenguaje base

### Implementación en archivos
- `config/settings/`: Configuración de infraestructura
- `*/repositories.py`: Acceso a datos
- `*/adapters/`: Adaptadores para sistemas externos
- `middleware/`: Componentes de procesamiento transversal
- `requirements.txt`: Definición de dependencias
- `activate.ps1`/`activate.sh`: Scripts para activación del entorno virtual

## Comunicación entre Capas

La comunicación entre capas sigue un patrón de dependencia descendente y principios de inversión de dependencia:

```
┌─────────────────────────┐
│  Capa de Presentación   │
└────────────┬────────────┘
             │ Llamadas a servicios/controladores
             ▼
┌─────────────────────────┐
│   Capa de Aplicación    │
└────────────┬────────────┘
             │ Manipulación de entidades
             ▼
┌─────────────────────────┐
│    Capa de Dominio      │
└────────────┬────────────┘
             │ Operaciones de infraestructura
             ▼
┌─────────────────────────┐
│Capa de Infraestructura  │
└─────────────────────────┘

   Comunicación inversa
          ^
          │
     Events/Signals
          │
          │
```

1. **Presentación → Aplicación**
   - Las vistas llaman a servicios de aplicación
   - Los formularios invocan operaciones de la capa de aplicación
   - La UI consume API endpoints

2. **Aplicación → Dominio**
   - Los servicios de aplicación coordinan entidades de dominio
   - Los workflows manipulan objetos de dominio
   - Las tareas asíncronas procesan entidades de dominio

3. **Dominio → Infraestructura**
   - Los modelos utilizan el ORM para persistencia
   - Los servicios de dominio utilizan repositorios
   - Los eventos de dominio disparan operaciones de infraestructura

4. **Comunicación inversa (eventos)**
   - Signals de Django para propagación de eventos entre capas
   - Patrón Observer para notificaciones
   - Callbacks para comunicación asíncrona

## Ejemplo de Flujo de Trabajo entre Capas

### Generación de Contenido Educativo

1. **Capa de Presentación**
   - Profesor completa formulario de solicitud de contenido
   - UI envía solicitud AJAX al endpoint correspondiente

2. **Capa de Aplicación**
   - `ContentGenerationAPIView` recibe la solicitud
   - `ContentGenerationService` coordina el proceso
   - Se crea tarea asíncrona `generate_content_task`

3. **Capa de Dominio**
   - Se crea entidad `ContentRequest`
   - `ContentEvaluationService` valida parámetros
   - Se aplican reglas de negocio educativas

4. **Capa de Infraestructura**
   - `OpenAIAdapter` se comunica con API externa
   - Redis gestiona cola de tareas asíncronas
   - ORM persiste el contenido generado

5. **Respuesta ascendente**
   - Signal `content_generated` notifica el evento
   - `ContentGenerationService` procesa el resultado
   - La UI se actualiza mediante WebSockets/polling

### Clasificación de Materiales Educativos

1. **Capa de Presentación**
   - Interfaz muestra secciones "Material de Clase" y "Material Personalizado"
   - Profesor sube o genera nuevo material educativo

2. **Capa de Aplicación**
   - `MaterialService` recibe la solicitud de creación
   - Determina el tipo de material (SCORM u otro)

3. **Capa de Dominio**
   - Se aplica lógica de clasificación según reglas de negocio
   - SCORM siempre se clasifica como "Material Personalizado"
   - Otros materiales según su origen y propiedades

4. **Capa de Infraestructura**
   - Se persiste material con su clasificación
   - Se almacenan archivos en sistema de archivos/S3

5. **Presentación de resultados**
   - La interfaz de usuario muestra el material en la sección correspondiente
   - Se actualiza el contador de materiales por categoría

## Beneficios de la Arquitectura por Capas

1. **Separación de responsabilidades**
   - Cada capa tiene un propósito claro y delimitado
   - Cambios en una capa no afectan necesariamente a otras

2. **Mantenibilidad**
   - Código organizado por función/responsabilidad
   - Facilidad para encontrar y modificar componentes específicos

3. **Testeabilidad**
   - Pruebas unitarias enfocadas en cada capa
   - Posibilidad de mockear capas inferiores

4. **Escalabilidad**
   - Posibilidad de escalar componentes específicos
   - Distribución de carga entre capas

5. **Evolución**
   - Cambios tecnológicos afectan principalmente a una capa
   - Adaptabilidad a nuevos requisitos o tecnologías

## Consideraciones de Implementación

1. **Evitar dependencias circulares**
   - Mantener flujo de dependencia en una dirección
   - Usar eventos para comunicación inversa

2. **Interfaces claras entre capas**
   - DTOs para transferencia de datos
   - Contratos explícitos entre servicios

3. **No saltarse capas**
   - Respetar jerarquía de dependencias
   - Evitar que presentación acceda directamente al dominio

4. **Balance entre pureza y pragmatismo**
   - Framework Django impone ciertos compromisos
   - Pragmatismo en la implementación manteniendo conceptos separados

## Mejoras Recientes en la Arquitectura

1. **Mejoras en la Capa de Presentación**
   - Rediseño de la interfaz de estudiante con navegación simplificada
   - Implementación de botón de usuario elegante en la esquina superior derecha
   - Eliminación de secciones poco utilizadas (Calendario Académico, Próximas Entregas)
   - Mejora del perfil de estudiante con estilos consistentes y headers de gradiente

2. **Mejoras en la Capa de Dominio**
   - Implementación de lógica para prevenir errores con archivos faltantes
   - Clasificación automática de materiales en "Material de Clase" y "Material Personalizado"
   - Configuración de paquetes SCORM para aparecer siempre en sección "Material Personalizado"

3. **Mejoras en la Documentación**
   - Diagrama de entidad-relación completo en docs/user/database_diagram.md
   - Diagrama de clases visualizando relaciones de objetos en docs/user/class_diagram.md
   - Documentación detallada de entidades y sus relaciones

## Próximas Mejoras Planeadas

1. **Capa de Presentación**
   - Implementación de tema oscuro (dark mode)
   - Mejora de accesibilidad según estándares WCAG
   - Optimización para dispositivos móviles

2. **Capa de Aplicación**
   - Implementación de caché de nivel de aplicación para contenidos frecuentes
   - Sistema de notificaciones en tiempo real
   - Mejora del rendimiento en generación de contenido

3. **Capa de Dominio**
   - Extensión de reglas de negocio para evaluación automática
   - Nuevos tipos de materiales educativos
   - Refinamiento del modelo de progreso del estudiante

4. **Capa de Infraestructura**
   - Migración completa a contenedores Docker
   - Implementación de CI/CD para despliegue continuo
   - Mejoras en seguridad y auditoría

## Conclusión

La arquitectura por capas implementada en el sistema educativo proporciona una estructura organizada y modular que facilita el desarrollo, mantenimiento y evolución del sistema. La clara separación de responsabilidades entre presentación, aplicación, dominio e infraestructura permite que cada componente se centre en su función específica, resultando en un sistema más robusto, escalable y adaptable a cambios futuros en requisitos o tecnologías.

El diseño actual refleja un equilibrio entre los principios teóricos de la arquitectura por capas y las consideraciones prácticas de implementación con Django, resultando en un sistema que aprovecha las ventajas del framework mientras mantiene una estructura conceptual limpia y bien organizada. 