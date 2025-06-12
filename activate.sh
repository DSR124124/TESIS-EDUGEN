#!/bin/bash

# Script para activar el entorno virtual en Linux/Mac
echo -e "\033[32mActivando entorno virtual...\033[0m"
source .venv/bin/activate

# Verificar si el entorno virtual se activó correctamente
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "\033[32mEntorno virtual activado correctamente: $VIRTUAL_ENV\033[0m"
else
    echo -e "\033[31mError al activar el entorno virtual\033[0m"
    exit 1
fi

# Mostrar información del proyecto
echo -e "\033[36mSistema Educativo - Entorno activado\033[0m"
echo -e "\033[36mPara ejecutar el proyecto: python manage.py runserver\033[0m" 