@echo off
echo 🚀 DEPLOY MANUAL SIMPLE DE EDUGEN A AZURE
echo ==========================================

echo.
echo 🔧 Paso 1: Verificando Azure CLI...
az --version
if %errorlevel% neq 0 (
    echo ❌ Azure CLI no está disponible
    pause
    exit /b 1
)

echo.
echo 🔧 Paso 2: Verificando login de Azure...
az account show
if %errorlevel% neq 0 (
    echo ❌ No estás logueado en Azure
    echo Ejecutando az login...
    az login
)

echo.
echo 🔧 Paso 3: Configurando variables de entorno en Azure...
az webapp config appsettings set --resource-group rg-edugen --name edugen-app --settings ^
    DJANGO_SETTINGS_MODULE="config.settings.azure_production" ^
    DATABASE_NAME="edugen" ^
    DATABASE_USER="postgres" ^
    DATABASE_PASSWORD="EduGen123!" ^
    DATABASE_HOST="edugen-db-2024-01.postgres.database.azure.com" ^
    DATABASE_PORT="5432" ^
    SECRET_KEY="your-production-secret-key-here" ^
    ALLOWED_HOSTS="edugen-app.azurewebsites.net" ^
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" ^
    ENABLE_ORYX_BUILD="true" ^
    WEBSITES_CONTAINER_START_TIME_LIMIT="1800"

echo.
echo 🔧 Paso 4: Ejecutando deploy...
az webapp up --name edugen-app --resource-group rg-edugen --runtime "PYTHON:3.11" --sku B1

if %errorlevel% equ 0 (
    echo.
    echo 🎉 ¡DEPLOY COMPLETADO EXITOSAMENTE!
    echo 🌐 URL: https://edugen-app.azurewebsites.net
    echo 🔧 Admin: https://edugen-app.azurewebsites.net/admin/
    echo 👤 Usuario: admin / EduGenAdmin123!
) else (
    echo.
    echo ❌ Deploy falló. Revisa los errores arriba.
)

echo.
pause 