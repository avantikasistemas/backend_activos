from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Schemas.Activos.consultar_activo import ConsultarActivo
from Class.Parametros import Parametros
from Utils.decorator import http_decorator
from Config.db import get_db

parametros_router = APIRouter()

@parametros_router.post('/params/obtener_macroprocesos', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_macroprocesos(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_macroprocesos()
    return response

@parametros_router.post('/params/obtener_estados', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_estados(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_estados()
    return response

@parametros_router.post('/params/obtener_sedes', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_sedes(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_sedes()
    return response

@parametros_router.post('/params/obtener_centros', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_centros(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_centros()
    return response

@parametros_router.post('/params/obtener_grupo_contable', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_grupo_contable(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_grupo_contable()
    return response

@parametros_router.post('/params/obtener_proveedor', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_proveedor(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_proveedor()
    return response

@parametros_router.post('/params/obtener_tercero', tags=["Parametros"], response_model=dict)
@http_decorator
def obtener_tercero(request: Request, db: Session = Depends(get_db)):
    response = Parametros(db).obtener_tercero()
    return response
