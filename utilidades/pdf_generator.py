from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generar_pdf(datos, output_path):
    """
    Genera un PDF A4 con resguardo (parte superior) + etiqueta (parte inferior).

    datos = {
        'codigo': 'REP-2026-00001',
        'nombre_cliente': 'Carlos García',
        'telefono': '612345678',
        'email': 'carlos@email.com',
        'tipo_dispositivo': 'Móvil',
        'marca': 'Samsung',
        'modelo': 'Galaxy S23',
        'averia': 'Pantalla rota',
        'observaciones': 'Golpe en esquina inferior',
        'fecha': datetime.now()
    }
    """
    w, h = A4  # 210 x 297 mm
    c = canvas.Canvas(output_path, pagesize=A4)

    # PARTE SUPERIOR — Resguardo
    margen = 2 * cm
    y = h - margen

    # Cabecera
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margen, y, "RepairHub")
    y -= 0.6 * cm
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(margen, y, "Servicio técnico de reparaciones — Tel: 600 000 000")
    y -= 1.5 * cm

    # Código de reparación (grande)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margen, y, datos['codigo'])

    # Fecha a la derecha
    c.setFont("Helvetica", 10)
    fecha_str = datos['fecha'].strftime('%d/%m/%Y %H:%M')
    c.drawRightString(w - margen, y, f"Fecha: {fecha_str}")
    y -= 1.5 * cm

    # Línea separadora
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.5)
    c.line(margen, y, w - margen, y)
    y -= 1 * cm

    # Datos del cliente
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen, y, "DATOS DEL CLIENTE")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(margen, y, f"Nombre: {datos['nombre_cliente']}")
    y -= 0.5 * cm
    contacto = []
    if datos.get('telefono'):
        contacto.append(f"Tel: {datos['telefono']}")
    if datos.get('email'):
        contacto.append(f"Email: {datos['email']}")
    c.drawString(margen, y, " | ".join(contacto))
    y -= 1 * cm

    # Datos del dispositivo
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen, y, "DATOS DEL DISPOSITIVO")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(margen, y, f"Tipo: {datos['tipo_dispositivo']}    Marca: {datos.get('marca', '-')}    Modelo: {datos.get('modelo', '-')}")
    y -= 0.8 * cm

    # Avería
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen, y, "AVERÍA / MOTIVO DE ENTRADA")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    # Dividir texto largo en líneas
    averia = datos['averia']
    max_chars = 80
    while averia:
        c.drawString(margen, y, averia[:max_chars])
        averia = averia[max_chars:]
        y -= 0.5 * cm

    if datos.get('observaciones'):
        y -= 0.3 * cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margen, y, "OBSERVACIONES")
        y -= 0.6 * cm
        c.setFont("Helvetica", 10)
        obs = datos['observaciones']
        while obs:
            c.drawString(margen, y, obs[:max_chars])
            obs = obs[max_chars:]
            y -= 0.5 * cm

    # Condiciones de servicio
    y -= 0.5 * cm
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    condiciones = [
        "CONDICIONES DE SERVICIO:",
        "1. El plazo de recogida es de 30 días desde la notificación de finalización.",
        "2. El presupuesto no incluye IVA salvo que se indique expresamente.",
        "3. RepairHub no se hace responsable de datos almacenados en el dispositivo.",
        "4. Este resguardo es necesario para la recogida del dispositivo."
    ]
    for linea in condiciones:
        c.drawString(margen, y, linea)
        y -= 0.4 * cm

    # Línea de firma
    y -= 0.8 * cm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(margen, y, "Firma del cliente: ___________________________")
    c.drawRightString(w - margen, y, f"Fecha: {datos['fecha'].strftime('%d/%m/%Y')}")

    # LÍNEA DE CORTE
    corte_y = 9 * cm
    c.setDash(3, 3)
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.line(margen, corte_y, w - margen, corte_y)
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.drawCentredString(w / 2, corte_y + 0.2 * cm, "✂ Cortar por aquí — Etiqueta para el dispositivo")
    c.setDash()

    # PARTE INFERIOR — Etiqueta
    etiqueta_y = corte_y - 0.5 * cm
    etiqueta_h = 7.5 * cm
    etiqueta_x = margen

    # Borde de la etiqueta
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(etiqueta_x, etiqueta_y - etiqueta_h, w - 2 * margen, etiqueta_h)

    # Contenido de la etiqueta
    ey = etiqueta_y - 0.8 * cm

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(etiqueta_x + 0.5 * cm, ey, datos['codigo'])

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(w - margen - 0.5 * cm, ey, "RepairHub")
    ey -= 1 * cm

    c.setFont("Helvetica", 11)
    c.drawString(etiqueta_x + 0.5 * cm, ey, f"Cliente: {datos['nombre_cliente']}")
    ey -= 0.7 * cm

    dispositivo = f"{datos['tipo_dispositivo']} — {datos.get('marca', '')} {datos.get('modelo', '')}".strip()
    c.drawString(etiqueta_x + 0.5 * cm, ey, f"Dispositivo: {dispositivo}")
    ey -= 0.7 * cm

    averia_corta = datos['averia'][:50] + ('...' if len(datos['averia']) > 50 else '')
    c.drawString(etiqueta_x + 0.5 * cm, ey, f"Avería: {averia_corta}")
    ey -= 0.7 * cm

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(etiqueta_x + 0.5 * cm, ey, f"Entrada: {datos['fecha'].strftime('%d/%m/%Y %H:%M')}")

    c.save()
    return output_path
