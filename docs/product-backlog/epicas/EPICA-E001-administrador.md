# EP-01: Gestión de Usuarios y Autenticación

## 📝 Descripción de la Épica
Como **sistema educativo**, necesito gestionar usuarios con diferentes roles (Director, Profesor, Estudiante) para controlar el acceso y funcionalidades según el tipo de usuario.

## 🎯 Objetivos de Negocio
- Implementar autenticación segura con Google OAuth 2.0
- Gestionar roles y permisos granulares
- Permitir autoregistro de estudiantes y gestión de profesores
- Proporcionar perfil personalizable por usuario

## 📊 Información General
- **Epic ID**: EP-01
- **Prioridad**: 🔴 Must Have
- **Story Points**: 55 SP
- **Sprint Goal**: S1-S3 (6 semanas)
- **Dependencias**: Ninguna (épica base)

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Directores, Profesores, Estudiantes
- **Development Team**: Backend, Frontend, DevOps

## 🎬 User Stories

### **US-01.1: Autenticación con Google OAuth** (13 SP)
**Como** usuario del sistema  
**Quiero** autenticarme con mi cuenta de Google  
**Para** acceder de forma segura sin crear otra contraseña  

#### **Criterios de Aceptación**
- [ ] El sistema muestra botón "Iniciar sesión con Google"
- [ ] Redirecciona correctamente al flujo OAuth de Google
- [ ] Captura información básica del perfil (nombre, email, foto)
- [ ] Crea sesión segura con tokens JWT
- [ ] Redirige al dashboard según el rol del usuario
- [ ] Maneja errores de autenticación graciosamente

#### **Definición de Listo**
- [ ] Código implementado y testeado
- [ ] Integración con Google OAuth 2.0 configurada
- [ ] Tests unitarios e integración >90% coverage
- [ ] Documentación técnica actualizada
- [ ] Revisión de código aprobada
- [ ] Desplegado en ambiente de testing

---

### **US-01.2: Gestión de Roles de Usuario** (8 SP)
**Como** Director del sistema  
**Quiero** asignar roles específicos a los usuarios  
**Para** controlar el acceso a funcionalidades según su posición  

#### **Criterios de Aceptación**
- [ ] Sistema soporta 3 roles: Director, Profesor, Estudiante
- [ ] Director puede asignar/cambiar roles de usuarios
- [ ] Permisos granulares por rol implementados
- [ ] Middleware de autorización funcional
- [ ] Interfaz de gestión de roles intuitiva
- [ ] Logs de cambios de roles

#### **Roles y Permisos**
```yaml
Director:
  - manage_users: true
  - manage_courses: true
  - view_reports: true
  - system_settings: true

Profesor:
  - create_content: true
  - manage_courses: assigned_only
  - view_students: true
  - grade_assignments: true

Estudiante:
  - view_content: true
  - submit_assignments: true
  - view_grades: own_only
  - create_portfolio: true
```

---

### **US-01.3: Registro de Estudiantes** (8 SP)
**Como** estudiante potencial  
**Quiero** registrarme automáticamente en el sistema  
**Para** acceder a los cursos sin intervención manual  

#### **Criterios de Aceptación**
- [ ] Formulario de registro con validaciones
- [ ] Verificación de email obligatoria
- [ ] Rol de "Estudiante" asignado automáticamente
- [ ] Notificación de bienvenida por email
- [ ] Integración con Google OAuth opcional
- [ ] Prevención de registros duplicados

---

### **US-01.4: Gestión de Profesores** (8 SP)
**Como** Director  
**Quiero** invitar y gestionar profesores  
**Para** mantener control sobre quién puede crear contenido  

#### **Criterios de Aceptación**
- [ ] Sistema de invitaciones por email
- [ ] Profesor confirma cuenta y establece perfil
- [ ] Director puede activar/desactivar profesores
- [ ] Lista de profesores con estados (activo/inactivo/pendiente)
- [ ] Búsqueda y filtrado de profesores
- [ ] Asignación de cursos a profesores

---

### **US-01.5: Perfil de Usuario Personalizable** (13 SP)
**Como** usuario del sistema  
**Quiero** gestionar mi perfil personal  
**Para** personalizar mi experiencia y mantener mi información actualizada  

#### **Criterios de Aceptación**
- [ ] Página de perfil con información básica
- [ ] Subida de foto de perfil (hasta 2MB)
- [ ] Campos personalizables según el rol
- [ ] Cambio de contraseña (si no usa OAuth)
- [ ] Configuración de notificaciones
- [ ] Historial de actividad del usuario

#### **Campos por Rol**
```yaml
Director:
  - nombre_completo: required
  - email: required
  - telefono: optional
  - cargo: required
  - biografia: optional

Profesor:
  - nombre_completo: required
  - email: required
  - especialidad: required
  - experiencia: optional
  - redes_sociales: optional

Estudiante:
  - nombre_completo: required
  - email: required
  - fecha_nacimiento: optional
  - intereses: optional
  - objetivos_aprendizaje: optional
```

---

### **US-01.6: Sistema de Notificaciones** (5 SP)
**Como** usuario del sistema  
**Quiero** recibir notificaciones relevantes  
**Para** mantenerme informado de actividades importantes  

