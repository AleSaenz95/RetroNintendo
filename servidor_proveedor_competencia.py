from flask import Flask, jsonify
import pyodbc

app = Flask(__name__)

# Conexión a la base de datos ServiciosExterno
conn_servicios_externo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ALE;"  
    "DATABASE=ServiciosExterno;"
    "Trusted_Connection=yes;"
)

# Conexión a la base de datos RetroNintendo
conn_retro_nintendo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ALE;"  
    "DATABASE=RetroNintendo;"
    "Trusted_Connection=yes;"
)


@app.route('/api/comparar_precios', methods=['GET'])
def comparar_precios():
    try:
        cursor_competencia = conn_servicios_externo.cursor()
        cursor_inventario = conn_retro_nintendo.cursor()

        cursor_competencia.execute("SELECT item_id, nombre_articulo, precio FROM ProveedorCompetencia")
        competencia_items = cursor_competencia.fetchall()

        comparacion_precios = []

        for item in competencia_items:
            print(f"Procesando artículo: {item.nombre_articulo}")  # Log
            item_id = item.item_id
            nombre_articulo = item.nombre_articulo
            precio_competencia = item.precio

            cursor_inventario.execute("SELECT precio FROM Inventario WHERE nombre_articulo = ?", nombre_articulo)
            inventario_item = cursor_inventario.fetchone()

            if inventario_item:
                precio_retronintendo = inventario_item.precio
            else:
                precio_retronintendo = None

            comparacion_precios.append({
                "nombre_articulo": nombre_articulo,
                "precio_competencia": precio_competencia,
                "precio_retronintendo": precio_retronintendo
            })

        cursor_competencia.close()
        cursor_inventario.close()

        return jsonify(comparacion_precios)
    except Exception as e:
        print(f"Error: {e}")  # Log
        return jsonify({"error": f"Error interno: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(port=5004, debug=True)
