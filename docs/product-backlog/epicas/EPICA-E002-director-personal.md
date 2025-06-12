# EPICA-E002: Gestión de Personal Docente y Estudiantes

## 📝 Descripción de la Épica
Como **director**, necesito gestionar el personal docente y estudiantes de la institución para mantener control administrativo, asignar responsabilidades y monitorear el desempeño académico.

## 🎯 Objetivos de Negocio
- Gestionar registro y perfiles de profesores
- Administrar matrícula y datos de estudiantes
- Asignar profesores a materias y cursos
- Monitorear desempeño y actividad
- Generar reportes administrativos

## 📊 Información General
- **Epic ID**: EPICA-E002
- **Rol**: 🎓 DIRECTOR
- **Prioridad**: 🔴 Must Have
- **Story Points**: 89 SP
- **Sprint Goal**: S2-S4 (6 semanas)
- **Dependencias**: EPICA-E001 (Administrador)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Directores, Administradores
- **Development Team**: Backend, Frontend, UX/UI Designer

## 🎬 User Stories

### **US-02.1: Gestión de Profesores** (21 SP)
**Como** director  
**Quiero** gestionar el registro y perfiles de profesores  
**Para** mantener actualizada la información del personal docente  

#### **Criterios de Aceptación**
- [ ] Lista completa de profesores con información básica
- [ ] Formulario de registro de nuevo profesor
- [ ] Edición de perfiles de profesores existentes
- [ ] Estados de profesor (activo, inactivo, licencia)
- [ ] Búsqueda y filtrado por especialidad o estado
- [ ] Exportar lista de profesores a Excel/PDF

#### **Campos de Profesor**
```yaml
Información Personal:
  - nombre_completo: required
  - email: required, unique
  - telefono: optional
  - direccion: optional
  
Información Profesional:
  - especialidad: required
  - titulo_profesional: required
  - experiencia_anos: required
  - fecha_ingreso: required
  - salario: optional, confidential
  
Estado:
  - estado: [activo, inactivo, licencia, despedido]
  - fecha_ultimo_acceso: auto
  - cursos_asignados: relationship
```

---

### **US-02.2: Gestión de Estudiantes** (21 SP)
**Como** director  
**Quiero** administrar la matrícula y datos de estudiantes  
**Para** mantener control del cuerpo estudiantil  

#### **Criterios de Aceptación**
- [ ] Lista de estudiantes con información académica
- [ ] Proceso de matrícula/inscripción
- [ ] Edición de datos de estudiantes
- [ ] Estados de matrícula (activo, suspendido, graduado)
- [ ] Búsqueda por nombre, código o curso
- [ ] Reportes de matrícula por período

#### **Información de Estudiante**
```yaml
Datos Personales:
  - nombre_completo: required
  - email: required, unique
  - fecha_nacimiento: optional
  - telefono_contacto: optional
  
Datos Académicos:
  - codigo_estudiante: auto-generated, unique
  - fecha_matricula: required
  - nivel_academico: required
  - estado_matricula: [activo, suspendido, graduado, retirado]
  - cursos_inscritos: relationship
  
Contacto Emergencia:
  - contacto_nombre: optional
  - contacto_telefono: optional
  - contacto_relacion: optional
```

---

### **US-02.3: Asignación de Profesores a Materias** (13 SP)
**Como** director  
**Quiero** asignar profesores a materias específicas  
**Para** organizar la distribución de carga académica  

#### **Criterios de Aceptación**
- [ ] Interfaz de arrastrar y soltar para asignaciones
- [ ] Vista de materias disponibles y profesores
- [ ] Validación de especialidad vs materia
- [ ] Límite de materias por profesor configurable
- [ ] Historial de asignaciones previas
- [ ] Notificación automática al profesor asignado

---

### **US-02.4: Dashboard de Desempeño** (13 SP)
**Como** director  
**Quiero** monitorear el desempeño de profesores y estudiantes  
**Para** tomar decisiones administrativas informadas  

#### **Criterios de Aceptación**
- [ ] Métricas de actividad de profesores
- [ ] Estadísticas de progreso estudiantil por curso
- [ ] Alertas de bajo rendimiento
- [ ] Comparativas entre períodos académicos
- [ ] Gráficos de tendencias de desempeño
- [ ] Exportar reportes de desempeño

#### **Métricas Incluidas**
```yaml
Profesores:
  - tiempo_plataforma_semanal: hours
  - contenido_creado_mes: count
  - estudiantes_asignados: count
  - calificacion_promedio_estudiantes: 1-5
  
Estudiantes:
  - porcentaje_completitud_curso: percentage
  - tiempo_dedicado_semanal: hours
  - calificaciones_promedio: grade
  - progreso_vs_cronograma: percentage
```

