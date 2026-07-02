from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.ControlActas import ControlActas
from Utils.decorator import http_decorator
from Config.db import get_db

control_actas_router = APIRouter()

@control_actas_router.post('/control_actas/terceros_con_acta', tags=["Control Actas"], response_model=dict)
@http_decorator
def terceros_con_acta(request: Request, db: Session = Depends(get_db)):
    response = ControlActas(db).terceros_con_acta()
    return response

@control_actas_router.post('/control_actas/listar', tags=["Control Actas"], response_model=dict)
@http_decorator
def listar(request: Request, db: Session = Depends(get_db)):
    response = ControlActas(db).listar()
    return response

@control_actas_router.post('/control_actas/guardar', tags=["Control Actas"], response_model=dict)
@http_decorator
def guardar(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ControlActas(db).guardar(data)
    return response

@control_actas_router.post('/control_actas/detalle', tags=["Control Actas"], response_model=dict)
@http_decorator
def detalle(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ControlActas(db).detalle(data)
    return response

@control_actas_router.post('/control_actas/registrar_revision', tags=["Control Actas"], response_model=dict)
@http_decorator
def registrar_revision(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ControlActas(db).registrar_revision(data)
    return response

@control_actas_router.post('/control_actas/historial_tercero', tags=["Control Actas"], response_model=dict)
@http_decorator
def historial_tercero(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ControlActas(db).historial_tercero(data)
    return response

@control_actas_router.post('/control_actas/guardar_seguimiento', tags=["Control Actas"], response_model=dict)
@http_decorator
def guardar_seguimiento(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ControlActas(db).guardar_seguimiento(data)
    return response
