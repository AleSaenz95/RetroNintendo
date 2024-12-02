import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pyodbc
from datetime import date
import requests 
import os
from decimal import Decimal
from zeep import Client


app = Flask(__name__, template_folder='templates')
app.secret_key = 'tu_secreto'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = {}




# Cadenas de conexión
CONN_STR_PRINCIPAL = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

CONN_STR_SERVICIOS_EXTERNO = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo_SE;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

# Función para conexión a la base de datos
def get_db_connection(conn_str):
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        print("Conexión exitosa.")
        return conn
    except pyodbc.InterfaceError as e:
        print(f"Error de conexión (interface): {e}")
    except pyodbc.OperationalError as e:
        print(f"Error operacional: {e}")
    except Exception as e:
        print(f"Error inesperado al conectar a la base de datos: {e}")
    return None

# Verificar conexiones al iniciar
@app.route('/test_connections')
def test_connections():
    conn_principal = get_db_connection(CONN_STR_PRINCIPAL)
    conn_servicios = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)

    if conn_principal:
        conn_principal.close()
        principal_status = "Conexión a RetroNintendo exitosa."
    else:
        principal_status = "Error al conectar a RetroNintendo."

    if conn_servicios:
        conn_servicios.close()
        servicios_status = "Conexión a ServiciosExterno exitosa."
    else:
        servicios_status = "Error al conectar a ServiciosExterno."

    return jsonify({
        "RetroNintendo": principal_status,
        "ServiciosExterno": servicios_status
    })





# conn_str = (
#     "DRIVER={SQL Server};"
#     "SERVER=ALE;"
#     "DATABASE=RetroNintendo;"
#     "Trusted_Connection=yes;"
# )

# try:
#     conn = pyodbc.connect(conn_str)
#     print("Conexión exitosa a la base de datos.")
# except Exception as e:
#     print(f"Error en la conexión: {e}")




# Configuración del SMTP para Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "retronintendo1986@gmail.com"
EMAIL_PASS = "frqg gqyg pvqv vper"

# Ruta para agregar una nueva reseña

# Ruta para ver las reseñas guardadas
@app.route('/ver-resenas')
def ver_resenas():
    # Obtener la conexión a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar función para manejar conexiones
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = "SELECT nombre_juego, resena FROM Resenas"
        cursor.execute(query)
        reseñas = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener reseñas: {e}")
        return "Error al obtener las reseñas.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Renderizar la plantilla con las reseñas
    return render_template('ver_resenas.html', reseñas=reseñas)


@app.route('/enviar-mensaje', methods=['GET', 'POST'])
def enviar_mensaje():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']  # Nuevo campo correo
        mensaje = request.form['mensaje']

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
        if conn is None:
            return "Error al conectar con la base de datos.", 500

        try:
            cursor = conn.cursor()
            query = "INSERT INTO Contactos (nombre, correo, mensaje) VALUES (?, ?, ?)"
            cursor.execute(query, (nombre, correo, mensaje))
            conn.commit()
            cursor.close()  # Cerrar el cursor después de usarlo
        except Exception as e:
            print(f"Error al guardar el mensaje: {e}")
            return "Error al guardar el mensaje.", 500
        finally:
            conn.close()  # Cerrar la conexión

        # Redirigir a la página de visualización de mensajes
        return redirect('/ver-mensajes')

    # Renderizar el formulario de contacto si el método es GET
    return render_template('recibir_mensaje.html')


@app.route('/ver-mensajes')
def ver_mensajes():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = "SELECT nombre, correo, mensaje FROM Contactos"
        cursor.execute(query)
        mensajes = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener los mensajes: {e}")
        return "Error al obtener los mensajes.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Renderizar el HTML con los mensajes
    return render_template('ver_mensajes.html', mensajes=mensajes)



@app.route('/catalogo')
def catalogo():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = "SELECT item_id, nombre_articulo, descripcion, precio, cantidad_disponible FROM Inventario"
        cursor.execute(query)
        articulos = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener el catálogo: {e}")
        return "Error al obtener el catálogo.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Renderizar la plantilla con los artículos del catálogo
    return render_template('catalogo.html', articulos=articulos)


@app.route('/producto/<int:item_id>')
def detalle_producto(item_id):
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = "SELECT item_id, nombre_articulo, descripcion, precio, cantidad_disponible, imagen FROM Inventario WHERE item_id = ?"
        cursor.execute(query, (item_id,))  # Asegurarse de pasar un tuple para evitar errores de sintaxis
        producto = cursor.fetchone()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener el producto: {e}")
        return "Error al obtener los detalles del producto.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Verificar si el producto existe
    if not producto:
        return "Producto no encontrado.", 404

    # Renderizar la plantilla con los detalles del producto
    return render_template('detalle_producto.html', producto=producto)


############ Sección de Órdenes ###################

