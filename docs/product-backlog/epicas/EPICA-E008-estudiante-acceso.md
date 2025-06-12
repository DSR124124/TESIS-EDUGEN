# EPICA-E008: Acceso a Portfolios Organizados por Tema

## 📝 Descripción de la Épica
Como **estudiante**, necesito acceder a portfolios educativos organizados por tema y materia para encontrar fácilmente el contenido de aprendizaje relevante y seguir mi progreso académico de manera estructurada.

## 🎯 Objetivos de Negocio
- Proporcionar acceso intuitivo a materiales educativos
- Organizar contenido por temas, materias y dificultad
- Implementar sistema de navegación eficiente
- Mostrar progreso de aprendizaje en tiempo real
- Crear experiencia personalizada por estudiante

## 📊 Información General
- **Epic ID**: EPICA-E008
- **Rol**: 👨‍🎓 ESTUDIANTE
- **Prioridad**: 🔴 Must Have
- **Story Points**: 55 SP
- **Sprint Goal**: S9-S10 (4 semanas)
- **Dependencias**: EPICA-E005 (Editor), EPICA-E007 (Asignación)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Estudiantes, Profesores (visionado)
- **Development Team**: Frontend, Backend, UX/UI Designer

## 🎬 User Stories

### **US-08.1: Dashboard de Portfolios por Materia** (13 SP)
**Como** estudiante  
**Quiero** ver mis portfolios organizados por materia  
**Para** acceder rápidamente al contenido de cada curso  

#### **Criterios de Aceptación**
- [ ] Vista de tarjetas con cada materia inscrita
- [ ] Indicador de progreso por materia (%)
- [ ] Última actividad y fecha de acceso
- [ ] Número de materiales pendientes
- [ ] Filtros por estado (completado, en progreso, pendiente)
- [ ] Búsqueda por nombre de materia

#### **Estructura de Dashboard**
```yaml
Materia Card:
  - Nombre de la materia
  - Profesor asignado
  - Progreso visual (barra de progreso)
  - Número de portfolios/temas
  - Última actividad
  - Estado (activo, completado, retrasado)
  - Acceso rápido al portfolio
```

---

### **US-08.2: Navegación Temática Jerárquica** (13 SP)
**Como** estudiante  
**Quiero** navegar por temas organizados jerárquicamente  
**Para** encontrar contenido específico de manera lógica  

#### **Criterios de Aceptación**
- [ ] Estructura de árbol expandible
- [ ] Breadcrumbs para navegación
- [ ] Iconos descriptivos por tipo de contenido
- [ ] Indicadores de contenido nuevo
- [ ] Marcadores de contenido completado
- [ ] Estimación de tiempo por tema

#### **Jerarquía de Navegación**
```
Materia
├── Unidad 1: Tema Principal
│   ├── 📚 Subtema 1.1: Conceptos básicos
│   │   ├── 📄 Material teórico
│   │   ├── 🎥 Video explicativo
│   │   └── ✅ Ejercicio práctico
│   └── 📚 Subtema 1.2: Aplicación
└── Unidad 2: Tema Avanzado
    └── ...
```

---

### **US-08.3: Sistema de Marcadores y Favoritos** (8 SP)
**Como** estudiante  
**Quiero** marcar contenido importante como favorito  
**Para** acceder rápidamente a materiales clave  

#### **Criterios de Aceptación**
- [ ] Botón de marcador en cada material
- [ ] Sección de "Favoritos" en el dashboard
- [ ] Categorización de favoritos por tags
- [ ] Búsqueda dentro de favoritos
- [ ] Compartir favoritos con otros estudiantes
- [ ] Exportar lista de favoritos

---

### **US-08.4: Visualización de Progreso Personal** (8 SP)
**Como** estudiante  
**Quiero** ver mi progreso detallado  
**Para** entender mi avance y planificar mis estudios  

#### **Criterios de Aceptación**
- [ ] Gráfico de progreso general por materia
- [ ] Calendario de actividades completadas
- [ ] Métricas de tiempo dedicado por tema
- [ ] Comparación con promedio de la clase
- [ ] Predicción de finalización
- [ ] Identificación de áreas débiles

#### **Métricas Incluidas**
```yaml
Progreso:
  - Porcentaje completado por materia
  - Tiempo total dedicado
  - Racha de días consecutivos
  - Objetivos semanales/mensuales

Rendimiento:
  - Puntuación promedio en ejercicios
  - Tiempo promedio por actividad
  - Comparación con compañeros
  - Tendencia de mejora
```

---

### **US-08.5: Búsqueda Avanzada de Contenido** (8 SP)
**Como** estudiante  
**Quiero** buscar contenido específico  
**Para** encontrar rápidamente información relevante  

#### **Criterios de Aceptación**
- [ ] Búsqueda por texto completo
- [ ] Filtros avanzados (tipo, materia, fecha, profesor)
- [ ] Búsqueda por tags y categorías
- [ ] Historial de búsquedas
- [ ] Sugerencias automáticas
- [ ] Resultados destacados y relevantes

---

### **US-08.6: Acceso Offline y Sincronización** (5 SP)
**Como** estudiante  
**Quiero** acceder a contenido sin conexión  
**Para** estudiar en cualquier lugar y momento  

