# EPICA-E007: Asignación de Materiales en Portfolios

## 📝 Descripción de la Épica
Como **profesor**, necesito asignar materiales educativos a portfolios estudiantiles organizados por tema para estructurar el contenido de aprendizaje y facilitar el acceso de estudiantes a recursos específicos.

## 🎯 Objetivos de Negocio
- Organizar materiales educativos en portfolios temáticos
- Asignar contenido específico a grupos de estudiantes
- Crear rutas de aprendizaje personalizadas
- Facilitar acceso estructurado al contenido
- Monitorear consumo de materiales asignados

## 📊 Información General
- **Epic ID**: EPICA-E007
- **Rol**: 👨‍🏫 PROFESOR
- **Prioridad**: 🔴 Must Have
- **Story Points**: 55 SP
- **Sprint Goal**: S8-S9 (4 semanas)
- **Dependencias**: EPICA-E005 (Editor Contenido)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Profesores, Estudiantes
- **Development Team**: Backend, Frontend

## 🎬 User Stories

### **US-07.1: Creación de Portfolios Temáticos** (21 SP)
**Como** profesor  
**Quiero** crear portfolios organizados por tema  
**Para** estructurar el contenido de manera lógica para estudiantes  

#### **Criterios de Aceptación**
- [ ] Creación de portfolios con título y descripción
- [ ] Organización jerárquica de temas y subtemas
- [ ] Configuración de orden de visualización
- [ ] Asignación de iconos y colores temáticos
- [ ] Fechas de disponibilidad por portfolio
- [ ] Plantillas predefinidas por materia

#### **Estructura de Portfolio**
```yaml
Portfolio Structure:
  title: "Álgebra Lineal - Fundamentos"
  description: "Conceptos básicos de vectores y matrices"
  theme_color: "#4CAF50"
  icon: "calculate"
  
  sections:
    - name: "Vectores"
      order: 1
      materials: []
    - name: "Matrices"
      order: 2
      materials: []
    - name: "Determinantes"
      order: 3
      materials: []
```

---

### **US-07.2: Asignación de Materiales a Portfolios** (13 SP)
**Como** profesor  
**Quiero** asignar materiales creados a portfolios específicos  
**Para** organizar el contenido en rutas de aprendizaje coherentes  

#### **Criterios de Aceptación**
- [ ] Selección múltiple de materiales para asignar
- [ ] Drag & drop para organizar materiales en portfolios
- [ ] Configuración de orden dentro del portfolio
- [ ] Asignación a múltiples portfolios simultáneamente
- [ ] Previsualización de estructura final
- [ ] Validación de coherencia temática

---

### **US-07.3: Gestión de Acceso por Estudiante** (8 SP)
**Como** profesor  
**Quiero** controlar qué estudiantes acceden a qué portfolios  
**Para** personalizar la experiencia de aprendizaje  

#### **Criterios de Aceptación**
- [ ] Asignación masiva de portfolios a grupos de estudiantes
- [ ] Configuración de acceso individual por estudiante
- [ ] Fechas de inicio y fin de acceso
- [ ] Prerrequisitos entre portfolios
- [ ] Notificación automática de nuevos portfolios asignados
- [ ] Vista de permisos y accesos actuales

---

### **US-07.4: Monitoreo de Progreso en Portfolios** (8 SP)
**Como** profesor  
**Quiero** monitorear el progreso de estudiantes en portfolios  
**Para** identificar dificultades y ajustar el contenido  

#### **Criterios de Aceptación**
- [ ] Dashboard de progreso por portfolio y estudiante
- [ ] Métricas de tiempo dedicado por sección
- [ ] Identificación de materiales más/menos consultados
- [ ] Alertas de estudiantes con progreso lento
- [ ] Reportes de completitud por tema
- [ ] Comparativas entre diferentes portfolios

---

### **US-07.5: Versionado y Actualización de Portfolios** (5 SP)
**Como** profesor  
**Quiero** versionar y actualizar portfolios  
**Para** mejorar el contenido sin afectar estudiantes activos  

