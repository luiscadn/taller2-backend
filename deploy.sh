#!/usr/bin/env bash
# ==============================================================================
# Script de Despliegue Automatizado - Taller 2 DevOps: taller2-backend
# Universidad ICESI - Despliegue sin requerir privilegios sudo
# ==============================================================================

set -e

PORT=${PORT:-8080}
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

echo "=== [1/5] Iniciando despliegue de taller2-backend en puerto $PORT ==="

# ------------------------------------------------------------------------------
# 1. Verificación de Red / Firewall (Sin requerir sudo)
# ------------------------------------------------------------------------------
echo "=== [2/5] Verificación de Red ==="
echo "[INFO] Omitiendo configuración de UFW/sudo (despliegue en entorno sin privilegios root, firewall desactivado)."

# ------------------------------------------------------------------------------
# 2. Configuración de Entorno Virtual y Dependencias de Python
# ------------------------------------------------------------------------------
echo "=== [3/5] Verificando Entorno de Python y Dependencias ==="
if ! command -v python3 > /dev/null 2>&1; then
    echo "[ERROR] python3 no está instalado. Por favor instale Python 3.9+ antes de continuar."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual venv..."
    python3 -m venv venv
fi

echo "Instalando / Actualizando dependencias desde requirements.txt..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt --quiet

# ------------------------------------------------------------------------------
# 3. Permisos de Persistencia (SoR)
# ------------------------------------------------------------------------------
echo "=== [4/5] Configurando Permisos de Persistencia (sor_history.txt) ==="
touch sor_history.txt
chmod 666 sor_history.txt || true
echo "Permisos de lectura/escritura (chmod 666) asignados a sor_history.txt."

# ------------------------------------------------------------------------------
# 4. Detener instancias previas y Ejecutar Servidor en Segundo Plano (nohup)
# ------------------------------------------------------------------------------
echo "=== [5/5] Ejecutando Backend con Uvicorn en segundo plano ==="

# Buscar y finalizar procesos anteriores corriendo en el mismo puerto 8080
PID=$(lsof -ti:$PORT || true)
if [ -n "$PID" ]; then
    echo "Deteniendo proceso previo en el puerto $PORT (PID: $PID)..."
    kill -9 $PID || true
    sleep 1
fi

# Iniciar Uvicorn usando nohup
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port $PORT > backend.log 2>&1 &
NEW_PID=$!

sleep 2

if ps -p $NEW_PID > /dev/null; then
    echo "=========================================================================="
    echo "🚀 ¡DESPLIEGUE EXITOSO DE taller2-backend!"
    echo "PID del Proceso: $NEW_PID"
    echo "URL Backend:     http://localhost:$PORT"
    echo "Health Check:    http://localhost:$PORT/health"
    echo "Log de Salida:   $APP_DIR/backend.log"
    echo "=========================================================================="
else
    echo "[ERROR] El servidor falló al iniciar. Revisa $APP_DIR/backend.log para más detalles."
    cat backend.log
    exit 1
fi
