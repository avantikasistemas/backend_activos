from typing import Optional
from pydantic import BaseModel

class ConsultarActivo(BaseModel):
    codigo: str = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