#### **Criterios de Aceptación**
- [ ] Sistema de versiones para portfolios
- [ ] Actualización sin interrumpir estudiantes activos
- [ ] Notificación de cambios a estudiantes
- [ ] Rollback a versiones anteriores si es necesario
- [ ] Comparación entre versiones
- [ ] Migración gradual de estudiantes a nuevas versiones

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class PortfolioTemplate(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject_area = models.CharField(max_length=100)
    theme_color = models.CharField(max_length=7, default='#4CAF50')
    icon = models.CharField(max_length=50, default='folder')
    is_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Portfolio(models.Model):
    template = models.ForeignKey(PortfolioTemplate, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True)
    available_until = models.DateTimeField(null=True)

class PortfolioSection(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    prerequisites = models.ManyToManyField('self', blank=True)

class PortfolioMaterial(models.Model):
    section = models.ForeignKey(PortfolioSection, on_delete=models.CASCADE)
    content = models.ForeignKey('ModularContent', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_required = models.BooleanField(default=True)
    estimated_duration = models.DurationField(null=True)
    
class StudentPortfolioAccess(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    started_date = models.DateTimeField(null=True)
    completed_date = models.DateTimeField(null=True)
    completion_percentage = models.FloatField(default=0.0)
```

### **API Endpoints**
```yaml
Portfolio Management:
  GET    /api/teacher/portfolios/              # Lista portfolios
  POST   /api/teacher/portfolios/              # Crear portfolio
  GET    /api/teacher/portfolios/{id}/         # Detalle portfolio
  PUT    /api/teacher/portfolios/{id}/         # Actualizar portfolio
  DELETE /api/teacher/portfolios/{id}/         # Eliminar portfolio

Material Assignment:
  POST   /api/teacher/portfolios/{id}/materials/ # Asignar materiales
  PUT    /api/teacher/portfolios/{id}/reorder/   # Reordenar contenido
  DELETE /api/teacher/portfolio-materials/{id}/ # Quitar material

Student Access:
  POST   /api/teacher/portfolios/{id}/assign/   # Asignar a estudiantes
  GET    /api/teacher/portfolios/{id}/students/ # Ver estudiantes asignados
  PUT    /api/teacher/portfolio-access/{id}/    # Modificar acceso

Progress Monitoring:
  GET    /api/teacher/portfolios/{id}/progress/ # Progreso general
  GET    /api/teacher/students/{id}/portfolios/ # Progreso por estudiante
  GET    /api/teacher/portfolios/{id}/analytics/ # Analíticas detalladas
```

## 🧪 Casos de Prueba

### **Test Suite: Portfolio Management**
```python
class PortfolioManagementTestCase(TestCase):
    def test_create_portfolio_structure(self):
        # Test creación de portfolio con secciones
        pass
    
    def test_assign_materials_to_portfolio(self):
        # Test asignación de materiales
        pass
    
    def test_student_access_control(self):
        # Test control de acceso de estudiantes
        pass

class PortfolioProgressTestCase(TestCase):
    def test_progress_calculation(self):
        # Test cálculo de progreso
        pass
    
    def test_completion_tracking(self):
        # Test tracking de completitud
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Creación y gestión completa de portfolios temáticos
- [ ] Asignación flexible de materiales a portfolios
- [ ] Control granular de acceso por estudiante
- [ ] Monitoreo detallado de progreso
- [ ] Sistema de versionado para actualizaciones

### **No Funcionales**
- [ ] Carga de portfolios < 2 segundos
- [ ] Asignación masiva < 30 segundos para 100 estudiantes
- [ ] Interfaz responsive para gestión en tablets
- [ ] Sincronización en tiempo real de cambios
- [ ] Soporte para 50+ portfolios por profesor

### **Técnicos**
- [ ] Cobertura de tests > 85%
- [ ] API REST documentada
- [ ] Validaciones de integridad de datos
- [ ] Optimización de consultas para progreso
- [ ] Backup automático de asignaciones

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Portfolios creados**: >3 por profesor activo
- **Materiales asignados**: >80% contenido organizado en portfolios
- **Acceso estudiantes**: >90% estudiantes acceden a portfolios asignados
- **Completitud promedio**: >70% portfolios completados por estudiantes

### **KPIs de Eficiencia**
- **Tiempo organización**: >50% reducción vs organización manual
- **Satisfacción profesores**: >4.2/5 en facilidad de asignación
- **Engagement estudiantes**: >60% tiempo en portfolios vs navegación libre
- **Precisión progreso**: >95% tracking correcto de avance

Esta épica proporciona la **estructura organizacional** fundamental para la experiencia educativa de los estudiantes. 