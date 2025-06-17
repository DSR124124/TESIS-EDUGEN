# 🎓 Sistema de Autenticación Dual para Estudiantes

## 📖 Resumen

El sistema EduGen ahora soporta **3 métodos de autenticación** para estudiantes:

1. **Usuario + Contraseña** (tradicional)
2. **Email + Contraseña** (tradicional)  
3. **Google OAuth** (social)

---

## 🚀 Cómo Funciona

### **Para Estudiantes:**

#### Opción 1: Login con Usuario
```
URL: https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/
Usuario: ana_garcia
Contraseña: estudiante123
```

#### Opción 2: Login con Email
```
URL: https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/
Email: ana.garcia@tecnicofap.edu.pe
Contraseña: estudiante123
```

#### Opción 3: Login con Google
```
URL: https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/
Hacer clic en "Iniciar sesión con Google"
```

---

## 👨‍💼 Para Directores

### **Crear Estudiante (Interfaz Web):**

1. **Ir a:** Director → Estudiantes → Crear
2. **Completar datos básicos** del estudiante
3. **Configurar autenticación:**
   - ✅ **"Generar usuario automáticamente"** = Usuario basado en nombre + DNI
   - ✅ **"Contraseña predeterminada"** = `estudiante123` (o personalizar)
   - ❌ **"Vincular con Google"** = Solo si el estudiante tiene Gmail

4. **Guardar:** El sistema muestra las credenciales generadas

### **Comandos de Django (SSH/Console):**

```bash
# Crear estudiantes de ejemplo
python manage.py manage_students --create

# Listar todos los estudiantes
python manage.py manage_students --list

# Resetear todas las contraseñas
python manage.py manage_students --reset-passwords

# Habilitar Google OAuth para un estudiante
python manage.py manage_students --enable-google ana.garcia@tecnicofap.edu.pe

# Deshabilitar Google OAuth
python manage.py manage_students --disable-google ana.garcia@tecnicofap.edu.pe
```

---

## 🔧 Scripts Disponibles

### **1. Crear Estudiantes Masivamente:**
```bash
python scripts/create_students_with_passwords.py
```

### **2. Resetear Contraseñas:**
```bash
python scripts/create_students_with_passwords.py --reset
```

### **3. Probar Autenticación:**
```bash
python scripts/test_student_authentication.py
```

---

## 📊 Ejemplos de Credenciales

| Estudiante | Usuario | Email | Contraseña | Google |
|------------|---------|-------|------------|---------|
| Ana García | `ana_garcia` | `ana.garcia@tecnicofap.edu.pe` | `estudiante123` | ❌ |
| Carlos Mendoza | `carlos_mendoza` | `carlos.mendoza@tecnicofap.edu.pe` | `estudiante123` | ❌ |
| Sofía Hernández | `sofia_hernandez` | `sofia.hernandez@tecnicofap.edu.pe` | `estudiante123` | ❌ |

---

## 🔐 Configuración de Seguridad

### **Contraseñas por Defecto:**
- **Estudiantes:** `estudiante123`
- **Profesores:** `profesor123`
- **Director:** `director123`

### **Generación de Usuarios:**
- **Formato:** `primera_letra_nombre + dni`
- **Ejemplo:** Ana García (DNI: 12345678) → `a12345678`

### **Emails Institucionales:**
- **Formato:** `nombre.apellido@tecnicofap.edu.pe`
- **Ejemplo:** Ana García → `ana.garcia@tecnicofap.edu.pe`

---

## 🛠️ Configuración Técnica

### **Backend de Autenticación:**
```python
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Google OAuth
    'django.contrib.auth.backends.ModelBackend',  # Usuario/Email + Contraseña
)
```

### **Template de Login:**
- Formulario tradicional + Botón Google OAuth
- Validación client-side y server-side
- Mensajes de error personalizados

### **Modelos:**
```python
# Usuario
class CustomUser:
    username = CharField()  # Para login tradicional
    email = EmailField()    # Para login por email
    password = CharField()  # Hash de contraseña
    role = CharField()      # 'student', 'teacher', 'director'

# Estudiante
class Student:
    google_account_linked = BooleanField()  # ¿Usa Google OAuth?
    google_account = EmailField()           # Email de Google
    google_linked_at = DateTimeField()      # Cuándo se vinculó
```

---

## 🔄 Flujo de Autenticación

### **Login Tradicional:**
1. Usuario ingresa credenciales
2. Django valida contra `ModelBackend`
3. Si es válido → Redirige al dashboard
4. Si es inválido → Muestra error

### **Login con Google:**
1. Usuario hace clic en "Google"
2. Redirección a Google OAuth
3. Google retorna datos del usuario
4. Pipeline personalizado valida
5. Si existe cuenta → Login exitoso
6. Si no existe → Error de autorización

---

## 📱 Uso Diario

### **Estudiantes SIN Gmail:**
```
1. Ir a: https://tu-app.azurewebsites.net/login/
2. Introducir: Usuario o Email
3. Introducir: Contraseña (predeterminada)
4. Click: "Iniciar Sesión"
```

### **Estudiantes CON Gmail:**
```
1. Ir a: https://tu-app.azurewebsites.net/login/
2. Click: "Iniciar sesión con Google"
3. Autorizar aplicación en Google
4. Acceso automático al dashboard
```

---

## ⚡ Beneficios

✅ **Flexibilidad:** Múltiples métodos de acceso  
✅ **Simplicidad:** Contraseñas fáciles de recordar  
✅ **Escalabilidad:** Creación masiva de usuarios  
✅ **Seguridad:** Validación en múltiples capas  
✅ **Usabilidad:** Interface moderna e intuitiva  

---

## 🆘 Resolución de Problemas

### **Error: "Usuario o contraseña incorrectos"**
- ✅ Verificar que el usuario existe: `python manage.py manage_students --list`
- ✅ Resetear contraseña: `python manage.py manage_students --reset-passwords`

### **Error: "Access Denied" con Google**
- ✅ Verificar que la cuenta Google está vinculada
- ✅ Usar login tradicional como alternativa

### **Error: "Perfil de estudiante no encontrado"**
- ✅ Verificar que existe perfil Student asociado
- ✅ Crear perfil desde el admin Django

---

## 📞 Comandos de Emergencia

```bash
# En Azure SSH Console

# Activar todos los estudiantes
python3 -c "
from apps.academic.models import Student
for s in Student.objects.all():
    s.user.is_active = True
    s.user.set_password('estudiante123')
    s.user.save()
    print(f'✅ {s.user.get_full_name()}')
"

# Crear estudiante específico
python3 -c "
from django.contrib.auth import get_user_model
from apps.academic.models import Student
User = get_user_model()

user = User.objects.create_user(
    username='test_student',
    email='test@tecnicofap.edu.pe',
    password='estudiante123',
    first_name='Test',
    last_name='Student',
    role='student'
)

Student.objects.create(
    user=user,
    dni='99999999',
    birth_date='2005-01-01',
    guardian_name='Test Guardian',
    guardian_phone='999999999'
)
print(f'✅ Usuario creado: test_student / estudiante123')
"
```

---

**✅ Sistema de autenticación dual implementado y funcionando**  
*Fecha: Junio 2025 | Versión: 2.0* 