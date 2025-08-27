from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime
import traceback

class Activos:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para consultar un activo
    def consultar_activo(self, data: dict):
        """ Api que realiza la consulta del activo. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        codigo = data["codigo"]

        try:
            # Consultamos el activo en la base de datos
            data_activo = self.querys.get_activo(codigo)
            if data_activo["retirado"] == 1:
                raise CustomException("Activo se encuentra retirado.")
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", data_activo)

        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener información de activo: {e}")
            raise CustomException(f"{e}")

    # Función para retirar un activo
    def retirar_activo(self, data: dict):
        """ Api que realiza el retiro de un activo. """

        # Asignamos nuestros datos de entrada a sus respectivas variables
        codigo = data["codigo"]
        motivo = data["motivo"]

        try:
            # Consultamos el activo en la base de datos
            data_activo = self.querys.get_activo(codigo)
            if data_activo["retirado"] == 1:
                raise CustomException("Activo se encuentra retirado.")

            # Retiramos el activo
            self.querys.retirar_activo(codigo, motivo)

            # Retornamos la información.
            return self.tools.output(200, "Activo retirado con éxito.")

        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener información de activo: {e}")
            raise CustomException(f"{e}")
