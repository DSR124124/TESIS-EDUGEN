# EPICA-E004: Administración de Cursos y Estudiantes

## 📝 Descripción de la Épica
Como **profesor**, necesito administrar mis cursos asignados y gestionar estudiantes para organizar el proceso educativo, crear estructura académica y monitorear el progreso de mis estudiantes.

## 🎯 Objetivos de Negocio
- Gestionar estructura de cursos y materias
- Organizar estudiantes por secciones y grupos
- Crear calendario académico y cronogramas
- Monitorear asistencia y participación
- Evaluar y calificar estudiantes

## 📊 Información General
- **Epic ID**: EPICA-E004
- **Rol**: 👨‍🏫 PROFESOR
- **Prioridad**: 🔴 Must Have
- **Story Points**: 89 SP
- **Sprint Goal**: S4-S6 (6 semanas)
- **Dependencias**: EPICA-E002 (Personal Docente)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Profesores, Estudiantes (indirectos)
- **Development Team**: Backend, Frontend, UX/UI Designer

## 🎬 User Stories

### **US-04.1: Dashboard de Cursos del Profesor** (21 SP)
**Como** profesor  
**Quiero** un dashboard centralizado de mis cursos  
**Para** acceder rápidamente a toda mi información académica  

#### **Criterios de Aceptación**
- [ ] Vista de tarjetas con todos los cursos asignados
- [ ] Información resumida por curso (estudiantes, progreso, actividades)
- [ ] Acceso rápido al editor de contenido por curso
- [ ] Calendarios de actividades y entregas
- [ ] Notificaciones pendientes por curso
- [ ] Estadísticas de engagement por curso

#### **Información por Curso**
```yaml
Curso Card:
  - nombre_curso: "Matemáticas Avanzadas"
  - codigo_curso: "MAT-301"
  - periodo_academico: "2025-1"
  - total_estudiantes: 28
  - progreso_promedio: 75%
  - actividades_pendientes: 3
  - ultima_actividad: "Hace 2 días"
  - proximo_vencimiento: "Tarea 3 - 15 Mar"
```

---

### **US-04.2: Gestión de Estudiantes por Curso** (21 SP)
**Como** profesor  
**Quiero** gestionar la lista de estudiantes de mis cursos  
**Para** mantener control de la clase y personalizar la enseñanza  

#### **Criterios de Aceptación**
- [ ] Lista completa de estudiantes inscritos por curso
- [ ] Perfiles básicos de estudiantes con foto
- [ ] Estados de estudiantes (activo, inactivo, retirado)
- [ ] Agrupación de estudiantes por equipos o secciones
- [ ] Comunicación directa con estudiantes
- [ ] Exportar listas de estudiantes

#### **Funcionalidades de Gestión**
```yaml
Lista de Estudiantes:
  - vista_tabla: sortable, filterable
  - vista_tarjetas: fotos y info básica
  - busqueda_rapida: por nombre o código
  - filtros: estado, rendimiento, grupo
  
Acciones Estudiante:
  - enviar_mensaje_individual: directo
  - asignar_grupo: drag and drop
  - ver_progreso_detallado: modal
  - exportar_datos: Excel, PDF
```

---

### **US-04.3: Estructura de Contenido por Temas** (13 SP)
**Como** profesor  
**Quiero** organizar mi curso en unidades y temas  
**Para** crear una estructura lógica de aprendizaje  

#### **Criterios de Aceptación**
- [ ] Creación de unidades temáticas
- [ ] Organización jerárquica de contenidos
- [ ] Arrastrar y soltar para reordenar temas
- [ ] Fechas de inicio y fin por unidad
- [ ] Prerrequisitos entre unidades
- [ ] Vista de árbol expandible de contenidos

#### **Estructura Jerárquica**
```
Curso: Matemáticas Avanzadas
├── Unidad 1: Cálculo Diferencial
│   ├── Tema 1.1: Límites y continuidad
│   ├── Tema 1.2: Derivadas básicas
│   └── Tema 1.3: Aplicaciones de derivadas
├── Unidad 2: Cálculo Integral
│   ├── Tema 2.1: Integrales indefinidas
│   └── Tema 2.2: Integrales definidas
└── Unidad 3: Aplicaciones
    └── Tema 3.1: Problemas de optimización
```

---

### **US-04.4: Calendario y Cronograma Académico** (13 SP)
**Como** profesor  
**Quiero** gestionar un calendario de actividades  
**Para** planificar y comunicar fechas importantes  

#### **Criterios de Aceptación**
- [ ] Calendario visual mensual/semanal
- [ ] Creación de eventos y actividades
- [ ] Fechas de entrega y evaluaciones
- [ ] Sincronización con calendario personal
- [ ] Notificaciones automáticas a estudiantes
- [ ] Exportar calendario a formatos estándar (iCal)

---

### **US-04.5: Sistema de Evaluación y Calificaciones** (13 SP)
**Como** profesor  
**Quiero** crear y gestionar evaluaciones  
**Para** medir el progreso de mis estudiantes  