---

### **US-02.5: Comunicación y Notificaciones** (13 SP)
**Como** director  
**Quiero** comunicarme con profesores y estudiantes  
**Para** mantener información fluida en la institución  

#### **Criterios de Aceptación**
- [ ] Sistema de mensajería interna
- [ ] Envío de notificaciones masivas
- [ ] Categorización por grupos (profesores, estudiantes, curso)
- [ ] Plantillas de mensajes predefinidas
- [ ] Historial de comunicaciones enviadas
- [ ] Confirmación de lectura de mensajes importantes

---

### **US-02.6: Reportes Administrativos** (8 SP)
**Como** director  
**Quiero** generar reportes administrativos  
**Para** análisis institucional y cumplimiento regulatorio  

#### **Criterios de Aceptación**
- [ ] Reporte de matrícula por período
- [ ] Reporte de desempeño académico general
- [ ] Reporte de actividad de profesores
- [ ] Exportación en múltiples formatos (PDF, Excel, CSV)
- [ ] Programación de reportes automáticos
- [ ] Dashboards ejecutivos interactivos

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    professional_title = models.CharField(max_length=100)
    years_experience = models.PositiveIntegerField()
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=20, choices=TEACHER_STATUS)
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_code = models.CharField(max_length=15, unique=True)
    enrollment_date = models.DateField()
    academic_level = models.CharField(max_length=50)
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
class TeacherSubjectAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_students = models.PositiveIntegerField(default=30)
```

### **API Endpoints**
```yaml
Teachers:
  GET    /api/director/teachers/           # Lista profesores
  POST   /api/director/teachers/           # Crear profesor
  GET    /api/director/teachers/{id}/      # Detalle profesor
  PUT    /api/director/teachers/{id}/      # Actualizar profesor
  DELETE /api/director/teachers/{id}/      # Desactivar profesor

Students:
  GET    /api/director/students/           # Lista estudiantes
  POST   /api/director/students/           # Matricular estudiante
  GET    /api/director/students/{id}/      # Detalle estudiante
  PUT    /api/director/students/{id}/      # Actualizar estudiante
  
Assignments:
  GET    /api/director/assignments/        # Ver asignaciones
  POST   /api/director/assignments/        # Crear asignación
  PUT    /api/director/assignments/{id}/   # Modificar asignación
  DELETE /api/director/assignments/{id}/   # Eliminar asignación

Reports:
  GET    /api/director/reports/enrollment/ # Reporte matrícula
  GET    /api/director/reports/performance/ # Reporte desempeño
  GET    /api/director/reports/activity/   # Reporte actividad
```

## 🧪 Casos de Prueba

### **Test Suite: Gestión Personal**
```python
class TeacherManagementTestCase(TestCase):
    def test_create_teacher_profile(self):
        # Test creación de perfil de profesor
        pass
    
    def test_teacher_specialization_validation(self):
        # Test validación de especialidad
        pass
    
    def test_teacher_status_changes(self):
        # Test cambios de estado de profesor
        pass

class StudentManagementTestCase(TestCase):
    def test_student_enrollment(self):
        # Test proceso de matrícula
        pass
    
    def test_student_code_generation(self):
        # Test generación automática de código
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Gestión completa de profesores con todos los estados
- [ ] Administración de estudiantes con proceso de matrícula
- [ ] Sistema de asignación profesor-materia funcional
- [ ] Dashboard de métricas de desempeño
- [ ] Sistema de comunicación interna
- [ ] Generación de reportes administrativos

### **No Funcionales**
- [ ] Carga de listas < 2 segundos para 1000+ registros
- [ ] Búsqueda con resultados < 1 segundo
- [ ] Exportación de reportes < 10 segundos
- [ ] Interfaz responsive para tablets
- [ ] Acceso por roles correctamente implementado

### **Técnicos**
- [ ] Cobertura de tests > 85%
- [ ] API REST completamente documentada
- [ ] Validaciones robustas en formularios
- [ ] Logs de auditoría para cambios críticos
- [ ] Backup automático de datos sensibles

## 📈 Métricas de Éxito

### **KPIs Operacionales**
- **Tiempo de registro profesor**: <5 minutos
- **Tiempo de matrícula estudiante**: <3 minutos
- **Uso de reportes**: >80% directores los utilizan semanalmente
- **Precisión de asignaciones**: >95% sin conflictos

### **KPIs de Adopción**
- **Satisfacción directores**: >4.3/5 en usabilidad
- **Reducción tiempo administrativo**: >30% vs proceso manual
- **Datos actualizados**: >90% perfiles completos
- **Uso sistema comunicación**: >70% mensajes vs email

Esta épica establece las **bases administrativas** fundamentales para el funcionamiento del sistema educativo. 