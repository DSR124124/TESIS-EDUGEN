# 🎓 Sistema de Autenticación Dual para Estudiantes

## 📖 Resumen

El sistema EduGen ahora soporta **2 métodos de autenticación** para estudiantes:

1. **Email + Contraseña** (principal)
2. **Usuario + Contraseña** (alternativo)

**Nota:** Google OAuth está disponible pero deshabilitado por defecto para estudiantes.

---

## 🚀 Cómo Funciona

### **Para Estudiantes del 4to F - Polo Jiménez:**

#### Opción 1: Login con Email (Recomendado)
```
URL: http://127.0.0.1:8000/login/
Email: 61791657@cased.edu.pe
Contraseña: 61791657
```

#### Opción 2: Login con Usuario (Alternativo)
```
URL: http://127.0.0.1:8000/login/
Usuario: carlos_eduardo_serna_ventura
Contraseña: 61791657
```

---

## 👨‍💼 Para Directores

### **Estudiantes Registrados (4to F - Polo Jiménez):**

Los siguientes 20 estudiantes están registrados y pueden hacer login:

| **Nro** | **Nombre Completo** | **Email** | **Contraseña** |
|---|---|---|---|
| 1 | Carlos Eduardo Serna Ventura | `61791657@cased.edu.pe` | `61791657` |
| 2 | Gabriela Isabel Obregón Escudero | `61912715@cased.edu.pe` | `61912715` |
| 3 | Luciana Brigitte Orejuela Rentería | `61996238@cased.edu.pe` | `61996238` |
| 4 | Chanel Yazmín Chalco Cardenas | `73921044@cased.edu.pe` | `73921044` |
| 5 | Brunella Alejandra Ruiz Mera | `61907427@cased.edu.pe` | `61907427` |
| 6 | Alvaro Fabian Vilca Quiroz | `61912578@cased.edu.pe` | `61912578` |
| 7 | Mateo Martín Sánchez Sullón | `73724440@cased.edu.pe` | `73724440` |
| 8 | Gabriela Alexandra Edones Castro | `61933419@cased.edu.pe` | `61933419` |
| 9 | Valeria Deyanira Saavedra Tavara | `61851650@cased.edu.pe` | `61851650` |
| 10 | Nicolás Carlos Lazo Adrianzen | `62544018@cased.edu.pe` | `62544018` |
| 11 | Henry Pabbov Silupú Chavez | `61912911@cased.edu.pe` | `61912911` |
| 12 | Tiago Arie Mori | `73846445@cased.edu.pe` | `73846445` |
| 13 | Miguel Ángel Vera Ortiz | `72583221@cased.edu.pe` | `72583221` |
| 14 | Luis Fernando Cardenas Esculonte | `61792050@cased.edu.pe` | `61792050` |
| 15 | Adrianna Alessandra Beaumont Narro | `61851954@cased.edu.pe` | `61851954` |
| 16 | Dominyk Emmanuel Zaga Toro | `73400838@cased.edu.pe` | `73400838` |
| 17 | José Alonso Arica Paxi | `73839017@cased.edu.pe` | `73839017` |
| 18 | Saul Santiago Reyes Ramos | `73718377@cased.edu.pe` | `73718377` |
| 19 | Yaritza Thais Torres Ramírez | `61792348@cased.edu.pe` | `61792348` |
| 20 | Ariana Valentina Ortega Falconi | `73914527@cased.edu.pe` | `73914527` |

### **Información del Aula:**
- **Institución:** TÉCNICO FAP MANUEL POLO JIMÉNEZ
- **Grado:** 4to (CUARTO)
- **Sección:** F
- **Estudiantes:** 21/30 (incluyendo a Gabriela Isabel)
- **Edades:** 15-16 años

---

## 🔧 Comandos de Verificación

### **Verificar estudiantes del 4to F:**
```bash
python manage.py shell -c "
from apps.academic.models import Section, Enrollment;
seccion_f = Section.objects.filter(name='F', grade__name='CUARTO').first();
enrollments = Enrollment.objects.filter(section=seccion_f, status='ACTIVE');
print(f'Estudiantes en 4to F: {enrollments.count()}');
[print(f'{i+1}. {e.student.user.get_full_name()} - {e.student.user.email}') for i, e in enumerate(enrollments)]
"
```

### **Probar autenticación de un estudiante:**
```bash
python manage.py shell -c "
from django.contrib.auth import authenticate;
user = authenticate(username='61791657@cased.edu.pe', password='61791657');
print(f'Login exitoso: {user is not None}');
print(f'Usuario: {user.get_full_name() if user else \"Error\"}')
"
```

