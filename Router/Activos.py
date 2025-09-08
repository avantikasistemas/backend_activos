from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Schemas.Activos.consultar_activo import ConsultarActivo
from Schemas.Activos.retirar_activo import RetirarActivo
from Schemas.Activos.guardar_activo import GuardarActivo
from Schemas.Activos.actualizar_activo import ActualizarActivo
from Schemas.Activos.consultar_historial import ConsultarHistorial
from Schemas.Activos.activos_x_tercero import ActivosXtercero
from Class.Activos import Activos
from Utils.decorator import http_decorator
from Config.db import get_db
import socket

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
    ip = request.client.host
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = None
    data = getattr(request.state, "json_data", {})
    response = Activos(db).retirar_activo(data, hostname)
    return response

@activos_router.post('/guardar_activo', tags=["Activos"], response_model=dict)
@http_decorator
def guardar_activo(request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = None
    data = getattr(request.state, "json_data", {})
    response = Activos(db).guardar_activo(data, hostname)
    return response

@activos_router.post('/actualizar_activo', tags=["Activos"], response_model=dict)
@http_decorator
def actualizar_activo(request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = None
    data = getattr(request.state, "json_data", {})
    response = Activos(db).actualizar_activo(data, hostname)
    return response

@activos_router.post('/consultar_historial', tags=["Activos"], response_model=dict)
@http_decorator
def consultar_historial(request: Request, consultar_historial: ConsultarHistorial, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).consultar_historial(data)
    return response

@activos_router.post('/activos_x_tercero', tags=["Activos"], response_model=dict)
@http_decorator
def activos_x_tercero(request: Request, activos_x_tercero: ActivosXtercero, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).activos_x_tercero(data)
    return response

@activos_router.post('/generar_acta', tags=["Activos"], response_model=dict)
@http_decorator
def generar_acta(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).generar_acta(data)
    return response

@activos_router.post('/enviar_correo', tags=["Activos"], response_model=dict)
@http_decorator
def enviar_correo(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).enviar_correo(data)
    return response

@activos_router.post('/consultar_datos_pdf', tags=["Activos"], response_model=dict)
@http_decorator
def consultar_datos_pdf(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).consultar_datos_pdf(data)
    return response

@activos_router.post('/responder_acta', tags=["Activos"], response_model=dict)
@http_decorator
def responder_acta(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Activos(db).responder_acta(data)
    return response
