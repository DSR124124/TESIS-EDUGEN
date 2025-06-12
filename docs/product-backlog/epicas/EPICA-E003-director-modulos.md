# EPICA-E003: Control y Desactivación de Módulos Pedagógicos

## 📝 Descripción de la Épica
Como **director**, necesito controlar y configurar los módulos pedagógicos disponibles en el sistema para personalizar las herramientas según las necesidades educativas de la institución.

## 🎯 Objetivos de Negocio
- Configurar módulos pedagógicos activos/inactivos
- Personalizar herramientas por nivel educativo
- Controlar acceso a funcionalidades avanzadas
- Adaptar la plataforma a metodología institucional
- Simplificar interfaz según necesidades

## 📊 Información General
- **Epic ID**: EPICA-E003
- **Rol**: 🎓 DIRECTOR
- **Prioridad**: 🔴 Must Have
- **Story Points**: 34 SP
- **Sprint Goal**: S3-S4 (4 semanas)
- **Dependencias**: EPICA-E001 (Administrador), EPICA-E002 (Personal)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Directores, Profesores (afectados)
- **Development Team**: Backend, Frontend

## 🎬 User Stories

### **US-03.1: Panel de Control de Módulos** (13 SP)
**Como** director  
**Quiero** un panel centralizado para gestionar módulos  
**Para** configurar las herramientas disponibles en la institución  

#### **Criterios de Aceptación**
- [ ] Lista visual de todos los módulos disponibles
- [ ] Toggle switch para activar/desactivar módulos
- [ ] Descripción clara de cada módulo y sus funcionalidades
- [ ] Vista previa de impacto al desactivar módulo
- [ ] Confirmación antes de cambios críticos
- [ ] Log de cambios realizados con fecha y usuario

#### **Módulos Controlables**
```yaml
Editor de Contenido:
  - Módulo de Formato de Texto: [Activo/Inactivo]
  - Módulo de Diseño y Layout: [Activo/Inactivo]
  - Módulo Multimedia: [Activo/Inactivo]
  - Módulo Educativo: [Activo/Inactivo]
  - Herramientas de IA: [Activo/Inactivo]

Funcionalidades Estudiante:
  - Sistema de Gamificación: [Activo/Inactivo]
  - Portfolios Temáticos: [Activo/Inactivo]
  - Progreso Detallado: [Activo/Inactivo]
  - Acceso Offline: [Activo/Inactivo]

Funcionalidades Avanzadas:
  - Paquetes SCORM: [Activo/Inactivo]
  - Análisis con IA: [Activo/Inactivo]
  - Reportes Avanzados: [Activo/Inactivo]
  - API Externa: [Activo/Inactivo]
```

---

### **US-03.2: Configuración por Nivel Educativo** (8 SP)
**Como** director  
**Quiero** configurar módulos específicos por nivel  
**Para** adaptar herramientas según la edad y capacidad de estudiantes  

#### **Criterios de Aceptación**
- [ ] Definición de niveles educativos (primaria, secundaria, universidad)
- [ ] Configuración independiente por nivel
- [ ] Plantillas predefinidas por tipo de institución
- [ ] Vista comparativa entre niveles
- [ ] Aplicación automática según nivel del estudiante
- [ ] Herencia de configuraciones padre-hijo

---

### **US-03.3: Impacto y Previsualización** (8 SP)
**Como** director  
**Quiero** ver el impacto de cambios antes de aplicarlos  
**Para** tomar decisiones informadas sobre la configuración  

#### **Criterios de Aceptación**
- [ ] Simulador de vista profesor con cambios aplicados
- [ ] Simulador de vista estudiante con cambios aplicados
- [ ] Contador de usuarios afectados por cambio
- [ ] Lista de funcionalidades que se perderán
- [ ] Recomendaciones automáticas del sistema
- [ ] Opción de reversión rápida de cambios

---

### **US-03.4: Notificaciones y Comunicación** (5 SP)
**Como** director  
**Quiero** comunicar cambios a usuarios afectados  
**Para** minimizar confusión y mantener transparencia  

#### **Criterios de Aceptación**
- [ ] Notificación automática a profesores sobre cambios
- [ ] Mensaje personalizado opcional del director
- [ ] Cronograma de aplicación de cambios
- [ ] Centro de ayuda con guías de nuevas configuraciones
- [ ] Feedback collection sobre cambios implementados
- [ ] Rollback comunicado si es necesario

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class ModuleConfiguration(models.Model):
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    module_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    configuration_json = models.JSONField(default=dict)
    education_level = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ModuleChangeLog(models.Model):
    configuration = models.ForeignKey(ModuleConfiguration, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20)  # activate, deactivate, configure
    previous_state = models.JSONField()
    new_state = models.JSONField()
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ModuleTemplate(models.Model):
    name = models.CharField(max_length=100)
    institution_type = models.CharField(max_length=50)
    description = models.TextField()
    default_configuration = models.JSONField()
    is_predefined = models.BooleanField(default=True)