# Ruta para el formulario de compra desde el catálogo
@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        cliente_nombre = request.form['cliente_nombre']
        tipo_orden = request.form['tipo_orden']
        total = float(request.form['total'])
        producto_nombre = request.form['producto_nombre']
        numero_tarjeta = request.form['numero_tarjeta']
        fecha_vencimiento = request.form['fecha_vencimiento']
        codigo_seguridad = request.form['codigo_seguridad']

        # Payload para el endpoint de pago
        payload = {
            "numero_tarjeta": numero_tarjeta,
            "fecha_vencimiento": fecha_vencimiento,
            "codigo_seguridad": codigo_seguridad,
            "monto": total,
            "descripcion_comercio": "Compra en RetroNintendo"
        }

        try:
            # Llamar al endpoint de procesamiento de pagos
            response = requests.post("http://127.0.0.1:5000/procesar_compra", json=payload)
            response_data = response.json()

            if response.status_code == 200:
                # Conectar a la base de datos
                conn = get_db_connection(CONN_STR_PRINCIPAL)
                if conn is None:
                    return "Error al conectar con la base de datos.", 500

                try:
                    cursor = conn.cursor()
                    # Insertar la orden en la tabla Ordenes
                    query_orden = """
                        INSERT INTO Ordenes (cliente_nombre, tipo_orden, total, fecha, producto_nombre)
                        VALUES (?, ?, ?, GETDATE(), ?)
                    """
                    cursor.execute(query_orden, (cliente_nombre, tipo_orden, total, producto_nombre))

                    # Obtener el ID de la orden recién creada
                    orden_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

                    # Reducir la cantidad disponible en el inventario
                    cursor.execute("""
                        UPDATE Inventario
                        SET cantidad_disponible = cantidad_disponible - 1
                        WHERE nombre_articulo = ?
                    """, producto_nombre)

                    # Insertar en el reporte de ventas
                    cursor.execute("EXEC InsertarEnReporteVentas ?, ?, ?, ?", producto_nombre, 1, total, orden_id)

                    # Manejar los pedidos express
                    if tipo_orden == "Envío Express":
                        direccion_entrega = request.form['direccion_entrega']
                        estado_entrega = "En proceso"
                        cursor.execute("""
                            EXEC InsertarPedidoExpress ?, ?, ?, ?
                        """, cliente_nombre, direccion_entrega, estado_entrega, orden_id)

                    # Guardar los cambios
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"Error al procesar la compra: {e}")
                    return "Error al procesar la compra en la base de datos.", 500
                finally:
                    cursor.close()
                    conn.close()

                # Redirigir al gestor de órdenes
                return redirect('/gestor_ordenes')
            else:
                # Manejo de errores en el procesamiento del pago
                error_msg = response_data.get('error', 'Error desconocido')
                return f"Error en el pago: {error_msg}", 400

        except requests.RequestException as e:
            print(f"Error al conectar al servicio de pago: {e}")
            return "Error al conectar con el servicio de pago.", 500

    # Si el método es GET, obtener los detalles del producto
    item_id = request.args.get('item_id')
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre_articulo, precio
            FROM Inventario
            WHERE item_id = ?
        """, (item_id,))
        producto = cursor.fetchone()
        if not producto:
            return "Producto no encontrado.", 404

        producto_nombre = producto[0]
        producto_precio = producto[1]
    except Exception as e:
        print(f"Error al obtener los detalles del producto: {e}")
        return "Error al obtener los detalles del producto.", 500
    finally:
        cursor.close()
        conn.close()

    # Renderizar la plantilla de compra
    return render_template('comprar.html', producto_nombre=producto_nombre, producto_precio=producto_precio)


# Ruta para el gestor de órdenes
@app.route('/gestor_ordenes')
def gestor_ordenes():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = """
            SELECT orden_id, cliente_nombre, producto_nombre, tipo_orden, total
            FROM Ordenes
        """
        cursor.execute(query)
        ordenes = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener las órdenes: {e}")
        return "Error al obtener las órdenes.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Añadir el código de rastreo para las órdenes de tipo "Envío Express"
    ordenes_con_rastreo = []
    for orden in ordenes:
        codigo_rastreo = f"RN-{orden[0]}" if orden[3] == "Envío Express" else ""
        ordenes_con_rastreo.append({
            "orden_id": orden[0],
            "cliente_nombre": orden[1],
            "producto_nombre": orden[2],
            "tipo_orden": orden[3],
            "total": orden[4],
            "codigo_rastreo": codigo_rastreo
        })

    # Renderizar la plantilla con las órdenes
    return render_template('gestor_ordenes.html', ordenes=ordenes_con_rastreo)




# Ruta para ver detalles de una orden
@app.route('/ver_orden/<int:orden_id>')
def ver_orden(orden_id):
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = """
            SELECT orden_id, cliente_nombre, tipo_orden, total, fecha 
            FROM Ordenes 
            WHERE orden_id = ?
        """
        cursor.execute(query, (orden_id,))  # Usar tuple para evitar errores de parámetros
        orden = cursor.fetchone()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener la orden: {e}")
        return "Error al obtener los detalles de la orden.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Verificar si la orden existe
    if not orden:
        return "Orden no encontrada.", 404

    # Renderizar la plantilla con los detalles de la orden
    return render_template('ver_orden.html', orden=orden)


# Ruta para procesar una orden (cambiar estado a procesado)
@app.route('/procesar_orden/<int:orden_id>')
def procesar_orden(orden_id):
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = "UPDATE Ordenes SET estado='Procesado' WHERE orden_id = ?"
        cursor.execute(query, (orden_id,))  # Usar tuple para evitar errores
        conn.commit()  # Confirmar los cambios
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al procesar la orden: {e}")
        return "Error al procesar la orden.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Redirigir al gestor de órdenes después de procesar
    return redirect('/gestor_ordenes')



########### Reporte###############
@app.route('/reporte_ventas')
def reporte_ventas():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = """
            SELECT producto, 
                   SUM(cantidad_vendida) AS total_vendido, 
                   SUM(ingresos) AS total_ingresos 
            FROM ReporteVentas 
            GROUP BY producto
        """
        cursor.execute(query)
        ventas = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al consultar el reporte de ventas: {e}")
        return "Error al consultar el reporte de ventas.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Preparar los datos para el gráfico
    productos = [venta[0] for venta in ventas]
    cantidades = [venta[1] for venta in ventas]
    ingresos = [venta[2] for venta in ventas]

    # Renderizar la plantilla con los datos del reporte
    return render_template(
        'reporte_ventas.html', 
        productos=productos, 
        cantidades=cantidades, 
        ingresos=ingresos
    )

###################Pedidos express####

@app.route('/pedidos_express')
def pedidos_express():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()
        query = """
            SELECT express_order_id, cliente_nombre, direccion_entrega, estado_entrega, fecha, quien_recibe
            FROM PedidosExpress
        """
        cursor.execute(query)
        pedidos = cursor.fetchall()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        print(f"Error al obtener los pedidos express: {e}")
        return "Error al obtener los pedidos express.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Renderizar la plantilla con los datos de los pedidos express
    return render_template('pedidos_express.html', pedidos=pedidos)



###### envios


@app.route('/completar_pedido', methods=['POST'])
def completar_pedido():
    express_order_id = request.form['express_order_id']
    return render_template('completar_pedido.html', express_order_id=express_order_id)

@app.route('/confirmar_completado', methods=['POST'])
def confirmar_completado():
    express_order_id = request.form['express_order_id']
    quien_recibe = request.form['quien_recibe']

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
    if conn is None:
        return "Error al conectar con la base de datos.", 500

    try:
        cursor = conn.cursor()

        # Actualizar el estado y quien recibe en la tabla PedidosExpress
        query_pedidos = """
            UPDATE PedidosExpress 
            SET estado_entrega = 'Completado', quien_recibe = ?
            WHERE express_order_id = ?
        """
        cursor.execute(query_pedidos, (quien_recibe, express_order_id))

        # Actualizar la tabla Envios con quien recibe
        query_envios = """
            UPDATE Envios 
            SET quien_recibe = ? 
            WHERE envio_id = (
                SELECT envio_id 
                FROM Envios 
                WHERE item_id = (
                    SELECT item_id 
                    FROM PedidosExpress 
                    WHERE express_order_id = ?
                )
            )
        """
        cursor.execute(query_envios, (quien_recibe, express_order_id))

        # Confirmar los cambios
        conn.commit()
        cursor.close()  # Cerrar el cursor después de usarlo
    except Exception as e:
        conn.rollback()  # Revertir los cambios en caso de error
        print(f"Error al confirmar el completado del pedido: {e}")
        return "Error al confirmar el completado del pedido.", 500
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

    # Redirigir a la página de pedidos express
    return redirect('/pedidos_express')




################# acerca de


@app.route('/acerca_de')
def acerca_de():
    return render_template('acerca_de.html')



#################### login
# Ruta para el registro


# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:  # Verificación de solicitud AJAX
            data = request.get_json()
            correo = data.get('correo')
            password = data.get('password')
        else:  # Manejo de solicitud normal
            correo = request.form['correo']
            password = request.form['password']

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)  # Usar la función de conexión
        if conn is None:
            return "Error al conectar con la base de datos.", 500

        try:
            cursor = conn.cursor()
            query = """
                SELECT usuario_id, nombre_usuario, password_hash, intentos_fallidos, cuenta_bloqueada, fecha_registro
                FROM Usuarios 
                WHERE correo = ?
            """
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()
        except Exception as e:
            print(f"Error al consultar el usuario: {e}")
            return "Error al procesar la solicitud.", 500
        finally:
            cursor.close()
            conn.close()

        if usuario:
            usuario_id, nombre_usuario, password_hash, intentos_fallidos, cuenta_bloqueada, fecha_registro = usuario
            
            # Convertir fecha_registro a datetime.date si es una cadena
            if isinstance(fecha_registro, str):
                fecha_registro = datetime.strptime(fecha_registro, '%Y-%m-%d').date()
            
            # Verificar si la cuenta está bloqueada
            if cuenta_bloqueada:
                mensaje = "Cuenta bloqueada. Verifique su correo para desbloquear."
                return manejar_respuesta(request.is_json, mensaje, url_for('solicitar_restablecimiento'))
            
            # Calcular si la contraseña tiene más de 90 días
            fecha_vencimiento = fecha_registro + timedelta(days=90)
            if date.today() > fecha_vencimiento:
                codigo_actualizacion = random.randint(100000, 999999)
                session['codigo_actualizacion'] = codigo_actualizacion
                session['usuario_id_reset'] = usuario_id
                
                enviar_codigo_verificacion(correo, codigo_actualizacion, "actualizacion")
                
                mensaje = "Tu contraseña ha expirado. Te hemos enviado un código de verificación para actualizarla."
                return manejar_respuesta(request.is_json, mensaje, url_for('verificar_codigo_actualizacion'))

            # Verificar la contraseña
            if check_password_hash(password_hash, password):
                codigo_verificacion = random.randint(100000, 999999)
                session['codigo_verificacion'] = codigo_verificacion
                session['usuario_id_temp'] = usuario_id
                enviar_codigo_verificacion(correo, codigo_verificacion, "login")
                
                registrar_auditoria(usuario_id, "Inicio de sesión", "Usuario inició sesión con éxito")

                mensaje = "Código de verificación enviado a tu correo."
                return manejar_respuesta(request.is_json, mensaje, url_for('verificar_codigo'))
            else:
                return manejar_intentos_fallidos(usuario_id, intentos_fallidos, correo, request.is_json)
        else:
            mensaje = "Usuario no encontrado."
            return manejar_respuesta(request.is_json, mensaje)

    return render_template('login.html')

# Función auxiliar para manejar la respuesta según el tipo de solicitud
def manejar_respuesta(es_json, mensaje, redireccion=None):
    if es_json:
        return jsonify(success=bool(redireccion), message=mensaje)
    else:
        flash(mensaje)
        return redirect(redireccion) if redireccion else render_template('login.html')

# Función auxiliar para manejar intentos fallidos
def manejar_intentos_fallidos(usuario_id, intentos_fallidos, correo, es_json):
    intentos_fallidos = (intentos_fallidos or 0) + 1
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Usuarios SET intentos_fallidos = ? WHERE usuario_id = ?", (intentos_fallidos, usuario_id))
        conn.commit()
        registrar_auditoria(usuario_id, "Intento fallido de inicio de sesión", "Intento fallido de inicio de sesión")
        
        if intentos_fallidos >= 3:
            cursor.execute("UPDATE Usuarios SET cuenta_bloqueada = 1 WHERE usuario_id = ?", (usuario_id,))
            conn.commit()
            codigo_desbloqueo = random.randint(100000, 999999)
            session['codigo_desbloqueo'] = codigo_desbloqueo
            enviar_codigo_verificacion(correo, codigo_desbloqueo, "desbloqueo")
            mensaje = "Cuenta bloqueada por intentos fallidos."
            return manejar_respuesta(es_json, mensaje, url_for('solicitar_restablecimiento'))
        else:
            mensaje = "Credenciales incorrectas."
            return manejar_respuesta(es_json, mensaje)
    except Exception as e:
        print(f"Error al manejar intentos fallidos: {e}")
        return "Error al procesar los intentos fallidos.", 500
    finally:
        conn.close()





# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('nombre_usuario', None)
    return redirect(url_for('login'))

# Ruta para el index, donde se muestra el nombre del usuario si está loggeado
@app.route('/')
def index():
    nombre_usuario = session.get('nombre_usuario')
    return render_template('index.html', nombre_usuario=nombre_usuario)

#actualizar contrasena vencida

@app.route('/actualizar_contrasena', methods=['GET', 'POST'])
def actualizar_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']
        nueva_password = request.form['nueva_password']
        confirm_password = request.form['confirm_password']

        # Verificar que ambas contraseñas coincidan
        if nueva_password != confirm_password:
            flash("Las contraseñas no coinciden.")
            return redirect(url_for('actualizar_contrasena'))

        # Verificar que la nueva contraseña cumpla con los requisitos
        if (len(nueva_password) < 8 or len(nueva_password) > 14 or 
            not any(char.islower() for char in nueva_password) or 
            not any(char.isupper() for char in nueva_password) or 
            not any(char in "!@#$%^&*()-_+=" for char in nueva_password)):
            flash("La contraseña no cumple con los requisitos. Debe tener entre 8 y 14 caracteres, incluir al menos una letra mayúscula, una minúscula y un carácter especial.")
            return redirect(url_for('actualizar_contrasena'))

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)
        if conn is None:
            flash("Error al conectar con la base de datos.")
            return redirect(url_for('actualizar_contrasena'))

        try:
            cursor = conn.cursor()

            # Verificar si el correo existe en la base de datos
            query = "SELECT usuario_id, password_hash FROM Usuarios WHERE correo = ?"
            cursor.execute(query, (correo,))
            resultado = cursor.fetchone()

            if resultado:
                usuario_id = resultado[0]
                password_hash_actual = resultado[1]

                # Verificar si la nueva contraseña es igual a la anterior
                if check_password_hash(password_hash_actual, nueva_password):
                    flash("La nueva contraseña no puede ser igual a la anterior.")
                    return redirect(url_for('actualizar_contrasena'))

                # Generar el hash de la nueva contraseña
                nuevo_password_hash = generate_password_hash(nueva_password)
                fecha_actual = datetime.now().strftime('%Y-%m-%d')

                # Actualizar en la base de datos
                update_query = "UPDATE Usuarios SET password_hash = ?, fecha_registro = ? WHERE correo = ?"
                cursor.execute(update_query, (nuevo_password_hash, fecha_actual, correo))
                conn.commit()

                flash("Contraseña actualizada exitosamente.")
                return redirect(url_for('login'))
            else:
                flash("Correo no encontrado.")
                return redirect(url_for('actualizar_contrasena'))
        except pyodbc.Error as e:
            print(f"Error al actualizar la contraseña: {e}")
            flash("Error al actualizar la contraseña. Intenta de nuevo.")
            return redirect(url_for('actualizar_contrasena'))
        finally:
            conn.close()  # Asegurarse de cerrar la conexión

    # Mostrar la página de actualización de contraseña en caso de una solicitud GET
    return render_template('actualizar_contrasena.html')


# Implementación de la doble verificación y el envío de código de verificación
def generar_codigo_verificacion():
    return str(random.randint(100000, 999999))

# Función para enviar un correo de verificación
def enviar_codigo_verificacion(correo, codigo, tipo):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_USER
        mensaje['To'] = correo
        mensaje['Subject'] = 'Código de Verificación - RetroNintendo'

        if tipo == "login":
            cuerpo = f'Tu código de inicio de sesión es: {codigo}'
        elif tipo == "restablecimiento":
            cuerpo = f'Tu código de restablecimiento de contraseña es: {codigo}'
        elif tipo == "desbloqueo":
            cuerpo = f'Tu código para desbloquear la cuenta es: {codigo}'
        elif tipo == "actualizacion":
            cuerpo = f'Tu código para actualizar la contraseña es: {codigo}'
        else:
            cuerpo = f'Tu código de verificación es: {codigo}'

        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Envío de correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.ehlo()
            servidor.starttls()  # Iniciar la conexión TLS
            servidor.ehlo()
            servidor.login(EMAIL_USER, EMAIL_PASS)
            servidor.send_message(mensaje)
            print(f"Correo enviado exitosamente a {correo} con el código {codigo}.")
    except smtplib.SMTPException as e:
        print(f"Error al enviar el correo: {e}")
        flash(f"Error al enviar el correo: {e}. Por favor, inténtelo de nuevo.")

# Ruta para restablecer contraseña
@app.route('/restablecer', methods=['GET', 'POST'])
def restablecer():
    if request.method == 'POST':
        correo = request.form.get('correo')  # Usar .get para evitar KeyError si el campo está vacío
        if not correo:
            flash("Por favor, proporciona un correo válido.")
            return redirect(url_for('restablecer'))

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)
        if conn is None:
            flash("Error al conectar con la base de datos.")
            return redirect(url_for('restablecer'))

        try:
            cursor = conn.cursor()
            query = "SELECT usuario_id FROM Usuarios WHERE correo = ? AND cuenta_bloqueada = 1"
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()

            if usuario:
                session['usuario_id_temp'] = usuario[0]

                # Generar un código de desbloqueo y guardarlo en la sesión
                codigo_desbloqueo = random.randint(100000, 999999)
                session['codigo_desbloqueo'] = codigo_desbloqueo

                # Enviar el código de desbloqueo por correo
                enviar_codigo_verificacion(correo, codigo_desbloqueo, "desbloqueo")
                flash("Código de desbloqueo enviado a tu correo.")
                return redirect(url_for('verificar_desbloqueo'))
            else:
                flash("Correo no encontrado o la cuenta no está bloqueada.")
                return redirect(url_for('restablecer'))
        except Exception as e:
            print(f"Error al consultar la cuenta bloqueada: {e}")
            flash("Ocurrió un error al procesar la solicitud. Intenta nuevamente.")
            return redirect(url_for('restablecer'))
        finally:
            conn.close()  # Asegurarse de cerrar la conexión
    return render_template('restablecer.html')



# Ruta para verificar código de desbloqueo
@app.route('/verificar_desbloqueo', methods=['GET', 'POST'])
def verificar_desbloqueo():
    if request.method == 'POST':
        codigo_usuario = request.form.get('codigo')  # Usar .get para evitar KeyError
        codigo_desbloqueo = session.get('codigo_desbloqueo')

        if not codigo_usuario:
            flash("Por favor, ingresa el código de desbloqueo.")
            return redirect(url_for('verificar_desbloqueo'))

        if codigo_usuario == str(codigo_desbloqueo):
            usuario_id = session.pop('usuario_id_temp', None)
            if not usuario_id:
                flash("No se pudo identificar al usuario. Intenta nuevamente.")
                return redirect(url_for('restablecer'))

            # Conectar a la base de datos
            conn = get_db_connection(CONN_STR_PRINCIPAL)
            if conn is None:
                flash("Error al conectar con la base de datos.")
                return redirect(url_for('verificar_desbloqueo'))

            try:
                cursor = conn.cursor()
                # Desbloquear la cuenta y resetear intentos fallidos
                query = "UPDATE Usuarios SET intentos_fallidos = 0, cuenta_bloqueada = 0 WHERE usuario_id = ?"
                cursor.execute(query, (usuario_id,))
                conn.commit()

                # Registrar la acción en la auditoría
                registrar_auditoria(usuario_id, "Cuenta desbloqueada", "Cuenta desbloqueada exitosamente")
                session.pop('codigo_desbloqueo', None)  # Eliminar el código de desbloqueo de la sesión
                flash("Cuenta desbloqueada. Por favor, inicia sesión.")
                return redirect(url_for('login'))
            except Exception as e:
                print(f"Error al desbloquear la cuenta: {e}")
                flash("Error al desbloquear la cuenta. Intenta nuevamente.")
                return redirect(url_for('verificar_desbloqueo'))
            finally:
                conn.close()  # Asegurarse de cerrar la conexión
        else:
            flash("Código incorrecto. Intenta nuevamente.")
            return redirect(url_for('verificar_desbloqueo'))

    return render_template('verificar_desbloqueo.html')




# Ruta para verificar código de inicio de sesión
@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigo_usuario = request.form.get('codigo')  # Usar .get para evitar KeyError
        codigo_verificacion = session.get('codigo_verificacion')

        # Validar que se haya ingresado un código
        if not codigo_usuario:
            flash("Por favor, ingresa el código de verificación.")
            return redirect(url_for('verificar_codigo'))

        # Comparar el código ingresado con el almacenado en la sesión
        if codigo_usuario == str(codigo_verificacion):
            session.pop('codigo_verificacion', None)  # Eliminar el código de la sesión

            usuario_id_temp = session.pop('usuario_id_temp', None)
            if not usuario_id_temp:
                flash("No se pudo identificar al usuario. Intenta nuevamente.")
                return redirect(url_for('login'))

            # Conectar a la base de datos
            conn = get_db_connection(CONN_STR_PRINCIPAL)
            if conn is None:
                flash("Error al conectar con la base de datos.")
                return redirect(url_for('verificar_codigo'))

            try:
                cursor = conn.cursor()
                # Obtener el nombre del usuario con base en el usuario_id
                cursor.execute("SELECT nombre_usuario FROM Usuarios WHERE usuario_id = ?", (usuario_id_temp,))
                resultado = cursor.fetchone()

                if resultado:
                    session['usuario_id'] = usuario_id_temp
                    session['nombre_usuario'] = resultado[0]
                    flash("Inicio de sesión exitoso.")
                    return redirect(url_for('index'))
                else:
                    flash("No se pudo recuperar la información del usuario. Intenta nuevamente.")
                    return redirect(url_for('login'))
            except Exception as e:
                print(f"Error al verificar el código: {e}")
                flash("Error al verificar el código. Intenta nuevamente.")
                return redirect(url_for('verificar_codigo'))
            finally:
                conn.close()  # Asegurarse de cerrar la conexión
        else:
            flash("Código incorrecto. Intenta nuevamente.")
            return redirect(url_for('verificar_codigo'))

    return render_template('verificar_codigo.html')


##### Olvide mi contrasena

# Ruta para solicitar restablecimiento de contraseña
@app.route('/solicitar_restablecimiento', methods=['GET', 'POST'])
def solicitar_restablecimiento():
    if request.method == 'POST':
        correo = request.form.get('correo')  # Obtener el correo del formulario

        # Validar que el correo no esté vacío
        if not correo:
            flash("Por favor, proporciona un correo válido.")
            return redirect(url_for('solicitar_restablecimiento'))

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)
        if conn is None:
            flash("Error al conectar con la base de datos.")
            return redirect(url_for('solicitar_restablecimiento'))

        try:
            cursor = conn.cursor()
            query = "SELECT usuario_id FROM Usuarios WHERE correo = ?"
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()

            if usuario:
                session['usuario_id_reset'] = usuario[0]

                # Generar el código de restablecimiento
                codigo_reset = random.randint(100000, 999999)
                session['codigo_reset'] = codigo_reset

                # Enviar el correo con el código
                enviar_codigo_verificacion(correo, codigo_reset, "restablecimiento")
                print(f"Correo enviado exitosamente a {correo} con el código {codigo_reset}.")
                flash("Código de verificación enviado a tu correo.")
                return redirect(url_for('verificar_pregunta_seguridad'))
            else:
                flash("Correo no encontrado.")
                return redirect(url_for('solicitar_restablecimiento'))
        except Exception as e:
            print(f"Error al procesar la solicitud de restablecimiento: {e}")
            flash("Ocurrió un error al procesar la solicitud. Intenta nuevamente.")
            return redirect(url_for('solicitar_restablecimiento'))
        finally:
            conn.close()  # Asegurarse de cerrar la conexión
    return render_template('solicitar_restablecimiento.html')




# Nueva ruta para verificar la respuesta de seguridad
@app.route('/verificar_pregunta_seguridad', methods=['GET', 'POST'])
def verificar_pregunta_seguridad():
    if 'usuario_id_reset' not in session:
        flash("Primero solicita el restablecimiento de contraseña.")
        return redirect(url_for('solicitar_restablecimiento'))

    usuario_id = session.get('usuario_id_reset')

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        flash("Error al conectar con la base de datos.")
        return redirect(url_for('solicitar_restablecimiento'))

    try:
        cursor = conn.cursor()
        query = "SELECT respuesta1, respuesta2, respuesta3 FROM Usuarios WHERE usuario_id = ?"
        cursor.execute(query, (usuario_id,))
        respuestas = cursor.fetchone()

        if not respuestas:
            flash("No se encontraron preguntas de seguridad para este usuario.")
            return redirect(url_for('solicitar_restablecimiento'))

        # Lista de preguntas de seguridad
        preguntas = [
            "¿Cuál es tu color favorito?",
            "¿Cuál es tu juego favorito?",
            "¿Dónde vives?"
        ]

        if request.method == 'POST':
            respuesta_usuario = request.form.get('respuesta')
            pregunta_index = int(request.form.get('pregunta_index'))

            # Validar que los campos no estén vacíos
            if not respuesta_usuario:
                flash("Por favor, responde la pregunta.")
                return redirect(url_for('verificar_pregunta_seguridad'))

            # Verificar si la respuesta coincide
            if respuesta_usuario.strip().lower() == respuestas[pregunta_index].strip().lower():
                flash("Pregunta de seguridad verificada. Puedes continuar con el restablecimiento.")
                return redirect(url_for('verificar_codigo_restablecimiento'))
            else:
                flash("Respuesta incorrecta. Intenta nuevamente.")
                return redirect(url_for('verificar_pregunta_seguridad'))

        # Seleccionar aleatoriamente una pregunta de seguridad
        pregunta_index = random.randint(0, 2)
        pregunta_aleatoria = preguntas[pregunta_index]

        return render_template(
            'verificar_pregunta_seguridad.html',
            pregunta_aleatoria=pregunta_aleatoria,
            pregunta_index=pregunta_index
        )
    except Exception as e:
        print(f"Error al verificar la pregunta de seguridad: {e}")
        flash("Error al verificar la pregunta de seguridad. Intenta nuevamente.")
        return redirect(url_for('solicitar_restablecimiento'))
    finally:
        conn.close()  # Asegurarse de cerrar la conexión


# Ruta para actualizar la nueva contraseña después de la verificación
@app.route('/actualizar_nueva_contrasena', methods=['GET', 'POST'])
def actualizar_nueva_contrasena():
    if request.method == 'POST':
        nueva_password = request.form.get('nueva_password')
        confirm_password = request.form.get('confirm_password')

        # Verificar que ambas contraseñas coincidan
        if not nueva_password or not confirm_password:
            flash("Por favor, completa todos los campos.")
            return redirect(url_for('actualizar_nueva_contrasena'))

        if nueva_password != confirm_password:
            flash("Las contraseñas no coinciden.")
            return redirect(url_for('actualizar_nueva_contrasena'))

        # Validar requisitos de la contraseña
        if (len(nueva_password) < 8 or len(nueva_password) > 14 or 
            not any(char.isupper() for char in nueva_password) or 
            not any(char.islower() for char in nueva_password) or 
            not any(char.isdigit() for char in nueva_password) or 
            not any(char in "!@#$%^&*()-_+=" for char in nueva_password)):
            flash("La contraseña debe tener entre 8 y 14 caracteres, incluir al menos una letra mayúscula, una minúscula, un número y un carácter especial.")
            return redirect(url_for('actualizar_nueva_contrasena'))

        # Obtener usuario_id desde la sesión
        usuario_id = session.get('usuario_id_reset')
        if not usuario_id:
            flash("No se pudo identificar al usuario. Intenta nuevamente.")
            return redirect(url_for('solicitar_restablecimiento'))

        # Conectar a la base de datos
        conn = get_db_connection(CONN_STR_PRINCIPAL)
        if conn is None:
            flash("Error al conectar con la base de datos.")
            return redirect(url_for('actualizar_nueva_contrasena'))

        try:
            nuevo_password_hash = generate_password_hash(nueva_password)
            cursor = conn.cursor()

            # Actualizar la contraseña y resetear intentos fallidos y cuenta bloqueada
            query = """
                UPDATE Usuarios 
                SET password_hash = ?, intentos_fallidos = 0, cuenta_bloqueada = 0 
                WHERE usuario_id = ?
            """
            cursor.execute(query, (nuevo_password_hash, usuario_id))
            conn.commit()

            flash("Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.")

            # Limpiar variables de sesión
            session.pop('usuario_id_reset', None)
            session.pop('codigo_reset', None)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error al actualizar la contraseña: {e}")
            flash("Error al actualizar la contraseña. Intenta nuevamente.")
            return redirect(url_for('actualizar_nueva_contrasena'))
        finally:
            conn.close()  # Asegurar el cierre de la conexión

    return render_template('actualizar_nueva_contrasena.html')



def registrar_auditoria(usuario_id, tipo_evento, detalle=""):
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        print("Error al conectar con la base de datos para registrar la auditoría.")
        return

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO Auditoria (usuario_id, tipo_evento, fecha, detalle) 
            VALUES (?, ?, ?, ?)
        """
        fecha = datetime.now()
        cursor.execute(query, (usuario_id, tipo_evento, fecha, detalle))
        conn.commit()
        print(f"Auditoría registrada: Usuario {usuario_id}, Evento: {tipo_evento}")
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")
    finally:
        conn.close()  # Asegurarse de cerrar la conexión


