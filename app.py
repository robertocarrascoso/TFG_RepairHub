from flask import Flask, render_template
from config import DB_CONFIG, SECRET_KEY
from datetime import datetime

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


if __name__ == '__main__':
    app.run(debug=True)
