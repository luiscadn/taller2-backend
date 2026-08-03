import logging
from datetime import datetime, timezone
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
    description="API REST de Operaciones Matemáticas (HU1 - Servicio de Suma)",
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

# Schemas Pydantic
class OperationRequest(BaseModel):
    a: float = Field(..., description="Primer operando")
    b: float = Field(..., description="Segundo operando")

class OperationResponse(BaseModel):
    result: float
    operation: str
    timestamp: str

@app.get("/")
def read_root():
    return {
        "service": "taller2-backend",
        "status": "running",
        "hu": "HU1",
        "docs": "/docs"
    }

# HU1: Servicio de Suma (Único Endpoint Operacional en HU1)
@app.post("/api/sum", response_model=OperationResponse)
def calculate_sum(payload: OperationRequest):
    result = payload.a + payload.b
    op_str = f"SUMA: {payload.a} + {payload.b} = {result}"
    logger.info(op_str)
    return OperationResponse(
        result=result,
        operation=op_str,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
