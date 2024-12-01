from flask import Flask, jsonify, request
import pyodbc
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


# Ruta para obtener todos los videojuegos del proveedor externo
@app.route('/api/videojuegos_proveedor', methods=['GET'])
def obtener_videojuegos_proveedor():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT juego_id, nombre_juego, precio, plataforma, stock_disponible FROM VideojuegosProveedor")
        videojuegos = cursor.fetchall()
        
        # Convertir los resultados en un formato JSON
        videojuegos_list = [
            {
                "juego_id": row.juego_id,
                "nombre_juego": row.nombre_juego,
                "precio": row.precio,
                "plataforma": row.plataforma,
                "stock_disponible": row.stock_disponible
            }
            for row in videojuegos
        ]
        
        return jsonify(videojuegos_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Ruta para agregar un videojuego al proveedor externo
@app.route('/api/videojuegos_proveedor', methods=['POST'])
def agregar_videojuegos_proveedor():
    data = request.json

    # Verificar si data es una lista
    if not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de videojuegos"}), 400

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    try:
        for videojuego in data:
            nombre_juego = videojuego.get('nombre_juego')
            precio = videojuego.get('precio')
            plataforma = videojuego.get('plataforma')
            stock_disponible = videojuego.get('stock_disponible', 0)

            if not nombre_juego or precio is None:
                return jsonify({"error": "Cada videojuego debe tener un nombre y precio"}), 400

            # Insertar cada videojuego en la base de datos
            cursor.execute("""
                INSERT INTO VideojuegosProveedor (nombre_juego, precio, plataforma, stock_disponible)
                VALUES (?, ?, ?, ?)
            """, (nombre_juego, precio, plataforma, stock_disponible))
        
        conn.commit()  # Hacer commit después de todas las inserciones
        return jsonify({"mensaje": "Videojuegos agregados exitosamente"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()





if __name__ == "__main__":
    # Cambia el puerto predeterminado según la lista de puertos
    port = int(os.environ.get("PORT", 5003))  # 5003 para servidor_proveedor_externo.py
    app.run(host="0.0.0.0", port=port)