#### **Criterios de Aceptación**
- [ ] Creación de diferentes tipos de evaluación (tarea, examen, proyecto)
- [ ] Configuración de rúbricas de calificación
- [ ] Asignación de pesos por tipo de evaluación
- [ ] Cálculo automático de calificaciones finales
- [ ] Libro de calificaciones digital
- [ ] Generación de reportes de calificaciones

#### **Tipos de Evaluación**
```yaml
Tareas:
  - peso_porcentual: configurable
  - fecha_entrega: required
  - instrucciones: rich text
  - archivos_adjuntos: supported
  
Exámenes:
  - tiempo_limite: opcional
  - intentos_permitidos: configurable
  - calificacion_automatica: supported
  - banco_preguntas: available
  
Proyectos:
  - evaluacion_grupal: supported
  - rubricas_detalladas: available
  - entrega_multiple: supported
  - peer_review: opcional
```

---

### **US-04.6: Comunicación con Estudiantes** (8 SP)
**Como** profesor  
**Quiero** comunicarme efectivamente con mis estudiantes  
**Para** mantener engagement y resolver dudas  

#### **Criterios de Aceptación**
- [ ] Foro de discusión por curso
- [ ] Mensajería directa con estudiantes
- [ ] Anuncios masivos a toda la clase
- [ ] Q&A section para preguntas frecuentes
- [ ] Notificaciones push y email
- [ ] Moderación de contenido inapropiado

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class Course(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    academic_period = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    max_students = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

class CourseUnit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    prerequisites = models.ManyToManyField('self', blank=True)

class StudentEnrollment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS)
    final_grade = models.FloatField(null=True, blank=True)

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    due_date = models.DateTimeField()
    max_points = models.FloatField()
    weight_percentage = models.FloatField()
```

### **API Endpoints**
```yaml
Courses:
  GET    /api/teacher/courses/                # Mis cursos
  POST   /api/teacher/courses/                # Crear curso
  GET    /api/teacher/courses/{id}/           # Detalle curso
  PUT    /api/teacher/courses/{id}/           # Actualizar curso

Students:
  GET    /api/teacher/courses/{id}/students/  # Estudiantes del curso
  POST   /api/teacher/courses/{id}/enroll/    # Inscribir estudiante
  PUT    /api/teacher/students/{id}/grade/    # Calificar estudiante

Content Structure:
  GET    /api/teacher/courses/{id}/units/     # Unidades del curso
  POST   /api/teacher/courses/{id}/units/     # Crear unidad
  PUT    /api/teacher/units/{id}/reorder/     # Reordenar unidades

Assignments:
  GET    /api/teacher/courses/{id}/assignments/ # Evaluaciones
  POST   /api/teacher/assignments/             # Crear evaluación
  GET    /api/teacher/assignments/{id}/grades/ # Calificaciones

Communication:
  GET    /api/teacher/courses/{id}/messages/   # Mensajes del curso
  POST   /api/teacher/courses/{id}/announce/   # Anuncio a clase
  GET    /api/teacher/courses/{id}/forum/      # Foro de discusión
```

## 🧪 Casos de Prueba

### **Test Suite: Course Management**
```python
class CourseManagementTestCase(TestCase):
    def test_create_course_structure(self):
        # Test creación de curso con unidades
        pass
    
    def test_student_enrollment(self):
        # Test inscripción de estudiantes
        pass
    
    def test_grade_calculation(self):
        # Test cálculo automático de calificaciones
        pass

class AssignmentTestCase(TestCase):
    def test_assignment_creation(self):
        # Test creación de evaluaciones
        pass
    
    def test_due_date_notifications(self):
        # Test notificaciones de fechas de entrega
        pass
```

## 🎨 Diseño UX/UI

### **Dashboard Layout**
```css
.teacher-dashboard {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  padding: 2rem;
}

.course-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.course-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.student-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.student-card {
  text-align: center;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Dashboard completo de cursos del profesor
- [ ] Gestión integral de estudiantes por curso
- [ ] Estructura jerárquica de contenidos
- [ ] Calendario y cronograma académico
- [ ] Sistema de evaluación y calificaciones
- [ ] Comunicación efectiva con estudiantes

### **No Funcionales**
- [ ] Carga del dashboard < 3 segundos
- [ ] Operaciones CRUD < 1 segundo
- [ ] Soporte para 500+ estudiantes por profesor
- [ ] Responsive design para tablets
- [ ] Sincronización en tiempo real

### **Técnicos**
- [ ] Cobertura de tests > 85%
- [ ] API REST completamente documentada
- [ ] Validaciones robustas en formularios
- [ ] Notificaciones en tiempo real (WebSocket)
- [ ] Backup automático de calificaciones

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Tiempo creación curso**: <10 minutos setup completo
- **Uso dashboard diario**: >80% profesores acceden diariamente
- **Engagement estudiantes**: >60% participan en foros
- **Reducción emails**: >50% comunicación via plataforma

### **KPIs de Eficiencia**
- **Tiempo calificación**: >40% reducción vs método tradicional
- **Precisión calificaciones**: >99% cálculos automáticos correctos
- **Satisfacción profesores**: >4.4/5 en facilidad de uso
- **Retención estudiantes**: >85% completan cursos

Esta épica establece la **base académica fundamental** para que los profesores gestionen efectivamente sus cursos y estudiantes. 