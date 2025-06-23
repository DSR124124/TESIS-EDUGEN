# 📚 Manuales de Despliegue - Sistema EduGen

## 🎯 Guías Disponibles

Este proyecto incluye varios manuales de despliegue según tus necesidades específicas:

---

## 📖 Manuales Disponibles

### 1. 🚀 **MANUAL_DESPLIEGUE_COMPLETO.md**
**Para: Instalación desde cero en cualquier entorno**

- ✅ **Ideal para:** Nuevas instalaciones, desarrollo local, primera vez
- 📋 **Incluye:** Desde descargar el proyecto hasta tenerlo funcionando
- 🎯 **Cubre:** Windows, Linux, macOS, desarrollo y producción
- 📦 **Contenido:**
  - Instalación de Python, Git, PostgreSQL
  - Clonado desde GitHub
  - Configuración de entorno virtual
  - Base de datos local y remota
  - Variables de entorno
  - Carga de datos iniciales
  - Pruebas del sistema
  - Despliegue en Azure

### 2. ☁️ **MANUAL_DESPLIEGUE_AZURE.md**
**Para: Despliegue específico en Azure App Service**

- ✅ **Ideal para:** Despliegue en producción Azure
- 📋 **Incluye:** Configuración específica de Azure
- 🎯 **Cubre:** App Service, PostgreSQL Azure, variables de entorno
- 📦 **Contenido:**
  - Configuración de Azure CLI
  - Creación de recursos Azure
  - PostgreSQL en Azure
  - Variables de entorno Azure
  - Monitoreo y logs
  - Solución de problemas Azure

### 3. 📜 **scripts/README_PRODUCTION_DEPLOYMENT.md** *(Eliminado)*
**Para: Scripts de migración de estudiantes**

- ✅ **Ideal para:** Carga de datos de estudiantes específicos
- 📋 **Incluye:** Scripts para estudiantes 4F y 5A
- 🎯 **Cubre:** Migración automática de datos
- 📦 **Contenido:** *(Archivo eliminado, contenido integrado en otros manuales)*

---

## 🛤️ ¿Qué Manual Usar?

### 🆕 **¿Primera vez con el proyecto?**
```
📖 Usa: MANUAL_DESPLIEGUE_COMPLETO.md
🎯 Te guiará paso a paso desde cero
```

### ☁️ **¿Ya tienes el proyecto y quieres desplegarlo en Azure?**
```
📖 Usa: MANUAL_DESPLIEGUE_AZURE.md
🎯 Configuración específica para Azure
```

### 🔧 **¿Necesitas resolver problemas específicos?**
```
📖 Revisa: Sección de "Solución de Problemas" en ambos manuales
🎯 Problemas comunes y sus soluciones
```

---

## 🚀 Flujo Recomendado

### Para Desarrollo Local
```bash
1. 📖 Sigue MANUAL_DESPLIEGUE_COMPLETO.md (Secciones 1-8)
2. 🧪 Prueba el sistema localmente
3. 🔧 Realiza tus modificaciones
4. 📤 Sube cambios a GitHub
```

### Para Producción Azure
```bash
1. ✅ Asegúrate de que funciona localmente
2. 📖 Sigue MANUAL_DESPLIEGUE_AZURE.md
3. ☁️ Configura recursos Azure
4. 🚀 Despliega desde GitHub
5. 📊 Monitorea y mantén
```

---

## 🎯 Características de Cada Manual

| Aspecto | Manual Completo | Manual Azure |
|---------|----------------|--------------|
| **Audiencia** | Principiantes | Usuarios con experiencia |
| **Alcance** | Instalación completa | Solo despliegue Azure |
| **Duración** | 2-4 horas | 30-60 minutos |
| **Prerequisitos** | Ninguno | Proyecto ya configurado |
| **Entornos** | Local + Producción | Solo Producción |

---

## 📞 Soporte

### 🆘 Si tienes problemas:

1. **Revisa la sección de solución de problemas** en el manual correspondiente
2. **Verifica los logs** del sistema
3. **Consulta la documentación oficial** de Django/Azure
4. **Revisa las variables de entorno** y configuración

### 📋 Información útil para reportar problemas:

```bash
# Información del sistema
python --version
pip list
python manage.py check

# Logs recientes
# En desarrollo
python manage.py runserver --verbosity=2

# En Azure
az webapp log tail --name tu-app --resource-group tu-rg
```

---

## 🔄 Actualizaciones

Los manuales se actualizan regularmente. Verifica siempre que tengas la versión más reciente:

```bash
git pull origin main
```

---

**💡 Tip:** Empieza siempre con el **Manual Completo** si es tu primera vez, incluso si tu objetivo final es Azure. Te dará una base sólida para entender el sistema. 