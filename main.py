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
    description="API REST de Operaciones Matemáticas y Telemetría para Simulación DevOps (Universidad ICESI)",
    version="1.0.0"
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
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
