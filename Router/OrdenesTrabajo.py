from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.OrdenesTrabajo import OrdenesTrabajo
from Utils.decorator import http_decorator
from Config.db import get_db

orden_trabajo_router = APIRouter()

@orden_trabajo_router.post('/guardar_orden_trabajo', tags=["Ordenes de Trabajo"], response_model=dict)
@http_decorator
def guardar_orden_trabajo(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = OrdenesTrabajo(db).guardar_orden_trabajo(data)
    return response

@orden_trabajo_router.post('/consultar_data_ot', tags=["Ordenes de Trabajo"], response_model=dict)
@http_decorator
def consultar_data_ot(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = OrdenesTrabajo(db).consultar_data_ot(data)
    return response

@orden_trabajo_router.post('/actualizar_estado_ot', tags=["Ordenes de Trabajo"], response_model=dict)
@http_decorator
def actualizar_estado_ot(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = OrdenesTrabajo(db).actualizar_estado_ot(data)
    return response

@orden_trabajo_router.post('/agregar_actividad_ot', tags=["Ordenes de Trabajo"], response_model=dict)
@http_decorator
def agregar_actividad_ot(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = OrdenesTrabajo(db).agregar_actividad_ot(data)
    return response
