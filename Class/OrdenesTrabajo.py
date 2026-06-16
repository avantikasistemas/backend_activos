from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime, date
import calendar
from fastapi.responses import StreamingResponse
import io
from io import BytesIO
import os
from urllib.parse import urljoin
import base64
import uuid
import re
from io import BytesIO
from PIL import Image
import json

UPLOAD_FOLDER = "Uploads/"
EXTENSIONES = ["jpg", "jpeg", "png"]

class OrdenesTrabajo:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para guardar una orden de trabajo
    def guardar_orden_trabajo(self, data: dict):
        """ Api que realiza la creación de una orden de trabajo. """

        try:
            # Creamos la orden de trabajo en la base de datos
            orden_trabajo_id = self.querys.guardar_orden_trabajo(data)

            # Si es preventivo y el activo pertenece al grupo de servidores, registrar en GSC
            if data.get("tipo_mantenimiento") in (1, 2):
                grupo = self.querys.get_grupo_activo(data["activo_id"])
                if str(grupo) == self.GRUPO_SERVIDORES:
                    self.querys.insertar_gsc_registro(self._resumen_gsc())

            # Retornamos la información.
            return self.tools.output(200, "Orden de trabajo creada con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para consultar la información de una orden de trabajo
    def consultar_data_ot(self, data: dict):
        """ Api que realiza la consulta de la información de una orden de trabajo. """

        try:
            # Consultamos la información de la orden de trabajo en la base de datos
            orden_trabajo = self.querys.consultar_data_ot(data["ot_id"])
            
            # Consultamos si hay actividades asociadas a la orden de trabajo
            actividades = self.querys.consultar_actividades_ot(data["ot_id"])
            
            # Creamos la respuesta
            response = {
                "orden_trabajo": orden_trabajo,
                "actividades": actividades,
            }

            # Retornamos la información.
            return self.tools.output(200, "Consulta exitosa.", response)

        except CustomException as e:
            raise CustomException(f"{e}")

    GRUPO_SERVIDORES = "16"

    def _resumen_gsc(self) -> str:
        now = datetime.now()
        hora = str(now.hour % 12 or 12)
        ampm = 'a.m.' if now.hour < 12 else 'p.m.'
        return f"Registro MNT - {now.day}/{now.month}/{now.year}, {hora}:{now.minute:02d}:{now.second:02d} {ampm}"

    def _siguiente_fecha_ciclo(self, fecha_desde: str):
        """Calcula las fechas de la siguiente OT en el ciclo marzo/septiembre.
        Marzo -> Septiembre del mismo año. Septiembre -> Marzo del año siguiente."""
        fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        mes, año = fecha.month, fecha.year

        if mes == 9:
            sig_año, sig_mes = año + 1, 3
        elif mes == 3:
            sig_año, sig_mes = año, 9
        else:
            return None

        ultimo_dia = calendar.monthrange(sig_año, sig_mes)[1]
        return (
            date(sig_año, sig_mes, 1).strftime('%Y-%m-%d'),
            date(sig_año, sig_mes, ultimo_dia).strftime('%Y-%m-%d'),
        )

    # Función para agregar una actividad a una orden de trabajo
    def agregar_actividad_ot(self, data: dict):
        """ Api que agrega una actividad a una orden de trabajo. """

        try:
            ot_id = data["ot_id"]
            descripcion = data["descripcion"]
            tecnico = data["tecnico"]
            estado = data["estado"]

            if not ot_id:
                raise CustomException("El ID de la orden de trabajo es obligatorio.")
            if not descripcion:
                raise CustomException("La descripción es obligatoria.")
            if not estado:
                raise CustomException("El estado es obligatorio.")

            # Agregamos la actividad a la orden de trabajo en la base de datos
            self.querys.agregar_actividad_ot(ot_id, descripcion, tecnico)

            # Actualizamos el estado de la orden de trabajo
            self.querys.actualizar_estado_ot(ot_id, estado)

            # Si la OT quedó completada, creamos la siguiente OT programada
            ESTADO_COMPLETADO = 3
            if int(estado) == ESTADO_COMPLETADO:
                ot_data = self.querys.consultar_data_ot(ot_id)
                siguiente = self._siguiente_fecha_ciclo(ot_data["fecha_programacion_desde"])
                if siguiente:
                    fecha_desde, fecha_hasta = siguiente
                    nueva_ot_params = {
                        "activo_id": ot_data["activo_id"],
                        "tipo_mantenimiento": ot_data["tipo_mantenimiento"],
                        "fecha_programacion_desde": fecha_desde,
                        "fecha_programacion_hasta": fecha_hasta,
                        "tecnico_asignado": ot_data["tecnico_asignado"],
                        "descripcion": ot_data["descripcion"],
                    }
                    self.querys.guardar_orden_trabajo(nueva_ot_params)
                    # Si la nueva OT es preventiva y el activo es del grupo de servidores, registrar en GSC
                    if nueva_ot_params["tipo_mantenimiento"] == 1:
                        grupo = self.querys.get_grupo_activo(ot_data["activo_id"])
                        if str(grupo) == self.GRUPO_SERVIDORES:
                            self.querys.insertar_gsc_registro(self._resumen_gsc())

            # Retornamos la información.
            return self.tools.output(200, "Actividad agregada con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    def guardar_ordenes_masivas(self, data: dict):
        """ Api que realiza la creación masiva de órdenes de trabajo. """

        try:
            grupo = data["grupo"]
            fecha_programacion_desde = data["fecha_programacion_desde"]
            fecha_programacion_hasta = data["fecha_programacion_hasta"]
            tecnico_asignado = data["tecnico_asignado"]
            descripcion = data["descripcion"]
            
            activos_x_grupo = self.querys.obtener_activos_x_grupo(grupo)
            if activos_x_grupo:
                for activo in activos_x_grupo:
                    params = {
                        "activo_id": activo["id"],
                        "tipo_mantenimiento": 1,
                        "fecha_programacion_desde": fecha_programacion_desde,
                        "fecha_programacion_hasta": fecha_programacion_hasta,
                        "tecnico_asignado": tecnico_asignado,
                        "descripcion": descripcion,
                    }
                    self.querys.guardar_orden_trabajo(params)
                    # Si el grupo es de servidores, registrar cada OT preventiva en GSC
                    if str(grupo) == self.GRUPO_SERVIDORES:
                        self.querys.insertar_gsc_registro(self._resumen_gsc())

            # Retornamos la información.
            return self.tools.output(200, "Órdenes de trabajo creadas con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para consultar las órdenes de trabajo
    def consultar_ordenes_trabajo(self, data: dict):
        """ Api que realiza la consulta de las órdenes de trabajo. """

        try:
            
            if data["position"] <= 0:
                message = "El campo posición no es válido"
                raise CustomException(message)

            # Consultamos la información de las órdenes de trabajo en la base de datos
            ordenes_trabajo = self.querys.consultar_ordenes_trabajo(data)

            registros = ordenes_trabajo["registros"]
            cant_registros = ordenes_trabajo["cant_registros"]
            
            if not registros:
                message = "No hay listado que mostrar."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })
                
            if cant_registros%data["limit"] == 0:
                total_pag = cant_registros//data["limit"]
            else:
                total_pag = cant_registros//data["limit"] + 1
                
            if total_pag < int(data["position"]):
                message = "La posición excede el número total de registros."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })
                
            registros_dict = {
                "total_registros": cant_registros,
                "total_pag": total_pag,
                "posicion_pag": data["position"],
                "registros": registros
            }

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", registros_dict)

        except CustomException as e:
            raise CustomException(f"{e}")
