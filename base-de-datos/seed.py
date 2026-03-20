"""
seed.py — Insertar datos de prueba en la base de datos.
Ejecutar: python base-de-datos/seed.py
Solo necesario cuando se conecte a MariaDB real (en el servidor).
"""
import mysql.connector
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="repairhub_user",
    password="tu_contraseña",
    database="repairhub"
)
cursor = conn.cursor()

# Limpiar tablas
cursor.execute("DELETE FROM historial_estados")
cursor.execute("DELETE FROM reparaciones")
cursor.execute("DELETE FROM clientes")
cursor.execute("DELETE FROM usuarios")
cursor.execute("ALTER TABLE clientes AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE reparaciones AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE historial_estados AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE usuarios AUTO_INCREMENT = 1")

# Usuario administrador por defecto
cursor.execute(
    "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
    ('Administrador', 'admin@repairhub.com', generate_password_hash('admin123'), 'admin')
)
cursor.execute(
    "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
    ('Roberto', 'roberto@repairhub.com', generate_password_hash('tecnico123'), 'tecnico')
)
conn.commit()

# Clientes
clientes = [
    ('Carlos García', '612345678', 'carlos@email.com'),
    ('María López', '623456789', 'maria@email.com'),
    ('Pedro Sánchez', '634567890', ''),
    ('Ana Martínez', '', 'ana@email.com'),
    ('Luis Fernández', '656789012', 'luis@email.com'),
    ('Elena Ruiz', '667890123', 'elena@email.com'),
    ('Javier Moreno', '678901234', ''),
    ('Carmen Jiménez', '689012345', 'carmen@email.com'),
    ('Roberto Díaz', '690123456', 'roberto@email.com'),
    ('Lucía Torres', '601234567', ''),
    ('Miguel Navarro', '611223344', 'miguel@email.com'),
    ('Patricia Gil', '622334455', 'patricia@email.com'),
]

for nombre, tel, email in clientes:
    cursor.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)", (nombre, tel, email))

conn.commit()

# Reparaciones
tipos = ['Móvil', 'Tablet', 'Portátil', 'Ordenador', 'Consola']
marcas_modelos = {
    'Móvil': [('Samsung', 'Galaxy S23'), ('Apple', 'iPhone 14'), ('Xiaomi', 'Redmi Note 13'), ('OnePlus', '12')],
    'Tablet': [('Apple', 'iPad Air 5'), ('Samsung', 'Galaxy Tab S9'), ('Lenovo', 'Tab P11')],
    'Portátil': [('HP', 'Pavilion 15'), ('Lenovo', 'ThinkPad T14'), ('Dell', 'XPS 13'), ('ASUS', 'VivoBook')],
    'Ordenador': [('Custom', 'Sobremesa'), ('HP', 'ProDesk'), ('Lenovo', 'ThinkCentre')],
    'Consola': [('Sony', 'PS5'), ('Microsoft', 'Xbox Series X'), ('Nintendo', 'Switch')],
}
averias = {
    'Móvil': ['Pantalla rota', 'No carga', 'Batería hinchada', 'Cámara borrosa', 'No enciende'],
    'Tablet': ['Pantalla rota', 'Puerto de carga dañado', 'Batería dura poco', 'Touch no responde'],
    'Portátil': ['No enciende', 'Pantalla en negro', 'Teclado no funciona', 'Muy lento', 'Ventilador ruidoso'],
    'Ordenador': ['Pantalla azul', 'No arranca', 'Disco duro roto', 'Fuente de alimentación'],
    'Consola': ['No lee discos', 'Se sobrecalienta', 'Mando no conecta', 'Error de sistema'],
}
estados_completo = ['Recibido', 'Diagnosticado', 'Presupuesto enviado', 'Presupuesto aceptado', 'Reparando', 'Listo', 'Entregado']

for i in range(1, 26):
    tipo = random.choice(tipos)
    marca, modelo = random.choice(marcas_modelos[tipo])
    averia = random.choice(averias[tipo])
    cliente_id = random.randint(1, len(clientes))
    fecha_base = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 65))

    # Decidir hasta qué estado llega
    num_estados = random.randint(1, len(estados_completo))
    estado_actual = estados_completo[num_estados - 1]

    presupuesto = round(random.uniform(30, 200), 2) if num_estados >= 3 else None
    aceptado = True if num_estados >= 4 else (False if num_estados == 3 and random.random() < 0.2 else None)
    precio = presupuesto if num_estados >= 6 else None

    codigo = f"REP-2026-{i:05d}"

    cursor.execute("""
        INSERT INTO reparaciones (codigo, cliente_id, tipo_dispositivo, marca, modelo, averia, estado, presupuesto, precio_final, presupuesto_aceptado, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (codigo, cliente_id, tipo, marca, modelo, averia, estado_actual, presupuesto, precio, aceptado, fecha_base))

    rep_id = cursor.lastrowid

    # Historial de estados
    for j in range(num_estados):
        fecha_estado = fecha_base + timedelta(days=j, hours=random.randint(1, 8))
        cursor.execute("INSERT INTO historial_estados (reparacion_id, estado, tecnico, fecha) VALUES (%s, %s, %s, %s)",
                       (rep_id, estados_completo[j], 'Roberto', fecha_estado))

conn.commit()
cursor.close()
conn.close()
print(f"Seed completado: 2 usuarios, {len(clientes)} clientes, 25 reparaciones.")
