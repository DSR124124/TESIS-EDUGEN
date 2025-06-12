# EPICA-E010: Seguimiento de Progreso Académico

## 📝 Descripción de la Épica
Como **estudiante**, necesito monitorear mi progreso académico y visualizar mi rendimiento para entender mi avance en el aprendizaje y identificar áreas de mejora.

## 🎯 Objetivos de Negocio
- Proporcionar visibilidad del progreso académico personal
- Motivar el aprendizaje continuo con métricas claras
- Identificar fortalezas y áreas de mejora
- Facilitar autoevaluación y autorregulación del aprendizaje
- Generar insights personalizados para mejor rendimiento

## 📊 Información General
- **Epic ID**: EPICA-E010
- **Rol**: 👨‍🎓 ESTUDIANTE
- **Prioridad**: 🔴 Must Have
- **Story Points**: 34 SP
- **Sprint Goal**: S10-S11 (4 semanas)
- **Dependencias**: EPICA-E009 (Recursos), EPICA-E008 (Acceso)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Estudiantes
- **Development Team**: Backend, Frontend, Data Analytics

## 🎬 User Stories

### **US-10.1: Dashboard Personal de Progreso** (13 SP)
**Como** estudiante  
**Quiero** ver un dashboard con mi progreso académico  
**Para** entender mi rendimiento actual y tendencias  

#### **Criterios de Aceptación**
- [ ] Vista general de progreso por materia/curso
- [ ] Gráficos de tendencia de calificaciones
- [ ] Métricas de tiempo dedicado al estudio
- [ ] Indicadores de metas cumplidas/pendientes
- [ ] Comparativa con promedio de la clase (opcional)
- [ ] Widgets personalizables de métricas importantes

#### **Métricas del Dashboard**
```yaml
Progreso General:
  - porcentaje_completitud_global: 78%
  - calificacion_promedio: 8.5/10
  - tiempo_semanal_promedio: "12.5 horas"
  - metas_cumplidas: "7 de 10"
  
Por Materia:
  - matematicas: 85% completado, 9.2 promedio
  - ciencias: 72% completado, 8.1 promedio
  - literatura: 90% completado, 8.8 promedio
  
Tendencias:
  - mejora_ultimas_4_semanas: +0.7 puntos
  - constancia_estudio: "Muy buena"
  - materiales_favoritos: ["videos", "ejercicios"]
```

---

### **US-10.2: Tracking de Actividades y Tiempo** (8 SP)
**Como** estudiante  
**Quiero** ver el tiempo que dedico a cada actividad de estudio  
**Para** optimizar mi distribución del tiempo  

#### **Criterios de Aceptación**
- [ ] Log automático de tiempo por material/portfolio
- [ ] Gráficos de distribución de tiempo por materia
- [ ] Identificación de patrones de estudio más efectivos
- [ ] Metas de tiempo y alertas de cumplimiento
- [ ] Comparativa entre tiempo planificado vs real
- [ ] Exportar reportes de actividad

---

### **US-10.3: Calificaciones y Evaluaciones** (8 SP)
**Como** estudiante  
**Quiero** ver todas mis calificaciones organizadas  
**Para** monitorear mi rendimiento académico  

#### **Criterios de Aceptación**
- [ ] Lista cronológica de todas las evaluaciones
- [ ] Detalle de calificaciones por tipo (tareas, exámenes, proyectos)
- [ ] Cálculo automático de promedios ponderados
- [ ] Gráficos de evolución de calificaciones
- [ ] Identificación de mejores/peores rendimientos por tema
- [ ] Proyección de calificación final por materia

---

### **US-10.4: Metas y Objetivos Personales** (5 SP)
**Como** estudiante  
**Quiero** establecer y seguir metas académicas personales  
**Para** mantener motivación y dirección en mi aprendizaje  

#### **Criterios de Aceptación**
- [ ] Creación de metas SMART personalizadas
- [ ] Tracking automático de progreso hacia metas
- [ ] Notificaciones de hitos alcanzados
- [ ] Sugerencias de metas basadas en rendimiento
- [ ] Celebración visual de logros conseguidos
- [ ] Ajuste dinámico de metas según progreso

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class StudentProgress(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE, null=True)
    completion_percentage = models.FloatField(default=0.0)
    time_spent_total = models.DurationField(default=timedelta(0))
    last_activity = models.DateTimeField(auto_now=True)
    current_streak_days = models.PositiveIntegerField(default=0)
    average_grade = models.FloatField(null=True)