```

### **API Endpoints**
```yaml
Module Management:
  GET    /api/director/modules/                    # Lista todos los módulos
  PUT    /api/director/modules/{module}/           # Actualizar estado de módulo
  POST   /api/director/modules/bulk-update/       # Actualización masiva
  GET    /api/director/modules/preview/           # Preview de cambios

Configuration:
  GET    /api/director/modules/templates/         # Plantillas disponibles
  POST   /api/director/modules/apply-template/    # Aplicar plantilla
  GET    /api/director/modules/impact/{module}/   # Análisis de impacto

Change Management:
  GET    /api/director/modules/changelog/         # Historial de cambios
  POST   /api/director/modules/rollback/{id}/     # Revertir cambio
  GET    /api/director/modules/affected-users/    # Usuarios afectados
```

### **Frontend Components**
```javascript
const ModuleControlComponents = {
  ModuleToggleGrid: {
    // Grid de switches para módulos
    features: ['bulk-actions', 'filter-by-category', 'search']
  },
  
  ImpactPreview: {
    // Simulador de impacto de cambios
    features: ['before-after-view', 'user-count', 'feature-comparison']
  },
  
  ConfigurationWizard: {
    // Asistente de configuración guiada
    features: ['step-by-step', 'templates', 'recommendations']
  },
  
  ChangeTimeline: {
    // Timeline de cambios realizados
    features: ['chronological-view', 'rollback-buttons', 'impact-metrics']
  }
}
```

## 🧪 Casos de Prueba

### **Test Suite: Module Management**
```python
class ModuleControlTestCase(TestCase):
    def test_activate_module(self):
        # Test activación de módulo
        pass
    
    def test_deactivate_module_with_users(self):
        # Test desactivación con usuarios activos
        pass
    
    def test_configuration_inheritance(self):
        # Test herencia de configuraciones
        pass
    
    def test_impact_analysis(self):
        # Test análisis de impacto correcto
        pass
```

### **Test Suite: Templates**
```python
class TemplateApplicationTestCase(TestCase):
    def test_apply_predefined_template(self):
        # Test aplicación de plantilla predefinida
        pass
    
    def test_custom_template_creation(self):
        # Test creación de plantilla personalizada
        pass
```

## 🎨 Diseño UX/UI

### **Principios de Diseño**
- **Control Intuitivo**: Switches claros y comprensibles
- **Feedback Visual**: Indicadores de estado y cambios
- **Seguridad**: Confirmaciones para cambios críticos
- **Transparencia**: Impacto claro de cada decisión

### **Interface Layout**
```css
.module-control-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.module-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.module-card.inactive {
  opacity: 0.6;
  background-color: #f5f5f5;
}

.impact-preview {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 2rem;
  margin: 1rem 0;
}
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Panel de control de módulos completamente funcional
- [ ] Configuración independiente por nivel educativo
- [ ] Sistema de previsualización de impacto
- [ ] Notificaciones automáticas a usuarios afectados
- [ ] Historial completo de cambios realizados
- [ ] Capacidad de rollback de cambios

### **No Funcionales**
- [ ] Cambios aplicados en tiempo real < 30 segundos
- [ ] Preview de impacto generado < 5 segundos
- [ ] Interfaz responsive en tablets y desktop
- [ ] Sin interrupciones para usuarios no afectados
- [ ] Recuperación automática en caso de fallos

### **Técnicos**
- [ ] Cobertura de tests > 90%
- [ ] Validaciones robustas antes de aplicar cambios
- [ ] Logs detallados de todas las operaciones
- [ ] Backup automático antes de cambios críticos
- [ ] API documentada para integraciones

## 📈 Métricas de Éxito

### **KPIs Operacionales**
- **Tiempo de configuración inicial**: <15 minutos
- **Precisión de preview**: >95% coincidencia con resultado real
- **Tiempo de aplicación de cambios**: <2 minutos
- **Tasa de rollback**: <5% de cambios revertidos

### **KPIs de Adopción**
- **Uso de plantillas**: >60% configuraciones usan plantillas
- **Personalización activa**: >80% instituciones modifican configuración default
- **Satisfacción directores**: >4.2/5 en facilidad de uso
- **Reducción de soporte**: >40% menos tickets relacionados con módulos

### **KPIs de Impacto**
- **Reducción tiempo configuración**: >50% vs configuración manual
- **Usuarios afectados negativamente**: <2% reportan problemas
- **Adopción post-cambio**: >85% usuarios continúan usando nuevas configuraciones

Esta épica proporciona **control granular y flexible** sobre las funcionalidades del sistema, permitiendo adaptación a diferentes contextos educativos. 