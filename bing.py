import time
import random
import os
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

EDGE_DRIVER_PATH = r"C:\edgedriver_win64\msedgedriver.exe"  
HISTORIAL_PATH = "busquedas_usadas.txt"

def obtener_palabras_api(cantidad):
    url = f"https://random-word-api.herokuapp.com/word?number={cantidad}"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            print("Error al obtener palabras de la API:", respuesta.status_code)
            return []
    except Exception as e:
        print("Error en la conexión con la API:", e)
        return []

# Cargar historial
if os.path.exists(HISTORIAL_PATH):
    with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
        ya_usados = set(line.strip() for line in f.readlines())
else:
    ya_usados = set()

# Obtener nuevas palabras
palabras_aleatorias = []
intentos = 0

while len(palabras_aleatorias) < 45 and intentos < 10:
    nuevas = obtener_palabras_api(50)
    nuevas_filtradas = [p for p in nuevas if p not in ya_usados]
    palabras_aleatorias.extend(nuevas_filtradas)
    palabras_aleatorias = list(set(palabras_aleatorias))  # Quitar duplicados
    intentos += 1

palabras_aleatorias = palabras_aleatorias[:45]

if len(palabras_aleatorias) < 45:
    print(f"No se pudieron obtener suficientes palabras únicas. Se obtuvieron {len(palabras_aleatorias)}.")
    exit()

# Configurar navegador
options = Options()
options.use_chromium = True
options.add_argument("--start-maximized")

driver = webdriver.Edge(service=EdgeService(executable_path=EDGE_DRIVER_PATH), options=options)

try:
    for i, consulta in enumerate(palabras_aleatorias):
        driver.get("https://www.bing.com/")
        time.sleep(2)

        caja_busqueda = driver.find_element(By.NAME, "q")
        caja_busqueda.clear()
        caja_busqueda.send_keys(consulta)
        caja_busqueda.submit()

        print(f"[{i+1}/45] Buscando: {consulta}")
        time.sleep(random.randint(3, 6))

except Exception as e:
    print("Ocurrió un error:", e)

finally:
    driver.quit()
    with open(HISTORIAL_PATH, "a", encoding="utf-8") as f:
        for palabra in palabras_aleatorias:
            f.write(palabra + "\n")
