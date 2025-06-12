# EPICA-E009: Acceso y Navegación de Recursos Educativos

## 📝 Descripción de la Épica
Como **estudiante**, necesito acceder y navegar fácilmente por recursos educativos asignados para consumir contenido de aprendizaje de manera eficiente y encontrar rápidamente la información que necesito.

## 🎯 Objetivos de Negocio
- Facilitar acceso intuitivo a materiales de estudio
- Proporcionar navegación eficiente entre recursos
- Ofrecer múltiples formas de descubrir contenido
- Optimizar experiencia de consumo de materiales
- Reducir tiempo de búsqueda de información

## 📊 Información General
- **Epic ID**: EPICA-E009
- **Rol**: 👨‍🎓 ESTUDIANTE
- **Prioridad**: 🔴 Must Have
- **Story Points**: 55 SP
- **Sprint Goal**: S9-S10 (4 semanas)
- **Dependencias**: EPICA-E007 (Portfolios), EPICA-E008 (Acceso)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Estudiantes
- **Development Team**: Frontend, UX/UI Designer

## 🎬 User Stories

### **US-09.1: Navegación por Portfolios Asignados** (21 SP)
**Como** estudiante  
**Quiero** navegar por portfolios que me han sido asignados  
**Para** acceder al contenido de forma estructurada por tema  

#### **Criterios de Aceptación**
- [ ] Vista de tarjetas de portfolios asignados
- [ ] Indicadores de progreso visual por portfolio
- [ ] Acceso directo a última posición visitada
- [ ] Filtrado por materia o profesor
- [ ] Búsqueda rápida dentro de portfolios
- [ ] Notificaciones de nuevos portfolios disponibles

#### **Interface de Portfolio**
```yaml
Portfolio Card:
  - thumbnail: tema_color + icono
  - titulo: "Álgebra Lineal - Fundamentos"
  - progreso: "65% completado"
  - ultimo_acceso: "Hace 2 días"
  - nuevos_materiales: badge_count
  - profesor: "Dr. González"
  - estimado_restante: "45 min"
```

---

### **US-09.2: Exploración de Contenido por Categorías** (13 SP)
**Como** estudiante  
**Quiero** explorar contenido organizado por categorías  
**Para** descubrir materiales relacionados con mi área de estudio  

#### **Criterios de Aceptación**
- [ ] Vista de categorías con iconos temáticos
- [ ] Subcategorías organizadas jerárquicamente
- [ ] Contador de materiales por categoría
- [ ] Filtros por tipo de contenido (video, texto, ejercicio)
- [ ] Ordenamiento por fecha, popularidad o relevancia
- [ ] Vista previa rápida de materiales

#### **Categorías Disponibles**
```yaml
Matemáticas:
  - Álgebra: 45 materiales
  - Cálculo: 32 materiales
  - Geometría: 28 materiales
  
Ciencias:
  - Física: 38 materiales
  - Química: 25 materiales
  - Biología: 31 materiales
  
Humanidades:
  - Historia: 22 materiales
  - Literatura: 29 materiales
  - Filosofía: 18 materiales
```

---

### **US-09.3: Búsqueda Avanzada de Recursos** (8 SP)
**Como** estudiante  
**Quiero** buscar recursos usando múltiples criterios  
**Para** encontrar exactamente el contenido que necesito  

#### **Criterios de Aceptación**
- [ ] Búsqueda por texto completo en título y contenido
- [ ] Filtros por tipo de archivo (PDF, video, interactivo)
- [ ] Filtros por nivel de dificultad
- [ ] Filtros por duración estimada
- [ ] Filtros por profesor o materia
- [ ] Resultados destacados y sugerencias automáticas

---

### **US-09.4: Favoritos y Marcadores** (8 SP)
**Como** estudiante  
**Quiero** marcar contenido como favorito  
**Para** acceder rápidamente a materiales importantes  

#### **Criterios de Aceptación**
- [ ] Botón de favorito en cada material
- [ ] Sección de favoritos en navegación principal
- [ ] Organización de favoritos en carpetas personales
- [ ] Etiquetas personalizadas para clasificación
- [ ] Exportar lista de favoritos
- [ ] Compartir favoritos con compañeros de clase

---

### **US-09.5: Historial y Continuación de Lectura** (5 SP)
**Como** estudiante  
**Quiero** ver mi historial de recursos visitados  
**Para** continuar donde dejé mi estudio  

