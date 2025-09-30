from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime
import traceback

class Parametros:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para obtener los macroprocesos
    def obtener_macroprocesos(self):
        """ Api que realiza la consulta de los macroprocesos. """

        try:
            macroprocesos = self.querys.obtener_macroprocesos()
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", macroprocesos)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los estados
    def obtener_estados(self):
        """ Api que realiza la consulta de los estados. """

        try:
            estados = self.querys.obtener_estados()
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", estados)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener las sedes
    def obtener_sedes(self):
        """ Api que realiza la consulta de las sedes. """

        try:
            sedes = self.querys.obtener_sedes()
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", sedes)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los centros
    def obtener_centros(self):
        """ Api que realiza la consulta de los centros. """

        try:
            centros = self.querys.obtener_centros()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", centros)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los grupos contables
    def obtener_grupo_contable(self):
        """ Api que realiza la consulta de los grupos contables. """

        try:
            grupos = self.querys.obtener_grupo_contable()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", grupos)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los proveedores
    def obtener_proveedor(self):
        """ Api que realiza la consulta de los proveedores. """

        try:
            proveedores = self.querys.obtener_proveedor(1)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", proveedores)

        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener información de proveedores: {e}")
            raise CustomException(f"{e}")

    # Función para obtener los terceros
    def obtener_tercero(self):
        """ Api que realiza la consulta de los terceros. """

        try:
            empleados = self.querys.obtener_proveedor(4)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", empleados)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los macroprocesos por grupo
    def obtener_macroproceso_x_grupo(self, data):
        """ Api que realiza la consulta de los macroprocesos por grupo. """

        try:
            macroprocesos = self.querys.obtener_macroproceso_x_grupo(data["grupo"])

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", macroprocesos)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para obtener los activos por grupo
    def obtener_activos_x_grupo(self, data):
        """ Api que realiza la consulta de los activos por grupo. """

        try:
            activos = self.querys.obtener_activos_x_grupo(data["grupo"])

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", activos)

        except CustomException as e:
            raise CustomException(f"{e}")
