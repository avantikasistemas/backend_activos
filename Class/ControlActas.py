from Utils.tools import Tools, CustomException
from Utils.querys import Querys


class ControlActas:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Devuelve todos los terceros cruzados con si tienen acta activa
    def terceros_con_acta(self):
        try:
            data = self.querys.ca_terceros_con_acta()
            return self.tools.output(200, "Datos encontrados.", data)
        except CustomException as e:
            raise CustomException(f"{e}")

    # Lista todas las auditorías registradas
    def listar(self):
        try:
            data = self.querys.ca_listar()
            return self.tools.output(200, "Datos encontrados.", data)
        except CustomException as e:
            raise CustomException(f"{e}")

    # Crea una nueva auditoría trimestral con los terceros seleccionados
    def guardar(self, data: dict):
        try:
            anio        = data["anio"]
            trimestre   = data["trimestre"]
            seleccionados = data["seleccionados"]   # lista de {nit, acta_id}

            if not anio or not trimestre:
                raise CustomException("El año y el trimestre son obligatorios.")
            if not seleccionados or len(seleccionados) == 0:
                raise CustomException("Debe seleccionar al menos un tercero.")

            control_id = self.querys.ca_guardar(anio, trimestre, seleccionados)
            return self.tools.output(200, "Auditoría creada correctamente.", {"control_id": control_id})
        except CustomException as e:
            raise CustomException(f"{e}")

    # Detalle de una auditoría: cabecera + detalles de terceros
    def detalle(self, data: dict):
        try:
            control_id = data["control_id"]
            resultado  = self.querys.ca_detalle(control_id)
            return self.tools.output(200, "Datos encontrados.", resultado)
        except CustomException as e:
            raise CustomException(f"{e}")

    # Historial de todas las revisiones de un tercero (auditorías + seguimientos)
    def historial_tercero(self, data: dict):
        try:
            nit = data["tercero_nit"]
            historial = self.querys.ca_historial_tercero(nit)
            return self.tools.output(200, "Historial encontrado.", historial)
        except CustomException as e:
            raise CustomException(f"{e}")

    # Guarda una revisión de seguimiento fuera del ciclo trimestral
    def guardar_seguimiento(self, data: dict):
        try:
            detalle_id  = data["detalle_id"]
            tercero_nit = data["tercero_nit"]
            coincide    = data["coincide"]
            observacion = data.get("observacion", "")

            if int(coincide) not in (0, 1):
                raise CustomException("El campo coincide debe ser 1 (sí) o 0 (no).")
            if int(coincide) == 0 and not observacion:
                raise CustomException("La observación es obligatoria cuando el acta no coincide.")

            self.querys.ca_guardar_seguimiento(detalle_id, tercero_nit, int(coincide), observacion)
            return self.tools.output(200, "Seguimiento registrado correctamente.")
        except CustomException as e:
            raise CustomException(f"{e}")

    # Registra la revisión (coincide/no + observación) de un tercero
    def registrar_revision(self, data: dict):
        try:
            detalle_id  = data["detalle_id"]
            coincide    = data["coincide"]       # 1 = coincide, 0 = no coincide
            observacion = data.get("observacion", "")

            if coincide not in (0, 1):
                raise CustomException("El campo coincide debe ser 1 (sí) o 0 (no).")
            if int(coincide) == 0 and not observacion:
                raise CustomException("La observación es obligatoria cuando el acta no coincide.")

            self.querys.ca_registrar_revision(detalle_id, coincide, observacion)
            return self.tools.output(200, "Revisión registrada correctamente.")
        except CustomException as e:
            raise CustomException(f"{e}")
