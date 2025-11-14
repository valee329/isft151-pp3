@echo off
echo ===========================================
echo     OnlyFood - Deploy Script (Windows)
echo ===========================================

REM 1) Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

REM 2) Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

REM 3) Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM 4) Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM 5) Exportar variables de entorno necesarias
echo Configurando variables de entorno...

set FLASK_ENV=production
set SECRET_KEY=CAMBIAR_ESTE_VALOR
set DB_HOST=localhost
set DB_USER=tu_usuario
set DB_PASS=tu_password
set DB_NAME=onlyfood

REM 6) Mostrar configuración final
echo:
echo Variables de entorno configuradas:
echo FLASK_ENV=%FLASK_ENV%
echo DB_HOST=%DB_HOST%
echo DB_USER=%DB_USER%
echo DB_NAME=%DB_NAME%
echo:

REM 7) Iniciar la aplicación
echo Iniciando la aplicación...
python run.py

pause
