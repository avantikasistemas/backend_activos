from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime
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

    # Función para actualizar el estado de una orden de trabajo
    def actualizar_estado_ot(self, data: dict):
        """ Api que actualiza el estado de una orden de trabajo. """

        try:
            ot_id = data["ot_id"]
            estado_ot = data["estado"]
            if not estado_ot:
                raise CustomException("El estado es obligatorio.")

            # Consultamos la información de la orden de trabajo en la base de datos
            self.querys.actualizar_estado_ot(ot_id, estado_ot)

            # Retornamos la información.
            return self.tools.output(
                200, 
                f"La orden de trabajo #{ot_id} ha cambiado de estado."
            )

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para agregar una actividad a una orden de trabajo
    def agregar_actividad_ot(self, data: dict):
        """ Api que agrega una actividad a una orden de trabajo. """

        try:
            ot_id = data["ot_id"]
            descripcion = data["descripcion"]
            tecnico = data["tecnico"]

            if not ot_id:
                raise CustomException("El ID de la orden de trabajo es obligatorio.")
            if not descripcion:
                raise CustomException("La descripción es obligatoria.")

            # Agregamos la actividad a la orden de trabajo en la base de datos
            self.querys.agregar_actividad_ot(ot_id, descripcion, tecnico)

            # Retornamos la información.
            return self.tools.output(200, f"Actividad agregada con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")
