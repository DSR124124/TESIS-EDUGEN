# EPICA-E006: Importación y Uso de Paquetes SCORM

## 📝 Descripción de la Épica
Como **profesor**, necesito importar y utilizar paquetes educativos SCORM para integrar contenido externo profesional y aprovechar recursos educativos estándar de la industria.

## 🎯 Objetivos de Negocio
- Integrar contenido educativo estándar SCORM 1.2 y 2004
- Reutilizar recursos educativos externos de calidad
- Trackear progreso de estudiantes en contenido SCORM
- Reducir tiempo de creación de contenido especializado
- Cumplir estándares de e-learning internacionales

## 📊 Información General
- **Epic ID**: EPICA-E006
- **Rol**: 👨‍🏫 PROFESOR
- **Prioridad**: 🟡 Should Have
- **Story Points**: 55 SP
- **Sprint Goal**: S7-S8 (4 semanas)
- **Dependencias**: EPICA-E005 (Editor Contenido)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Profesores, Estudiantes
- **Development Team**: Backend, Frontend

## 🎬 User Stories

### **US-06.1: Importación de Paquetes SCORM** (21 SP)
**Como** profesor  
**Quiero** importar paquetes SCORM a mi curso  
**Para** utilizar contenido educativo profesional  

#### **Criterios de Aceptación**
- [ ] Subida de archivos ZIP SCORM (hasta 100MB)
- [ ] Validación automática de estructura SCORM
- [ ] Soporte para SCORM 1.2 y SCORM 2004
- [ ] Preview del contenido antes de publicar
- [ ] Detección automática de metadatos del paquete
- [ ] Logs de errores detallados en caso de falla

#### **Formatos Soportados**
```yaml
SCORM Versions:
  - SCORM_1_2: "1.2 ADL SCORM"
  - SCORM_2004: "2004 3rd/4th Edition"
  
File Requirements:
  - max_size: 100MB
  - format: ZIP compressed
  - structure: imsmanifest.xml required
  - content: HTML, Flash, HTML5 supported
```

---

### **US-06.2: Gestión de Biblioteca SCORM** (13 SP)
**Como** profesor  
**Quiero** gestionar mi biblioteca de paquetes SCORM  
**Para** reutilizar contenido en múltiples cursos  

#### **Criterios de Aceptación**
- [ ] Lista de paquetes SCORM importados
- [ ] Información detallada de cada paquete (título, descripción, duración)
- [ ] Búsqueda y filtrado por temática o nivel
- [ ] Previsualización de contenido SCORM
- [ ] Duplicación de paquetes entre cursos
- [ ] Eliminación con confirmación

---

### **US-06.3: Integración en Estructura de Curso** (8 SP)
**Como** profesor  
**Quiero** integrar paquetes SCORM en mi estructura de curso  
**Para** crear un flujo de aprendizaje coherente  

#### **Criterios de Aceptación**
- [ ] Inserción de SCORM en unidades específicas
- [ ] Ordenamiento con otros tipos de contenido
- [ ] Configuración de prerrequisitos
- [ ] Asignación de puntajes y pesos
- [ ] Configuración de intentos permitidos
- [ ] Fechas de disponibilidad

---

### **US-06.4: Tracking y Progreso SCORM** (13 SP)
**Como** profesor  
**Quiero** monitorear el progreso de estudiantes en contenido SCORM  
**Para** evaluar el aprendizaje y dar seguimiento  

#### **Criterios de Aceptación**
- [ ] Dashboard de progreso por estudiante
- [ ] Reportes de tiempo dedicado por paquete
- [ ] Status de completitud (started, incomplete, completed)
- [ ] Puntajes obtenidos en evaluaciones SCORM
- [ ] Tracking de intentos y reintentos
- [ ] Exportar reportes de progreso

