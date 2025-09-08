from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime
from fastapi.responses import StreamingResponse
from io import BytesIO
import os
from urllib.parse import urljoin

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
            
            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", data_activo)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para retirar un activo
    def retirar_activo(self, data: dict, hostname: str):
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
            
            mensaje = f"""
                Activo retirado del inventario. \n
                Motivo: {motivo}
            """
            
            # Guardamos el historial del activo
            self.querys.guardar_historial({
                "activo_id": data_activo["id"],
                "descripcion": mensaje,
                "usuario": hostname
            })

            # Retornamos la información.
            return self.tools.output(200, "Activo retirado con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para guardar un activo
    def guardar_activo(self, data: dict, hostname: str):
        """ Api que realiza la creación de un activo. """

        try:
            # Creamos el activo en la base de datos
            activo_id = self.querys.guardar_activo(data)

            # Guardamos el historial del activo
            self.querys.guardar_historial({
                "activo_id": activo_id,
                "descripcion": "Activo registrado en el sistema.",
                "usuario": hostname
            })

            # Retornamos la información.
            return self.tools.output(200, "Activo guardado con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para actualizar un activo
    def actualizar_activo(self, data: dict, hostname: str):
        """ Api que realiza la actualización de un activo. """

        try:
            # Consultamos el activo en la base de datos
            data_activo = self.querys.get_activo(data["codigo"])

            # Generamos el mensaje de cambios
            mensaje = self.querys.generar_mensaje_cambios(data, data_activo)

            # Actualizamos el activo en la base de datos
            self.querys.actualizar_activo(data)

            # Guardamos el historial del activo
            self.querys.guardar_historial({
                "activo_id": data_activo["id"],
                "descripcion": mensaje,
                "usuario": hostname
            })

            # Retornamos la información.
            return self.tools.output(200, "Activo actualizado con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para consultar el historial de un activo
    def consultar_historial(self, data: dict):
        """ Api que realiza la consulta del historial de un activo. """

        try:
            # Consultamos el historial en la base de datos
            historial = self.querys.consultar_historial(data)

            # Retornamos la información.
            return self.tools.output(200, "Historial encontrado.", historial)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para consultar los activos de un tercero
    def activos_x_tercero(self, data: dict):
        """ Api que realiza la consulta de los activos de un tercero. """

        try:
            # Asignamos nuestros datos de entrada a sus respectivas variables
            tercero = data["tercero"]
            
            # Consultamos los activos en la base de datos
            activos = self.querys.activos_x_tercero(tercero)

            # Retornamos la información.
            return self.tools.output(200, "Activos encontrados.", activos)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para generar un acta
    def generar_acta(self, data: dict):
        """ Api que realiza la generación de un acta. """

        try:
            # Asignamos la firma del creador
            firma_creador = "Assets/firmas/firma_creador.jpg"

            # Generamos el PDF del acta
            pdf_bytes = self.tools.generar_acta_pdf(data, firma_creador)

            # Creamos el nombre del archivo (sin caracteres inválidos)
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{data['tercero']}_acta_{fecha_str}.pdf"

            # Esta ruta hay que armarla con el macroproceso correspondiente
            archivo_ruta = f"Uploads/Macroprocesos/TIC/{file_name}"

            # Guardar el PDF en la ruta especificada
            os.makedirs(os.path.dirname(archivo_ruta), exist_ok=True)
            with open(archivo_ruta, "wb") as f:
                f.write(pdf_bytes)
                
            # Desactivamos las actas anteriores del tercero
            self.querys.buscar_y_desactivar_actas_anteriores(data['tercero'])

            # Guardamos el acta en la base de datos
            acta_id = self.querys.guardar_acta(data, file_name, archivo_ruta)
            
            # Asignamos la variable de entorno de la url del frontend
            base_url = os.getenv("FRONTEND_BASE_URL")
            
            # Construimos la URL de la firma del usuario
            path = f"/activo/firmar/tercero/{acta_id}"

            # Construimos el link completo
            link = urljoin(base_url.rstrip('/')+'/', path.lstrip('/'))

            # Actualizamos el link del acta en la base de datos
            self.querys.actualizar_link_acta(acta_id, link)

            # Retornamos la información.
            return StreamingResponse(
                BytesIO(pdf_bytes),
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/pdf",
                },
            )

        except CustomException as e:
            raise CustomException(f"{e}")

    def enviar_correo(self, data: dict):
        """ Api que realiza el envío del correo con el acta. """

        try:
            
            body = f"""\
                <!DOCTYPE html>
                <html lang="es">
                    <head>
                        <meta charset="utf-8">
                        <meta name="x-apple-disable-message-reformatting">
                        <meta name="viewport" content="width=device-width,initial-scale=1">
                        <title>Notificación de Anulación</title>
                    </head>
                    <body style="margin:0;padding:0;background:#f4f6f8;">
                        <h4>prueba</h4>
                    </body>
                </html>
            """
            
            # Enviamos el correo
            self.tools.send_email_individual(
                to_email="sistemas@avantika.com.co",
                cc_emails=["auxiliartic@avantika.com.co", "sistemas@avantika.com.co"],
                subject="Prueba",
                body=body,
                logo_path=None,
                mail_sender="sistemas@avantika.com.co"
            )

            # Retornamos la información.
            return self.tools.output(200, "Correo enviado con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")
