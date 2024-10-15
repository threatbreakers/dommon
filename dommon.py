import os
import csv
import requests
from datetime import datetime

# Información del bot de Telegram
TOKEN = "TOKEN BOT TELEGRAM"
CHAT_ID = "CHAT ID CANAL"  # Reemplazar con el ID o username del canal

# URL del CSV a descargar
URL_CSV = "https://www.nic.cl/registry/Ultimos.do?t=1h&f=csv"

# Obtener el directorio donde está almacenado el script
directorio_script = os.path.dirname(os.path.abspath(__file__))

# Función para descargar el archivo CSV
def descargar_csv(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        nombre_archivo = f"ultimos_{fecha_actual}.csv"

        # Crear la ruta completa usando el directorio del script
        ruta_archivo = os.path.join(directorio_script, nombre_archivo)

        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(response.content)

        return ruta_archivo  # Devolver la ruta completa del archivo
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
        return None

# Función para leer el contenido de un archivo CSV
def leer_csv(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            return list(csv.reader(archivo))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_archivo}")
        return []

# Función para enviar mensajes a Telegram
def enviar_a_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Mensaje enviado a Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a Telegram: {e}")

# Función principal para gestionar la descarga, comparación y envío
def main():
    nombre_archivo_nuevo = descargar_csv(URL_CSV)
    if not nombre_archivo_nuevo:
        return

    # Comprobar si hay un archivo anterior
    archivos_csv = sorted([f for f in os.listdir(directorio_script) if f.startswith("ultimos_") and f.endswith(".csv")])

    if len(archivos_csv) < 2:
        print("No hay suficiente historial para realizar la comparación.")
        return

    archivo_anterior = archivos_csv[-2]

    # Leer archivos CSV
    contenido_nuevo = leer_csv(nombre_archivo_nuevo)
    contenido_anterior = leer_csv(os.path.join(directorio_script, archivo_anterior))

    # Comparar archivos y detectar líneas nuevas
    lineas_nuevas = [linea for linea in contenido_nuevo if linea not in contenido_anterior]

    # Enviar líneas nuevas a Telegram
    if lineas_nuevas:
        print(f"{len(lineas_nuevas)} Nuevos dominios encontrados.")
        for linea in lineas_nuevas:
            mensaje = f"Nuevo Dominio: {' '.join(linea)}"
            enviar_a_telegram(mensaje)
    else:
        print("No se encontraron dominios nuevos.")

if __name__ == "__main__":
    main()
