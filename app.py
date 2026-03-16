from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from config import DB_CONFIG, SECRET_KEY
from utilidades.pdf_generator import generar_pdf
from datetime import datetime
import os

app = Flask(__name__,
            template_folder='plantillas',
            static_folder='estaticos')
app.secret_key = SECRET_KEY

# Modo preview: datos hardcodeados (fake) para desarrollar sin base de datos
# Cambiaresmos a False cuando se conecte a la MariaDB real:
PREVIEW_MODE = True

# Datos hardcodeados (fake)
if PREVIEW_MODE:
    mock_clientes = [
        {'id': 1, 'nombre': 'Carlos García', 'telefono': '612345678', 'email': 'carlos@email.com', 'created_at': datetime(2026, 1, 15)},
        {'id': 2, 'nombre': 'María López', 'telefono': '623456789', 'email': 'maria@email.com', 'created_at': datetime(2026, 2, 3)},
        {'id': 3, 'nombre': 'Pedro Porro', 'telefono': '634567890', 'email': '', 'created_at': datetime(2026, 2, 10)},
    ]

    mock_reparaciones = [
        {'id': 1, 'codigo': 'REP-2026-00001', 'cliente_id': 1, 'tipo_dispositivo': 'Móvil', 'marca': 'Samsung', 'modelo': 'Galaxy S23', 'averia': 'Pantalla rota', 'observaciones': 'Golpe en esquina inferior', 'estado': 'Entregado', 'presupuesto': 120.00, 'precio_final': 120.00, 'presupuesto_aceptado': True, 'created_at': datetime(2026, 1, 10), 'updated_at': datetime(2026, 1, 15)},
        {'id': 2, 'codigo': 'REP-2026-00002', 'cliente_id': 2, 'tipo_dispositivo': 'Portátil', 'marca': 'HP', 'modelo': 'Pavilion 15', 'averia': 'No enciende', 'observaciones': '', 'estado': 'Reparando', 'presupuesto': 85.00, 'precio_final': None, 'presupuesto_aceptado': True, 'created_at': datetime(2026, 2, 1), 'updated_at': datetime(2026, 2, 8)},
        {'id': 3, 'codigo': 'REP-2026-00003', 'cliente_id': 3, 'tipo_dispositivo': 'Móvil', 'marca': 'iPhone', 'modelo': '14 Pro', 'averia': 'Batería se agota rápido', 'observaciones': '', 'estado': 'Presupuesto enviado', 'presupuesto': 65.00, 'precio_final': None, 'presupuesto_aceptado': None, 'created_at': datetime(2026, 2, 15), 'updated_at': datetime(2026, 2, 18)},
        {'id': 4, 'codigo': 'REP-2026-00004', 'cliente_id': 1, 'tipo_dispositivo': 'Tablet', 'marca': 'iPad', 'modelo': 'Air 5', 'averia': 'Puerto de carga no funciona', 'observaciones': '', 'estado': 'Recibido', 'presupuesto': None, 'precio_final': None, 'presupuesto_aceptado': None, 'created_at': datetime(2026, 3, 1), 'updated_at': datetime(2026, 3, 1)},
        {'id': 5, 'codigo': 'REP-2026-00005', 'cliente_id': 2, 'tipo_dispositivo': 'Consola', 'marca': 'Sony', 'modelo': 'PS5', 'averia': 'No lee discos', 'observaciones': '', 'estado': 'Diagnosticado', 'presupuesto': None, 'precio_final': None, 'presupuesto_aceptado': None, 'created_at': datetime(2026, 3, 2), 'updated_at': datetime(2026, 3, 3)},
    ]

    mock_historial = [
        {'id': 1, 'reparacion_id': 1, 'estado': 'Recibido', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 10, 9, 30)},
        {'id': 2, 'reparacion_id': 1, 'estado': 'Diagnosticado', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 11, 11, 0)},
        {'id': 3, 'reparacion_id': 1, 'estado': 'Presupuesto enviado', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 11, 15, 0)},
        {'id': 4, 'reparacion_id': 1, 'estado': 'Presupuesto aceptado', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 12, 10, 0)},
        {'id': 5, 'reparacion_id': 1, 'estado': 'Reparando', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 13, 9, 0)},
        {'id': 6, 'reparacion_id': 1, 'estado': 'Listo', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 14, 17, 0)},
        {'id': 7, 'reparacion_id': 1, 'estado': 'Entregado', 'tecnico': 'Roberto', 'fecha': datetime(2026, 1, 15, 12, 0)},
    ]


