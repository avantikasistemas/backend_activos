from Utils.tools import Tools, CustomException
from sqlalchemy import text
from datetime import datetime, date
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
            
            data = dict(result._mapping)
            for k, v in data.items():
                if isinstance(v, datetime):
                    data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                if isinstance(v, date):
                    data[k] = v.strftime('%Y-%m-%d')
            return data
        except CustomException as e:
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

    # Query para retirar un activo
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

    # Query para guardar un activo
    def guardar_activo(self, data: dict):
        try:
            sql = """
                INSERT INTO intranet_activos (codigo, descripcion, modelo, serie, marca, estado, vida_util, 
                proveedor, tercero, docto_compra, fecha_compra, caracteristicas, sede, centro, grupo, macroproceso_encargado, 
                macroproceso, costo_compra)
                OUTPUT INSERTED.id
                VALUES (:codigo, :descripcion, :modelo, :serie, :marca, :estado, :vida_util, 
                :proveedor, :tercero, :docto_compra, :fecha_compra, :caracteristicas, :sede, :centro, :grupo,
                :macroproceso_encargado, :macroproceso, :costo_compra)"""
            result = self.db.execute(text(sql), data)
            inserted_id = result.scalar()
            self.db.commit()
            return inserted_id
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al guardar activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para actualizar un activo
    def actualizar_activo(self, data: dict):
        try:
            sql = """
                UPDATE intranet_activos 
                SET descripcion = :descripcion, modelo = :modelo, serie = :serie, marca = :marca, estado = :estado, vida_util = :vida_util, 
                proveedor = :proveedor, tercero = :tercero, docto_compra = :docto_compra, fecha_compra = :fecha_compra, caracteristicas = :caracteristicas, sede = :sede, centro = :centro, grupo = :grupo,
                macroproceso_encargado = :macroproceso_encargado, macroproceso = :macroproceso, costo_compra = :costo_compra
                WHERE codigo = :codigo;"""
            self.db.execute(text(sql), data)
            self.db.commit()
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al actualizar activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para guardar historial de un activo
    def guardar_historial(self, data: dict):
        try:
            sql = """
                INSERT INTO intranet_activos_historial (activo_id, descripcion, usuario)
                VALUES (:activo_id, :descripcion, :usuario);"""
            self.db.execute(text(sql), data)
            self.db.commit()
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al guardar historial de activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar el historial de un activo
    def consultar_historial(self, data: dict):
        try:
            
            sql = """
                SELECT id FROM intranet_activos WHERE codigo = :codigo;
            """
            activo = self.db.execute(text(sql), data).fetchone()
            if not activo:
                raise CustomException("Activo no encontrado.")

            sql2 = """
                SELECT * 
                FROM intranet_activos_historial 
                WHERE activo_id = :activo_id AND estado = 1;"""
            result = self.db.execute(text(sql2), {"activo_id": activo.id}).fetchall()
            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, datetime):
                            row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            return data_list
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al consultar historial de activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener macroprocesos por grupo
    def obtener_macroproceso_x_grupo(self, grupo: str):
        try:
            sql = """
                SELECT ipm.id, ipm.nombre
                FROM intranet_macroproceso_x_grupo imxp
                JOIN intranet_perfiles_macroproceso ipm ON ipm.id = imxp.macroproceso_id
                WHERE imxp.grupo_id = :grupo
                AND imxp.estado = 1 AND ipm.estado = 1
            """
            result = self.db.execute(text(sql), {"grupo": grupo}).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al consultar macroprocesos por grupo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener el nombre de un campo por su id
    def obtener_nombre_por_id(self, campo, id_valor):
        """Obtiene el nombre correspondiente a un id según el campo."""
        if campo == "sede":
            result = self.db.execute(text("SELECT nombre FROM intranet_activos_sedes WHERE id = :id"), {"id": id_valor}).fetchone()
            return result.nombre if result else id_valor
        elif campo == "centro":
            result = self.db.execute(text("SELECT descripcion FROM centros WHERE centro = :id"), {"id": id_valor}).fetchone()
            return result.descripcion if result else id_valor
        elif campo == "grupo":
            result = self.db.execute(text("SELECT descripcion FROM activos_gru WHERE grupo = :id"), {"id": id_valor}).fetchone()
            return result.descripcion if result else id_valor
        elif campo == "estado":
            result = self.db.execute(text("SELECT nombre FROM intranet_activos_estados WHERE id = :id"), {"id": id_valor}).fetchone()
            return result.nombre if result else id_valor
        elif campo == "macroproceso":
            result = self.db.execute(text("SELECT nombre FROM intranet_perfiles_macroproceso WHERE id = :id"), {"id": id_valor}).fetchone()
            return result.nombre if result else id_valor
        elif campo == "macroproceso_encargado":
            result = self.db.execute(text("SELECT nombre FROM intranet_perfiles_macroproceso WHERE id = :id"), {"id": id_valor}).fetchone()
            return result.nombre if result else id_valor
        elif campo == "tercero":
            result = self.db.execute(text("SELECT nombres FROM terceros WHERE nit = :id"), {"id": id_valor}).fetchone()
            return result.nombres if result else id_valor
        elif campo == "proveedor":
            result = self.db.execute(text("SELECT nombres FROM terceros WHERE nit = :id"), {"id": id_valor}).fetchone()
            return result.nombres if result else id_valor
        # Agrega más campos según necesidad
        return id_valor

    # Query para generar un mensaje de cambios
    def generar_mensaje_cambios(self, payload, data_activo):
        """Genera el mensaje de cambios mostrando nombres en vez de ids para campos especiales."""
        campos_id = ["sede", "centro", "grupo", "estado", "macroproceso", "macroproceso_encargado", "tercero", "proveedor"]
        mensaje = []
        for campo, valor_nuevo in payload.items():
            valor_actual = data_activo.get(campo)
            if valor_actual != valor_nuevo:
                if campo in campos_id:
                    nombre_actual = self.obtener_nombre_por_id(campo, valor_actual)
                    nombre_nuevo = self.obtener_nombre_por_id(campo, valor_nuevo)
                    mensaje.append(f"se cambió el campo {campo} antes: {nombre_actual}, ahora: {nombre_nuevo}")
                else:
                    mensaje.append(f"se cambió el campo {campo} antes: {valor_actual}, ahora: {valor_nuevo}")
        return "; ".join(mensaje)

    # Query para consultar los activos de un tercero
    def activos_x_tercero(self, tercero: str):
        """ Api que realiza la consulta de los activos de un tercero. """

        try:
            response = dict()
            list_activos = list()

            # Consultamos los activos en la base de datos
            sql = """
            SELECT TOP(1) t.nombres, tt.descripcion AS cargo, a.macroproceso, pm.nombre AS macroproceso_nombre
            FROM dbo.intranet_activos a
            LEFT JOIN terceros t ON t.nit = a.tercero
            LEFT JOIN terceros_3 tt ON tt.concepto_3 = t.concepto_3
            LEFT JOIN intranet_perfiles_macroproceso pm ON pm.id = a.macroproceso
            WHERE a.tercero = :tercero
            """
            result = self.db.execute(text(sql), {"tercero": tercero}).fetchone()
            
            response = {"cabecera": dict(result._mapping)} if result else {}
            
            if response:
                sql2 = """
                SELECT a.id, a.codigo, a.descripcion, a.modelo, a.serie, a.marca, a.estado, ae.nombre AS estado_nombre
                FROM dbo.intranet_activos a
                INNER JOIN dbo.intranet_activos_estados ae ON ae.id = a.estado
                WHERE a.tercero = :tercero
                """
                result2 = self.db.execute(text(sql2), {"tercero": tercero}).fetchall()
                list_activos = [dict(row._mapping) for row in result2] if result2 else []

                # Agregar la lista de activos a la respuesta
                response["activos"] = list_activos
            
            return response
                

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()