#### **Criterios de Aceptación**
- [ ] Historial cronológico de materiales visitados
- [ ] Botón "Continuar donde dejé" en materiales parciales
- [ ] Tiempo dedicado por sesión de estudio
- [ ] Materiales visitados recientemente en dashboard
- [ ] Limpieza automática de historial antiguo
- [ ] Restaurar sesión tras cierre de navegador

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class StudentResourceAccess(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    resource = models.ForeignKey('ModularContent', on_delete=models.CASCADE)
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    access_count = models.PositiveIntegerField(default=1)
    time_spent = models.DurationField(default=timedelta(0))
    completion_percentage = models.FloatField(default=0.0)
    is_favorite = models.BooleanField(default=False)

class StudentBookmark(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    resource = models.ForeignKey('ModularContent', on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class StudentSearchHistory(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    search_query = models.CharField(max_length=200)
    results_count = models.PositiveIntegerField()
    clicked_resource = models.ForeignKey('ModularContent', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### **API Endpoints**
```yaml
Resource Navigation:
  GET    /api/student/portfolios/               # Portfolios asignados
  GET    /api/student/categories/               # Categorías disponibles
  GET    /api/student/categories/{id}/resources/ # Recursos por categoría
  GET    /api/student/resources/recent/         # Recursos recientes

Search & Discovery:
  GET    /api/student/search/                   # Búsqueda de recursos
  POST   /api/student/search/advanced/          # Búsqueda avanzada
  GET    /api/student/search/suggestions/       # Sugerencias automáticas
  GET    /api/student/resources/recommended/    # Recursos recomendados

Bookmarks & Favorites:
  GET    /api/student/bookmarks/                # Lista de marcadores
  POST   /api/student/bookmarks/                # Crear marcador
  PUT    /api/student/bookmarks/{id}/           # Actualizar marcador
  DELETE /api/student/bookmarks/{id}/           # Eliminar marcador

Progress & History:
  GET    /api/student/history/                  # Historial de acceso
  POST   /api/student/resources/{id}/track/     # Trackear progreso
  GET    /api/student/resources/{id}/resume/    # Reanudar lectura
```

### **Frontend Components**
```javascript
const StudentNavigationComponents = {
  PortfolioGrid: {
    // Grid de portfolios con progreso
    features: ['progress-indicators', 'quick-resume', 'search-within']
  },
  
  CategoryExplorer: {
    // Explorador jerárquico de categorías
    features: ['tree-navigation', 'breadcrumbs', 'filters']
  },
  
  SearchInterface: {
    // Interfaz de búsqueda avanzada
    features: ['auto-complete', 'filters', 'saved-searches']
  },
  
  BookmarkManager: {
    // Gestor de marcadores y favoritos
    features: ['folder-organization', 'tags', 'export']
  },
  
  ProgressTracker: {
    // Tracker de progreso y continuación
    features: ['reading-position', 'time-tracking', 'auto-resume']
  }
}
```

## 🧪 Casos de Prueba

### **Test Suite: Resource Navigation**
```python
class ResourceNavigationTestCase(TestCase):
    def test_portfolio_access(self):
        # Test acceso a portfolios asignados
        pass
    
    def test_category_browsing(self):
        # Test navegación por categorías
        pass
    
    def test_search_functionality(self):
        # Test funcionalidad de búsqueda
        pass

class BookmarkTestCase(TestCase):
    def test_bookmark_creation(self):
        # Test creación de marcadores
        pass
    
    def test_favorite_management(self):
        # Test gestión de favoritos
        pass
```

## 🎨 Diseño UX/UI

### **Mobile-First Design**
```css
.student-dashboard {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

@media (min-width: 768px) {
  .student-dashboard {
    grid-template-columns: 250px 1fr;
    padding: 2rem;
  }
}

.portfolio-card {
  background: linear-gradient(135deg, var(--theme-color) 0%, var(--theme-color-dark) 100%);
  border-radius: 12px;
  padding: 1.5rem;
  color: white;
  transition: transform 0.3s ease;
}

.portfolio-card:hover {
  transform: translateY(-4px);
}

.progress-bar {
  height: 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: white;
  transition: width 0.5s ease;
}
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Navegación fluida por portfolios asignados
- [ ] Exploración eficiente por categorías
- [ ] Búsqueda avanzada con múltiples filtros
- [ ] Sistema completo de favoritos y marcadores
- [ ] Historial y continuación automática de lectura

### **No Funcionales**
- [ ] Carga de portfolios < 2 segundos
- [ ] Búsqueda con resultados < 1 segundo
- [ ] Interfaz responsive optimizada para móviles
- [ ] Offline support para contenido descargado
- [ ] Accesibilidad WCAG 2.1 AA compliant

### **Técnicos**
- [ ] Progressive Web App (PWA) features
- [ ] Lazy loading para mejor performance
- [ ] Cache inteligente de contenido frecuente
- [ ] Analytics de uso para mejoras futuras
- [ ] Sincronización cross-device

## 📈 Métricas de Éxito

### **KPIs de Adopción**
- **Tiempo navegación**: <3 minutos para encontrar contenido
- **Uso portfolios**: >80% estudiantes acceden diariamente
- **Engagement**: >45 minutos promedio por sesión
- **Favoritos**: >5 marcadores promedio por estudiante

### **KPIs de Experiencia**
- **Satisfacción navegación**: >4.3/5 en usabilidad
- **Tasa abandono**: <15% en búsquedas
- **Retorno contenido**: >60% vuelven a materiales favoritos
- **Completitud**: >70% estudiantes completan materiales iniciados

Esta épica proporciona la **experiencia de navegación fundamental** para que los estudiantes accedan eficientemente al contenido educativo. 