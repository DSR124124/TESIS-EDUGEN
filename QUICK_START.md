# 🚀 Guía de Inicio Rápido - EduGen

## ⚡ Instalación en 5 Minutos

### 1. Clonar y Configurar
```bash
git clone <URL_DEL_REPOSITORIO>
cd sistema-educativo
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Ejecutar
```bash
python manage.py runserver
```

**¡Listo!** Abre http://localhost:8000

## 🎯 Acceso Rápido

- **Admin**: http://localhost:8000/admin
- **Dashboard**: http://localhost:8000/dashboard
- **Director Panel**: http://localhost:8000/director

## 📱 Usuarios de Prueba

Después de crear el superusuario, puedes crear usuarios de prueba desde el admin panel para cada rol:

- **Estudiante**: Para acceder a portafolios
- **Profesor**: Para crear contenido con IA
- **Director**: Para gestión institucional

## 🤖 Configurar IA (Opcional)

Para usar la generación de contenido con IA:

1. Obtén una API key de DeepSeek
2. Configura en `config/settings/__init__.py`:
   ```python
   DEEPSEEK_API_KEY = "tu-api-key-aqui"
   ```

## 🌐 Despliegue en Azure

Ver documentación completa en el README.md principal.

Variables de entorno necesarias:
- `SECRET_KEY`
- `DATABASE_URL` 
- `DEEPSEEK_API_KEY`
- `ALLOWED_HOSTS`

---

Para documentación completa, ver [README.md](README.md) 