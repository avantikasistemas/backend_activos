from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Schemas.Activos.consultar_activo import ConsultarActivo
from Schemas.Activos.retirar_activo import RetirarActivo
from Class.Activos import Activos
from Utils.decorator import http_decorator
from Config.db import get_db

activos_router = APIRouter()

@activos_router.post('/consultar_activo', tags=["Activos"], response_model=dict)
@http_decorator
def consultar_activo(request: Request, consultar_activo: ConsultarActivo, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).consultar_activo(data)
    return response

@activos_router.post('/retirar_activo', tags=["Activos"], response_model=dict)
@http_decorator
def retirar_activo(request: Request, retirar_activo: RetirarActivo, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).retirar_activo(data)
    return response
