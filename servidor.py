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





import pyodbc

# Cadena de conexión para la base de datos principal
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"  # Asegúrate de usar el controlador correcto
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

# Cadena de conexión para la base de datos de servicios externos
conn_str_servicios_externo = (
    "DRIVER={ODBC Driver 17 for SQL Server};"  # Asegúrate de usar el controlador correcto
    "SERVER=tiusr3pl.cuc-carrera-ti.ac.cr;"
    "DATABASE=tiusr3pl_RetroNintendo_SE;"
    "UID=tiusr3pl66;"
    "PWD=LpsLt5Awx&nb8$b2;"
)

# Función para conectar a la base de datos principal
def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        print("Conexión exitosa a la base de datos principal.")
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos principal: {e}")
        return None

# Intentar conexión a la base de datos de servicios externos
try:
    conn_servicios_externo = pyodbc.connect(conn_str_servicios_externo)
    print("Conexión exitosa a la base de datos de servicios externos.")
except pyodbc.Error as e:
    conn_servicios_externo = None
    print(f"Error al conectar a la base de datos de servicios externos: {e}")

# Probar conexión a la base de datos principal
try:
    conn = pyodbc.connect(conn_str)
    print("Conexión exitosa a la base de datos principal.")
except pyodbc.Error as e:
    conn = None
    print(f"Error en la conexión a la base de datos principal: {e}")






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
    cursor = conn.cursor()
    query = "SELECT nombre_juego, resena FROM Resenas"
    cursor.execute(query)
    reseñas = cursor.fetchall()

    return render_template('ver_resenas.html', reseñas=reseñas)

# Ruta para recibir y guardar un mensaje (página de contacto)
@app.route('/enviar-mensaje', methods=['GET', 'POST'])
def enviar_mensaje():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']  # Nuevo campo correo
        mensaje = request.form['mensaje']

        # Guardar el mensaje en la base de datos
        cursor = conn.cursor()
        query = "INSERT INTO Contactos (nombre, correo, mensaje) VALUES (?, ?, ?)"
        cursor.execute(query, (nombre, correo, mensaje))
        conn.commit()

        return redirect('/ver-mensajes')
    return render_template('recibir_mensaje.html')

# Ruta para ver los mensajes guardados
@app.route('/ver-mensajes')
def ver_mensajes():
    cursor = conn.cursor()
    query = "SELECT nombre, correo, mensaje FROM Contactos"
    cursor.execute(query)
    mensajes = cursor.fetchall()

    return render_template('ver_mensajes.html', mensajes=mensajes)


# Ruta para ver los juegos del catálogo
@app.route('/catalogo')
def catalogo():
    cursor = conn.cursor()
    query = "SELECT item_id, nombre_articulo, descripcion, precio, cantidad_disponible FROM Inventario"
    cursor.execute(query)
    articulos = cursor.fetchall()

    return render_template('catalogo.html', articulos=articulos)

# Ruta para vista del producto
@app.route('/producto/<int:item_id>')
def detalle_producto(item_id):
    cursor = conn.cursor()
    query = "SELECT item_id, nombre_articulo, descripcion, precio, cantidad_disponible, imagen FROM Inventario WHERE item_id = ?"
    cursor.execute(query, item_id)
    producto = cursor.fetchone()

    return render_template('detalle_producto.html', producto=producto)

############ Sección de Órdenes ###################

