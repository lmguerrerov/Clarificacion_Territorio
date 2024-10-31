#!/usr/bin/env python
# coding: utf-8

# In[8]:


import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from math import sqrt
import pandas as pd
import requests
from PIL import Image, ImageTk
from io import BytesIO
import io
from pyproj import Proj, Transformer

# Función para calcular la distancia entre dos puntos en coordenadas nacionales
def distance(norte1, este1, norte2, este2):
    return sqrt((norte2 - norte1)**2 + (este2 - este1)**2)

# Función para descargar el archivo CSV desde Google Drive
def download_csv_from_drive(url):
    file_id = url.split('/')[-2]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(download_url)
    data = response.content.decode('utf-8')
    return pd.read_csv(io.StringIO(data), delimiter=';')

# Cargar los datos en un DataFrame
url = "https://drive.google.com/file/d/1YP96yxCFSNtt6U4bF2Mvmes4YywbFfls/view"
df = download_csv_from_drive(url)

# Verificar si las columnas 'Norte' y 'Este' existen en el DataFrame
if 'Norte' not in df.columns or 'Este' not in df.columns:
    raise KeyError("El DataFrame no contiene las columnas 'Norte' y 'Este'.")

# Función para encontrar las seis estaciones más cercanas
def find_nearest_stations(norte, este):
    df['Distancia'] = df.apply(lambda row: distance(norte, este, row['Norte'], row['Este']), axis=1)
    nearest_stations = df.nsmallest(6, 'Distancia')
    return nearest_stations

# Define el sistema de referencia de origen y destino
transformer = Transformer.from_crs("epsg:4326", "epsg:9377", always_xy=True)

# Función para convertir latitud/longitud a coordenadas nacionales
def latlon_to_norte_este(lat_grados, lat_minutos, lat_segundos, lon_grados, lon_minutos, lon_segundos, lat_dir, lon_dir):
    # Convierte grados, minutos, segundos a decimal
    lat = lat_grados + lat_minutos / 60 + lat_segundos / 3600
    lon = lon_grados + lon_minutos / 60 + lon_segundos / 3600
    
    # Aplica el signo según la dirección seleccionada
    if lat_dir == 'S':
        lat = -lat
    if lon_dir == 'W':
        lon = -lon
    
    # Realiza la conversión de coordenadas
    este, norte = transformer.transform(lon, lat)
    return norte, este

