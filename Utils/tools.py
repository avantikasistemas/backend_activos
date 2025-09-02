# import base64
# from Utils.constants import BASE_PATH_TEMPLATE
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pytz
from datetime import datetime, timezone
from decimal import Decimal
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter, legal
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from PIL import Image

# Cargar variables de entorno
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 25))

class Tools:

    def outputpdf(self, codigo, file_name, data={}):
        response = Response(
            status_code=codigo,
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        return response

    """ Esta funcion permite darle formato a la respuesta de la API """
    def output(self, codigo, message, data={}):

        response = JSONResponse(
            status_code=codigo,
            content=jsonable_encoder({
                "code": codigo,
                "message": message,
                "data": data,
            }),
            media_type="application/json"
        )
        return response

    # """ Esta funcion permite obtener el template """
    # def get_content_template(self, template_name: str):
    #     template = f"{BASE_PATH_TEMPLATE}/{template_name}"

    #     content = ""
    #     with open(template, 'r') as f:
    #         content = f.read()

    #     return content

    def result(self, msg, code=400, error="", data=[]):
        return {
            "body": {
                "statusCode": code,
                "message": msg,
                "data": data,
                "Exception": error
            }
        }

    # Función para formatear las fechas    
    def format_date(self, date, normal_format, output_format):
        fecha_objeto = datetime.strptime(date, normal_format)
        fecha_formateada = fecha_objeto.strftime(output_format)
        return fecha_formateada

    # Función para formatear las fechas    
    def format_date2(self, date):
        # Convertir la cadena a un objeto datetime
        fecha_objeto = datetime.fromisoformat(date)
        # Formatear la fecha al formato deseado
        fecha_formateada = fecha_objeto.strftime("%d-%m-%Y")
        return fecha_formateada
    
    # Función para formatear fechas con zona horaria
    def format_datetime(self, dt_str):
        dt = datetime.strptime(
            dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(pytz.timezone('America/Bogota'))
        return local_dt.strftime("%d-%m-%Y %H:%M:%S")
    
    # Función para formatear a dinero    
    def format_money(self, value: str):
        value = value.replace(",", "")
        valor_decimal = Decimal(value)
        return valor_decimal

    # Función para enviar correos electrónicos
    def send_email_individual(self, to_email, cc_emails, subject, body, logo_path=None, mail_sender=None):
        """Envía un correo electrónico a un destinatario con copia a otros y adjunta un logo si está disponible."""
        msg = MIMEMultipart()
        msg['From'] = mail_sender
        msg['To'] = to_email
        msg['Cc'] = ", ".join(cc_emails) if cc_emails else ""
        msg['Subject'] = subject

        # Agregar el contenido HTML
        msg.attach(MIMEText(body, 'html'))
        
        # Adjuntar el logo si está disponible
        if logo_path:
            try:
                with open(logo_path, 'rb') as img:
                    logo = MIMEImage(img.read())
                    logo.add_header('Content-ID', '<company_logo>')
                    msg.attach(logo)
            except Exception as e:
                print(f"Error adjuntando el logo: {e}")
        
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.sendmail(mail_sender, [to_email] + cc_emails, msg.as_string())
            print(f"Correo enviado a {to_email} con copia a {', '.join(cc_emails)}")
        except Exception as ex:
            print(f"Error al enviar correo a {to_email}: {ex}")

    # Función para generar un mensaje de cambios
    def generar_mensaje_cambios(self, payload, data_activo):
        mensaje = []
        for campo, valor_nuevo in payload.items():
            valor_actual = data_activo.get(campo)
            if valor_actual != valor_nuevo:
                mensaje.append(f"Se cambió el campo {campo} antes: {valor_actual}, ahora: {valor_nuevo}")
        return "; ".join(mensaje)

    # Función para generar un pdf
    def generar_acta_pdf(self, data, firma_creador):

        # Ruta del archivo PDF original
        original_pdf_path = os.path.join('Templates', 'acta_entrega.pdf')

        # Cargar el PDF original
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()

        # Crear un buffer en memoria para el nuevo contenido
        packet  = BytesIO()

        # Crear un objeto canvas de ReportLab
        pdf = canvas.Canvas(packet , pagesize=letter)
        pdf.setFont('Helvetica', 10)

        cabecera = data["payload"]["cabecera"]
        activos = data["payload"]["activos"]

        # Escribir datos en el PDF
        pdf.drawString(262, 605, f"{cabecera['nombres']}")
        pdf.drawString(86, 589, f"{cabecera['cargo']}")
        pdf.drawString(170, 574, f"{cabecera['macroproceso_nombre']}")

        # Dibujar la tabla de activos entregados
        self.dibujar_tabla_activos_entregados(pdf, activos, 540)

        # # Function for set the X mark on the report
        # self.set_type_service(pdf, data["type_service"])

        # # Ajustamos descripción dinamicamente
        # y_position = 527
        # y_position = self.ajust_long_text(
        #     pdf,
        #     "DESCRIPCIÓN DE LA ACTIVIDAD: ",
        #     data['service_description'], 
        #     32, 
        #     y_position, 
        #     510
        # )

        # # Ajustamos informatión dinamicamente
        # y_position -= 30
        # y_position = self.ajust_long_text(
        #     pdf,
        #     "",
        #     data['information'], 
        #     32, 
        #     y_position, 
        #     510
        # )

        # # Ajustar la lista de tareas justo debajo de la descripción
        # tasks = data["tasks"]
        # if tasks:
        #     y_position = self.ajust_list(pdf, tasks, x=28, y=y_position - 20)  # Ajusta el espaciado

        # # Agregar las imágenes justo debajo de la lista de mantenimiento
        # image_paths = data["files"]
        # if image_paths:
        #     max_height = 170  # Altura mínima para imágenes
        #     y_position = self.ajust_images(pdf, image_paths, x=100, y=0, max_height=max_height, page_height=letter[1])

        # Guardar el PDF con los datos escritos en el buffer
        pdf.save()

        # Mover el buffer al principio
        packet.seek(0)

        # Leer el nuevo PDF con los datos
        new_pdf = PdfReader(packet)

        # Combinar cada página del PDF original con las páginas generadas
        for i, page in enumerate(reader.pages):
            if i == 0:  # Solo superponer en la primera página del original
                page.merge_page(new_pdf.pages[0])
                writer.add_page(page)
            else:
                writer.add_page(page)

        # Agregar las páginas adicionales del nuevo PDF (imágenes en este caso)
        for i in range(1, len(new_pdf.pages)):
            writer.add_page(new_pdf.pages[i])

        # Guardar el PDF final en memoria
        output_buffer = BytesIO()
        writer.write(output_buffer)

        # Mover el buffer al principio
        output_buffer.seek(0)

        return output_buffer.read()

    # Función para dibujar la tabla de activos entregados
    def dibujar_tabla_activos_entregados(self, pdf, activos, y_start):
        # Parámetros de la tabla
        headers = ["Código", "Descripcion", "Marca", "Serial", "Estado"]
        col_widths = [45, 200, 80, 150, 90]
        x_start = 25
        # Altura de la página menos margen inferior
        page_height = letter[1]
        margen_inferior = 40

        pdf.setFont('Helvetica-Bold', 11)
        pdf.setFillColorRGB(0.31, 0.51, 0.75)  # #4f81bf
        pdf.drawString(35, 540, "2. ACTIVOS ENTREGADOS")
        pdf.setFillColorRGB(0, 0, 0)  # Restaurar color negro
        # Función para dibujar el encabezado de la tabla, ajustando la posición en páginas nuevas
        def dibujar_encabezado(y, es_primera_pagina):
            if es_primera_pagina:
                titulo_y = y
            else:
                titulo_y = page_height - 60  # 60 puntos desde el borde superior en páginas nuevas
            cabecera_y = titulo_y - 25
            pdf.setFillColorRGB(0.09, 0.29, 0.55)  # Azul oscuro
            pdf.setFont('Helvetica', 10)
            pdf.rect(x_start, cabecera_y, sum(col_widths), 20, fill=1, stroke=0)
            x = x_start + 5
            for i, h in enumerate(headers):
                pdf.setFillColorRGB(1, 1, 1)
                if h == "Estado":
                    estado_font = 'Helvetica'
                    estado_font_size = 10
                    estado_text_width = pdf.stringWidth(h, estado_font, estado_font_size)
                    estado_col_width = col_widths[i]
                    estado_x_center = x + (estado_col_width - estado_text_width) / 2
                    pdf.drawString(estado_x_center, cabecera_y + 5, h)
                else:
                    pdf.drawString(x, cabecera_y + 5, h)
                x += col_widths[i]
            return cabecera_y - 30
        # Iniciar en la primera página
        y = dibujar_encabezado(y_start, True)
        pdf.setFont('Helvetica', 10)
        # Primero calcula la altura de cada fila
        filas_info = []
        desc_font = 'Helvetica'
        desc_font_size = 8
        desc_col_width = 200
        altura_estandar = 30
        altura_extra = 11
        for activo in activos:
            descripcion = activo["descripcion"] if activo["descripcion"] else ''
            pdf.setFont(desc_font, desc_font_size)
            palabras = descripcion.split()
            line = ''
            desc_lines = []
            for palabra in palabras:
                test_line = line + (' ' if line else '') + palabra
                if pdf.stringWidth(test_line, desc_font, desc_font_size) > desc_col_width:
                    if line:
                        desc_lines.append(line)
                    line = palabra
                else:
                    line = test_line
            if line:
                desc_lines.append(line)
            # Mostrar máximo 2 líneas
            desc_lines = desc_lines[:2]
            # Si solo hay una línea, altura estándar; si hay más, sumar altura extra por cada línea adicional
            if len(desc_lines) == 1:
                row_height = altura_estandar
            else:
                row_height = altura_estandar + (len(desc_lines) - 1) * altura_extra
            filas_info.append({
                "activo": activo,
                "desc_lines": desc_lines,
                "row_height": row_height
            })
        # Ahora dibuja cada fila usando la altura calculada
        for idx, fila in enumerate(filas_info):
            activo = fila["activo"]
            desc_lines = fila["desc_lines"]
            row_height = fila["row_height"]
            # Si la siguiente fila no cabe, crear nueva página y dibujar encabezado más arriba
            if y - row_height < margen_inferior:
                pdf.showPage()
                y = dibujar_encabezado(y_start, False)
            # Alternar color de fondo
            if idx % 2 == 0:
                pdf.setFillColorRGB(0.93, 0.97, 1)  # Azul claro
            else:
                pdf.setFillColorRGB(0.87, 0.92, 0.98)  # Otro azul claro
            pdf.rect(x_start, y, sum(col_widths), row_height, fill=1, stroke=0)
            # Dibujar texto
            pdf.setFillColorRGB(0, 0, 0)
            # Código (solo en la primera línea)
            pdf.setFont('Helvetica', 10)
            pdf.drawString(x_start + 5, y + row_height - 15, str(activo.get("codigo", "")))
            # Descripción (todas las líneas, desde arriba hacia abajo)
            pdf.setFont(desc_font, desc_font_size)
            desc_x = x_start + col_widths[0] + 5
            desc_y = y + row_height - 15
            for line in desc_lines:
                pdf.drawString(desc_x, desc_y, line)
                desc_y -= 11
            # Marca, Serie, Estado (solo en la primera línea)
            pdf.setFont('Helvetica', 10)
            marca_x = x_start + col_widths[0] + col_widths[1] + 5
            pdf.drawString(marca_x, y + row_height - 15, str(activo["marca"] if activo["marca"] else ''))
            serie_x = marca_x + col_widths[2]
            pdf.drawString(serie_x, y + row_height - 15, str(activo["serie"] if activo["serie"] else ''))
            estado_x = serie_x + col_widths[3]
            estado_valor = str(activo.get("estado_nombre", ""))
            estado_font = 'Helvetica'
            estado_font_size = 10
            # Calcular el ancho del texto y centrarlo en la columna
            estado_text_width = pdf.stringWidth(estado_valor, estado_font, estado_font_size)
            estado_col_width = col_widths[4]
            estado_x_center = estado_x + (estado_col_width - estado_text_width) / 2
            pdf.drawString(estado_x_center, y + row_height - 15, estado_valor)
            y -= row_height
        pdf.setFillColorRGB(0, 0, 0)
        return y

class CustomException(Exception):
    """ Esta clase hereda de la clase Exception y permite
        interrumpir la ejecucion de un metodo invocando una excepcion
        personalizada """
    def __init__(self, message="", codigo=400, data={}):
        self.codigo = codigo
        self.message = message
        self.data = data
        self.resultado = {
            "body": {
                "statusCode": codigo,
                "message": message,
                "data": data,
                "Exception": "CustomException"
            }
        }