# Scripts de Migración a Producción - Estudiantes Polo Jiménez

Este directorio contiene los scripts necesarios para migrar automáticamente los estudiantes del colegio **TÉCNICO FAP MANUEL POLO JIMÉNEZ** a un entorno de producción.

## 📋 Scripts Disponibles

### 1. `deploy_production_students.py` - Estudiantes 4to F
- **Grado:** CUARTO (4to)
- **Sección:** F
- **Estudiantes:** 20
- **Edades:** 15-16 años

### 2. `deploy_production_students_5a.py` - Estudiantes 5to A
- **Grado:** QUINTO (5to)
- **Sección:** A
- **Estudiantes:** 15
- **Edades:** 16-17 años

## 🚀 Uso en Producción

### Ejecutar Scripts Individualmente

```bash
# Para estudiantes de 4to F
python scripts/deploy_production_students.py

# Para estudiantes de 5to A
python scripts/deploy_production_students_5a.py
```

### Ejecutar Ambos Scripts (Migración Completa)

```bash
# Ejecutar ambos scripts en secuencia
python scripts/deploy_production_students.py && python scripts/deploy_production_students_5a.py
```

## ⚙️ Configuración

Los scripts están configurados para usar `config.settings.production`. Si necesitas probar en desarrollo, cambia temporalmente la línea:

```python
# Cambiar de:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# A:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
```

## 🎯 Características de los Scripts

### ✅ Funcionalidades
- **Seguridad:** Los scripts son seguros para ejecutar múltiples veces
- **No duplica datos:** Detecta usuarios existentes y los actualiza
- **Verificación:** Prueba la autenticación después del registro
- **Estructura completa:** Crea institución, grados, secciones y matrículas
- **Consistencia:** Mantiene la misma estructura de datos entre grados

### 📊 Estructura de Datos Aplicada
- **Dirección:** Vacía (consistente entre grados)
- **Apoderado:** "Apoderado de [Primer nombre]"
- **Teléfono Apoderado:** "999999999"
- **Google OAuth:** Deshabilitado
- **Acceso:** Login normal (email + contraseña)

## 🔐 Credenciales de Acceso

### Formato de Credenciales
- **Email:** `[DNI]@cased.edu.pe`
- **Contraseña:** `[DNI]`

### Ejemplos de Acceso

**4to F:**
- Email: `61791657@cased.edu.pe` / Contraseña: `61791657`
- Email: `61912715@cased.edu.pe` / Contraseña: `61912715`

**5to A:**
- Email: `61516890@cased.edu.pe` / Contraseña: `61516890`
- Email: `61374502@cased.edu.pe` / Contraseña: `61374502`

## 📈 Salida Esperada

### Ejemplo de Ejecución Exitosa
```
================================================================================
🎓 SCRIPT DE MIGRACIÓN A PRODUCCIÓN - ESTUDIANTES 5TO A
🏫 Institución: TÉCNICO FAP MANUEL POLO JIMÉNEZ
📚 Grado: 5to (QUINTO) - Sección: A
👥 Estudiantes: 15
================================================================================

🚀 Iniciando migración a producción...

🏫 Configurando institución...
   ✅ Institución encontrada: TÉCNICO FAP MANUEL POLO JIMÉNEZ
📚 Configurando estructura académica...
   ✅ Grado encontrado: QUINTO
   ✅ Sección encontrada: QUINTO - Sección A
👥 Registrando estudiantes...

 1/15. Nicolle Elizabeth Cruz Clawijo          ✅ CREADO
       📧 61516890@cased.edu.pe
       🔑 61516890
       🔐 Login: ✅

 2/15. Dayra Chunga Acosta                     ✅ CREADO
       📧 61374502@cased.edu.pe
       🔑 61374502
       🔐 Login: ✅

[... más estudiantes ...]

🔢 Actualizando contadores...
   ✅ Sección QUINTO - Sección A: 15 estudiantes
🔍 Verificando sistema...
   🧪 Nicolle Elizabeth: ✅ OK
   🧪 Dayra: ✅ OK
   🧪 Nephi Mijhail: ✅ OK
   📊 Total estudiantes activos: 35
   📊 Total matrículas activas: 35

================================================================================
🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!
================================================================================
✅ Estudiantes creados: 15
🔄 Estudiantes actualizados: 0
❌ Errores: 0

📋 INFORMACIÓN DE ACCESO:
   URL: https://tu-dominio-produccion.com/login/
   Método: Email + Contraseña
   Ejemplo: 61516890@cased.edu.pe / 61516890

🎯 CARACTERÍSTICAS DE LAS CUENTAS:
   - Edades: 16-17 años (nacidos 2008-2009)
   - Acceso: Login normal (email + contraseña)
   - Google OAuth: Deshabilitado
   - Estructura: Igual que estudiantes 4F

✅ El sistema está listo para producción!
================================================================================
```

## 🛠️ Resolución de Problemas

### Error: "Multiple users returned"
Si aparece este error, significa que hay usuarios duplicados. El script maneja esto automáticamente usando `.first()`.

### Error: "Module not found"
Asegúrate de ejecutar el script desde el directorio raíz del proyecto:
```bash
cd /ruta/al/proyecto
python scripts/deploy_production_students_5a.py
```

### Error de Autenticación
Verifica que el backend de autenticación esté configurado correctamente en `settings.py`:
```python
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

## 📞 Soporte

Si encuentras problemas durante la migración, revisa:
1. Configuración de la base de datos
2. Variables de entorno
3. Configuración de autenticación
4. Logs del servidor

---

**Nota:** Estos scripts están diseñados específicamente para el colegio TÉCNICO FAP MANUEL POLO JIMÉNEZ y sus estudiantes de 4to F y 5to A. 