# Ruta para la auditoría
@app.route('/auditoria')
def auditoria():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        flash("Error al conectar con la base de datos.")
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()

        # Consultar los usuarios y la auditoría
        query_usuarios = "SELECT usuario_id, nombre_usuario FROM Usuarios"
        cursor.execute(query_usuarios)
        usuarios = cursor.fetchall()

        query_auditoria = """
            SELECT a.usuario_id, u.nombre_usuario, a.tipo_evento, a.fecha, a.detalle
            FROM Auditoria a
            LEFT JOIN Usuarios u ON a.usuario_id = u.usuario_id
            ORDER BY a.fecha DESC
        """
        cursor.execute(query_auditoria)
        auditoria = cursor.fetchall()

        # Renderizar la plantilla con los datos
        return render_template('auditoria.html', usuarios=usuarios, auditoria=auditoria)
    except Exception as e:
        print(f"Error al consultar la auditoría: {e}")
        flash("Error al cargar los datos de auditoría. Intenta nuevamente.")
        return redirect(url_for('index'))
    finally:
        conn.close()  # Asegurarse de cerrar la conexión

# Ruta para verificar el código de restablecimiento de contraseña

@app.route('/verificar_codigo_restablecimiento', methods=['GET', 'POST'])
def verificar_codigo_restablecimiento():
    if request.method == 'POST':
        codigo_usuario = request.form['codigo']
        if 'codigo_reset' in session and codigo_usuario == str(session['codigo_reset']):
            flash("Código verificado. Puedes restablecer tu contraseña.")
            return redirect(url_for('actualizar_nueva_contrasena'))
        else:
            flash("Código incorrecto. Intenta de nuevo.")
            return redirect(url_for('verificar_codigo_restablecimiento'))

    return render_template('verificar_codigo_restablecimiento.html')




