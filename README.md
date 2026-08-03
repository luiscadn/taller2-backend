# 🚀 Repositorio 1: taller2-backend

Servicio API REST para el **Taller 2: Simulación de Despliegue DevOps — La Pared de la Confusión y Automatización** de la Universidad ICESI. Desarrollado en Python con FastAPI y Uvicorn.

---

## 📋 Historias de Usuario Implementadas

- **HU1 (Servicio de Suma)**: `POST /api/sum` → Recibe `{"a": float, "b": float}`, retorna `{"result": float}` y persiste la operación en `sor_history.txt`.
- **HU2 (Multi-Operación)**:
  - `POST /api/subtract` → Resta los valores y persiste.
  - `POST /api/multiply` → Multiplica los valores y persiste.
- **HU3 (Historial SoR)**: `GET /api/history` → Retorna las últimas 5 operaciones exitosas registradas en `sor_history.txt`.
- **HU4 (División con Validación - Fase 2)**: `POST /api/divide` → Si `b == 0`, retorna HTTP 400 Bad Request `{"error": "División por cero no permitida"}` y escribe un error en logs de Ops.
- **HU5 (Telemetría / Health Check - Fase 2)**: `GET /health` → Retorna el estado del servicio (`UP`), tiempo de actividad (uptime) y permisos de escritura en la persistencia.

---

## 📂 Estructura del Repositorio

```text
taller2-backend/
├── main.py            # API REST con FastAPI (HU1 a HU5)
├── requirements.txt   # Dependencias del proyecto (fastapi, uvicorn, pydantic)
├── deploy.sh          # Script Bash de despliegue e infraestructura como código (Fase 2)
├── sor_history.txt    # Archivo de persistencia de operaciones (Sistema de Registro)
├── .gitignore         # Exclusiones de Git (venv, logs, sor_history.txt)
└── README.md          # Instrucciones de despliegue para Fase 1 y Fase 2
```

---

## 🛠️ Guía de Despliegue Manual — Fase 1 (Silos Organizacionales / ZIP)

En la Fase 1, la comunicación entre **Devs** y **Ops** se realiza a través de un canal asincrónico empaquetando el código en un archivo `.zip`.

### Instrucciones para Ops (Servidor de Producción PC 1):

1. **Descomprimir el código**:
   ```bash
   unzip taller2-backend.zip -d taller2-backend
   cd taller2-backend
   ```

2. **Configurar la Regla de Firewall (UFW)**:
   > ⚠️ **RESTRICCIÓN DE RED**: El cortafuegos debe bloquear todo el tráfico entrante excepto el puerto del Backend (`8080`).
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 8080/tcp comment 'Permitir Backend Taller 2'
   sudo ufw enable
   sudo ufw status verbose
   ```

3. **Crear Entorno Virtual e Instalar Dependencias**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Garantizar Permisos de Persistencia**:
   ```bash
   touch sor_history.txt
   chmod 666 sor_history.txt
   ```

5. **Iniciar el Servidor**:
   ```bash
   nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 > backend.log 2>&1 &
   ```

6. **Verificar Ejecución**:
   ```bash
   curl http://localhost:8080/health
   ```

---

## ⚡ Guía de Despliegue Automatizado — Fase 2 (Adopción DevOps / IaC)

En la Fase 2, se eliminan los silos y el equipo ejecuta el script de automatización `deploy.sh`:

1. **Dar permisos de ejecución al script**:
   ```bash
   chmod +x deploy.sh
   ```

2. **Ejecutar el script de despliegue**:
   ```bash
   ./deploy.sh
   ```

El script `deploy.sh` realizará automáticamente:
- Apertura del puerto `8080` en el firewall `ufw` (si aplica en Linux).
- Verificación/creación del entorno virtual `venv` e instalación de dependencias.
- Asignación de permisos `chmod 666` al archivo de persistencia `sor_history.txt`.
- Detención de instancias previas y arranque en segundo plano mediante `nohup`.

---

## 🧪 Pruebas Rápidas con cURL

```bash
# HU1: Suma
curl -X POST http://localhost:8080/api/sum -H "Content-Type: application/json" -d '{"a": 10, "b": 5}'

# HU4: División por Cero (debe retornar 400 Bad Request)
curl -i -X POST http://localhost:8080/api/divide -H "Content-Type: application/json" -d '{"a": 10, "b": 0}'

# HU3: Historial
curl http://localhost:8080/api/history

# HU5: Health Check
curl http://localhost:8080/health
```