#### **Criterios de Aceptación**
- [ ] Notificaciones en tiempo real (WebSocket)
- [ ] Notificaciones por email configurables
- [ ] Centro de notificaciones en la interfaz
- [ ] Marcado de leído/no leído
- [ ] Filtrado por tipo de notificación
- [ ] Configuración de preferencias de notificación

#### **Tipos de Notificaciones**
- **Académicas**: Nuevos cursos, tareas, calificaciones
- **Sistema**: Mantenimiento, actualizaciones
- **Sociales**: Comentarios, menciones, colaboraciones
- **Seguridad**: Intentos de acceso, cambios de contraseña

---

## 🧪 Casos de Prueba

### **Test Suite: Autenticación**
```python
class AuthenticationTestCase(TestCase):
    def test_google_oauth_login(self):
        # Test successful Google OAuth flow
        pass
    
    def test_invalid_credentials(self):
        # Test error handling for invalid auth
        pass
    
    def test_token_expiration(self):
        # Test JWT token expiration handling
        pass
```

### **Test Suite: Roles y Permisos**
```python
class RolePermissionTestCase(TestCase):
    def test_director_permissions(self):
        # Test director can access all features
        pass
    
    def test_profesor_restrictions(self):
        # Test profesor cannot access admin features
        pass
    
    def test_estudiante_permissions(self):
        # Test estudiante has limited access
        pass
```

## 🔧 Consideraciones Técnicas

### **Arquitectura de Autenticación**
```python
# Authentication flow
1. User clicks "Login with Google"
2. Redirect to Google OAuth consent screen
3. Google returns authorization code
4. Exchange code for access token
5. Fetch user profile from Google API
6. Create/update user in database
7. Generate JWT token
8. Set secure HTTP-only cookie
9. Redirect to dashboard
```

### **Modelo de Datos**
```python
# models.py
class User(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=100, unique=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='profiles/', null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    social_links = models.JSONField(default=dict)
    notification_preferences = models.JSONField(default=dict)
```

### **API Endpoints**
```yaml
Authentication:
  POST /api/auth/google/          # Google OAuth login
  POST /api/auth/logout/          # Logout user
  POST /api/auth/refresh/         # Refresh JWT token
  GET  /api/auth/me/              # Get current user info

User Management:
  GET    /api/users/              # List users (Director only)
  POST   /api/users/              # Create user (Director only)
  GET    /api/users/{id}/         # Get user details
  PUT    /api/users/{id}/         # Update user
  DELETE /api/users/{id}/         # Delete user (Director only)

Profile:
  GET    /api/profile/            # Get my profile
  PUT    /api/profile/            # Update my profile
  POST   /api/profile/avatar/     # Upload profile picture
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] Autenticación con Google OAuth 2.0 implementada
- [ ] Tres roles funcionales (Director, Profesor, Estudiante)
- [ ] Permisos granulares aplicados correctamente
- [ ] Autoregistro de estudiantes operativo
- [ ] Gestión de profesores por Director
- [ ] Perfiles personalizables por rol
- [ ] Sistema de notificaciones básico

### **No Funcionales**
- [ ] Tiempo de respuesta de login < 2 segundos
- [ ] Seguridad: tokens JWT con expiración
- [ ] Escalabilidad: soporta 1000+ usuarios concurrentes
- [ ] Usabilidad: interfaz intuitiva y responsive
- [ ] Disponibilidad: 99.9% uptime
- [ ] Rendimiento: carga de perfil < 1 segundo

### **Técnicos**
- [ ] Cobertura de tests > 90%
- [ ] Documentación API completa
- [ ] Logs de auditoría implementados
- [ ] Manejo de errores robusto
- [ ] Validación de entrada en todos los endpoints
- [ ] Cumplimiento GDPR para datos personales

## 📈 Métricas de Éxito

### **KPIs Funcionales**
- **Tasa de registro exitoso**: >95%
- **Tiempo promedio de login**: <3 segundos
- **Errores de autenticación**: <1%
- **Adopción de perfiles completos**: >80%

### **KPIs Técnicos**
- **Uptime del sistema**: >99.9%
- **Tiempo de respuesta API**: <500ms
- **Errores de servidor**: <0.1%
- **Cobertura de tests**: >90%

## 🔄 Retrospectiva y Mejoras

### **Preguntas para Retrospectiva**
1. ¿El flujo de autenticación es intuitivo?
2. ¿Los roles y permisos son suficientes?
3. ¿Hay funcionalidades faltantes en el perfil?
4. ¿El sistema de notificaciones es útil?

### **Posibles Mejoras Futuras**
- Autenticación multifactor (2FA)
- Single Sign-On (SSO) con otros sistemas
- Roles personalizados dinámicos
- Integración con directorio activo
- Análisis de comportamiento de usuarios

---

## 📚 Recursos y Referencias

### **Documentación Técnica**
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django Authentication](https://docs.djangoproject.com/en/4.2/topics/auth/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)

### **Herramientas de Desarrollo**
- **Testing**: pytest, django-test-utils
- **Authentication**: django-allauth, PyJWT
- **API**: Django REST Framework
- **Frontend**: React, Axios

### **Compliance y Seguridad**
- **GDPR**: Protección de datos personales
- **OWASP**: Top 10 security practices
- **OAuth 2.0**: Secure authorization framework 