#### **Criterios de Aceptación**
- [ ] Descarga de materiales para acceso offline
- [ ] Sincronización automática al conectar
- [ ] Indicador de contenido disponible offline
- [ ] Gestión de espacio de almacenamiento
- [ ] Priorización de descargas
- [ ] Actualización incremental

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class StudentPortfolioAccess(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.ForeignKey('PortfolioMaterial', on_delete=models.CASCADE)
    access_date = models.DateTimeField(auto_now_add=True)
    completion_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    time_spent = models.DurationField(default=timedelta(0))
    last_position = models.JSONField(default=dict)  # Para reanudar
    is_favorite = models.BooleanField(default=False)
    
class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    completion_percentage = models.FloatField(default=0.0)
    total_time_spent = models.DurationField(default=timedelta(0))
    last_access = models.DateTimeField(auto_now=True)
    streak_days = models.IntegerField(default=0)
```

### **API Endpoints**
```yaml
Portfolio Access:
  GET    /api/student/portfolios/           # Lista portfolios del estudiante
  GET    /api/student/portfolios/{id}/      # Detalle de portfolio específico
  POST   /api/student/portfolios/{id}/access/ # Registrar acceso
  PUT    /api/student/portfolios/{id}/progress/ # Actualizar progreso

Favoritos:
  GET    /api/student/favorites/            # Lista de favoritos
  POST   /api/student/favorites/            # Agregar favorito
  DELETE /api/student/favorites/{id}/       # Quitar favorito

Búsqueda:
  GET    /api/student/search/               # Búsqueda de contenido
  GET    /api/student/search/suggestions/   # Sugerencias de búsqueda

Progreso:
  GET    /api/student/progress/             # Progreso general
  GET    /api/student/progress/{subject}/   # Progreso por materia
```

### **Frontend Components**
```javascript
// Componentes principales
const StudentPortfolioComponents = {
  DashboardView: {
    // Vista principal con tarjetas de materias
    features: ['progress-bars', 'quick-access', 'recent-activity']
  },
  
  ThemeNavigation: {
    // Navegación jerárquica por temas
    features: ['tree-view', 'breadcrumbs', 'icons']
  },
  
  ContentViewer: {
    // Visualizador de contenido multimedia
    features: ['offline-support', 'progress-tracking', 'favorites']
  },
  
  ProgressDashboard: {
    // Dashboard de métricas y progreso
    features: ['charts', 'calendar', 'goals']
  }
}
```

## 🧪 Casos de Prueba

### **Test Suite: Navegación**
```python
class PortfolioNavigationTestCase(TestCase):
    def test_subject_dashboard_load(self):
        # Test carga dashboard con materias del estudiante
        pass
    
    def test_theme_hierarchy_navigation(self):
        # Test navegación jerárquica por temas
        pass
    
    def test_breadcrumb_navigation(self):
        # Test navegación con breadcrumbs
        pass
```

### **Test Suite: Progreso**
```python
class ProgressTrackingTestCase(TestCase):
    def test_progress_calculation(self):
        # Test cálculo correcto de progreso
        pass
    
    def test_time_tracking(self):
        # Test seguimiento de tiempo por actividad
        pass
    
    def test_completion_status(self):
        # Test estados de completitud
        pass
```

## 🎨 Diseño UX/UI

### **Principios de Diseño**
- **Simplicidad**: Navegación intuitiva sin complejidad
- **Claridad Visual**: Iconografía clara y consistente
- **Feedback Visual**: Indicadores claros de progreso
- **Personalización**: Experiencia adaptada al estudiante
- **Accesibilidad**: Cumplimiento WCAG 2.1 AA

### **Paleta de Colores**
```css
:root {
  --student-primary: #4CAF50;     /* Verde éxito */
  --student-secondary: #2196F3;   /* Azul información */
  --student-accent: #FF9800;      /* Naranja atención */
  --student-success: #8BC34A;     /* Verde claro */
  --student-warning: #FFC107;     /* Amarillo advertencia */
  --student-error: #F44336;       /* Rojo error */
}
```

### **Responsive Design**
```css
/* Breakpoints para estudiantes */
.portfolio-grid {
  display: grid;
  gap: 1.5rem;
  
  /* Desktop */
  grid-template-columns: repeat(3, 1fr);
  
  /* Tablet */
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  /* Mobile */
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
}
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Dashboard intuitivo con todas las materias del estudiante
- [ ] Navegación jerárquica por temas y subtemas
- [ ] Sistema de favoritos funcional
- [ ] Visualización clara del progreso personal
- [ ] Búsqueda avanzada de contenido
- [ ] Acceso offline básico
- [ ] Sincronización automática

### **No Funcionales**
- [ ] Carga inicial del dashboard < 2 segundos
- [ ] Navegación entre temas < 1 segundo
- [ ] Búsqueda con resultados < 3 segundos
- [ ] Soporte offline para contenido básico
- [ ] Responsive design en móviles

### **Técnicos**
- [ ] Cobertura de tests > 85%
- [ ] API REST documentada
- [ ] Optimización de consultas DB
- [ ] Caching inteligente
- [ ] Progressive Web App (PWA) features

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Tiempo diario promedio**: >30 minutos por estudiante
- **Tasa de completitud**: >70% de portfolios completados
- **Uso de favoritos**: >50% estudiantes usan favoritos
- **Acceso mobile**: >40% accesos desde móvil

### **KPIs de Experiencia**
- **Satisfacción estudiante**: >4.2/5 en usabilidad
- **Tasa de rebote**: <20% en dashboard
- **Sesiones por estudiante**: >5 por semana
- **Retención**: >80% estudiantes activos mensualmente

---

## 📱 Compatibilidad y Accesibilidad

### **Dispositivos Soportados**
- **Desktop**: Windows, macOS, Linux (Chrome, Firefox, Safari, Edge)
- **Tablet**: iPad, Android tablets
- **Mobile**: iOS 12+, Android 8+
- **Conectividad**: Online, offline limitado

### **Accesibilidad**
- **WCAG 2.1 AA** compliance
- **Screen readers** compatibility
- **Keyboard navigation** complete
- **High contrast** mode support
- **Text scaling** up to 200%

Esta épica garantiza que los estudiantes tengan una experiencia **intuitiva y eficiente** para acceder a su contenido educativo. 