# Conexión a MariaDB (solo cuando PREVIEW_MODE = False)
def get_db():
    if PREVIEW_MODE:
        return None
    import mysql.connector
    return mysql.connector.connect(**DB_CONFIG)


# Rutas
@app.route('/')
def dashboard():
    if PREVIEW_MODE:
        pendientes = len([r for r in mock_reparaciones if r['estado'] != 'Entregado'])
        este_mes = len([r for r in mock_reparaciones if r['created_at'].month == datetime.now().month and r['created_at'].year == datetime.now().year])
        ingresos_mes = sum(r['precio_final'] or 0 for r in mock_reparaciones if r['estado'] == 'Entregado' and r['updated_at'].month == datetime.now().month)
        ultimas = sorted(mock_reparaciones, key=lambda r: r['created_at'], reverse=True)[:5]

        # Añadir nombre del cliente
        for rep in ultimas:
            cliente = next((c for c in mock_clientes if c['id'] == rep['cliente_id']), None)
            rep['cliente_nombre'] = cliente['nombre'] if cliente else 'Desconocido'

        return render_template('dashboard.html',
            pendientes=pendientes,
            este_mes=este_mes,
            ingresos_mes=ingresos_mes,
            tiempo_medio=3.5,
            ultimas=ultimas,
            reparaciones=mock_reparaciones
        )

    # Con base de datos real
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM reparaciones WHERE estado != 'Entregado'")
    pendientes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM reparaciones WHERE MONTH(created_at) = MONTH(NOW()) AND YEAR(created_at) = YEAR(NOW())")
    este_mes = cursor.fetchone()['total']

    cursor.execute("SELECT COALESCE(SUM(precio_final), 0) as total FROM reparaciones WHERE estado = 'Entregado' AND MONTH(updated_at) = MONTH(NOW()) AND YEAR(updated_at) = YEAR(NOW())")
    ingresos_mes = cursor.fetchone()['total']

    cursor.execute("""
        SELECT r.*, c.nombre as cliente_nombre
        FROM reparaciones r
        JOIN clientes c ON r.cliente_id = c.id
        ORDER BY r.created_at DESC LIMIT 5
    """)
    ultimas = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('dashboard.html',
        pendientes=pendientes,
        este_mes=este_mes,
        ingresos_mes=ingresos_mes,
        tiempo_medio=0,
        ultimas=ultimas,
        reparaciones=[]
    )


