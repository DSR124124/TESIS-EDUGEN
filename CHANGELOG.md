# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Estructura inicial del proyecto
- Sistema de autenticación
- Gestión de usuarios y roles
- Dashboard para profesores
- Generación de contenido con IA
- Sistema de portafolios

### Changed
- Mejorada la estructura del proyecto
- Actualizada la documentación
- Optimizado el sistema de generación de contenido

### Fixed
- Corregidos problemas de rendimiento
- Solucionados errores de seguridad
- Mejorado el manejo de errores

## [0.1.0] - 2024-04-17

### Added
- Versión inicial del sistema
- Funcionalidades básicas implementadas

## [NUEVO] - 2024-XX-XX

### Correcciones
- **Materiales SCORM**: Corregidas las acciones para materiales de tipo SCORM en la interfaz de profesor
  - Solucionado error al acceder a `material.scorm_id` cuando no existe el paquete SCORM
  - Mejorada la verificación de existencia de paquetes SCORM antes de generar URLs
  - Reemplazado sistema de búsqueda de texto por verificación directa del campo `scorm_package`
  - Agregado manejo de casos donde material está marcado como SCORM pero no tiene paquete asociado
  - Eliminado JavaScript complejo e innecesario para manejo de enlaces SCORM
  - Implementada lógica consistente entre templates de dashboard y portfolios

### Técnico
- Actualizado template `course_topic_detail.html` con verificaciones seguras para materiales SCORM
- Actualizado template `topic_detail.html` para usar enlaces directos en lugar de JavaScript
- Mejorada vista `CourseTopicDetailView` para establecer correctamente atributos SCORM
- Mejorada vista `TopicDetailView` para consistencia en manejo de materiales SCORM
- Agregada lógica de recuperación automática de paquetes SCORM huérfanos 