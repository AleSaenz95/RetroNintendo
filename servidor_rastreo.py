from datetime import datetime
from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Configuración de conexión a la base de datos
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=ALE;" 
    "DATABASE=ServiciosExterno;"
    "Trusted_Connection=yes;"
)

# Ruta para obtener el estado de un paquete según el código
@app.route('/api/rastreo_paquete/<codigo_paquete>', methods=['GET'])
def obtener_estado_paquete(codigo_paquete):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    try:
        # Consultar la información del paquete en la base de datos
        cursor.execute("SELECT codigo_paquete, estado, ubicacion_actual, ultima_actualizacion FROM RastreoPaquetes WHERE codigo_paquete = ?", codigo_paquete)
        paquete = cursor.fetchone()
        
        if not paquete:
            return jsonify({"error": "Paquete no encontrado"}), 404
        
        # Formatear la respuesta JSON
        paquete_info = {
            "codigo_paquete": paquete.codigo_paquete,
            "estado": paquete.estado,
            "ubicacion_actual": paquete.ubicacion_actual,
            "ultima_actualizacion": paquete.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(paquete_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/api/actualizar_estado_paquete', methods=['POST'])
def actualizar_estado_paquete():
    data = request.json
    codigo_paquete = data.get('codigo_paquete')
    nuevo_estado = data.get('estado')
    nueva_ubicacion = data.get('ubicacion')

    if not codigo_paquete or not nuevo_estado:
        return jsonify({"error": "Código de paquete y nuevo estado son necesarios"}), 400

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE RastreoPaquetes
            SET estado = ?, ubicacion_actual = ?, ultima_actualizacion = ?
            WHERE codigo_paquete = ?
        """, (nuevo_estado, nueva_ubicacion, datetime.now(), codigo_paquete))
        conn.commit()
        
        return jsonify({"mensaje": "Estado del paquete actualizado exitosamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    app.run(port=5004, debug=True)