# Ruta para el formulario de compra desde el catálogo
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

        # Llamar al endpoint interno para procesar el pago
        payload = {
            "numero_tarjeta": numero_tarjeta,
            "fecha_vencimiento": fecha_vencimiento,
            "codigo_seguridad": codigo_seguridad,
            "monto": total,
            "descripcion_comercio": "Compra en RetroNintendo"
        }

        response = requests.post("http://127.0.0.1:5000/procesar_compra", data=payload)
        response_data = response.json()

        # Verificar si el pago fue exitoso
        if response.status_code == 200:
            # Continuar con el registro de la orden si el pago es exitoso
            cursor = conn.cursor()
            query_orden = "INSERT INTO Ordenes (cliente_nombre, tipo_orden, total, fecha, producto_nombre) VALUES (?, ?, ?, GETDATE(), ?)"
            cursor.execute(query_orden, (cliente_nombre, tipo_orden, total, producto_nombre))

            # Obtener el ID de la orden recién insertada
            orden_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            # Reducir la cantidad disponible en 1 en el inventario
            cursor.execute("UPDATE Inventario SET cantidad_disponible = cantidad_disponible - 1 WHERE nombre_articulo = ?", producto_nombre)

            # Llamar al procedimiento almacenado para insertar en ReporteVentas
            cursor.execute("EXEC InsertarEnReporteVentas ?, ?, ?, ?", producto_nombre, 1, total, orden_id)

            # Si el tipo de orden es Envío Express, insertar en PedidosExpress
            if tipo_orden == "Envío Express":
                direccion_entrega = request.form['direccion_entrega']
                estado_entrega = "En proceso"
                cursor.execute("EXEC InsertarPedidoExpress ?, ?, ?, ?", cliente_nombre, direccion_entrega, estado_entrega, orden_id)

            # Guardar los cambios en la base de datos
            conn.commit()
            return redirect('/gestor_ordenes')
        else:
            # Si el pago falla, mostrar el error
            return f"Error en el pago: {response_data.get('error', 'Error desconocido')}"

    # Obtener el producto seleccionado
    item_id = request.args.get('item_id')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_articulo, precio FROM Inventario WHERE item_id = ?", item_id)
    producto = cursor.fetchone()
    producto_nombre = producto[0]
    producto_precio = producto[1]

    return render_template('comprar.html', producto_nombre=producto_nombre, producto_precio=producto_precio)


# Ruta para el gestor de órdenes
@app.route('/gestor_ordenes')
def gestor_ordenes():
    cursor = conn.cursor()
    query = """
        SELECT orden_id, cliente_nombre, producto_nombre, tipo_orden, total 
        FROM Ordenes
    """
    cursor.execute(query)
    ordenes = cursor.fetchall()

    # Añadir el código de rastreo para las órdenes de tipo "Envío Express"
    ordenes_con_rastreo = []
    for orden in ordenes:
        codigo_rastreo = f"RN-{orden.orden_id}" if orden.tipo_orden == "Envío Express" else ""
        ordenes_con_rastreo.append({
            "orden_id": orden.orden_id,
            "cliente_nombre": orden.cliente_nombre,
            "producto_nombre": orden.producto_nombre,
            "tipo_orden": orden.tipo_orden,
            "total": orden.total,
            "codigo_rastreo": codigo_rastreo
        })

    return render_template('gestor_ordenes.html', ordenes=ordenes_con_rastreo)



# Ruta para ver detalles de una orden
@app.route('/ver_orden/<int:orden_id>')
def ver_orden(orden_id):
    cursor = conn.cursor()
    query = "SELECT orden_id, cliente_nombre, tipo_orden, total, fecha FROM Ordenes WHERE orden_id = ?"
    cursor.execute(query, orden_id)
    orden = cursor.fetchone()

    return render_template('ver_orden.html', orden=orden)

# Ruta para procesar una orden (cambiar estado a procesado)
@app.route('/procesar_orden/<int:orden_id>')
def procesar_orden(orden_id):
    cursor = conn.cursor()
    query = "UPDATE Ordenes SET estado='Procesado' WHERE orden_id = ?"
    cursor.execute(query, orden_id)
    conn.commit()

    return redirect('/gestor_ordenes')


########### Reporte###############
@app.route('/reporte_ventas')
def reporte_ventas():
    # Consultar los datos de la tabla de ReporteVentas
    cursor = conn.cursor()
    query = "SELECT producto, SUM(cantidad_vendida) as total_vendido, SUM(ingresos) as total_ingresos FROM ReporteVentas GROUP BY producto"
    cursor.execute(query)
    ventas = cursor.fetchall()

    # Preparar los datos para el gráfico
    productos = [venta[0] for venta in ventas]
    cantidades = [venta[1] for venta in ventas]
    ingresos = [venta[2] for venta in ventas]

    return render_template('reporte_ventas.html', productos=productos, cantidades=cantidades, ingresos=ingresos)

###################Pedidos express####