# Función para mostrar las estaciones más cercanas en una nueva ventana
def show_nearest_stations():
    def calculate_and_show():
        # Verificar si se usan coordenadas nacionales o latitud/longitud
        if lat_grados_entry.get() and long_grados_entry.get():
            lat_grados = float(lat_grados_entry.get().replace(',', '.'))
            lat_minutos = float(lat_minutos_entry.get().replace(',', '.'))
            lat_segundos = float(lat_segundos_entry.get().replace(',', '.'))
            lon_grados = float(long_grados_entry.get().replace(',', '.'))
            lon_minutos = float(long_minutos_entry.get().replace(',', '.'))
            lon_segundos = float(long_segundos_entry.get().replace(',', '.'))
            lat_dir = lat_dir_combobox.get()
            lon_dir = lon_dir_combobox.get()

            norte, este = latlon_to_norte_este(lat_grados, lat_minutos, lat_segundos, lon_grados, lon_minutos, lon_segundos, lat_dir, lon_dir)
        else:
            norte = float(norte_entry.get().replace(',', '.'))
            este = float(este_entry.get().replace(',', '.'))

        nearest_stations = find_nearest_stations(norte, este)
        
        # Limpiar el texto previo
        for widget in result_frame.winfo_children():
            widget.destroy()
        
        # Crear encabezados
        headers = ["ID", "Nombre Municipio", "Nombre Departamento", "Norte", "Este", "Distancia"]
        for i, header in enumerate(headers):
            header_label = tk.Label(result_frame, text=header, font=("Helvetica", 10, "bold"), bg="#f0f0f0", borderwidth=1, relief="solid")
            header_label.grid(row=0, column=i, sticky="nsew")

        # Llenar los datos de las estaciones más cercanas
        for row_index, row_data in enumerate(nearest_stations.itertuples(), start=1):
            for col_index, value in enumerate(row_data[1:], start=0):
                if col_index == 0:  # Suponiendo que el nombre de la estación está en la primera columna
                    station_name = value
                    url = f"https://www.colombiaenmapas.gov.co/?e=-70.73413803218989,4.446062377553575,-70.60178711055921,4.542923924561411,4686&b=igac&u=0&t=25&servicio=6&estacion={station_name}"
                    cell = tk.Label(result_frame, text=station_name, font=("Helvetica", 10), fg="blue", bg="#f0f0f0", borderwidth=1, relief="solid", cursor="hand2")
                    cell.bind("<Button-1>", lambda e, url=url: open_url(url))
                else:
                    cell = tk.Label(result_frame, text=value, font=("Helvetica", 10), bg="#f0f0f0", borderwidth=1, relief="solid")
                cell.grid(row=row_index, column=col_index, sticky="nsew")

        for i in range(len(headers)):
            result_frame.grid_columnconfigure(i, weight=1)

    def open_url(url):
        import webbrowser
        webbrowser.open_new(url)

    nearest_window = tk.Toplevel(root)
    nearest_window.title("Estaciones más cercanas")
    nearest_window.geometry("600x500")
    nearest_window.configure(bg="#f0f0f0")

    # Agregar la etiqueta con la información de diseño y contacto
    design_label = tk.Label(nearest_window, text="Diseñado por Luis Miguel Guerrero - Ing Topografico\nContacto: lmiguelguerrero@outlook.com", 
                            font=("Helvetica", 10), bg="#f0f0f0", justify="center")
    design_label.pack(pady=10)

    # Agregar instrucciones
    instructions = ("Vamos a calcular las estaciones IGAC más cercanas a su base.\n"
                    "Por favor ingrese la coordenada en Origen Nacional\n"
                    "o Latitud y Longitud (Grados, Minutos, Segundos).\n"
                    "Utilice el símbolo decimal: punto.")
    tk.Label(nearest_window, text=instructions, font=("Helvetica", 10), bg="#f0f0f0", justify="left").pack(pady=10)

    # Campos para coordenadas Norte y Este
    tk.Label(nearest_window, text="Ingrese su coordenada Norte:", font=("Helvetica", 10), bg="#f0f0f0").pack(pady=5)
    norte_entry = tk.Entry(nearest_window, font=("Helvetica", 10))
    norte_entry.pack(pady=5)

    tk.Label(nearest_window, text="Ingrese su coordenada Este:", font=("Helvetica", 10), bg="#f0f0f0").pack(pady=5)
    este_entry = tk.Entry(nearest_window, font=("Helvetica", 10))
    este_entry.pack(pady=5)

    # Crear un contenedor para Latitud
    lat_frame = tk.Frame(nearest_window, bg="#f0f0f0")
    lat_frame.pack(pady=5)

    tk.Label(lat_frame, text="Ingrese su Latitud (Grados, Minutos, Segundos):", font=("Helvetica", 10), bg="#f0f0f0").grid(row=0, column=0, columnspan=3)

    lat_grados_entry = tk.Entry(lat_frame, font=("Helvetica", 10), width=5)
    lat_grados_entry.grid(row=1, column=0, padx=2)
    lat_minutos_entry = tk.Entry(lat_frame, font=("Helvetica", 10), width=5)
    lat_minutos_entry.grid(row=1, column=1, padx=2)
    lat_segundos_entry = tk.Entry(lat_frame, font=("Helvetica", 10), width=5)
    lat_segundos_entry.grid(row=1, column=2, padx=2)

    lat_dir_combobox = ttk.Combobox(lat_frame, values=["N", "S"], font=("Helvetica", 10), width=3)
    lat_dir_combobox.grid(row=1, column=3, padx=5)
    lat_dir_combobox.current(0)  # Por defecto en "N"

    # Crear un contenedor para Longitud
    long_frame = tk.Frame(nearest_window, bg="#f0f0f0")
    long_frame.pack(pady=5)

    tk.Label(long_frame, text="Ingrese su Longitud (Grados, Minutos, Segundos):", font=("Helvetica", 10), bg="#f0f0f0").grid(row=0, column=0, columnspan=3)

    long_grados_entry = tk.Entry(long_frame, font=("Helvetica", 10), width=5)
    long_grados_entry.grid(row=1, column=0, padx=2)
    long_minutos_entry = tk.Entry(long_frame, font=("Helvetica", 10), width=5)
    long_minutos_entry.grid(row=1, column=1, padx=2)
    long_segundos_entry = tk.Entry(long_frame, font=("Helvetica", 10), width=5)
    long_segundos_entry.grid(row=1, column=2, padx=2)

    lon_dir_combobox = ttk.Combobox(long_frame, values=["E", "W"], font=("Helvetica", 10), width=3)
    lon_dir_combobox.grid(row=1, column=3, padx=5)
    lon_dir_combobox.current(1)  # Por defecto en "W"

    calculate_button = tk.Button(nearest_window, text="Calcular", command=calculate_and_show, font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=10, pady=5)
    calculate_button.pack(pady=10)

    result_frame = tk.Frame(nearest_window, bg="#f0f0f0")
    result_frame.pack(pady=10, fill="both", expand=True)





    
