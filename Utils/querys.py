from Utils.tools import Tools, CustomException
from sqlalchemy import text
from datetime import datetime, date
import traceback
import json
import ast

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
    def retirar_activo(self, codigo: str):
        try:
            sql = """
                UPDATE intranet_activos 
                SET retirado = 1, estado = 10, fecha_retiro = GETDATE() WHERE codigo = :codigo;"""
            self.db.execute(text(sql), {"codigo": codigo})
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
            data_activo = dict()
            sql = """
                SELECT ia.*, t.nombres as responsable, tt.nombres as proveedor
                FROM intranet_activos ia
                LEFT JOIN terceros tt ON tt.nit = ia.proveedor
                LEFT JOIN terceros t ON t.nit = ia.tercero
                WHERE ia.id = :id;
            """
            activo = self.db.execute(text(sql), {"id": data['activo_id']}).fetchone()
            if not activo:
                raise CustomException("Activo no encontrado.")
            data_activo = dict(activo._mapping)

            sql2 = """
                SELECT * 
                FROM intranet_activos_historial 
                WHERE activo_id = :activo_id AND estado = 1;"""
            result = self.db.execute(text(sql2), {"activo_id": data['activo_id']}).fetchall()
            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, datetime):
                            row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            return {"info": data_activo, "historial": data_list}
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
            SELECT TOP(1) t.nombres, tt.descripcion AS cargo, a.macroproceso, 
            pm.nombre AS macroproceso_nombre, t.mail
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
                WHERE a.tercero = :tercero AND a.retirado = 0
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

    # Query para guardar un acta
    def guardar_acta(self, data: dict, file_name: str, archivo_ruta: str):
        """ Api que realiza la creación de un acta. """

        try:
            sql = """
            INSERT INTO dbo.intranet_activos_pdfs_generados (tercero, payload, archivo_ruta)
            OUTPUT INSERTED.id
            VALUES (:tercero, :payload, :archivo_ruta)
            """
            result = self.db.execute(text(sql), {
                "tercero": data["tercero"],
                "payload": str(data),
                "archivo_ruta": archivo_ruta
            })
            inserted = result.scalar()
            self.db.commit()
            return inserted

        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para buscar y desactivar actas anteriores de un tercero
    def buscar_y_desactivar_actas_anteriores(self, tercero: str):
        """ Desactiva las actas anteriores de un tercero. """
        try:
            sql = """
            UPDATE dbo.intranet_activos_pdfs_generados
            SET estado = 0
            WHERE tercero = :tercero AND estado = 1 and firmado_tercero = 0
            """
            self.db.execute(text(sql), {"tercero": tercero})
            self.db.commit()
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para actualizar el link del acta generada
    def actualizar_link_acta(self, acta_id: int, link_pdf: str):
        """ Actualiza el link del acta generada. """
        try:
            sql = """
            UPDATE dbo.intranet_activos_pdfs_generados
            SET link_pdf = :link_pdf
            WHERE id = :acta_id
            """
            self.db.execute(text(sql), {"link_pdf": link_pdf, "acta_id": acta_id})
            self.db.commit()
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para verificar si un tercero existe
    def check_tercero(self, nit: str):
        """ Verifica si un tercero existe en la base de datos. """
        try:
            sql = """ SELECT * FROM terceros WHERE nit = :nit """
            result = self.db.execute(text(sql), {"nit": nit}).fetchone()

            if not result:
                raise CustomException("Tercero no encontrado.")
            
            if result.bloqueo != 0:
                raise CustomException("Tercero bloqueado.")
            
            return dict(result._mapping)

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener el link del acta generada
    def get_link_acta(self, nit: str):
        """ Obtiene el link del acta generada para un tercero. """
        try:
            sql = """
            SELECT TOP(1) * 
            FROM dbo.intranet_activos_pdfs_generados 
            WHERE tercero = :nit AND estado = 1
            ORDER BY id DESC
            """
            result = self.db.execute(text(sql), {"nit": nit}).fetchone()

            if not result or not result.link_pdf:
                raise CustomException("Acta no encontrada.")
            
            return dict(result._mapping)

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar los datos del pdf
    def consultar_datos_pdf(self, pdf_generado_id: int):
        """  """
        try:
            sql = """
            SELECT TOP(1) * 
            FROM dbo.intranet_activos_pdfs_generados 
            WHERE id = :pdf_generado_id AND estado = 1
            ORDER BY id DESC
            """
            result = self.db.execute(text(sql), {"pdf_generado_id": pdf_generado_id}).fetchone()

            if not result:
                raise CustomException("Acta no encontrada.")

            row = dict(result._mapping)

            # 🔑 Arreglar el campo payload si existe
            if "payload" in row and row["payload"]:
                try:
                    # El payload está guardado como string tipo dict de Python → lo convertimos
                    row["payload"] = json.dumps(ast.literal_eval(row["payload"]))
                except Exception:
                    pass  # si ya viene como JSON válido, no hacemos nada

            return row

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para actualizar el campo firma_tercero
    def actualizar_firma_acta(self, pdf_generado_id: int):
        """ Actualiza el campo firma en la tabla intranet_activos_pdfs_generados """
        try:
            sql = """
            UPDATE dbo.intranet_activos_pdfs_generados
            SET firmado_tercero = 1
            WHERE id = :pdf_generado_id
            """
            self.db.execute(text(sql), {"pdf_generado_id": pdf_generado_id})
            self.db.commit()
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # query para obtener los activos por grupo
    def obtener_activos_x_grupo(self, grupo: str):
        """ Api que realiza la consulta de los activos por grupo. """

        try:
            sql = """
            SELECT * FROM intranet_activos WHERE retirado = 0 AND grupo = :grupo
            """
            result = self.db.execute(text(sql), {"grupo": grupo}).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para consultar los activos según filtros
    def consultar_activos(self, data: dict):
        """ Consulta los activos según los filtros proporcionados. """
        try:
            
            cant_registros = 0
            limit = data["limit"]
            position = data["position"]
            filtros = data["filtros"]

            sql = """
                SELECT ia.*, iae.nombre as estado_descripcion, 
                ipm.nombre as macroproceso_encargado_nombre,
                ipm2.nombre as macroproceso_nombre,
                t.nombres as tercero_nombre, c.descripcion as centro_costo,
                ag.descripcion as grupo_nombre, ias.nombre as sede_nombre,
                tp.nombres as proveedor_nombre, COUNT(*) OVER() AS total_registros
                FROM intranet_activos ia
                INNER JOIN intranet_activos_estados iae ON iae.id = ia.estado
                LEFT JOIN intranet_perfiles_macroproceso ipm ON ipm.id = ia.macroproceso_encargado
                LEFT JOIN intranet_perfiles_macroproceso ipm2 ON ipm2.id = ia.macroproceso
                LEFT JOIN terceros t ON t.nit = ia.tercero
                LEFT JOIN terceros tp ON tp.nit = ia.proveedor
                LEFT JOIN centros c ON c.centro = ia.centro
                INNER JOIN activos_gru ag ON ag.grupo = ia.grupo
                LEFT JOIN intranet_activos_sedes ias ON ias.id= ia.sede
                WHERE ia.retirado IN (0,1)
            """

            if "codigo" in filtros and filtros["codigo"]:
                sql += " AND ia.codigo LIKE :codigo"
                self.query_params["codigo"] = f"%{filtros['codigo']}%"

            new_offset = self.obtener_limit(limit, position)
            self.query_params.update({"offset": new_offset, "limit": limit})
            sql = sql + " ORDER BY ia.id ASC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;"
            
            if self.query_params:
                result = self.db.execute(text(sql), self.query_params).fetchall()
            else:
                result = self.db.execute(text(sql)).fetchall()
            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                cant_registros = data_list[0]['total_registros']
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, datetime):
                            row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            return {"registros": data_list, "cant_registros": cant_registros}

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # query para obtener los tecnicos
    def obtener_tecnicos(self):
        """ Api que realiza la consulta los tecnicos asignados. """

        try:
            sql = """
            SELECT * FROM dbo.intranet_activos_tecnicos WHERE estado = 1
            """
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para guardar una orden de trabajo
    def guardar_orden_trabajo(self, data: dict):
        try:
            sql = """
                INSERT INTO dbo.intranet_ordenes_trabajo (activo_id, 
                tipo_mantenimiento, fecha_programacion_desde, fecha_programacion_hasta, 
                tecnico_asignado, descripcion)
                OUTPUT INSERTED.id
                VALUES (:activo_id, :tipo_mantenimiento, :fecha_programacion_desde,
                :fecha_programacion_hasta, :tecnico_asignado, :descripcion)"""
            result = self.db.execute(
                text(sql),
                {
                    "activo_id": data["activo_id"],
                    "tipo_mantenimiento": data["tipo_mantenimiento"],
                    "fecha_programacion_desde": data["fecha_programacion_desde"],
                    "fecha_programacion_hasta": data.get("fecha_programacion_hasta") if data.get("fecha_programacion_hasta") else data["fecha_programacion_desde"],
                    "tecnico_asignado": data["tecnico_asignado"],
                    "descripcion": data.get("descripcion"),        
                }
            )
            inserted_id = result.scalar()
            self.db.commit()
            return inserted_id
        except CustomException as e:
            traceback.print_exc()
            print(f"Error al guardar activo: {e}")
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para obtener el historia de ordenes de trabajo
    def get_historial_ot(self, activo_id: int):
        """ Api que realiza la consulta del historial de las ordenes de trabajo. """

        try:
            sql = """
                SELECT iot.*,
                iat.nombre as tecnico, ieot.nombre as estado_ot_nombre,
                CASE WHEN iot.tipo_mantenimiento = 1 THEN 'Preventivo' WHEN iot.tipo_mantenimiento = 2 THEN 'Correctivo' ELSE '' END AS tipo_mantenimiento_nombre
                FROM dbo.intranet_ordenes_trabajo iot
                INNER JOIN intranet_activos_tecnicos iat ON iat.id = iot.tecnico_asignado
                INNER JOIN intranet_estados_ordenes_trabajo ieot ON ieot.id = iot.estado_ot
                WHERE iot.activo_id = :activo_id
                AND iot.estado = 1
            """
            result = self.db.execute(text(sql), {"activo_id": activo_id}).fetchall()
            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, date):
                            row[k] = v.strftime('%Y-%m-%d')
            return data_list
        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para consultar los datos de una orden de trabajo
    def consultar_data_ot(self, ot_id: int):
        """ Api que realiza la consulta de una orden de trabajo. """

        try:
            sql = """                
                select iot.*, ia.descripcion as descripcion_activo, iat.nombre as tecnico, ieot.nombre as estado_ot_nombre,
                CASE WHEN iot.tipo_mantenimiento = 1 THEN 'Preventivo' WHEN iot.tipo_mantenimiento = 2 THEN 'Correctivo' ELSE '' END AS tipo_mantenimiento_nombre,
                ia.codigo
                from dbo.intranet_ordenes_trabajo iot
                inner join intranet_activos ia on ia.id = iot.activo_id
                INNER JOIN intranet_activos_tecnicos iat ON iat.id = iot.tecnico_asignado
                INNER JOIN intranet_estados_ordenes_trabajo ieot ON ieot.id = iot.estado_ot
                where iot.estado = 1 and iot.id = :ot_id
            """
            result = self.db.execute(text(sql), {"ot_id": ot_id}).fetchone()
            if not result:
                raise CustomException("Orden de trabajo no encontrada.")
            row = dict(result._mapping)
            for k, v in row.items():
                if isinstance(v, date):
                    row[k] = v.strftime('%Y-%m-%d')
            return row
        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para obtener los estados de las ot
    def obtener_estados_ot(self):
        """ Api que realiza la consulta de los estados de la sot. """

        try:
            sql = """
            SELECT * FROM dbo.intranet_estados_ordenes_trabajo WHERE estado = 1
            """
            result = self.db.execute(text(sql)).fetchall()
            return [dict(row._mapping) for row in result] if result else []
        except CustomException as e:
            raise CustomException(f"{e}")

    # Query para actualizar el estado de una orden de trabajo
    def actualizar_estado_ot(self, ot_id: int, estado_ot: int):
        """ Api que actualiza el estado de una orden de trabajo. """

        try:
            sql = """
                UPDATE dbo.intranet_ordenes_trabajo
                SET estado_ot = :estado_ot
                WHERE id = :ot_id AND estado = 1
            """
            result = self.db.execute(text(sql), {"estado_ot": estado_ot, "ot_id": ot_id})
            if result.rowcount == 0:
                raise CustomException("Orden de trabajo no encontrada o inactiva.")
            self.db.commit()
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar las actividades de una orden de trabajo
    def consultar_actividades_ot(self, ot_id: int):
        """ Api que realiza la consulta de las actividades de una orden de trabajo. """

        try:
            sql = """
                SELECT * FROM dbo.intranet_actividades_ordenes_trabajo
                WHERE orden_trabajo_id = :ot_id AND estado = 1
            """
            result = self.db.execute(text(sql), {"ot_id": ot_id}).fetchall()
            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, datetime):
                            row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            return data_list
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para agregar una actividad a una orden de trabajo
    def agregar_actividad_ot(self, ot_id: int, descripcion: str, tecnico: str):
        """ Api que agrega una actividad a una orden de trabajo. """

        try:
            sql = """
                INSERT INTO dbo.intranet_actividades_ordenes_trabajo (orden_trabajo_id, descripcion, tecnico)
                VALUES (:orden_trabajo_id, :descripcion, :tecnico)
            """
            self.db.execute(
                text(sql), 
                {
                    "orden_trabajo_id": ot_id, 
                    "descripcion": descripcion, 
                    "tecnico": tecnico
                }
            )
            self.db.commit()
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar las ordenes de trabajo
    def consultar_ordenes_trabajo(self, data: dict):
        """ Api que realiza la consulta de las ordenes de trabajo. """

        try:
            cant_registros = 0
            limit = data["limit"]
            position = data["position"]

            sql = """                
                select iot.*, ia.descripcion as descripcion_activo, iat.nombre as tecnico, ieot.nombre as estado_ot_nombre,
                CASE WHEN iot.tipo_mantenimiento = 1 THEN 'Preventivo' WHEN iot.tipo_mantenimiento = 2 THEN 'Correctivo' ELSE '' END AS tipo_mantenimiento_nombre,
                COUNT(*) OVER() AS total_registros, ia.codigo
                from dbo.intranet_ordenes_trabajo iot
                inner join intranet_activos ia on ia.id = iot.activo_id
                INNER JOIN intranet_activos_tecnicos iat ON iat.id = iot.tecnico_asignado
                INNER JOIN intranet_estados_ordenes_trabajo ieot ON ieot.id = iot.estado_ot
                where iot.estado = 1 AND ieot.id IN (1,2)
            """

            new_offset = self.obtener_limit(limit, position)
            self.query_params.update({"offset": new_offset, "limit": limit})
            sql = sql + " ORDER BY iot.id ASC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;"
            
            if self.query_params:
                result = self.db.execute(text(sql), self.query_params).fetchall()
            else:
                result = self.db.execute(text(sql)).fetchall()

            data_list = [dict(row._mapping) for row in result] if result else []
            if data_list:
                cant_registros = data_list[0]['total_registros']
                for row in data_list:
                    for k, v in row.items():
                        if isinstance(v, date):
                            row[k] = v.strftime('%Y-%m-%d')
            return {"registros": data_list, "cant_registros": cant_registros}
        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Función que arma el limite de paginación
    def obtener_limit(self, limit: int, position: int):
        offset = (position - 1) * limit
        return offset

    # Query para consultar las ordenes de trabajo por estado
    def obtener_ot_x_estado(self, estado_ot: dict):
        """ Api que realiza la consulta de las ot por estado. """

        try:
            sql = """                
                SELECT COUNT(*) AS total 
                FROM intranet_ordenes_trabajo 
                WHERE estado_ot = :estado_ot AND estado = 1
            """

            result = self.db.execute(text(sql), {"estado_ot": estado_ot}).fetchone()

            return dict(result._mapping)

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar el conteo de activos retirados
    def conteo_activos_retirados(self):
        """ Api que realiza la consulta de los activos retirados. """

        try:
            sql = """                
                SELECT retirado, COUNT(*) AS total
                FROM intranet_activos
                GROUP BY retirado;
            """

            result = self.db.execute(text(sql)).fetchall()

            data_list = [dict(row._mapping) for row in result] if result else []

            return data_list

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()

    # Query para consultar el conteo de tipos de mantenimiento de las ot
    def conteo_tipos_mantenimiento_ot(self):
        """ Api que realiza la consulta de los tipos de mantenimiento de las ot. """

        try:
            sql = """                
                SELECT tipo_mantenimiento, COUNT(*) AS total
                FROM intranet_ordenes_trabajo
                GROUP BY tipo_mantenimiento;
            """

            result = self.db.execute(text(sql)).fetchall()

            data_list = [dict(row._mapping) for row in result] if result else []

            return data_list

        except CustomException as e:
            raise CustomException(f"{e}")
        finally:
            self.db.close()
