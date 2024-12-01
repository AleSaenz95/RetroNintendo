from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from decimal import Decimal
import os

app = Flask(__name__)

# Configuración de la conexión a la base de datos de servicios externos
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo_SE;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)
     


# Endpoint para procesar pagos con tarjeta
@app.route('/api/pago_tarjeta', methods=['POST'])
def pago_tarjeta():
    data = request.json
    
    # Validar que los datos necesarios estén presentes
    required_fields = ["numero_tarjeta", "fecha_vencimiento", "codigo_seguridad", "monto", "descripcion_comercio"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Datos incompletos"}), 400
    
    numero_tarjeta = data['numero_tarjeta']
    fecha_vencimiento = data['fecha_vencimiento']
    codigo_seguridad = data['codigo_seguridad']
    monto = data['monto']
    descripcion_comercio = data['descripcion_comercio']
    fecha_transaccion = datetime.now()

    # Conectar a la base de datos
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Insertar el registro de pago en la base de datos
    try:
        cursor.execute("""
            INSERT INTO PagosTarjeta (numero_tarjeta, fecha_vencimiento, codigo_seguridad, monto, descripcion_comercio, fecha_transaccion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, numero_tarjeta, fecha_vencimiento, codigo_seguridad, monto, descripcion_comercio, fecha_transaccion)
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Error al procesar el pago: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    # Responder con confirmación de pago
    return jsonify({"mensaje": "Pago procesado exitosamente"}), 200


# Ruta para agregar saldo a la tarjeta
@app.route('/api/agregar_saldo', methods=['POST'])
def agregar_saldo():
    data = request.json
    numero_tarjeta = data.get('numero_tarjeta')
    monto = data.get('monto')

    if not numero_tarjeta or not monto:
        return jsonify({"error": "Número de tarjeta y monto son requeridos"}), 400

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT saldo FROM Tarjetas WHERE numero_tarjeta = ?", numero_tarjeta)
        tarjeta = cursor.fetchone()

        if not tarjeta:
            return jsonify({"error": "Tarjeta no encontrada"}), 404

        nuevo_saldo = tarjeta[0] + monto
        cursor.execute("UPDATE Tarjetas SET saldo = ? WHERE numero_tarjeta = ?", nuevo_saldo, numero_tarjeta)
        conn.commit()

        return jsonify({"mensaje": f"Saldo agregado exitosamente. Nuevo saldo: {nuevo_saldo}"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Ruta para procesar la compra y descontar saldo

from datetime import datetime

@app.route('/api/procesar_compra', methods=['POST'])
def procesar_compra():
    data = request.json
    numero_tarjeta = data.get('numero_tarjeta')
    fecha_vencimiento = data.get('fecha_vencimiento')  # En formato MM/YY (e.g., "12/25")
    codigo_seguridad = data.get('codigo_seguridad')
    monto = data.get('monto')

    if not all([numero_tarjeta, fecha_vencimiento, codigo_seguridad, monto]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    # Convertir monto a Decimal para operaciones con saldo_actual
    monto = Decimal(monto)

    # Convertir la fecha de vencimiento ingresada a un objeto datetime en formato MM/YY
    try:
        fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, "%m/%y")
    except ValueError:
        return jsonify({"error": "Formato de fecha de vencimiento inválido. Use MM/YY"}), 400

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        # Verificar que la tarjeta existe y el código de seguridad coincide
        cursor.execute("""
            SELECT saldo, codigo_seguridad, fecha_vencimiento
            FROM Tarjetas 
            WHERE numero_tarjeta = ?
        """, numero_tarjeta)
        
        tarjeta = cursor.fetchone()
        
        if not tarjeta:
            return jsonify({"error": "Tarjeta no encontrada"}), 404

        saldo_actual, codigo_seguridad_db, fecha_vencimiento_db = tarjeta

        # Validar código de seguridad
        if codigo_seguridad != codigo_seguridad_db:
            return jsonify({"error": "Código de seguridad incorrecto"}), 403

        # Convertir fecha_vencimiento_db a cadena en formato MM/YY
        if isinstance(fecha_vencimiento_db, datetime):
            fecha_vencimiento_db_str = fecha_vencimiento_db.strftime("%m/%y")
        else:
            fecha_vencimiento_db_str = datetime.strptime(fecha_vencimiento_db, "%Y-%m-%d").strftime("%m/%y")

        # Comparar solo el mes y el año en formato MM/YY
        if fecha_vencimiento != fecha_vencimiento_db_str:
            return jsonify({"error": "Fecha de vencimiento incorrecta"}), 403

        # Verificar que el saldo es suficiente
        if saldo_actual < monto:
            return jsonify({"error": "Saldo insuficiente"}), 400

        # Descontar el monto del saldo
        nuevo_saldo = saldo_actual - monto
        cursor.execute("UPDATE Tarjetas SET saldo = ? WHERE numero_tarjeta = ?", nuevo_saldo, numero_tarjeta)
        conn.commit()

        return jsonify({"mensaje": "Compra procesada exitosamente", "nuevo_saldo": nuevo_saldo}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()





@app.route('/api/registrar_tarjeta', methods=['POST'])
def registrar_tarjeta():
    data = request.json
    
    numero_tarjeta = data.get('numero_tarjeta')
    fecha_vencimiento = data.get('fecha_vencimiento')
    codigo_seguridad = data.get('codigo_seguridad')
    saldo = data.get('saldo', 0.00)
    nombre_titular = data.get('nombre_titular')

    # Validar que todos los datos requeridos estén presentes
    if not all([numero_tarjeta, fecha_vencimiento, codigo_seguridad, nombre_titular]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        # Insertar la nueva tarjeta en la base de datos
        cursor.execute("""
            INSERT INTO Tarjetas (numero_tarjeta, fecha_vencimiento, codigo_seguridad, saldo, nombre_titular)
            VALUES (?, ?, ?, ?, ?)
        """, numero_tarjeta, fecha_vencimiento, codigo_seguridad, saldo, nombre_titular)
        conn.commit()
        
        return jsonify({"mensaje": "Tarjeta registrada exitosamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()






if __name__ == "__main__":
    # Cambia el puerto predeterminado según la lista de puertos
    port = int(os.environ.get("PORT", 5001))  # 5001 para servidor_pagos.py
    app.run(host="0.0.0.0", port=port)
