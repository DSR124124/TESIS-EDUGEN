# EPICA-E013: Sistema de Gamificación y Logros

## 📝 Descripción de la Épica
Como **sistema**, necesito implementar elementos de gamificación para motivar el aprendizaje continuo, reconocer logros académicos y fomentar el engagement de estudiantes a través de mecánicas de juego.

## 🎯 Objetivos de Negocio
- Aumentar motivación y engagement de estudiantes
- Reconocer y celebrar logros académicos
- Fomentar competencia sana entre estudiantes
- Gamificar el proceso de aprendizaje
- Reducir tasas de abandono escolar

## 📊 Información General
- **Epic ID**: EPICA-E013
- **Rol**: 🤖 SISTEMA
- **Prioridad**: 🟡 Should Have
- **Story Points**: 55 SP
- **Sprint Goal**: S15-S17 (6 semanas)
- **Dependencias**: EPICA-E010 (Progreso), EPICA-E009 (Recursos)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Estudiantes
- **Development Team**: Backend, Frontend, Game Designer

## 🎬 User Stories

### **US-13.1: Sistema de Puntos y Niveles** (21 SP)
**Como** sistema  
**Quiero** asignar puntos por actividades académicas  
**Para** motivar el progreso continuo y crear sensación de logro  

#### **Criterios de Aceptación**
- [ ] Sistema de puntos por completar materiales
- [ ] Niveles académicos progresivos
- [ ] Multiplicadores de puntos por racha de estudio
- [ ] Bonificaciones por completar portfolios
- [ ] Rankings individuales y por clase
- [ ] Historia de puntos y niveles alcanzados

#### **Sistema de Puntuación**
```yaml
Acciones y Puntos:
  completar_material: 10 puntos
  completar_portfolio: 100 puntos
  primera_vez_dia: 5 puntos bonus
  racha_7_dias: 50 puntos bonus
  calificacion_excelente: 25 puntos bonus
  
Niveles:
  - Nivel 1: 0-100 puntos (Novato)
  - Nivel 2: 101-300 puntos (Aprendiz)
  - Nivel 3: 301-600 puntos (Estudiante)
  - Nivel 4: 601-1000 puntos (Avanzado)
  - Nivel 5: 1001+ puntos (Experto)
```

---

### **US-13.2: Sistema de Insignias y Logros** (13 SP)
**Como** sistema  
**Quiero** otorgar insignias por logros específicos  
**Para** reconocer diferentes tipos de éxito académico  

#### **Criterios de Aceptación**
- [ ] Insignias por completitud de cursos
- [ ] Insignias por constancia de estudio
- [ ] Insignias por colaboración y ayuda
- [ ] Insignias por mejora en calificaciones
- [ ] Colección personal de insignias
- [ ] Insignias compartibles en redes sociales

#### **Tipos de Insignias**
```yaml
Académicas:
  - "Maestro de Matemáticas": Completar todos los portfolios de matemáticas
  - "Científico Dedicado": 30 días consecutivos estudiando ciencias
  - "Lector Voraz": Leer 50+ materiales de literatura
  
Comportamiento:
  - "Estudiante Constante": 30 días de racha de estudio
  - "Madrugador": Estudiar antes de las 7 AM por 10 días
  - "Colaborador": Ayudar a 5 compañeros diferentes
  
Progreso:
  - "En Ascenso": Mejorar calificación promedio 1+ punto
  - "Perfeccionista": Obtener 100% en 5 evaluaciones
  - "Velocista": Completar material en tiempo récord
```

---

### **US-13.3: Desafíos y Competiciones** (13 SP)
**Como** sistema  
**Quiero** crear desafíos temporales y competiciones  
**Para** mantener el interés y fomentar participación activa  

#### **Criterios de Aceptación**
- [ ] Desafíos semanales automáticos
- [ ] Competiciones entre clases
- [ ] Eventos especiales por temporadas
- [ ] Leaderboards en tiempo real
- [ ] Recompensas por participación
- [ ] Desafíos personalizados por profesor

---

### **US-13.4: Avatares y Personalización** (8 SP)
**Como** sistema  
**Quiero** permitir personalización de avatares  
**Para** crear identidad personal y aumentar el apego emocional  

