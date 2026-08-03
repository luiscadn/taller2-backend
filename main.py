import os
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI
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
    description="API REST de Operaciones Matemáticas (HU3 - Persistencia SoR e Historial)",
    version="1.2.0"
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

# ------------------- RUTAS HTTP (HU1 - HU3) -------------------

@app.get("/")
def read_root():
    return {
        "service": "taller2-backend",
        "status": "running",
        "hu": "HU3",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