### **Listar todos los estudiantes activos:**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
students = User.objects.filter(role='student', is_active=True);
print(f'Total estudiantes activos: {students.count()}');
[print(f'- {s.get_full_name()} ({s.email})') for s in students[:10]]
"
```

---

## 🔐 Configuración de Seguridad

### **Contraseñas Actuales:**
- **Patrón:** Cada estudiante usa su código/número como contraseña
- **Ejemplo:** Email `61791657@cased.edu.pe` → Contraseña `61791657`

### **Generación de Usuarios:**
- **Formato:** `nombre_apellido_normalizado`
- **Ejemplo:** Carlos Eduardo Serna Ventura → `carlos_eduardo_serna_ventura`

### **Emails Institucionales:**
- **Formato:** `codigo@cased.edu.pe`
- **Ejemplo:** `61791657@cased.edu.pe`

### **Google OAuth:**
- **Estado:** Deshabilitado por defecto
- **Campo:** `google_account_linked = False` para todos los estudiantes

---

## 🛠️ Configuración Técnica

### **Backend de Autenticación:**
```python
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Google OAuth (disponible)
    'apps.accounts.backends.EmailBackend',       # Backend personalizado para email
    'django.contrib.auth.backends.ModelBackend', # Usuario + Contraseña tradicional
)
```

### **Backend Personalizado (EmailBackend):**
```python
class EmailBackend(ModelBackend):
    """
    Backend que permite login con email o username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar usuario por email o username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and user.is_active:
            return user
        return None
```

### **Modelos Actualizados:**
```python
# Usuario
class CustomUser:
    username = CharField()  # carlos_eduardo_serna_ventura
    email = EmailField()    # 61791657@cased.edu.pe
    password = CharField()  # Hash de 61791657
    role = CharField()      # 'student'

# Estudiante
class Student:
    dni = CharField()                    # 72345698
    birth_date = DateField()             # 2009-05-15 (15 años)
    google_account_linked = BooleanField()  # False
    google_account = EmailField()           # NULL
```

---

## 🔄 Flujo de Autenticación

### **Login con Email (Principal):**
1. Usuario ingresa: `61791657@cased.edu.pe`
2. Usuario ingresa: `61791657`
3. `EmailBackend` busca usuario por email
4. Valida contraseña hasheada
5. Si es válido → Redirige al dashboard de estudiante
6. Si es inválido → Muestra "Credenciales incorrectas"

### **Login con Username (Alternativo):**
1. Usuario ingresa: `carlos_eduardo_serna_ventura`
2. Usuario ingresa: `61791657`
3. `EmailBackend` busca usuario por username
4. Valida contraseña hasheada
5. Login exitoso → Dashboard

---

## 📱 Uso Diario para Estudiantes

### **Acceso Recomendado:**
```
1. Ir a: http://127.0.0.1:8000/login/
2. En "Usuario o Email": Introducir tu email (ej: 61791657@cased.edu.pe)
3. En "Contraseña": Introducir tu código (ej: 61791657)
4. Click: "Ingresar"
5. Acceso automático al dashboard de estudiante
```

### **Credenciales de Ejemplo:**
```
✅ Carlos Eduardo:
   Email: 61791657@cased.edu.pe
   Contraseña: 61791657

✅ Gabriela Isabel: 
   Email: 61912715@cased.edu.pe
   Contraseña: 61912715

✅ Luciana Brigitte:
   Email: 61996238@cased.edu.pe
   Contraseña: 61996238
```

---

## ⚡ Beneficios del Sistema Actual

✅ **Simplicidad:** Email = Contraseña fácil de recordar  
✅ **Flexibilidad:** Login con email o username  
✅ **Seguridad:** Contraseñas hasheadas con PBKDF2  
✅ **Escalabilidad:** Backend personalizado robusto  
✅ **Usabilidad:** Interface moderna e intuitiva  
✅ **Mantenibilidad:** Código limpio y documentado  

---

## 🆘 Resolución de Problemas

### **Error: "Credenciales incorrectas"**
1. ✅ Verificar que el email sea exacto: `61791657@cased.edu.pe`
2. ✅ Verificar que la contraseña sea exacta: `61791657`
3. ✅ Probar con username en lugar de email
4. ✅ Verificar que el usuario esté activo

### **Error: "Usuario no encontrado"**
1. ✅ Verificar en admin Django si existe el usuario
2. ✅ Verificar que tenga rol 'student'
3. ✅ Verificar que tenga perfil Student asociado

### **Error: "Sin permisos para acceder"**
1. ✅ Verificar que `user.is_active = True`
2. ✅ Verificar que `user.role = 'student'`
3. ✅ Verificar que existe matrícula activa

---

## 📞 Comandos de Emergencia

### **Resetear contraseña de un estudiante:**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user = User.objects.get(email='61791657@cased.edu.pe');
user.set_password('61791657');
user.save();
print('✅ Contraseña reseteada')
"
```

### **Activar todos los estudiantes:**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
students = User.objects.filter(role='student');
for user in students:
    user.is_active = True;
    user.save();
print(f'✅ {students.count()} estudiantes activados')
"
```

### **Verificar estado de un estudiante:**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model, authenticate;
from apps.academic.models import Student;
User = get_user_model();
email = '61791657@cased.edu.pe';
user = User.objects.get(email=email);
student = Student.objects.get(user=user);
auth = authenticate(username=email, password='61791657');
print(f'Usuario: {user.get_full_name()}');
print(f'Activo: {user.is_active}');
print(f'Rol: {user.role}');
print(f'DNI: {student.dni}');
print(f'Login funciona: {auth is not None}')
"
```

---

## 🏫 Información Institucional

### **Institución:**
- **Nombre:** TÉCNICO FAP MANUEL POLO JIMÉNEZ
- **Código:** POLO-JIMENEZ
- **Dominio:** @cased.edu.pe

### **Estructura Académica:**
- **Nivel:** Secundaria
- **Grado:** 4to (CUARTO)
- **Secciones:** A, B, C, F
- **Capacidad por sección:** 30 estudiantes

### **Estado Actual:**
- **Sección F:** 21 estudiantes registrados
- **Todos activos:** ✅
- **Todos pueden hacer login:** ✅
- **Edades:** 15-16 años

---

**✅ Sistema de autenticación dual implementado y funcionando**  
*Última actualización: Junio 2025 | Versión: 3.0*  
*Configurado para: 4to F - Polo Jiménez (21 estudiantes)* 