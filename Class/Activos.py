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

UPLOAD_FOLDER = "Uploads/"
EXTENSIONES = ["jpg", "jpeg", "png"]

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
            # Asignamos el tercero
            tercero = data["tercero"]
            macroproceso_id = data["payload"]["cabecera"]["macroproceso"]
            
            # Validamos que el tercero exista            
            if not macroproceso_id:
                raise CustomException("Tercero no tiene macroproceso asignado.")

            # Generamos el PDF del acta
            pdf_bytes = self.tools.generar_acta_pdf(data)

            # Creamos el nombre del archivo (sin caracteres inválidos)
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{data['tercero']}_acta_{fecha_str}.pdf"
            
            # Obtenemos los macroprocesos
            macroprocesos = self.querys.obtener_macroprocesos()
            
            # buscar el macroproceso activo por id
            macro = next(
                (m for m in macroprocesos 
                    if int(m.get("id")) == int(macroproceso_id)), None
            )

            # Validamos que el macroproceso exista y esté activo
            if not macro:
                raise CustomException("Macroproceso no válido o inactivo")

            # Obtenemos la carpeta del macroproceso
            carpeta = macro["nombre_carpeta"]

            # Esta ruta hay que armarla con el macroproceso correspondiente
            archivo_ruta = f"Uploads/Macroprocesos/{carpeta}/{file_name}"

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

    # Función para enviar el correo con el acta
    def enviar_correo(self, data: dict):
        """ Api que realiza el envío del correo con el acta. """

        try:

            data_tercero = self.querys.check_tercero(data['tercero'])

            correo_destino = data_tercero["mail"]

            data_link = self.querys.get_link_acta(data['tercero'])

            body_correo = self.build_correo(data_link["link_pdf"], data_tercero)

            # Enviamos el correo
            self.tools.send_email_individual(
                to_email=correo_destino,
                cc_emails=["auxiliartic@avantika.com.co"],
                subject="Acta de Activos - Avantika",
                body=body_correo,
                logo_path=None,
                mail_sender="auxiliartic@avantika.com.co"
            )

            # Retornamos la información.
            return self.tools.output(200, "Correo enviado con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para construir el correo
    def build_correo(self, link: str, data_tercero: dict):
        """ Función que construye el cuerpo del correo. """

        body = f"""\
            <!DOCTYPE html>
            <html lang="es">
                <head>
                    <meta charset="utf-8">
                    <meta name="x-apple-disable-message-reformatting">
                    <meta name="viewport" content="width=device-width,initial-scale=1">
                    <title>Notificación Acta de Activos</title>
                </head>
                <body style="margin:0;padding:0;background:#f4f6f8;">
                    <h4>Buen día estimado/a: {data_tercero['nombres']}</h4>
                    <p>A continuación te dejo el siguiente link donde podrás ver tus activos asignados y realizar el proceso de firma.</p>
                    <strong><p><a href="{link}">Ver Acta de Activos</a></p></strong>
                </body>
            </html>
        """
        return body

    # Función para consultar los datos para el PDF
    def consultar_datos_pdf(self, data: dict):
        """ Api que realiza la consulta de los datos para el PDF. """

        try:
            # Consultamos los datos en la base de datos
            datos_pdf = self.querys.consultar_datos_pdf(data["pdf_generado_id"])

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", datos_pdf)

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para responder un acta
    def responder_acta(self, data: dict):
        """ Api que realiza la respuesta del acta. """

        try:
            pdf_generado_id = data["pdf_generado_id"]
            observaciones = data["observaciones"]
            firma_tercero = data["firma_tercero"]
            archivo_ruta = data["archivo_ruta"]
            file_path = ''
            
            data_pdf = self.querys.consultar_datos_pdf(pdf_generado_id)
            if data_pdf["firmado_tercero"] == 1:
                return self.tools.output(210, "Acta ya se encuentra firmada.")

            if firma_tercero:
                file_path = self.proccess_image(firma_tercero)
                
            archivo_final = self.tools.reescribir_acta(archivo_ruta, file_path, observaciones)
            
            self.querys.actualizar_firma_acta(pdf_generado_id)
            
            # Retornamos la información.
            return StreamingResponse(
                BytesIO(archivo_final),
                headers={
                    "Content-Disposition": f"attachment; filename={file_path}",
                    "Content-Type": "application/pdf",
                },
            )



            # Retornamos la información.
            return self.tools.output(200, "Acta respondida con éxito.")

        except CustomException as e:
            raise CustomException(f"{e}")

    # Función para procesar imagen
    def proccess_image(self, firma_tercero):

        try:
            # Extraer el formato de la imagen
            file_extension = self.extract_file_extension(firma_tercero)

            # Verificar si la extensión es válida
            if file_extension not in EXTENSIONES:
                raise CustomException(f"Extensión no permitida: {file_extension}")

            # Eliminar el prefijo base64 antes de decodificar
            base64_data = re.sub(r"^data:image/\w+;base64,", "", firma_tercero)

            # Decodificar la imagen base64
            file_data = base64.b64decode(base64_data)

            # Open the image with Pillow
            image = Image.open(io.BytesIO(file_data))

            # Compress the image (resize or adjust quality)
            compressed_image_io = io.BytesIO()
            image = image.convert("RGB")  # Ensure the image is in RGB format (no alpha channel)
            
            # Save with compression
            image.save(
                compressed_image_io,
                format="JPEG",  # Convert to JPEG for better compression
                optimize=True,
                quality=75  # Adjust the quality (lower = more compression)
            )
            compressed_image_io.seek(0)
            compressed_data = compressed_image_io.read()

        except CustomException as e:
            print(e)
            raise CustomException(f"Error al decodificar la imagen: {str(e)}")

        # Generar un nombre único para cada archivo
        file_name = f"{str(uuid.uuid4())}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        # Guardar la imagen decodificada en el servidor
        try:
            with open(file_path, "wb") as file:
                file.write(compressed_data)
        except CustomException as e:
            print(e)
            raise CustomException(f"Error al guardar la imagen: {str(e)}")

        return file_path
    
    # Busca el prefijo que indica el tipo de archivo, como data:image/jpeg;base64,
    def extract_file_extension(self, file_base64: str):
        match = re.match(r"data:image/(?P<ext>\w+);base64,", file_base64)
        if not match:
            raise ValueError("Formato de imagen no válido o prefijo faltante")
        
        # Extrae la extensión (jpg, png, etc.)
        return match.group("ext")
