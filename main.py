import os
import time
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuración de Logging para trazabilidad de Ops
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("taller2-backend")

app = FastAPI(
    title="Taller 2 DevOps Backend",
    description="API REST de Operaciones Matemáticas, SoR y Telemetría para Simulación DevOps (Universidad ICESI)",
    version="2.0.0"
)

# Habilitar CORS para permitir llamadas desde el Frontend (PC 2 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constantes y Variables Globales de Estado
START_TIME = time.time()
HISTORY_FILE = os.path.abspath("sor_history.txt")

# Schemas Pydantic
class OperationRequest(BaseModel):
    a: float = Field(..., description="Primer operando")
    b: float = Field(..., description="Segundo operando")

class OperationResponse(BaseModel):
    result: float
    operation: str
    timestamp: str

class HistoryResponse(BaseModel):
    history: List[str]

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    persistence_writable: bool
    timestamp: str

def save_to_sor_history(operation_str: str) -> bool:
    """Guarda un registro de la operación exitosa en el archivo de persistencia local (SoR)."""
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = f"[{timestamp}] {operation_str}\n"
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"SoR Persistido: {operation_str}")
        return True
    except Exception as e:
        logger.error(f"Error al escribir en SoR history ({HISTORY_FILE}): {e}")
        return False

# ------------------- RUTAS HTTP (HU1 - HU5) -------------------

@app.get("/")
def read_root():
    return {
        "service": "taller2-backend",
        "status": "running",
        "fase": "Fase 2",
        "docs": "/docs"
    }

# HU1: Servicio de Suma
@app.post("/api/sum", response_model=OperationResponse)
def calculate_sum(payload: OperationRequest):
    result = payload.a + payload.b
    op_str = f"SUMA: {payload.a} + {payload.b} = {result}"
    save_to_sor_history(op_str)
    return OperationResponse(
        result=result,
        operation=op_str,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# HU2: Multi-Operación (Resta)
@app.post("/api/subtract", response_model=OperationResponse)
def calculate_subtract(payload: OperationRequest):
    result = payload.a - payload.b
    op_str = f"RESTA: {payload.a} - {payload.b} = {result}"
    save_to_sor_history(op_str)
    return OperationResponse(
        result=result,
        operation=op_str,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# HU2: Multi-Operación (Multiplicación)
@app.post("/api/multiply", response_model=OperationResponse)
def calculate_multiply(payload: OperationRequest):
    result = payload.a * payload.b
    op_str = f"MULTIPLICACION: {payload.a} * {payload.b} = {result}"
    save_to_sor_history(op_str)
    return OperationResponse(
        result=result,
        operation=op_str,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# HU4: División con Validación (Fase 2)
@app.post("/api/divide", response_model=OperationResponse)
def calculate_divide(payload: OperationRequest):
    if payload.b == 0:
        error_msg = f"Fallo de validación en División: Intento de división por cero (a={payload.a}, b={payload.b})"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "División por cero no permitida"}
        )
    
    result = payload.a / payload.b
    op_str = f"DIVISION: {payload.a} / {payload.b} = {result}"
    save_to_sor_history(op_str)
    return OperationResponse(
        result=result,
        operation=op_str,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# HU3: Historial SoR (Últimas 5 operaciones)
@app.get("/api/history", response_model=HistoryResponse)
def get_history():
    if not os.path.exists(HISTORY_FILE):
        return HistoryResponse(history=[])
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        # Retornar las últimas 5 operaciones en orden invertido (las más recientes primero)
        recent_history = list(reversed(lines[-5:]))
        return HistoryResponse(history=recent_history)
    except Exception as e:
        logger.error(f"Error al leer SoR history: {e}")
        return HistoryResponse(history=[])

# HU5: Telemetría / Health Check (Fase 2)
@app.get("/health", response_model=HealthResponse)
def health_check():
    uptime = round(time.time() - START_TIME, 2)
    
    # Verificar permisos de escritura en la persistencia SoR
    writable = False
    try:
        # Asegurarse que el archivo existe
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("")
        # Probar si el archivo es escribible
        writable = os.access(HISTORY_FILE, os.W_OK)
    except Exception as e:
        logger.error(f"Verificación de permisos fallida en {HISTORY_FILE}: {e}")
        writable = False
        
    return HealthResponse(
        status="UP",
        uptime_seconds=uptime,
        persistence_writable=writable,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