@app.route('/pedidos_express')
def pedidos_express():
    cursor = conn.cursor()
    query = """
        SELECT express_order_id, cliente_nombre, direccion_entrega, estado_entrega, fecha, quien_recibe
        FROM PedidosExpress
    """
    cursor.execute(query)
    pedidos = cursor.fetchall()

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
            SELECT envio_id FROM Envios WHERE item_id = (
                SELECT item_id FROM PedidosExpress WHERE express_order_id = ?
            )
        )
    """
    cursor.execute(query_envios, (quien_recibe, express_order_id))

    conn.commit()

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

        cursor = conn.cursor()
        query = "SELECT usuario_id, nombre_usuario, password_hash, intentos_fallidos, cuenta_bloqueada, fecha_registro FROM Usuarios WHERE correo = ?"
        cursor.execute(query, correo)
        usuario = cursor.fetchone()

        if usuario:
            usuario_id, nombre_usuario, password_hash, intentos_fallidos, cuenta_bloqueada, fecha_registro = usuario
            
            # Convertir fecha_registro a datetime.date si es una cadena
            if isinstance(fecha_registro, str):
                fecha_registro = datetime.strptime(fecha_registro, '%Y-%m-%d').date()
            
            # Verificar si la cuenta está bloqueada
            if cuenta_bloqueada:
                mensaje = "Cuenta bloqueada. Verifique su correo para desbloquear."
                if request.is_json:
                    return jsonify(success=False, message=mensaje)
                else:
                    flash(mensaje)
                    return redirect(url_for('solicitar_restablecimiento'))
            
            # Calcular si la contraseña tiene más de 90 días
            fecha_vencimiento = fecha_registro + timedelta(days=90)
            if date.today() > fecha_vencimiento:
                codigo_actualizacion = random.randint(100000, 999999)
                session['codigo_actualizacion'] = codigo_actualizacion
                session['usuario_id_reset'] = usuario_id
                
                enviar_codigo_verificacion(correo, codigo_actualizacion, "actualizacion")
                
                mensaje = "Tu contraseña ha expirado. Te hemos enviado un código de verificación para actualizarla."
                if request.is_json:
                    return jsonify(success=False, message=mensaje)
                else:
                    flash(mensaje)
                    return redirect(url_for('verificar_codigo_actualizacion'))

            # Verificar la contraseña
            if check_password_hash(password_hash, password):
                codigo_verificacion = random.randint(100000, 999999)
                session['codigo_verificacion'] = codigo_verificacion
                session['usuario_id_temp'] = usuario_id
                enviar_codigo_verificacion(correo, codigo_verificacion, "login")
                
                registrar_auditoria(usuario_id, "Inicio de sesión", "Usuario inició sesión con éxito")

                mensaje = "Código de verificación enviado a tu correo."
                if request.is_json:
                    return jsonify(success=True)
                else:
                    flash(mensaje)
                    return redirect(url_for('verificar_codigo'))
            else:
                # Manejo de intentos fallidos
                intentos_fallidos = (intentos_fallidos or 0) + 1
                query = "UPDATE Usuarios SET intentos_fallidos = ? WHERE usuario_id = ?"
                cursor.execute(query, (intentos_fallidos, usuario_id))
                conn.commit()

                registrar_auditoria(usuario_id, "Intento fallido de inicio de sesión", "Intento fallido de inicio de sesión")
              
                if intentos_fallidos >= 3:
                    query = "UPDATE Usuarios SET cuenta_bloqueada = 1 WHERE usuario_id = ?"
                    cursor.execute(query, usuario_id)
                    conn.commit()
                    mensaje = "Cuenta bloqueada por intentos fallidos."
                    
                    codigo_desbloqueo = random.randint(100000, 999999)
                    session['codigo_desbloqueo'] = codigo_desbloqueo
                    enviar_codigo_verificacion(correo, codigo_desbloqueo, "desbloqueo")

                    if request.is_json:
                        return jsonify(success=False, message=mensaje)
                    else:
                        flash(mensaje)
                        return redirect(url_for('solicitar_restablecimiento'))
                else:
                    mensaje = "Credenciales incorrectas."
                    if request.is_json:
                        return jsonify(success=False, message=mensaje)
                    else:
                        flash(mensaje)
        else:
            mensaje = "Usuario no encontrado."
            if request.is_json:
                return jsonify(success=False, message=mensaje)
            else:
                flash(mensaje)

    return render_template('login.html')




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
        if len(nueva_password) < 8 or len(nueva_password) > 14 or not any(char.islower() for char in nueva_password) or not any(char.isupper() for char in nueva_password) or not any(char in "!@#$%^&*()-_+=" for char in nueva_password):
            flash("La contraseña no cumple con los requisitos.")
            return redirect(url_for('actualizar_contrasena'))

        cursor = conn.cursor()

        # Verificar si el correo existe en la base de datos
        query = "SELECT usuario_id, password_hash FROM Usuarios WHERE correo = ?"
        cursor.execute(query, correo)
        resultado = cursor.fetchone()

        if resultado:
            usuario_id = resultado[0]
            password_hash_actual = resultado[1]

            # Verificar si la nueva contraseña es igual a la anterior
            if check_password_hash(password_hash_actual, nueva_password):
                flash("La nueva contraseña no puede ser igual a la anterior.")
                return redirect(url_for('actualizar_contrasena'))

            # Generar el hash de la nueva contraseña y formatear la fecha actual
            nuevo_password_hash = generate_password_hash(nueva_password)
            fecha_actual = datetime.now().strftime('%Y-%m-%d')

            try:
                # Actualizar en la base de datos usando el correo
                update_query = "UPDATE Usuarios SET password_hash = ?, fecha_registro = ? WHERE correo = ?"
                cursor.execute(update_query, (nuevo_password_hash, fecha_actual, correo))
                conn.commit()  # Confirmar los cambios

                flash("Contraseña actualizada exitosamente.")
                return redirect(url_for('login'))

            except pyodbc.Error as e:
                # Capturar y mostrar el error
                print(f"Error al actualizar la contraseña: {e}")
                flash("Error al actualizar la contraseña. Intenta de nuevo.")
                conn.rollback()  # Revertir cambios en caso de error
                return redirect(url_for('actualizar_contrasena'))

        else:
            flash("Correo no encontrado.")
            return redirect(url_for('actualizar_contrasena'))

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
        correo = request.form.get('correo')  # Cambia a .get para evitar KeyError
        if not correo:
            flash("Por favor, proporciona un correo válido.")
            return render_template('restablecer.html')

        cursor = conn.cursor()
        query = "SELECT usuario_id FROM Usuarios WHERE correo = ? AND cuenta_bloqueada = 1"
        cursor.execute(query, correo)
        usuario = cursor.fetchone()

        if usuario:
            session['usuario_id_temp'] = usuario[0]
            codigo_desbloqueo = random.randint(100000, 999999)
            session['codigo_desbloqueo'] = codigo_desbloqueo
            enviar_codigo_verificacion(correo, codigo_desbloqueo, "desbloqueo")
            flash("Código de desbloqueo enviado a tu correo.")
            return redirect(url_for('verificar_desbloqueo'))
        else:
            flash("Correo no encontrado o cuenta no está bloqueada.")
    
    return render_template('restablecer.html')



# Ruta para verificar código de desbloqueo
@app.route('/verificar_desbloqueo', methods=['GET', 'POST'])
def verificar_desbloqueo():
    if request.method == 'POST':
        codigo_usuario = request.form['codigo']
        if codigo_usuario == str(session.get('codigo_desbloqueo')):
            usuario_id = session.pop('usuario_id_temp', None)
            cursor = conn.cursor()
            query = "UPDATE Usuarios SET intentos_fallidos = 0, cuenta_bloqueada = 0 WHERE usuario_id = ?"
            cursor.execute(query, usuario_id)
            conn.commit()
            registrar_auditoria(usuario_id, "Cuenta desbloqueada", "Cuenta desbloqueada") #auditoria
            session.pop('codigo_desbloqueo', None)
            flash("Cuenta desbloqueada. Por favor, inicia sesión.")
            return redirect(url_for('login'))
        else:
            flash("Código incorrecto. Intenta de nuevo.")
    return render_template('verificar_desbloqueo.html')




# Ruta para verificar código de inicio de sesión
@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigo_usuario = request.form['codigo']
        if codigo_usuario == str(session.get('codigo_verificacion')):
            session.pop('codigo_verificacion', None)
            session['usuario_id'] = session.pop('usuario_id_temp', None)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_usuario FROM Usuarios WHERE usuario_id = ?", session['usuario_id'])
            session['nombre_usuario'] = cursor.fetchone()[0]
            flash("Inicio de sesión exitoso.")
            return redirect(url_for('index'))
        else:
            flash("Código incorrecto. Intenta de nuevo.")
    return render_template('verificar_codigo.html')


##### Olvide mi contrasena

# Ruta para solicitar restablecimiento de contraseña
@app.route('/solicitar_restablecimiento', methods=['GET', 'POST'])
def solicitar_restablecimiento():
    if request.method == 'POST':
        correo = request.form.get('correo')  # Obtener el correo del formulario
        cursor = conn.cursor()
        query = "SELECT usuario_id FROM Usuarios WHERE correo = ?"
        cursor.execute(query, correo)
        usuario = cursor.fetchone()

        if usuario:
            session['usuario_id_reset'] = usuario[0]
            
            # Generar el código de restablecimiento una sola vez
            codigo_reset = random.randint(100000, 999999)
            session['codigo_reset'] = codigo_reset
            
            # Enviar el correo con el código
            try:
                enviar_codigo_verificacion(correo, codigo_reset, "restablecimiento")
                print(f"Correo enviado exitosamente a {correo} con el código {codigo_reset}.")
                flash("Código de verificación enviado a tu correo.")
                return redirect(url_for('verificar_pregunta_seguridad'))
            except Exception as e:
                print(f"Error al enviar el correo: {e}")
                flash("Hubo un problema al enviar el correo. Inténtalo más tarde.")
                return redirect(url_for('solicitar_restablecimiento'))
        else:
            flash("Correo no encontrado.")
            return redirect(url_for('solicitar_restablecimiento'))

    return render_template('solicitar_restablecimiento.html')



# Nueva ruta para verificar la respuesta de seguridad

import random

@app.route('/verificar_pregunta_seguridad', methods=['GET', 'POST'])
def verificar_pregunta_seguridad():
    if 'usuario_id_reset' not in session:
        flash("Primero solicita el restablecimiento de contraseña.")
        return redirect(url_for('solicitar_restablecimiento'))

    usuario_id = session.get('usuario_id_reset')
    cursor = conn.cursor()
    query = "SELECT respuesta1, respuesta2, respuesta3 FROM Usuarios WHERE usuario_id = ?"
    cursor.execute(query, usuario_id)
    respuestas = cursor.fetchone()

    if not respuestas:
        flash("No se encontraron preguntas de seguridad para este usuario.")
        return redirect(url_for('solicitar_restablecimiento'))

    preguntas = [
        "¿Cuál es tu color favorito?",
        "¿Cuál es tu juego favorito?",
        "¿Dónde vives?"
    ]

    if request.method == 'POST':
        respuesta_usuario = request.form.get('respuesta')
        pregunta_index = int(request.form.get('pregunta_index'))

        # Verificar que la respuesta sea correcta
        if respuesta_usuario.lower() == respuestas[pregunta_index].lower():
            flash("Pregunta de seguridad verificada. Puedes continuar con el restablecimiento.")
            return redirect(url_for('verificar_codigo_restablecimiento'))
        else:
            flash("Respuesta incorrecta. Intenta nuevamente.")
            return redirect(url_for('verificar_pregunta_seguridad'))

    # Seleccionar aleatoriamente una pregunta de seguridad
    pregunta_index = random.randint(0, 2)
    pregunta_aleatoria = preguntas[pregunta_index]

    return render_template('verificar_pregunta_seguridad.html', pregunta_aleatoria=pregunta_aleatoria, pregunta_index=pregunta_index)



# Ruta para actualizar la nueva contraseña después de la verificación
@app.route('/actualizar_nueva_contrasena', methods=['GET', 'POST'])
def actualizar_nueva_contrasena():
    if request.method == 'POST':
        nueva_password = request.form['nueva_password']
        confirm_password = request.form['confirm_password']

        # Verificar que ambas contraseñas coincidan
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

        # Usar el usuario_id de la sesión
        usuario_id = session.get('usuario_id_reset')
        if usuario_id:
            nuevo_password_hash = generate_password_hash(nueva_password)
            cursor = conn.cursor()

            # Actualizar la contraseña y resetear intentos fallidos y cuenta_bloqueada
            query = "UPDATE Usuarios SET password_hash = ?, intentos_fallidos = 0, cuenta_bloqueada = 0 WHERE usuario_id = ?"
            cursor.execute(query, (nuevo_password_hash, usuario_id))
            conn.commit()

            flash("Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.")
            # Limpiar variables de sesión
            session.pop('usuario_id_reset', None)
            session.pop('preguntas_respuestas', None)
            session.pop('pregunta_index', None)
            session.pop('codigo_reset', None)
            return redirect(url_for('login'))
        else:
            flash("Error al restablecer la contraseña. Intenta nuevamente.")
    return render_template('actualizar_nueva_contrasena.html')


def registrar_auditoria(usuario_id, tipo_evento, detalle=""):
    cursor = conn.cursor()
    query = "INSERT INTO Auditoria (usuario_id, tipo_evento, fecha, detalle) VALUES (?, ?, ?, ?)"
    fecha = datetime.now()
    cursor.execute(query, (usuario_id, tipo_evento, fecha, detalle))
    conn.commit()


# Ruta para la auditoría
@app.route('/auditoria')
def auditoria():
    # Consultar los campos requeridos de la tabla de usuarios y auditoría
    cursor = conn.cursor()
    cursor.execute("SELECT usuario_id, nombre_usuario FROM Usuarios")  # Solo traemos los campos necesarios
    usuarios = cursor.fetchall()
    cursor.execute("SELECT * FROM Auditoria")
    auditoria = cursor.fetchall()

    return render_template('auditoria.html', usuarios=usuarios, auditoria=auditoria)

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
    cursor = conn.cursor()

    # Obtener todas las provincias del país seleccionado
    query = "SELECT DISTINCT provincia FROM Ubicaciones WHERE pais = ?"
    cursor.execute(query, pais)
    provincias = cursor.fetchall()

    # Crear una lista para enviar en formato JSON
    provincias_json = [{'provincia': row[0]} for row in provincias]
    return jsonify(provincias_json)

@app.route('/get_cantones', methods=['GET'])
def get_cantones():
    provincia = request.args.get('provincia')
    cursor = conn.cursor()

    # Obtener todos los cantones de la provincia seleccionada
    query = "SELECT DISTINCT canton FROM Ubicaciones WHERE provincia = ?"
    cursor.execute(query, provincia)
    cantones = cursor.fetchall()

    # Crear una lista para enviar en formato JSON
    cantones_json = [{'canton': row[0]} for row in cantones]
    return jsonify(cantones_json)

@app.route('/get_distritos', methods=['GET'])
def get_distritos():
    canton = request.args.get('canton')
    cursor = conn.cursor()

    # Obtener todos los distritos del cantón seleccionado
    query = "SELECT DISTINCT distrito FROM Ubicaciones WHERE canton = ?"
    cursor.execute(query, canton)
    distritos = cursor.fetchall()

    # Crear una lista para enviar en formato JSON
    distritos_json = [{'distrito': row[0]} for row in distritos]
    return jsonify(distritos_json)


# Ruta para ver los usuarios registrados y sus ubicaciones
@app.route('/ver_usuarios')
def ver_usuarios():
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
            LEFT JOIN Ubicaciones ub ON u.pais_id = ub.ubicacion_id
        """
        cursor.execute(query)
        usuarios = cursor.fetchall()

        return render_template('ver_usuarios.html', usuarios=usuarios)
    except Exception as e:
        print(f"Ocurrió un error al obtener los usuarios: {e}")
        return "Error al cargar los usuarios."




