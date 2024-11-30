from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Configuración de conexión a la base de datos RetroNintendo y ServiciosExterno
# Conexión a la base de datos ServiciosExterno
conn_str_servicios_externo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo_SE;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

# Conexión a la base de datos RetroNintendo
conn_str_retronintendo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)


# Ruta para verificar la identificación en ambas bases de datos usando GET
@app.route('/api/verificar_identificacion', methods=['GET'])
def verificar_identificacion():
    identificacion = request.args.get('identificacion')
    
    if not identificacion:
        return jsonify({"error": "Identificación es requerida"}), 400

    try:
        # Conectar a la base de datos RetroNintendo y verificar en la tabla Usuarios
        conn_retronintendo = pyodbc.connect(conn_str_retronintendo)
        cursor_retronintendo = conn_retronintendo.cursor()
        cursor_retronintendo.execute("SELECT nombre_usuario FROM Usuarios WHERE identificacion = ?", identificacion)
        usuario = cursor_retronintendo.fetchone()
        cursor_retronintendo.close()
        conn_retronintendo.close()

        # Si la identificación no existe en RetroNintendo, devolver que no existe
        if not usuario:
            return jsonify({"existe": False, "mensaje": "Identificación no encontrada en RetroNintendo"}), 404

        # Conectar a la base de datos ServiciosExterno y verificar en la tabla PersonasTSE
        conn_servicios_externo = pyodbc.connect(conn_str_servicios_externo)
        cursor_servicios_externo = conn_servicios_externo.cursor()
        cursor_servicios_externo.execute("SELECT nombre FROM PersonasTSE WHERE identificacion = ?", identificacion)
        persona_externa = cursor_servicios_externo.fetchone()
        cursor_servicios_externo.close()
        conn_servicios_externo.close()

        # Verificar si la identificación también existe en ServiciosExterno
        if persona_externa:
            return jsonify({"existe": True, "nombre": usuario[0], "mensaje": "Identificación encontrada en ambas bases de datos"})
        else:
            return jsonify({"existe": False, "mensaje": "Identificación no encontrada en ServiciosExterno"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002, debug=True)
