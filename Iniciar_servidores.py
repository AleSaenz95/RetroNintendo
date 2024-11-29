import subprocess

# Lista de servidores a ejecutar
servidores = [
    "python servidor.py",
    "python servidor_proveedor_externo.py",
    "python servidor_pagos.py",
    "python servidor_proveedor_competencia.py",
    "python servidor_rastreo.py",
    "python servidor_tipo_cambio.py",
    "python servidor_tse.py",
    "python RetroNintendo.py" ,
    "python servidor_comparar_precios.py"
]

# Ejecutar cada servidor en paralelo
procesos = []
for servidor in servidores:
    procesos.append(subprocess.Popen(servidor, shell=True))

# Esperar a que todos los procesos terminen
for proceso in procesos:
    proceso.communicate()