# Rutas para obtener las ubicaciones dinámicamente

@app.route('/get_provincias', methods=['GET'])
def get_provincias():
    pais = request.args.get('pais')

    # Validar que se proporcionó un país
    if not pais:
        return jsonify({"error": "El parámetro 'pais' es requerido."}), 400

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    try:
        cursor = conn.cursor()

        # Obtener todas las provincias del país seleccionado
        query = "SELECT DISTINCT provincia FROM Ubicaciones WHERE pais = ?"
        cursor.execute(query, pais)
        provincias = cursor.fetchall()

        # Crear una lista en formato JSON
        provincias_json = [{'provincia': row[0]} for row in provincias]
        return jsonify(provincias_json)
    except Exception as e:
        print(f"Error al obtener provincias: {e}")
        return jsonify({"error": "Ocurrió un error al obtener las provincias."}), 500
    finally:
        conn.close()  # Asegurar que la conexión se cierra

@app.route('/get_cantones', methods=['GET'])
def get_cantones():
    provincia = request.args.get('provincia')

    # Validar que se proporcionó una provincia
    if not provincia:
        return jsonify({"error": "El parámetro 'provincia' es requerido."}), 400

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    try:
        cursor = conn.cursor()

        # Obtener todos los cantones de la provincia seleccionada
        query = "SELECT DISTINCT canton FROM Ubicaciones WHERE provincia = ?"
        cursor.execute(query, (provincia,))
        cantones = cursor.fetchall()

        # Crear una lista en formato JSON
        cantones_json = [{'canton': row[0]} for row in cantones]
        return jsonify(cantones_json)
    except Exception as e:
        print(f"Error al obtener cantones: {e}")
        return jsonify({"error": "Ocurrió un error al obtener los cantones."}), 500
    finally:
        conn.close()  # Asegurar que la conexión se cierra