@app.route('/solicitudes_cotizacion')
def ver_solicitudes_cotizacion():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SolicitudesCotizacion")
    solicitudes = cursor.fetchall()
    cursor.close()

    # Renderizar el HTML y pasar las solicitudes a la plantilla
    return render_template('solicitudes_cotizacion.html', solicitudes=solicitudes)



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
                response = requests.get("http://127.0.0.1:5002/api/verificar_identificacion", params={"identificacion": identificacion})
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
        response = requests.get("http://127.0.0.1:5003/api/videojuegos_proveedor")
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
            response = requests.get(f"http://127.0.0.1:5111/api/rastreo_paquete/{codigo_paquete}")
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
        response = requests.get("http://127.0.0.1:5009/api/tipo_cambio")
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
    try:
        cursor_competencia = conn_servicios_externo.cursor()
        cursor_inventario = conn_str.cursor()

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





# Ruta para obtener el tipo de cambio
@app.route('/api/tipo_cambio', methods=['GET'])
def obtener_tipo_cambio():
    wsdl_url = 'https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx?WSDL'
    client = Client(wsdl=wsdl_url)
    
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
        
        # Extraer el tipo de cambio de acuerdo con la estructura obtenida
        tipo_cambio_venta = response['_value_1']['_value_1'][0]['INGC011_CAT_INDICADORECONOMIC']['NUM_VALOR']
        
        # Devolver el tipo de cambio en formato JSON
        return jsonify({"tipo_cambio_venta": float(tipo_cambio_venta)})
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener el tipo de cambio: {str(e)}"}), 500




# Ruta para verificar la identificación en ambas bases de datos usando GET
@app.route('/api/verificar_identificacion', methods=['GET'])
def verificar_identificacion():
    identificacion = request.args.get('identificacion')
    
    if not identificacion:
        return jsonify({"error": "Identificación es requerida"}), 400

    try:
        # Conectar a la base de datos RetroNintendo y verificar en la tabla Usuarios
        conn_retronintendo = pyodbc.connect(conn_str)
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


if __name__ == "__main__":
    # Cambia el puerto predeterminado según la lista de puertos
    port = int(os.environ.get("PORT", 5000))  # 5000 para servidor.py
    app.run(host="0.0.0.0", port=port)