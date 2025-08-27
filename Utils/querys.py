from Utils.tools import Tools, CustomException
from sqlalchemy import text
from datetime import datetime
import traceback

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Query para obtener la información del activo por código
    def get_activo(self, codigo: str):
        try:
            sql = """ SELECT * FROM intranet_activos WHERE codigo = :codigo """
            result = self.db.execute(text(sql), {"codigo": codigo}).fetchone()
            
            if not result:
                raise CustomException("Activo no encontrado.")
            
            return dict(result._mapping)
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener activo por código: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener los macroprocesos
    def obtener_macroprocesos(self):
        try:
            sql = """ SELECT * FROM intranet_perfiles_macroproceso WHERE estado = 1;"""
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener macroprocesos: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener los estados
    def obtener_estados(self):
        try:
            sql = """ SELECT * FROM intranet_activos_estados WHERE estado = 1;"""
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener estados: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener las sedes
    def obtener_sedes(self):
        try:
            sql = """ SELECT * FROM intranet_activos_sedes WHERE estado = 1;"""
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener sedes: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener los centros
    def obtener_centros(self):
        try:
            sql = """ SELECT centro AS id, descripcion AS nombre 
                FROM centros WHERE inactivo = 0 AND nomina = 'N';"""
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener centros: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener los grupos contables
    def obtener_grupo_contable(self):
        try:
            sql = """
                SELECT grupo AS id, descripcion AS nombre 
                FROM activos_gru;"""
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener grupos contables: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener los proveedores
    def obtener_proveedor(self, concepto: int):
        try:
            if concepto == 1:
                sql = """
                    SELECT nit AS id, nombres AS nombre 
                    FROM terceros WHERE concepto_1 in (:concepto,3) ORDER BY nombre;"""
            elif concepto == 4:
                sql = """
                    SELECT nit AS id, nombres AS nombre 
                    FROM terceros WHERE concepto_1 = :concepto ORDER BY nombre;"""
            result = self.db.execute(text(sql), {"concepto": concepto}).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al obtener proveedores: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    def retirar_activo(self, codigo: str, motivo: str):
        try:
            sql = """
                UPDATE intranet_activos 
                SET retirado = 1, estado = 10, motivo_retiro = :motivo, fecha_retiro = GETDATE() WHERE codigo = :codigo;"""
            self.db.execute(text(sql), {"codigo": codigo, "motivo": motivo})
            self.db.commit()
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al retirar activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()
