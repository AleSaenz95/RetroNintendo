import pyodbc
from datetime import datetime

# Configuración de conexión para ambas bases de datos
conn_retro_nintendo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ALE;"  
    "DATABASE=RetroNintendo;"
    "Trusted_Connection=yes;"
)

conn_servicios_externo = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ALE;"  
    "DATABASE=ServiciosExterno;"
    "Trusted_Connection=yes;"
)

def sincronizar_ordenes():
    cursor_retro = conn_retro_nintendo.cursor()
    cursor_servicios = conn_servicios_externo.cursor()

    try:
        # Seleccionar órdenes de tipo "Envío Express" de RetroNintendo
        cursor_retro.execute("SELECT orden_id, cliente_nombre, tipo_orden FROM Ordenes WHERE tipo_orden = 'Envío Express'")
        ordenes_express = cursor_retro.fetchall()

        for orden in ordenes_express:
            orden_id = orden.orden_id
            codigo_paquete = f"RN-{orden_id}"  # Genera un código de paquete basado en el ID de la orden
            estado_inicial = "En proceso"
            ubicacion_inicial = "Centro de distribución"

            # Verificar si la orden ya existe en la tabla RastreoPaquetes de ServiciosExterno
            cursor_servicios.execute("SELECT COUNT(*) FROM RastreoPaquetes WHERE codigo_paquete = ?", codigo_paquete)
            if cursor_servicios.fetchone()[0] == 0:
                # Insertar la orden en la tabla RastreoPaquetes de ServiciosExterno
                cursor_servicios.execute("""
                    INSERT INTO RastreoPaquetes (codigo_paquete, estado, ubicacion_actual, ultima_actualizacion)
                    VALUES (?, ?, ?, ?)
                """, (codigo_paquete, estado_inicial, ubicacion_inicial, datetime.now()))
                print(f"Orden {orden_id} sincronizada como paquete con código {codigo_paquete}.")
            else:
                print(f"Orden {orden_id} ya existe en el sistema de rastreo.")

        # Confirmar los cambios en ServiciosExterno
        conn_servicios_externo.commit()
        print("Sincronización completada.")
    
    except Exception as e:
        print(f"Error en la sincronización: {e}")
        conn_servicios_externo.rollback()
    
    finally:
        cursor_retro.close()
        cursor_servicios.close()

# Ejecutar la sincronización
sincronizar_ordenes()