# Función para calcular el número de semana GPS, número de semana GPS y el día del año
def calculate_gps_week_number(date):
    date_format = "%d-%m-%Y"
    target_date = datetime.strptime(date, date_format)
    gps_start_date = datetime(1980, 1, 6)  # Fecha de inicio del sistema GPS
    days_since_start = (target_date - gps_start_date).days
    gps_week = days_since_start // 7  # Calcula el número de semana GPS
    gps_day_of_week = days_since_start % 7  # Calcula el día dentro de la semana GPS
    gps_week_number = gps_week * 10 + gps_day_of_week  # Calcula el número de semana GPS
    day_of_year = target_date.timetuple().tm_yday  # Calcula el día del año
    year = target_date.year  # Obtiene el año
    return gps_week, gps_week_number, day_of_year, year

# Función para verificar si una URL es accesible
def check_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Función para descargar archivos desde una URL
def download_file(url, local_path):
    try:
        response = requests.get(url, stream=True)
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except Exception as e:
        print(f"Error al descargar {url}: {e}")
        return False

# Función para descargar las efemérides desde las URLs proporcionadas
def download_efemerides(date, folder_path):
    gps_week, gps_week_number, day_of_year, year = calculate_gps_week_number(date)

    # URLs basadas en el patrón proporcionado
    precise_url = f"http://lox.ucsd.edu/pub/products/{gps_week}/JAX0MGXFIN_{year}{day_of_year:03d}0000_01D_05M_ORB.SP3.gz"
    rapid_url = f"http://lox.ucsd.edu/pub/products/{gps_week}/igr{gps_week_number}.sp3.Z"

    precise_file = os.path.basename(precise_url)
    rapid_file = os.path.basename(rapid_url)

    files_downloaded = []
    files_not_available = []

    for url, label in [(precise_url, 'Precisas'), (rapid_url, 'Rápidas')]:
        local_path = os.path.join(folder_path, os.path.basename(url))
        if check_url(url):
            if download_file(url, local_path):
                files_downloaded.append((label, os.path.basename(local_path)))
            else:
                files_not_available.append(label)
        else:
            files_not_available.append(label)

    message = "Efemérides descargadas:\n"
    if files_downloaded:
        precise_files = [f for label, f in files_downloaded if label == 'Precisas']
        rapid_files = [f for label, f in files_downloaded if label == 'Rápidas']

        if precise_files:
            message += f"Precisas: {', '.join(precise_files)}\n"
        if rapid_files:
            message += f"Rápidas: {', '.join(rapid_files)}\n"

    if files_not_available:
        if 'Precisas' in files_not_available:
            message += "Las efemérides precisas no han sido cargadas al servidor.\n"
        if 'Rápidas' in files_not_available:
            message += "Las efemérides rápidas no han sido cargadas al servidor.\n"

    message += "\nConfío en que este programa le será de gran utilidad y cumpla con sus expectativas."

    # Mostrar el mensaje en una nueva ventana
    show_result_window(message)

# Función que inicia el proceso de descarga
def start_download():
    date = date_entry.get()  # Obtiene la fecha ingresada por el usuario
    # Abre un cuadro de diálogo para seleccionar la carpeta de guardado del archivo
    folder_path = filedialog.askdirectory()
    if folder_path:
        download_efemerides(date, folder_path)  # Llama a la función para descargar las efemérides

# Función para mostrar la ventana de resultados sin el QR
def show_result_window(message):
    result_window = tk.Toplevel(root)
    result_window.title("Resultado de la Descarga")
    result_window.geometry("400x300")
    result_window.configure(bg="#f0f0f0")

    message_label = tk.Label(result_window, text=message, font=("Helvetica", 10), bg="#f0f0f0", justify="left", wraplength=380)
    message_label.pack(pady=10)

    close_button = tk.Button(result_window, text="Cerrar", command=result_window.destroy, font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=10, pady=5)
    close_button.pack(pady=20)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Descargar Efemérides GNSS")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Título
title_label = tk.Label(root, text="Descargar Efemérides GNSS", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# Etiqueta y campo de entrada para la fecha
date_label = tk.Label(root, text="Ingrese la fecha (DD-MM-YYYY):", font=("Helvetica", 12), bg="#f0f0f0")
date_label.pack(pady=5)
date_entry = tk.Entry(root, font=("Helvetica", 12))
date_entry.pack(pady=5)

# Botón para iniciar la descarga
download_button = tk.Button(root, text="Descargar", command=start_download, font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
download_button.pack(pady=20)

# Botón para mostrar la ventana de estaciones cercanas
nearest_button = tk.Button(root, text="Estaciones Cercanas", command=show_nearest_stations, font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
nearest_button.pack(pady=20)

# Etiqueta con el nombre y título
footer_label = tk.Label(root, text="Miguel Guerrero Ing Topográfico UD", font=("Arial", 8), bg="#f0f0f0")
footer_label.pack(side="bottom", pady=10)

# Inicia el bucle principal de la interfaz gráfica
root.mainloop()


# In[ ]:




