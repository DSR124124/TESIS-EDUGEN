# EPICA-E015: API Externa y Integraciones

## 📝 Descripción de la Épica
Como **sistema**, necesito proporcionar APIs externas robustas y facilitar integraciones con sistemas educativos existentes para expandir el ecosistema y permitir interoperabilidad.

## 🎯 Objetivos de Negocio
- Facilitar integraciones con LMS existentes
- Proporcionar API pública para desarrolladores externos
- Conectar con sistemas institucionales (SIS, bibliotecas)
- Expandir ecosistema de partners tecnológicos
- Generar nuevas fuentes de ingresos via API

## 📊 Información General
- **Epic ID**: EPICA-E015
- **Rol**: 🤖 SISTEMA
- **Prioridad**: 🟢 Could Have
- **Story Points**: 89 SP
- **Sprint Goal**: S19-S21 (6 semanas)
- **Dependencias**: Todas las épicas del core system

## 👥 Stakeholders
- **Product Owner**: Director del proyecto
- **End Users**: Desarrolladores, Instituciones, Partners
- **Development Team**: Backend, DevOps, API Architects

## 🎬 User Stories

### **US-15.1: API REST Pública Completa** (34 SP)
**Como** desarrollador externo  
**Quiero** acceder a una API REST completa  
**Para** integrar funcionalidades educativas en mis aplicaciones  

#### **Criterios de Aceptación**
- [ ] Documentación OpenAPI/Swagger completa
- [ ] Endpoints para todas las funcionalidades principales
- [ ] Versionado de API con backward compatibility
- [ ] Rate limiting configurable por plan
- [ ] Sandbox environment para testing
- [ ] SDKs para lenguajes populares (Python, PHP, Node.js)

---

### **US-15.2: Sistema de Autenticación API** (21 SP)
**Como** sistema  
**Quiero** gestionar autenticación y autorización segura  
**Para** controlar acceso a recursos via API  

#### **Criterios de Aceptación**
- [ ] OAuth 2.0 y API Keys support
- [ ] Scopes granulares de permisos
- [ ] JWT tokens con refresh mechanism
- [ ] Webhook authentication con signatures
- [ ] Logs de auditoría de acceso API
- [ ] Dashboard de gestión de aplicaciones

---

### **US-15.3: Integraciones LMS Populares** (21 SP)
**Como** sistema  
**Quiero** integrar con LMS populares  
**Para** facilitar migración y coexistencia  

#### **Criterios de Aceptación**
- [ ] Conector para Moodle via web services
- [ ] Integración Canvas LTI 1.3 compliant
- [ ] Sync con Google Classroom API
- [ ] Importador de cursos Blackboard
- [ ] SSO integration con sistemas institucionales
- [ ] Grade passback automático

---

### **US-15.4: Webhooks y Notificaciones API** (13 SP)
**Como** desarrollador  
**Quiero** recibir notificaciones en tiempo real  
**Para** mantener sistemas sincronizados  

#### **Criterios de Aceptación**
- [ ] Sistema de webhooks configurable
- [ ] Retry logic con exponential backoff
- [ ] Firma de seguridad en payloads
- [ ] Dashboard de monitoreo de webhooks
- [ ] Eventos para todas las acciones principales
- [ ] Formato JSON estándar para eventos

---

## 🔧 Consideraciones Técnicas

### **API Architecture**
```python
# Django REST Framework Setup
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            application = APIApplication.objects.get(api_key=api_key, is_active=True)
            return (None, application)  # No user, but authenticated app
        except APIApplication.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

# API Versioning
class APIVersioning(BaseVersioning):
    allowed_versions = ['v1', 'v2']
    default_version = 'v1'
    version_param = 'version'

# Rate Limiting
class APIRateLimit(UserRateThrottle):
    scope = 'api_calls'
    
    def get_cache_key(self, request, view):
        if hasattr(request, 'auth') and hasattr(request.auth, 'application'):
            return f"throttle_api_{request.auth.application.id}"
        return super().get_cache_key(request, view)
```

### **OpenAPI Documentation**
```yaml
# swagger_schema.yml
openapi: 3.0.0
info:
  title: Sistema Educativo API
  description: API completa para integración con sistema educativo
  version: 2.0.0
  contact:
    name: API Support
    email: api-support@educativo.com

servers:
  - url: https://api.educativo.com/v2
    description: Production server
  - url: https://sandbox-api.educativo.com/v2
    description: Sandbox server

security:
  - ApiKeyAuth: []
  - OAuth2: [read, write]

paths:
  /students:
    get:
      summary: Lista estudiantes
      description: Obtiene lista de estudiantes con filtros opcionales
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: course_id
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Lista de estudiantes
          content:
            application/json:
              schema:
                type: object
                properties:
                  count:
                    type: integer
                  results:
                    type: array
                    items:
                      $ref: '#/components/schemas/Student'

components:
  schemas:
    Student:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
        enrollment_date:
          type: string
          format: date
        status:
          type: string
          enum: [active, inactive, graduated]

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.educativo.com/oauth/authorize
          tokenUrl: https://api.educativo.com/oauth/token
          scopes:
            read: Lectura de datos
            write: Escritura de datos
```

### **LMS Integrations**
```python
# Moodle Integration
class MoodleConnector:
    def __init__(self, moodle_url, token):
        self.base_url = f"{moodle_url}/webservice/rest/server.php"
        self.token = token
    
    async def sync_courses(self):
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                moodle_courses = await response.json()
                
                for course_data in moodle_courses:
                    await self.import_course(course_data)

# Canvas LTI Integration
class CanvasLTIProvider:
    def __init__(self):
        self.client_id = settings.CANVAS_CLIENT_ID
        self.deployment_id = settings.CANVAS_DEPLOYMENT_ID
    
    def handle_lti_launch(self, request):
        # Validate LTI 1.3 message
        lti_message = self.validate_lti_message(request)
        
        # Extract user and course information
        user_info = lti_message.get('https://purl.imsglobal.org/spec/lti/claim/custom')
        course_info = lti_message.get('https://purl.imsglobal.org/spec/lti/claim/context')
        
        # Create or update user in our system
        user = self.sync_lti_user(user_info)
        
        # Redirect to appropriate content
        return redirect('student_dashboard')

# Google Classroom Integration
class GoogleClassroomSync:
    def __init__(self, credentials):
        self.service = build('classroom', 'v1', credentials=credentials)
    
    async def sync_assignments(self, course_id):
        try:
            assignments = self.service.courses().courseWork().list(
                courseId=course_id
            ).execute()
            
            for assignment in assignments.get('courseWork', []):
                await self.import_assignment(assignment)
                
        except HttpError as error:
            logger.error(f"Error syncing assignments: {error}")
```

### **Webhook System**
```python
# Webhook Management
class WebhookManager:
    def __init__(self):
        self.retry_delays = [1, 5, 25, 125]  # Exponential backoff
    
    async def send_webhook(self, event_type, payload, application):
        webhook_url = application.webhook_url
        if not webhook_url:
            return
        
        signature = self.generate_signature(payload, application.webhook_secret)
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Event-Type': event_type,
            'User-Agent': 'SistemaEducativo-Webhook/1.0'
        }
        
        for attempt, delay in enumerate(self.retry_delays):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url, 
                        json=payload, 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status < 300:
                            await self.log_webhook_success(event_type, application)
                            return
                        
                        if response.status >= 400:
                            await asyncio.sleep(delay)
                            continue
                            
            except Exception as e:
                logger.error(f"Webhook attempt {attempt + 1} failed: {e}")
                if attempt < len(self.retry_delays) - 1:
                    await asyncio.sleep(delay)
        
        await self.log_webhook_failure(event_type, application)

# Event Types
WEBHOOK_EVENTS = {
    'student.enrolled': 'Estudiante inscrito en curso',
    'grade.updated': 'Calificación actualizada',
    'content.completed': 'Contenido completado',
    'portfolio.assigned': 'Portfolio asignado',
    'achievement.earned': 'Logro conseguido'
}
```

