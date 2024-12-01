from flask import Flask, jsonify
from zeep import Client
from datetime import datetime
import os

app = Flask(__name__)

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

if __name__ == "__main__":
    # Cambia el puerto predeterminado según la lista de puertos
    port = int(os.environ.get("PORT", 5009))  # 5009 para servidor_tipo_cambio.py
    app.run(host="0.0.0.0", port=port)
