import subprocess

# Lista de servidores con sus puertos únicos
servidores = [
    "python servidor.py --port 5000",
    "python servidor_proveedor_externo.py --port 5003",
    "python servidor_pagos.py --port 5001",
    "python servidor_proveedor_competencia.py --port 5005",
    "python servidor_rastreo.py --port 5111",  # Puerto actualizado
    "python servidor_tipo_cambio.py --port 5009",
    "python servidor_tse.py --port 5002",
    "python RetroNintendo.py --port 4000",
    "python servidor_comparar_precios.py --port 5011"
]

# Ejecutar cada servidor en paralelo
procesos = []
for servidor in servidores:
    procesos.append(subprocess.Popen(servidor, shell=True))

# Esperar a que todos los procesos terminen
for proceso in procesos:
    proceso.communicate()