#### **Métricas SCORM**
```yaml
Student Progress:
  - completion_status: [incomplete, completed, failed, passed]
  - score_raw: numeric score
  - score_min: minimum passing score
  - score_max: maximum possible score
  - time_spent: session duration
  - attempts_count: number of attempts
  - first_access: initial start date
  - last_access: most recent activity
```

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class SCORMPackage(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=10)  # 1.2, 2004
    file_path = models.FileField(upload_to='scorm_packages/')
    manifest_data = models.JSONField()
    description = models.TextField(blank=True)
    duration_estimate = models.DurationField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SCORMActivity(models.Model):
    course_unit = models.ForeignKey('CourseUnit', on_delete=models.CASCADE)
    scorm_package = models.ForeignKey(SCORMPackage, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    max_attempts = models.PositiveIntegerField(default=1)
    weight_percentage = models.FloatField(default=0.0)
    available_from = models.DateTimeField(null=True)
    available_until = models.DateTimeField(null=True)

class SCORMAttempt(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    scorm_activity = models.ForeignKey(SCORMActivity, on_delete=models.CASCADE)
    attempt_number = models.PositiveIntegerField()
    completion_status = models.CharField(max_length=20)
    score_raw = models.FloatField(null=True)
    score_min = models.FloatField(null=True)
    score_max = models.FloatField(null=True)
    time_spent = models.DurationField(default=timedelta(0))
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
```

### **API Endpoints**
```yaml
SCORM Management:
  POST   /api/teacher/scorm/upload/           # Subir paquete SCORM
  GET    /api/teacher/scorm/                  # Lista de paquetes
  GET    /api/teacher/scorm/{id}/             # Detalle del paquete
  DELETE /api/teacher/scorm/{id}/             # Eliminar paquete
  GET    /api/teacher/scorm/{id}/preview/     # Preview del contenido

Course Integration:
  POST   /api/teacher/courses/{id}/scorm/     # Agregar SCORM a curso
  PUT    /api/teacher/scorm-activities/{id}/  # Configurar actividad
  GET    /api/teacher/scorm-activities/{id}/progress/ # Progreso estudiantes

Student Interaction:
  GET    /api/student/scorm/{id}/launch/      # Lanzar contenido SCORM
  POST   /api/student/scorm/{id}/track/       # Tracking de progreso
  GET    /api/student/scorm/{id}/resume/      # Reanudar sesión
```

### **SCORM Runtime**
```javascript
// SCORM API Implementation
class SCORMRuntime {
  constructor(attemptId, studentId) {
    this.attemptId = attemptId;
    this.studentId = studentId;
    this.data = {};
  }

  LMSInitialize() {
    // Initialize SCORM session
    return "true";
  }

  LMSGetValue(element) {
    // Get SCORM data element
    return this.data[element] || "";
  }

  LMSSetValue(element, value) {
    // Set SCORM data element
    this.data[element] = value;
    this.saveToServer();
    return "true";
  }

  LMSCommit() {
    // Commit data to server
    this.saveToServer();
    return "true";
  }

  saveToServer() {
    fetch(`/api/student/scorm/${this.attemptId}/track/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(this.data)
    });
  }
}
```

## 🧪 Casos de Prueba

### **Test Suite: SCORM Processing**
```python
class SCORMProcessingTestCase(TestCase):
    def test_scorm_upload_validation(self):
        # Test validación de paquetes SCORM
        pass
    
    def test_manifest_parsing(self):
        # Test parsing del imsmanifest.xml
        pass
    
    def test_scorm_12_compatibility(self):
        # Test compatibilidad SCORM 1.2
        pass

class SCORMTrackingTestCase(TestCase):
    def test_progress_tracking(self):
        # Test tracking de progreso estudiante
        pass
    
    def test_score_calculation(self):
        # Test cálculo de puntuaciones
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Importación exitosa de paquetes SCORM 1.2 y 2004
- [ ] Biblioteca de gestión de paquetes SCORM
- [ ] Integración fluida en estructura de cursos
- [ ] Tracking completo de progreso estudiantil
- [ ] Reportes detallados de actividad SCORM

### **No Funcionales**
- [ ] Subida de paquetes < 2 minutos para 100MB
- [ ] Lanzamiento de contenido < 5 segundos
- [ ] Compatibilidad con navegadores modernos
- [ ] Sincronización de datos en tiempo real
- [ ] Soporte para 100+ estudiantes concurrentes

### **Técnicos**
- [ ] Cumplimiento estándares SCORM 1.2/2004
- [ ] API JavaScript completa para tracking
- [ ] Validación robusta de paquetes
- [ ] Backup automático de datos de progreso
- [ ] Logs detallados para debugging

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Paquetes SCORM subidos**: >5 por profesor activo
- **Uso en cursos**: >30% cursos incluyen contenido SCORM
- **Completitud estudiantes**: >70% completan actividades SCORM
- **Satisfacción profesores**: >4.0/5 con funcionalidad SCORM

### **KPIs Técnicos**
- **Tasa éxito subida**: >95% paquetes procesados correctamente
- **Precisión tracking**: >99% datos guardados correctamente
- **Performance**: Contenido carga <5 segundos
- **Compatibilidad**: >90% paquetes SCORM funcionan sin problemas

Esta épica permite **integración profesional** con el ecosistema global de contenido educativo SCORM. 