@app.route('/get_distritos', methods=['GET'])
def get_distritos():
    canton = request.args.get('canton')

    # Validar que se proporcionó un cantón
    if not canton:
        return jsonify({"error": "El parámetro 'canton' es requerido."}), 400

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    try:
        cursor = conn.cursor()

        # Obtener todos los distritos del cantón seleccionado
        query = "SELECT DISTINCT distrito FROM Ubicaciones WHERE canton = ?"
        cursor.execute(query, (canton,))
        distritos = cursor.fetchall()

        # Crear una lista en formato JSON
        distritos_json = [{'distrito': row[0]} for row in distritos]
        return jsonify(distritos_json)
    except Exception as e:
        print(f"Error al obtener distritos: {e}")
        return jsonify({"error": "Ocurrió un error al obtener los distritos."}), 500
    finally:
        conn.close()  # Asegurar que la conexión se cierra


# Ruta para ver los usuarios registrados y sus ubicaciones
@app.route('/ver_usuarios')
def ver_usuarios():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        flash("Error al conectar con la base de datos.")
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                u.usuario_id, 
                u.nombre_usuario, 
                u.correo, 
                ub.pais, 
                ub.provincia, 
                ub.canton, 
                ub.distrito
            FROM Usuarios u
            LEFT JOIN Ubicaciones ub ON u.ubicacion_id = ub.ubicacion_id
        """
        cursor.execute(query)
        usuarios = cursor.fetchall()

        # Renderizar la plantilla con los datos
        return render_template('ver_usuarios.html', usuarios=usuarios)
    except Exception as e:
        print(f"Ocurrió un error al obtener los usuarios: {e}")
        flash("Error al cargar los datos de usuarios. Intenta nuevamente.")
        return redirect(url_for('index'))
    finally:
        conn.close()  # Asegurar que la conexión se cierra



@app.route('/solicitudes_cotizacion')
def ver_solicitudes_cotizacion():
    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_PRINCIPAL)
    if conn is None:
        flash("Error al conectar con la base de datos.")
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()

        # Consultar las solicitudes de cotización
        query = """
            SELECT 
                cotizacion_id,
                usuario_id,
                total_estimado,
                direccion_entrega,
                email,
                fecha
            FROM SolicitudesCotizacion
            ORDER BY fecha DESC
        """
        cursor.execute(query)
        solicitudes = cursor.fetchall()

        # Renderizar el HTML y pasar las solicitudes a la plantilla
        return render_template('solicitudes_cotizacion.html', solicitudes=solicitudes)
    except Exception as e:
        print(f"Error al obtener las solicitudes de cotización: {e}")
        flash("Error al cargar las solicitudes de cotización. Intenta nuevamente.")
        return redirect(url_for('index'))
    finally:
        conn.close()  # Asegurar el cierre de la conexión

# Ruta al formulario de verificación de identificación
@app.route('/verificar_identificacion', methods=['GET', 'POST'])
def consultar_identificacion():
    resultado = None  # Inicializamos la variable de resultado como None
    if request.method == 'POST':
        identificacion = request.form.get('identificacion')
        if not identificacion:
            resultado = {"error": "Identificación es requerida"}
        else:
            # Enviar la solicitud GET al servidor TSE
            try:
                response = requests.get("http://127.0.0.1:5000/api/verificar_identificacion", params={"identificacion": identificacion})
                if response.status_code == 200:
                    resultado = response.json()
                elif response.status_code == 404:
                    resultado = {"existe": False, "mensaje": "Identificación no encontrada en una de las bases de datos"}
                else:
                    resultado = {"error": "Error en el servidor TSE"}
            except Exception as e:
                resultado = {"error": f"Error de conexión con el servidor TSE: {str(e)}"}

    # Renderizar el template de verificación y pasar el resultado
    return render_template('verificar_identificacion.html', resultado=resultado)





# Ruta para mostrar los videojuegos del proveedor externo
@app.route('/proveedor')
def mostrar_videojuegos_proveedor():
    try:
        # Hacer una solicitud GET al servidor del proveedor externo
        response = requests.get("http://127.0.0.1:5000/api/videojuegos_proveedor")
        videojuegos = response.json()
    except Exception as e:
        videojuegos = {"error": f"Error al conectar con el servidor del proveedor: {str(e)}"}

    # Renderizar el template y pasar los videojuegos
    return render_template('proveedor.html', videojuegos=videojuegos)




# Ruta para consultar el rastreo de paquetes
@app.route('/rastreo', methods=['GET', 'POST'])
def rastrear_paquete():
    rastreo_info = None
    if request.method == 'POST':
        codigo_paquete = request.form.get('codigo_paquete')
        
        try:
            # Solicitar la información de rastreo al servidor de rastreo externo
            response = requests.get(f"http://127.0.0.1:5000/api/rastreo_paquete/{codigo_paquete}")
            rastreo_info = response.json()
        except Exception as e:
            rastreo_info = {"error": f"Error de conexión: {str(e)}"}
    
    # Renderizar la página HTML de rastreo
    return render_template('rastreo.html', rastreo_info=rastreo_info)





#actualizar estado del paquete
@app.route('/actualizar_estado/<codigo_paquete>', methods=['GET', 'POST'])
def actualizar_estado(codigo_paquete):
    if request.method == 'POST':
        nuevo_estado = request.form['estado']
        nueva_ubicacion = request.form['ubicacion']
        
        # Crear una conexión específica para ServiciosExterno
        conn_servicios = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=ALE;"  # Asegúrate de que el nombre del servidor esté correcto
            "DATABASE=ServiciosExterno;"
            "Trusted_Connection=yes;"
        )
        cursor = conn_servicios.cursor()

        # Actualizar el estado y la ubicación en la base de datos ServiciosExterno
        cursor.execute("""
            UPDATE dbo.RastreoPaquetes  -- Asegúrate de especificar el esquema
            SET estado = ?, ubicacion_actual = ?, ultima_actualizacion = ?
            WHERE codigo_paquete = ?
        """, (nuevo_estado, nueva_ubicacion, datetime.now(), codigo_paquete))
        conn_servicios.commit()
        
        # Cerrar la conexión después de la actualización
        cursor.close()
        conn_servicios.close()

        return redirect(url_for('gestor_ordenes'))
    
    return render_template('actualizar_estado.html', codigo_paquete=codigo_paquete)






# Ruta para mostrar el tipo de cambio
@app.route('/tipo_cambio', methods=['GET'])
def tipo_cambio():
    try:
        response = requests.get("http://127.0.0.1:5000/api/tipo_cambio")
        tipo_cambio_data = response.json()
    except Exception as e:
        return jsonify({"error": f"Error al conectar con el servidor de tipo de cambio: {str(e)}"}), 500

    tipo_cambio_venta = tipo_cambio_data.get("tipo_cambio_venta", "No disponible")
    
    # Imprime el tipo de cambio para verificar
    print("Tipo de cambio recibido:", tipo_cambio_venta)

    return render_template('tipo_cambio.html', tipo_cambio=tipo_cambio_venta)


###########Nuevas conexiones


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



@app.route('/api/comparar_precios', methods=['GET'])
def comparar_precios():
    # Conectar a la base de datos principal y de servicios externos
    conn_inventario = get_db_connection(CONN_STR_PRINCIPAL)
    conn_competencia = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)

    if not conn_inventario or not conn_competencia:
        return jsonify({"error": "Error al conectar a una o ambas bases de datos."}), 500

    try:
        cursor_inventario = conn_inventario.cursor()
        cursor_competencia = conn_competencia.cursor()

        # Obtener los productos de la competencia
        query_competencia = "SELECT item_id, nombre_articulo, precio FROM ProveedorCompetencia"
        cursor_competencia.execute(query_competencia)
        competencia_items = cursor_competencia.fetchall()

        comparacion_precios = []

        # Comparar cada producto de la competencia con el inventario interno
        for item in competencia_items:
            item_id, nombre_articulo, precio_competencia = item

            # Buscar el precio del producto en el inventario interno
            query_inventario = "SELECT precio FROM Inventario WHERE nombre_articulo = ?"
            cursor_inventario.execute(query_inventario, (nombre_articulo,))
            inventario_item = cursor_inventario.fetchone()

            precio_retronintendo = inventario_item[0] if inventario_item else None

            # Agregar la comparación a la lista
            comparacion_precios.append({
                "nombre_articulo": nombre_articulo,
                "precio_competencia": precio_competencia,
                "precio_retronintendo": precio_retronintendo
            })

        return jsonify(comparacion_precios)
    except Exception as e:
        print(f"Error durante la comparación de precios: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        # Asegurar el cierre de conexiones
        if conn_inventario:
            conn_inventario.close()
        if conn_competencia:
            conn_competencia.close()




# Endpoint para procesar pagos con tarjeta
@app.route('/api/pago_tarjeta', methods=['POST'])
def pago_tarjeta():
    # Obtener los datos del cuerpo de la solicitud
    data = request.json

    # Validar que los datos necesarios estén presentes
    required_fields = ["numero_tarjeta", "fecha_vencimiento", "codigo_seguridad", "monto", "descripcion_comercio"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Datos incompletos. Por favor, proporciona todos los campos requeridos."}), 400

    # Asignar valores
    numero_tarjeta = data['numero_tarjeta']
    fecha_vencimiento = data['fecha_vencimiento']
    codigo_seguridad = data['codigo_seguridad']
    monto = data['monto']
    descripcion_comercio = data['descripcion_comercio']
    fecha_transaccion = datetime.now()

    # Conectar a la base de datos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos."}), 500

    try:
        cursor = conn.cursor()

        # Insertar el registro de pago en la base de datos
        query = """
            INSERT INTO PagosTarjeta (
                numero_tarjeta, 
                fecha_vencimiento, 
                codigo_seguridad, 
                monto, 
                descripcion_comercio, 
                fecha_transaccion
            ) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (numero_tarjeta, fecha_vencimiento, codigo_seguridad, monto, descripcion_comercio, fecha_transaccion))
        conn.commit()

        # Confirmación de pago exitosa
        return jsonify({"mensaje": "Pago procesado exitosamente"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al procesar el pago: {e}")
        return jsonify({"error": f"Error al procesar el pago: {str(e)}"}), 500
    finally:
        conn.close()  # Cerrar la conexión



# Ruta para agregar saldo a la tarjeta
@app.route('/api/agregar_saldo', methods=['POST'])
def agregar_saldo():
    data = request.json

    # Validar datos de entrada
    numero_tarjeta = data.get('numero_tarjeta')
    monto = data.get('monto')

    if not numero_tarjeta or not monto:
        return jsonify({"error": "Número de tarjeta y monto son requeridos"}), 400

    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()

        # Verificar si la tarjeta existe
        query_select = "SELECT saldo FROM Tarjetas WHERE numero_tarjeta = ?"
        cursor.execute(query_select, numero_tarjeta)
        tarjeta = cursor.fetchone()

        if not tarjeta:
            return jsonify({"error": "Tarjeta no encontrada"}), 404

        # Actualizar el saldo de la tarjeta
        saldo_actual = tarjeta[0]
        nuevo_saldo = saldo_actual + monto
        query_update = "UPDATE Tarjetas SET saldo = ? WHERE numero_tarjeta = ?"
        cursor.execute(query_update, (nuevo_saldo, numero_tarjeta))
        conn.commit()

        # Devolver respuesta exitosa
        return jsonify({"mensaje": f"Saldo agregado exitosamente. Nuevo saldo: {nuevo_saldo}"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al agregar saldo: {e}")
        return jsonify({"error": f"Error al agregar saldo: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# Ruta para procesar la compra y descontar saldo

@app.route('/api/procesar_compra', methods=['POST'])
def procesar_compra():
    # Obtener datos del cuerpo de la solicitud
    data = request.json
    numero_tarjeta = data.get('numero_tarjeta')
    fecha_vencimiento = data.get('fecha_vencimiento')  # En formato MM/YY (e.g., "12/25")
    codigo_seguridad = data.get('codigo_seguridad')
    monto = data.get('monto')

    # Validar que todos los campos sean proporcionados
    if not all([numero_tarjeta, fecha_vencimiento, codigo_seguridad, monto]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    try:
        monto = Decimal(monto)  # Convertir monto a Decimal para evitar errores
    except Exception:
        return jsonify({"error": "El monto debe ser un número válido"}), 400

    # Validar formato de la fecha de vencimiento
    try:
        fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, "%m/%y")
    except ValueError:
        return jsonify({"error": "Formato de fecha de vencimiento inválido. Use MM/YY"}), 400

    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()

        # Verificar si la tarjeta existe y si el código de seguridad coincide
        query_tarjeta = """
            SELECT saldo, codigo_seguridad, fecha_vencimiento
            FROM Tarjetas 
            WHERE numero_tarjeta = ?
        """
        cursor.execute(query_tarjeta, numero_tarjeta)
        tarjeta = cursor.fetchone()

        if not tarjeta:
            return jsonify({"error": "Tarjeta no encontrada"}), 404

        saldo_actual, codigo_seguridad_db, fecha_vencimiento_db = tarjeta

        # Validar código de seguridad
        if codigo_seguridad != codigo_seguridad_db:
            return jsonify({"error": "Código de seguridad incorrecto"}), 403

        # Validar fecha de vencimiento
        fecha_vencimiento_db_str = datetime.strptime(
            str(fecha_vencimiento_db), "%Y-%m-%d"
        ).strftime("%m/%y")

        if fecha_vencimiento != fecha_vencimiento_db_str:
            return jsonify({"error": "Fecha de vencimiento incorrecta"}), 403

        # Verificar si hay saldo suficiente
        if saldo_actual < monto:
            return jsonify({"error": "Saldo insuficiente"}), 400

        # Descontar el monto del saldo
        nuevo_saldo = saldo_actual - monto
        query_update = "UPDATE Tarjetas SET saldo = ? WHERE numero_tarjeta = ?"
        cursor.execute(query_update, (nuevo_saldo, numero_tarjeta))
        conn.commit()

        # Responder con el nuevo saldo
        return jsonify({"mensaje": "Compra procesada exitosamente", "nuevo_saldo": str(nuevo_saldo)}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error al procesar la compra: {e}")
        return jsonify({"error": f"Error al procesar la compra: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()





@app.route('/api/registrar_tarjeta', methods=['POST'])
def registrar_tarjeta():
    # Obtener los datos del cuerpo de la solicitud
    data = request.json
    
    numero_tarjeta = data.get('numero_tarjeta')
    fecha_vencimiento = data.get('fecha_vencimiento')  # Formato esperado: "MM/YY"
    codigo_seguridad = data.get('codigo_seguridad')
    saldo = data.get('saldo', 0.00)  # Saldo inicial opcional
    nombre_titular = data.get('nombre_titular')

    # Validar que todos los campos requeridos estén presentes
    if not all([numero_tarjeta, fecha_vencimiento, codigo_seguridad, nombre_titular]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    try:
        # Validar formato de fecha de vencimiento
        fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, "%m/%y")
    except ValueError:
        return jsonify({"error": "Formato de fecha de vencimiento inválido. Use MM/YY"}), 400

    # Convertir saldo a Decimal para evitar errores en cálculos posteriores
    try:
        saldo = Decimal(saldo)
    except Exception:
        return jsonify({"error": "El saldo debe ser un número válido"}), 400

    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()

        # Insertar la nueva tarjeta en la base de datos
        query = """
            INSERT INTO Tarjetas (numero_tarjeta, fecha_vencimiento, codigo_seguridad, saldo, nombre_titular)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, numero_tarjeta, fecha_vencimiento_dt, codigo_seguridad, saldo, nombre_titular)
        conn.commit()

        return jsonify({"mensaje": "Tarjeta registrada exitosamente"}), 201
    except Exception as e:
        conn.rollback()
        print(f"Error al registrar la tarjeta: {e}")
        return jsonify({"error": f"Error al registrar la tarjeta: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()







@app.route('/api/videojuegos_proveedor', methods=['GET'])
def obtener_videojuegos_proveedor():
    # Conectar a la base de datos de servicios externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()
        
        # Consultar los videojuegos del proveedor externo
        query = """
            SELECT juego_id, nombre_juego, precio, plataforma, stock_disponible 
            FROM VideojuegosProveedor
        """
        cursor.execute(query)
        videojuegos = cursor.fetchall()
        
        # Convertir los resultados en un formato JSON
        videojuegos_list = [
            {
                "juego_id": row[0],
                "nombre_juego": row[1],
                "precio": float(row[2]),  # Convertir a float para JSON
                "plataforma": row[3],
                "stock_disponible": row[4]
            }
            for row in videojuegos
        ]
        
        return jsonify(videojuegos_list), 200
    except Exception as e:
        print(f"Error al obtener videojuegos: {e}")
        return jsonify({"error": f"Error al obtener videojuegos: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/videojuegos_proveedor', methods=['POST'])
def agregar_videojuegos_proveedor():
    # Obtener los datos de la solicitud
    data = request.json

    # Validar que los datos recibidos sean una lista
    if not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de videojuegos"}), 400

    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()

        # Iterar sobre cada videojuego en la lista para insertarlo
        for videojuego in data:
            nombre_juego = videojuego.get('nombre_juego')
            precio = videojuego.get('precio')
            plataforma = videojuego.get('plataforma')
            stock_disponible = videojuego.get('stock_disponible', 0)

            # Validar campos obligatorios
            if not nombre_juego or precio is None:
                return jsonify({"error": "Cada videojuego debe tener un nombre y precio"}), 400

            # Insertar el videojuego en la base de datos
            query = """
                INSERT INTO VideojuegosProveedor (nombre_juego, precio, plataforma, stock_disponible)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (nombre_juego, precio, plataforma, stock_disponible))

        # Confirmar las inserciones
        conn.commit()
        return jsonify({"mensaje": "Videojuegos agregados exitosamente"}), 201
    except Exception as e:
        conn.rollback()  # Revertir cambios en caso de error
        print(f"Error al agregar videojuegos: {e}")
        return jsonify({"error": f"Error al agregar videojuegos: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()




# Ruta para obtener el estado de un paquete según el código
@app.route('/api/rastreo_paquete/<codigo_paquete>', methods=['GET'])
def obtener_estado_paquete(codigo_paquete):
    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()
        
        # Consultar la información del paquete en la base de datos
        query = """
            SELECT codigo_paquete, estado, ubicacion_actual, ultima_actualizacion 
            FROM RastreoPaquetes 
            WHERE codigo_paquete = ?
        """
        cursor.execute(query, (codigo_paquete,))
        paquete = cursor.fetchone()
        
        if not paquete:
            return jsonify({"error": "Paquete no encontrado"}), 404
        
        # Formatear la respuesta JSON
        paquete_info = {
            "codigo_paquete": paquete[0],
            "estado": paquete[1],
            "ubicacion_actual": paquete[2],
            "ultima_actualizacion": paquete[3].strftime('%Y-%m-%d %H:%M:%S') if paquete[3] else None
        }
        
        return jsonify(paquete_info), 200
    except Exception as e:
        print(f"Error al obtener estado del paquete: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()




@app.route('/api/actualizar_estado_paquete', methods=['POST'])
def actualizar_estado_paquete():
    # Obtener los datos del cuerpo de la solicitud
    data = request.json
    codigo_paquete = data.get('codigo_paquete')
    nuevo_estado = data.get('estado')
    nueva_ubicacion = data.get('ubicacion')

    # Validar los datos requeridos
    if not codigo_paquete or not nuevo_estado:
        return jsonify({"error": "Código de paquete y nuevo estado son necesarios"}), 400

    # Conectar a la base de datos de Servicios Externos
    conn = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
    if not conn:
        return jsonify({"error": "Error al conectar con la base de datos de servicios externos."}), 500

    try:
        cursor = conn.cursor()

        # Actualizar el estado y la ubicación del paquete
        query = """
            UPDATE RastreoPaquetes
            SET estado = ?, ubicacion_actual = ?, ultima_actualizacion = ?
            WHERE codigo_paquete = ?
        """
        cursor.execute(query, (nuevo_estado, nueva_ubicacion, datetime.now(), codigo_paquete))
        conn.commit()

        return jsonify({"mensaje": "Estado del paquete actualizado exitosamente"}), 200
    except Exception as e:
        print(f"Error al actualizar estado del paquete: {e}")
        conn.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()






# Ruta para obtener el tipo de cambio
from zeep import Client, Settings
from zeep.transports import Transport
import requests
from datetime import datetime

@app.route('/api/tipo_cambio', methods=['GET'])
def obtener_tipo_cambio():
    wsdl_url = 'https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx?WSDL'
    
    # Configuración del cliente
    session = requests.Session()
    transport = Transport(session=session)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)

    params = {
        'Indicador': '318',
        'FechaInicio': datetime.now().strftime('%d/%m/%Y'),
        'FechaFinal': datetime.now().strftime('%d/%m/%Y'),
        'Nombre': 'saenz2595@gmail.com',
        'SubNiveles': 'N',
        'CorreoElectronico': 'saenz2595@gmail.com',
        'Token': '59JGE1L5EZ'
    }
    
    try:
        # Llamar al servicio SOAP para obtener el tipo de cambio
        response = client.service.ObtenerIndicadoresEconomicos(**params)
        
        # Extraer el tipo de cambio de la estructura obtenida
        tipo_cambio_venta = response['INGC011_CAT_INDICADORECONOMIC'][0]['NUM_VALOR']
        
        # Devolver el tipo de cambio en formato JSON
        return jsonify({"tipo_cambio_venta": float(tipo_cambio_venta)})
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener el tipo de cambio: {str(e)}"}), 500





@app.route('/api/verificar_identificacion', methods=['GET'])
def verificar_identificacion():
    identificacion = request.args.get('identificacion')

    if not identificacion:
        return jsonify({"error": "Identificación es requerida"}), 400

    conn_retronintendo = None
    conn_servicios_externo = None

    try:
        # Conectar a la base de datos RetroNintendo y verificar en la tabla Usuarios
        conn_retronintendo = get_db_connection(CONN_STR_PRINCIPAL)
        if not conn_retronintendo:
            return jsonify({"error": "Error al conectar a la base de datos RetroNintendo."}), 500

        cursor_retronintendo = conn_retronintendo.cursor()
        query_retronintendo = "SELECT nombre_usuario FROM Usuarios WHERE identificacion = ?"
        cursor_retronintendo.execute(query_retronintendo, (identificacion,))
        usuario = cursor_retronintendo.fetchone()
        cursor_retronintendo.close()

        # Si la identificación no existe en RetroNintendo, devolver que no existe
        if not usuario:
            return jsonify({"existe": False, "mensaje": "Identificación no encontrada en RetroNintendo"}), 404

        # Conectar a la base de datos Servicios Externos y verificar en la tabla PersonasTSE
        conn_servicios_externo = get_db_connection(CONN_STR_SERVICIOS_EXTERNO)
        if not conn_servicios_externo:
            return jsonify({"error": "Error al conectar a la base de datos de servicios externos."}), 500

        cursor_servicios_externo = conn_servicios_externo.cursor()
        query_servicios_externo = "SELECT nombre FROM PersonasTSE WHERE identificacion = ?"
        cursor_servicios_externo.execute(query_servicios_externo, (identificacion,))
        persona_externa = cursor_servicios_externo.fetchone()
        cursor_servicios_externo.close()

        # Verificar si la identificación también existe en Servicios Externos
        if persona_externa:
            return jsonify({
                "existe": True,
                "nombre": usuario[0],
                "mensaje": "Identificación encontrada en ambas bases de datos"
            })
        else:
            return jsonify({
                "existe": False,
                "mensaje": "Identificación no encontrada en Servicios Externos"
            }), 404

    except Exception as e:
        print(f"Error al verificar la identificación: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

    finally:
        # Cierre seguro de las conexiones
        if conn_retronintendo:
            conn_retronintendo.close()
        if conn_servicios_externo:
            conn_servicios_externo.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