## 🔧 API Endpoints

### **Core API Endpoints**
```yaml
Students:
  GET    /api/v2/students/                    # Lista estudiantes
  POST   /api/v2/students/                    # Crear estudiante
  GET    /api/v2/students/{id}/               # Detalle estudiante
  PUT    /api/v2/students/{id}/               # Actualizar estudiante
  GET    /api/v2/students/{id}/progress/      # Progreso académico

Courses:
  GET    /api/v2/courses/                     # Lista cursos
  POST   /api/v2/courses/                     # Crear curso
  GET    /api/v2/courses/{id}/content/        # Contenido del curso
  POST   /api/v2/courses/{id}/enroll/         # Inscribir estudiante

Content:
  GET    /api/v2/content/                     # Lista contenido
  POST   /api/v2/content/                     # Crear contenido
  GET    /api/v2/content/{id}/                # Detalle contenido
  POST   /api/v2/content/{id}/track/          # Trackear progreso

Grades:
  GET    /api/v2/grades/                      # Lista calificaciones
  POST   /api/v2/grades/                      # Crear calificación
  PUT    /api/v2/grades/{id}/                 # Actualizar calificación

Webhooks:
  GET    /api/v2/webhooks/                    # Lista webhooks configurados
  POST   /api/v2/webhooks/                    # Configurar webhook
  DELETE /api/v2/webhooks/{id}/               # Eliminar webhook
  GET    /api/v2/webhooks/{id}/logs/          # Logs de webhook
```

## 🧪 Casos de Prueba

### **Test Suite: API External**
```python
class APIExternalTestCase(TestCase):
    def setUp(self):
        self.api_key = APIApplication.objects.create(
            name="Test App",
            api_key="test_key_123"
        )
    
    def test_api_authentication(self):
        # Test autenticación con API key
        response = self.client.get(
            '/api/v2/students/',
            HTTP_X_API_KEY='test_key_123'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limiting(self):
        # Test límites de tasa
        for i in range(100):  # Exceed rate limit
            response = self.client.get(
                '/api/v2/students/',
                HTTP_X_API_KEY='test_key_123'
            )
        
        self.assertEqual(response.status_code, 429)
    
    def test_webhook_delivery(self):
        # Test entrega de webhooks
        pass

class LMSIntegrationTestCase(TestCase):
    def test_moodle_course_import(self):
        # Test importación de cursos Moodle
        pass
    
    def test_canvas_lti_launch(self):
        # Test lanzamiento LTI Canvas
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] API REST pública completamente documentada y funcional
- [ ] Sistema de autenticación y autorización robusto
- [ ] Integraciones operativas con LMS populares
- [ ] Sistema de webhooks confiable con retry logic

### **No Funcionales**
- [ ] API response time < 200ms para 95% requests
- [ ] Rate limiting configurable por aplicación
- [ ] 99.9% uptime para endpoints públicos
- [ ] Documentación interactiva con Swagger UI
- [ ] SDKs disponibles para 3+ lenguajes

### **Técnicos**
- [ ] OpenAPI 3.0 specification completa
- [ ] Versionado de API con backward compatibility
- [ ] Monitoring y alertas para API usage
- [ ] Webhook delivery garantizada con retries
- [ ] Security scanning automático

## 📈 Métricas de Éxito

### **KPIs de Adopción API**
- **Aplicaciones registradas**: >50 en primer año
- **API calls mensuales**: >100,000 requests
- **Retención desarrolladores**: >70% activos después 6 meses
- **Documentación rating**: >4.5/5 en developer satisfaction

### **KPIs de Integración**
- **LMS conectados**: >10 instituciones usando integraciones
- **Data sync accuracy**: >99% precisión en sincronización
- **Integration time**: <2 semanas promedio setup
- **Partner satisfaction**: >4.0/5 en facilidad de integración

Esta épica establece el **ecosistema de integración** que permite expansión y interoperabilidad con sistemas externos. 