@app.route('/nueva-entrada', methods=['GET', 'POST'])
def nueva_entrada():
    if request.method == 'POST':
        # Recoger datos del formulario
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        tipo = request.form.get('tipo_dispositivo', '').strip()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        averia = request.form.get('averia', '').strip()
        observaciones = request.form.get('observaciones', '').strip()

        # Validación básica
        if not nombre or not averia or not tipo:
            flash('Nombre, avería y tipo de dispositivo son obligatorios.', 'error')
            return redirect(url_for('nueva_entrada'))

        if not telefono and not email:
            flash('Indica al menos un dato de contacto (teléfono o email).', 'error')
            return redirect(url_for('nueva_entrada'))

        if PREVIEW_MODE:
            # Buscar o crear cliente en datos mock
            cliente = next((c for c in mock_clientes if c['telefono'] == telefono or c['email'] == email), None)
            if not cliente:
                nuevo_id = max(c['id'] for c in mock_clientes) + 1
                cliente = {'id': nuevo_id, 'nombre': nombre, 'telefono': telefono, 'email': email, 'created_at': datetime.now()}
                mock_clientes.append(cliente)

            # Generar código
            year = datetime.now().year
            num = len(mock_reparaciones) + 1
            codigo = f"REP-{year}-{num:05d}"

            # Crear reparación
            nueva_rep = {
                'id': len(mock_reparaciones) + 1,
                'codigo': codigo,
                'cliente_id': cliente['id'],
                'tipo_dispositivo': tipo,
                'marca': marca,
                'modelo': modelo,
                'averia': averia,
                'observaciones': observaciones,
                'estado': 'Recibido',
                'presupuesto': None,
                'precio_final': None,
                'presupuesto_aceptado': None,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            mock_reparaciones.append(nueva_rep)

            # Registrar en historial
            mock_historial.append({
                'id': len(mock_historial) + 1,
                'reparacion_id': nueva_rep['id'],
                'estado': 'Recibido',
                'tecnico': 'Técnico',
                'fecha': datetime.now()
            })

            flash(f'Reparación {codigo} creada correctamente.', 'success')
            return redirect(url_for('nueva_entrada', pdf=codigo))

        # --- Con base de datos real ---
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Buscar cliente existente
        cursor.execute("SELECT * FROM clientes WHERE telefono = %s OR email = %s", (telefono, email))
        cliente = cursor.fetchone()

        if not cliente:
            cursor.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)", (nombre, telefono, email))
            db.commit()
            cliente_id = cursor.lastrowid
        else:
            cliente_id = cliente['id']

        # Generar código único
        year = datetime.now().year
        cursor.execute("SELECT COUNT(*) as total FROM reparaciones WHERE YEAR(created_at) = %s", (year,))
        num = cursor.fetchone()['total'] + 1
        codigo = f"REP-{year}-{num:05d}"

        # Insertar reparación
        cursor.execute("""
            INSERT INTO reparaciones (codigo, cliente_id, tipo_dispositivo, marca, modelo, averia, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (codigo, cliente_id, tipo, marca, modelo, averia, observaciones))
        reparacion_id = cursor.lastrowid

        # Insertar primer estado
        cursor.execute("INSERT INTO historial_estados (reparacion_id, estado, tecnico) VALUES (%s, 'Recibido', 'Técnico')", (reparacion_id,))
        db.commit()
        cursor.close()
        db.close()

        flash(f'Reparación {codigo} creada correctamente.', 'success')
        return redirect(url_for('nueva_entrada', pdf=codigo))

    return render_template('nueva_entrada.html')

@app.route('/reparaciones')
def reparaciones():
    return render_template('reparaciones.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/buscar')
def buscar():
    return render_template('buscar.html')


@app.route('/api/buscar-cliente')
def api_buscar_cliente():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    if PREVIEW_MODE:
        resultados = [c for c in mock_clientes if q.lower() in c['nombre'].lower() or q in c.get('telefono', '')]
        return jsonify(resultados[:5])

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM clientes
        WHERE nombre LIKE %s OR telefono LIKE %s OR email LIKE %s
        LIMIT 5
    """, (f'%{q}%', f'%{q}%', f'%{q}%'))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(resultados)


@app.route('/pdf/<codigo>')
def ver_pdf(codigo):
    if PREVIEW_MODE:
        rep = next((r for r in mock_reparaciones if r['codigo'] == codigo), None)
        if not rep:
            flash('Reparación no encontrada.', 'error')
            return redirect(url_for('dashboard'))

        cliente = next((c for c in mock_clientes if c['id'] == rep['cliente_id']), None)

        datos = {
            'codigo': rep['codigo'],
            'nombre_cliente': cliente['nombre'] if cliente else 'Desconocido',
            'telefono': cliente.get('telefono', '') if cliente else '',
            'email': cliente.get('email', '') if cliente else '',
            'tipo_dispositivo': rep['tipo_dispositivo'],
            'marca': rep.get('marca', ''),
            'modelo': rep.get('modelo', ''),
            'averia': rep['averia'],
            'observaciones': rep.get('observaciones', ''),
            'fecha': rep['created_at']
        }
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, c.nombre as nombre_cliente, c.telefono, c.email
            FROM reparaciones r
            JOIN clientes c ON r.cliente_id = c.id
            WHERE r.codigo = %s
        """, (codigo,))
        row = cursor.fetchone()
        cursor.close()
        db.close()

        if not row:
            flash('Reparación no encontrada.', 'error')
            return redirect(url_for('dashboard'))

        datos = {
            'codigo': row['codigo'],
            'nombre_cliente': row['nombre_cliente'],
            'telefono': row.get('telefono', ''),
            'email': row.get('email', ''),
            'tipo_dispositivo': row['tipo_dispositivo'],
            'marca': row.get('marca', ''),
            'modelo': row.get('modelo', ''),
            'averia': row['averia'],
            'observaciones': row.get('observaciones', ''),
            'fecha': row['created_at']
        }

    # Generar PDF
    pdf_dir = os.path.join(app.root_path, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f'{codigo}.pdf')

    generar_pdf(datos, pdf_path)
    return send_file(pdf_path, as_attachment=False, download_name=f'{codigo}.pdf')


if __name__ == '__main__':
    app.run(debug=True)
