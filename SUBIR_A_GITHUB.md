# 📤 Instrucciones para Subir a GitHub

## 🆕 Crear Nuevo Repositorio

### 1. **Crear en GitHub.com**

1. Ve a https://github.com/new
2. **Repository name**: `edugen-sistema-educativo` (o el nombre que prefieras)
3. **Description**: `🎓 Sistema integral de gestión educativa con IA - Django`
4. **Visibilidad**: 
   - ✅ **Public** (recomendado para portfolio)
   - ⚪ Private (si es para uso interno)
5. **NO marques**: 
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Haz clic en **"Create repository"**

### 2. **Conectar Repositorio Local**

Copia y ejecuta estos comandos (GitHub te dará la URL específica):

```bash
# Agregar el repositorio remoto
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git

# Configurar la rama principal
git branch -M main

# Subir el código
git push -u origin main
```

### 3. **Configurar GitHub Actions (Opcional)**

Si quieres despliegue automático a Azure:

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Agrega el secreto `AZUREAPPSERVICE_PUBLISHPROFILE_EDUGEN`
4. El workflow en `.github/workflows/deploy.yml` se ejecutará automáticamente

## 🔧 Comandos Exactos

Reemplaza `TU_USUARIO` y `TU_REPOSITORIO` con tus datos:

```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git branch -M main  
git push -u origin main
```

## ✅ Verificación

Después de subir, tu repositorio debería tener:

- ✅ README.md completo
- ✅ Código fuente organizado
- ✅ GitHub Actions configurado
- ✅ Licencia MIT
- ✅ .gitignore apropiado

## 🌟 Mejorar el Repositorio

### Agregar Topics/Tags:
En GitHub, ve a **Settings** → **General** → **Topics**

Agrega:
- `django`
- `python`
- `education`
- `ai-integration`
- `azure`
- `portfolio`
- `education-management`

### Configurar GitHub Pages (Opcional):
- **Settings** → **Pages**
- Source: Deploy from a branch → `main` → `/docs`

## 🚀 URLs de Ejemplo

Después de subir, tu repositorio estará en:
- **Código**: `https://github.com/TU_USUARIO/TU_REPOSITORIO`
- **Actions**: `https://github.com/TU_USUARIO/TU_REPOSITORIO/actions`
- **Releases**: `https://github.com/TU_USUARIO/TU_REPOSITORIO/releases`

---

¡Tu proyecto estará listo para ser compartido y contribuido! 🎉 