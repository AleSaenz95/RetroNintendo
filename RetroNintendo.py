from flask import Flask, request, jsonify, render_template, redirect, url_for, request, Flask
import pyodbc
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)

# Configuración de la conexión a SQL Server
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        print("Conexión exitosa a la base de datos.")
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ruta para registrar usuarios
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    print("Datos recibidos:", data)

    # Validar campos obligatorios (incluyendo identificacion)
    campos_obligatorios = ['nombre_usuario', 'correo', 'password', 'pais', 'provincia', 'canton', 'distrito', 'identificacion', 'respuesta1', 'respuesta2', 'respuesta3']
    if not all(data.get(field) for field in campos_obligatorios):
        return jsonify({"message": "Todos los campos son obligatorios."}), 400

    # Asignar valores recibidos, incluyendo identificacion
    nombre_usuario = data['nombre_usuario']
    correo = data['correo']
    password = data['password']
    pais = data['pais']
    provincia = data['provincia']
    canton = data['canton']
    distrito = data['distrito']
    identificacion = data['identificacion']
    respuesta1 = data['respuesta1']
    respuesta2 = data['respuesta2']
    respuesta3 = data['respuesta3']

    # Generar un hash de la contraseña
    password_hash = generate_password_hash(password)

    # Conectar a la base de datos y buscar ubicacion_id
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Buscar ubicacion_id correspondiente
            select_ubicacion_query = """
                SELECT ubicacion_id FROM Ubicaciones 
                WHERE pais = ? AND provincia = ? AND canton = ? AND distrito = ?
            """
            cursor.execute(select_ubicacion_query, (pais, provincia, canton, distrito))
            ubicacion = cursor.fetchone()

            if not ubicacion:
                return jsonify({"message": "No se encontró la ubicación especificada."}), 400

            ubicacion_id = ubicacion[0]

            # Insertar el nuevo usuario en la tabla Usuarios usando ubicacion_id y identificacion
            insert_usuario_query = """
                INSERT INTO Usuarios (nombre_usuario, correo, password_hash, ubicacion_id, identificacion, fecha_registro, respuesta1, respuesta2, respuesta3)
                VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, ?)
            """
            cursor.execute(insert_usuario_query, (nombre_usuario, correo, password_hash, ubicacion_id, identificacion, respuesta1, respuesta2, respuesta3))
            conn.commit()

            return jsonify({"message": "Usuario registrado exitosamente."}), 201
        except pyodbc.Error as e:
            print(f"Error al registrar usuario: {e}")
            return jsonify({"message": f"Ocurrió un error durante el registro: {e}"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"message": "No se pudo conectar a la base de datos."}), 500



# Ruta para la página principal (index)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para agregar una nueva reseña
@app.route('/agregar-resena', methods=['POST'])
def agregar_resena():
    print("Recibiendo solicitud de reseña...")
    
    # Verificar si los datos vienen en JSON
    if request.is_json:
        data = request.get_json()
        print("Datos recibidos (JSON):", data)
    else:
        return jsonify({"message": "Formato no válido. Se espera JSON."}), 400
    
    # Obtener campos del JSON
    nombre_juego = data.get('nombre_juego')
    resena = data.get('resena')
    
    # Validación de campos obligatorios
    if not nombre_juego or not resena:
        print("Faltan campos obligatorios:", data)  # Agregar depuración
        return jsonify({"message": "Faltan campos obligatorios"}), 400

    # Guardar reseña en la base de datos
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Resenas (nombre_juego, resena, fecha) VALUES (?, ?, ?)"
            cursor.execute(query, (nombre_juego, resena, datetime.now()))
            conn.commit()
            print("Reseña guardada correctamente.")
            return jsonify({"message": "Reseña guardada exitosamente."}), 201
        except pyodbc.Error as e:
            print(f"Error al guardar reseña: {e}")
            return jsonify({"message": f"Error al guardar la reseña: {e}"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"message": "No se pudo conectar a la base de datos."}), 500


# Ruta para ver reseñas en formato JSON
@app.route('/api/ver-resenas', methods=['GET'])
def ver_resenas_json():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT nombre_juego, resena, fecha FROM Resenas"
            cursor.execute(query)
            resenas = cursor.fetchall()
            
            # Convertir las reseñas a una lista de diccionarios para JSON
            resenas_json = [
                {"nombre_juego": resena[0], "resena": resena[1], "fecha": resena[2].strftime('%Y-%m-%d %H:%M')}
                for resena in resenas
            ]
            return jsonify(resenas=resenas_json), 200
        except pyodbc.Error as e:
            print(f"Error al obtener reseñas: {e}")
            return jsonify({"message": f"Ocurrió un error al obtener las reseñas: {e}"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"message": "No se pudo conectar a la base de datos."}), 500



#cotizacion
@app.route('/api/solicitud_cotizacion', methods=['POST'])
def solicitud_cotizacion():
    data = request.json
    
    # Validar datos recibidos
    if not data or 'usuario_id' not in data or 'productos' not in data:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    usuario_id = data['usuario_id']
    productos = data['productos']  # Lista de diccionarios con item_id y cantidad
    direccion_entrega = data.get('direccion_entrega')
    email = data.get('email')

    total_estimado = 0
    detalles_cotizacion = []

    # Conectar a la base de datos
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calcular el total estimado y preparar los detalles de la cotización
        for producto in productos:
            item_id = producto['item_id']
            cantidad = producto['cantidad']
            
            # Consultar el precio del producto en la base de datos
            cursor.execute("SELECT precio FROM Inventario WHERE item_id = ?", item_id)
            result = cursor.fetchone()
            
            if not result:
                return jsonify({'error': f'Producto con ID {item_id} no encontrado'}), 404
            
            precio_unitario = result[0]
            subtotal = precio_unitario * cantidad
            total_estimado += subtotal
            
            # Agregar detalle al listado para inserción posterior
            detalles_cotizacion.append({
                'item_id': item_id,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario
            })

        # Insertar la solicitud de cotización en la base de datos
        cursor.execute("""
            INSERT INTO SolicitudesCotizacion (usuario_id, total_estimado, direccion_entrega, email)
            VALUES (?, ?, ?, ?)
        """, usuario_id, total_estimado, direccion_entrega, email)
        conn.commit()

        # Obtener el ID de la cotización recién insertada
        cursor.execute("SELECT @@IDENTITY AS cotizacion_id;")
        cotizacion_id = cursor.fetchone()[0]

        # Insertar los detalles de la cotización
        for detalle in detalles_cotizacion:
            cursor.execute("""
                INSERT INTO DetalleCotizacion (cotizacion_id, item_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, cotizacion_id, detalle['item_id'], detalle['cantidad'], detalle['precio_unitario'])
        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()  # Hacer rollback en caso de error
        return jsonify({'error': str(e)}), 500

    finally:
        # Cerrar cursor y conexión
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Responder con un mensaje de confirmación
    return jsonify({
        'mensaje': 'Solicitud de cotización recibida',
        'cotizacion_id': cotizacion_id,
        'total_estimado': total_estimado
    }), 200








if __name__ == '__main__':
    app.run(debug=True, port=4000)         