#### **Criterios de Aceptación**
- [ ] Creación de avatar personalizable
- [ ] Desbloqueo de accesorios con puntos
- [ ] Temas y colores desbloqueables
- [ ] Showcase de logros en perfil
- [ ] Comparación de avatares con amigos
- [ ] Evolución visual del avatar con nivel

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class GamificationProfile(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_badges = models.PositiveIntegerField(default=0)
    avatar_data = models.JSONField(default=dict)
    last_activity_date = models.DateField(auto_now=True)

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    criteria = models.JSONField()  # Criteria for earning the badge
    points_reward = models.PositiveIntegerField(default=0)
    rarity = models.CharField(max_length=20)  # common, rare, epic, legendary
    is_active = models.BooleanField(default=True)

class StudentBadge(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    progress_data = models.JSONField(default=dict)

class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=50)  # daily, weekly, special
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_criteria = models.JSONField()
    reward_points = models.PositiveIntegerField()
    reward_badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField('Student', through='ChallengeParticipation')

class PointTransaction(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)
    points_earned = models.IntegerField()  # Can be negative for spending
    description = models.CharField(max_length=200)
    related_content = models.ForeignKey('ModularContent', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### **Gamification Engine**
```python
class GamificationEngine:
    def __init__(self):
        self.point_rules = self.load_point_rules()
        self.badge_rules = self.load_badge_rules()
    
    def award_points(self, student, action_type, related_content=None):
        base_points = self.point_rules.get(action_type, 0)
        
        # Apply multipliers
        multiplier = self.calculate_multiplier(student, action_type)
        final_points = int(base_points * multiplier)
        
        # Record transaction
        PointTransaction.objects.create(
            student=student,
            action_type=action_type,
            points_earned=final_points,
            description=f"Points for {action_type}",
            related_content=related_content
        )
        
        # Update profile
        profile = student.gamificationprofile
        profile.total_points += final_points
        profile.current_level = self.calculate_level(profile.total_points)
        profile.save()
        
        # Check for new badges
        self.check_badge_criteria(student)
        
        return final_points
    
    def check_badge_criteria(self, student):
        available_badges = Badge.objects.filter(is_active=True)
        earned_badges = student.studentbadge_set.values_list('badge_id', flat=True)
        
        for badge in available_badges.exclude(id__in=earned_badges):
            if self.evaluate_badge_criteria(student, badge.criteria):
                StudentBadge.objects.create(student=student, badge=badge)
                self.award_points(student, 'badge_earned')
```

### **API Endpoints**
```yaml
Gamification:
  GET    /api/gamification/profile/{student_id}/    # Perfil de gamificación
  GET    /api/gamification/leaderboard/             # Ranking de puntos
  GET    /api/gamification/badges/available/        # Insignias disponibles
  GET    /api/gamification/badges/earned/           # Insignias ganadas

Points & Levels:
  GET    /api/gamification/points/history/          # Historial de puntos
  POST   /api/gamification/points/award/            # Otorgar puntos
  GET    /api/gamification/level/requirements/      # Requisitos de nivel

Challenges:
  GET    /api/gamification/challenges/active/       # Desafíos activos
  POST   /api/gamification/challenges/join/{id}/    # Unirse a desafío
  GET    /api/gamification/challenges/progress/     # Progreso en desafíos

Avatar:
  GET    /api/gamification/avatar/{student_id}/     # Datos del avatar
  PUT    /api/gamification/avatar/customize/        # Personalizar avatar
  GET    /api/gamification/shop/items/              # Items de la tienda
```

## 🧪 Casos de Prueba

### **Test Suite: Gamification Logic**
```python
class GamificationTestCase(TestCase):
    def test_point_calculation(self):
        # Test cálculo correcto de puntos
        pass
    
    def test_level_progression(self):
        # Test progresión de niveles
        pass
    
    def test_badge_criteria_evaluation(self):
        # Test evaluación de criterios de insignias
        pass

class ChallengeTestCase(TestCase):
    def test_challenge_participation(self):
        # Test participación en desafíos
        pass
    
    def test_leaderboard_calculation(self):
        # Test cálculo de rankings
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Sistema de puntos y niveles completamente funcional
- [ ] Insignias otorgadas automáticamente según criterios
- [ ] Desafíos y competiciones operativos
- [ ] Sistema de avatares personalizable

### **No Funcionales**
- [ ] Cálculo de puntos en tiempo real < 1 segundo
- [ ] Leaderboards actualizados cada 5 minutos
- [ ] Soporte para 10,000+ estudiantes concurrentes
- [ ] 99.9% uptime para sistema de gamificación

### **Técnicos**
- [ ] Algoritmos optimizados para cálculo de rankings
- [ ] Cache distribuido para leaderboards
- [ ] Sistema de notificaciones para logros
- [ ] Analytics de engagement con gamificación

## 📈 Métricas de Éxito

### **KPIs de Engagement**
- **Participación activa**: >80% estudiantes participan en gamificación
- **Tiempo en plataforma**: >30% incremento promedio de sesión
- **Retorno diario**: >60% estudiantes regresan diariamente
- **Completitud actividades**: >25% incremento en completitud

### **KPIs de Motivación**
- **Insignias ganadas**: >5 insignias promedio por estudiante
- **Participación desafíos**: >70% estudiantes se unen a desafíos
- **Mejora rendimiento**: >15% incremento en calificaciones
- **Satisfacción**: >4.2/5 en diversión percibida del aprendizaje

Esta épica transforma el aprendizaje en una **experiencia lúdica y motivadora** que impulsa el engagement estudiantil. 