class StudySession(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    resource = models.ForeignKey('ModularContent', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    duration = models.DurationField(default=timedelta(0))
    completed = models.BooleanField(default=False)
    device_type = models.CharField(max_length=20)  # mobile, desktop, tablet

class StudentGoal(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField()
    current_value = models.FloatField(default=0.0)
    metric_type = models.CharField(max_length=50)  # grade, time, completion
    deadline = models.DateField()
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ProgressSnapshot(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    snapshot_date = models.DateField()
    total_time_week = models.DurationField()
    materials_completed_week = models.PositiveIntegerField()
    average_grade_week = models.FloatField(null=True)
    goals_achieved_week = models.PositiveIntegerField(default=0)
    engagement_score = models.FloatField()  # calculated score 0-100
```

### **API Endpoints**
```yaml
Progress Overview:
  GET    /api/student/progress/dashboard/       # Dashboard principal
  GET    /api/student/progress/summary/         # Resumen general
  GET    /api/student/progress/trends/          # Tendencias históricas
  GET    /api/student/progress/course/{id}/     # Progreso por curso

Time Tracking:
  GET    /api/student/time-tracking/            # Tiempo por actividad
  POST   /api/student/time-tracking/session/   # Iniciar sesión estudio
  PUT    /api/student/time-tracking/session/{id}/ # Finalizar sesión
  GET    /api/student/time-tracking/analytics/ # Analíticas de tiempo

Grades & Performance:
  GET    /api/student/grades/                   # Todas las calificaciones
  GET    /api/student/grades/course/{id}/       # Calificaciones por curso
  GET    /api/student/performance/analytics/   # Análisis de rendimiento
  GET    /api/student/performance/predictions/ # Predicciones de rendimiento

Goals Management:
  GET    /api/student/goals/                    # Lista de metas
  POST   /api/student/goals/                    # Crear meta
  PUT    /api/student/goals/{id}/               # Actualizar meta
  DELETE /api/student/goals/{id}/               # Eliminar meta
  POST   /api/student/goals/{id}/check/         # Marcar meta cumplida
```

### **Analytics & Calculations**
```python
class ProgressCalculator:
    @staticmethod
    def calculate_completion_percentage(student, portfolio):
        total_materials = PortfolioMaterial.objects.filter(
            section__portfolio=portfolio
        ).count()
        completed_materials = StudentResourceAccess.objects.filter(
            student=student,
            resource__portfoliomaterial__section__portfolio=portfolio,
            completion_percentage__gte=90
        ).count()
        return (completed_materials / total_materials) * 100 if total_materials > 0 else 0

    @staticmethod
    def calculate_engagement_score(student, week_start):
        # Algoritmo para calcular engagement score
        time_factor = StudySession.objects.filter(
            student=student,
            start_time__gte=week_start
        ).aggregate(total=Sum('duration'))['total']
        
        consistency_factor = StudySession.objects.filter(
            student=student,
            start_time__gte=week_start
        ).dates('start_time', 'day').count()
        
        completion_factor = StudentResourceAccess.objects.filter(
            student=student,
            last_accessed__gte=week_start,
            completion_percentage__gte=90
        ).count()
        
        # Formula weighted scoring
        return min(100, (time_factor * 0.4 + consistency_factor * 0.3 + completion_factor * 0.3))
```

## 🧪 Casos de Prueba

### **Test Suite: Progress Tracking**
```python
class ProgressTrackingTestCase(TestCase):
    def test_completion_percentage_calculation(self):
        # Test cálculo correcto de porcentaje de completitud
        pass
    
    def test_time_tracking_accuracy(self):
        # Test precisión del tracking de tiempo
        pass
    
    def test_grade_average_calculation(self):
        # Test cálculo de promedios de calificaciones
        pass

class GoalManagementTestCase(TestCase):
    def test_goal_creation_and_tracking(self):
        # Test creación y seguimiento de metas
        pass
    
    def test_automatic_goal_achievement_detection(self):
        # Test detección automática de metas logradas
        pass
```

## 🎨 Diseño UX/UI

### **Dashboard Responsive**
```css
.progress-dashboard {
  display: grid;
  grid-template-areas: 
    "summary summary"
    "charts goals"
    "activity activity";
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  padding: 2rem;
}

@media (max-width: 768px) {
  .progress-dashboard {
    grid-template-areas: 
      "summary"
      "charts"
      "goals"
      "activity";
    grid-template-columns: 1fr;
  }
}

.progress-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.progress-card:hover {
  transform: translateY(-2px);
}

.metric-widget {
  text-align: center;
  padding: 1rem;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.progress-ring {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(#4CAF50 0deg, #4CAF50 var(--progress-angle), #e0e0e0 var(--progress-angle));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Dashboard completo de progreso académico personal
- [ ] Tracking automático y preciso de tiempo de estudio
- [ ] Visualización comprehensiva de calificaciones
- [ ] Sistema de metas personales con seguimiento automático

### **No Funcionales**
- [ ] Carga de dashboard < 3 segundos
- [ ] Actualización de métricas en tiempo real
- [ ] Diseño responsive optimizado para móviles
- [ ] Precisión de 99%+ en cálculos de progreso
- [ ] Sincronización cross-device de datos

### **Técnicos**
- [ ] Algoritmos de cálculo optimizados
- [ ] Cache inteligente para métricas frecuentes
- [ ] Analytics pipeline para insights
- [ ] Backup automático de datos de progreso
- [ ] APIs documentadas para integraciones

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Acceso diario al dashboard**: >70% estudiantes
- **Metas creadas**: >3 metas promedio por estudiante
- **Engagement con métricas**: >5 minutos promedio por sesión
- **Retention**: >85% estudiantes usan después de 1 mes

### **KPIs de Impacto**
- **Mejora rendimiento**: >15% incremento en calificaciones
- **Constancia estudio**: >25% incremento en regularidad
- **Satisfacción estudiantes**: >4.4/5 en utilidad percibida
- **Autorregulación**: >60% estudiantes ajustan hábitos basado en datos

Esta épica empodera a los estudiantes con **visibilidad y control** sobre su propio progreso académico. 