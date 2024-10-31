#!/usr/bin/env python
# coding: utf-8

# In[4]:


import sys
import geopandas as gpd
import folium
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit, QComboBox

sys.setrecursionlimit(5000)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Consulta de Resguardos - Realizado por: Ing Luis Miguel Guerrero - lmiguelguerrero@outlook.com")
        self.setGeometry(300, 300, 600, 600)

        # Layout principal
        layout = QVBoxLayout()

        # Etiqueta para la selección del shapefile
        self.label = QLabel("Selecciona el archivo shapefile (.shp):")
        layout.addWidget(self.label)

        # Botón para seleccionar el shapefile
        self.btn_select_file = QPushButton("Seleccionar Shapefile")
        self.btn_select_file.clicked.connect(self.select_shapefile)
        layout.addWidget(self.btn_select_file)

        # ComboBox para seleccionar la columna del nombre
        self.combo_nombre = QComboBox(self)
        layout.addWidget(QLabel("Selecciona la columna correspondiente al nombre de la comunidad:"))
        layout.addWidget(self.combo_nombre)

        # ComboBox para seleccionar la columna del código de municipio
        self.combo_municipio = QComboBox(self)
        layout.addWidget(QLabel("Selecciona la columna correspondiente a los municipios:"))
        layout.addWidget(self.combo_municipio)

        # ComboBox para seleccionar la columna del código de departamento
        self.combo_departamento = QComboBox(self)
        layout.addWidget(QLabel("Selecciona la columna correspondiente a los departamentos:"))
        layout.addWidget(self.combo_departamento)

        # ComboBox para seleccionar la columna del ID del resguardo
        self.combo_id = QComboBox(self)
        layout.addWidget(QLabel("Selecciona la columna para los ID del territorio:"))
        layout.addWidget(self.combo_id)

        # Campo de texto para ingresar el nombre del resguardo
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Ingresa el nombre del Territorio Etnico")
        layout.addWidget(self.name_input)

        # Botón para realizar la búsqueda por nombre
        self.btn_search_name = QPushButton("Buscar Territorio por Nombre")
        self.btn_search_name.clicked.connect(self.search_resguardo_por_nombre)
        layout.addWidget(self.btn_search_name)

        # Campo de texto para ingresar el código del municipio
        self.municipio_input = QLineEdit(self)
        self.municipio_input.setPlaceholderText("Ingresa el Municipio")
        layout.addWidget(self.municipio_input)

        # Botón para realizar la búsqueda por código de municipio
        self.btn_search_municipio = QPushButton("Busca los territorios que se encuentren en el Municipio")
        self.btn_search_municipio.clicked.connect(self.search_resguardos_por_municipio)
        layout.addWidget(self.btn_search_municipio)

        # Campo de texto para ingresar el código del departamento
        self.departamento_input = QLineEdit(self)
        self.departamento_input.setPlaceholderText("Ingresa el Departamento")
        layout.addWidget(self.departamento_input)

        # Botón para realizar la búsqueda por código de departamento
        self.btn_search_departamento = QPushButton("Busca los territorios que se encuentren en el Departamento")
        self.btn_search_departamento.clicked.connect(self.search_resguardos_por_departamento)
        layout.addWidget(self.btn_search_departamento)

        # Campo de texto para ingresar el ID del resguardo
        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("Ingresa el ID del resguardo")
        layout.addWidget(self.id_input)

        # Botón para generar Mapa por ID
        self.btn_generar_mapa = QPushButton("Generar Mapa por ID")
        self.btn_generar_mapa.clicked.connect(self.generar_mapa_por_id)
        layout.addWidget(self.btn_generar_mapa)

        # Botón para generar Mapa por Municipio
        self.btn_generar_mapa_municipio = QPushButton("Generar Mapa por Municipio")
        self.btn_generar_mapa_municipio.clicked.connect(self.generar_mapa_resguardos_municipio)
        layout.addWidget(self.btn_generar_mapa_municipio)

        # Botón para generar Mapa por Departamento
        self.btn_generar_mapa_departamento = QPushButton("Generar Mapa por Departamento")
        self.btn_generar_mapa_departamento.clicked.connect(self.generar_mapa_resguardos_departamento)
        layout.addWidget(self.btn_generar_mapa_departamento)

        # Resultado de la búsqueda en un QTextEdit seleccionable
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Widget principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_shapefile(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Shapefile", "", "Shapefiles (*.shp);;Todos los archivos (*)", options=options)
        if file:
            self.shapefile_path = file
            self.label.setText(f"Shapefile seleccionado: {file}")

            # Cargar el shapefile y actualizar los ComboBox con las columnas disponibles
            gdf = gpd.read_file(self.shapefile_path)
            columns = gdf.columns.tolist()
            self.combo_nombre.addItems(columns)
            self.combo_municipio.addItems(columns)
            self.combo_departamento.addItems(columns)
            self.combo_id.addItems(columns)
        else:
            self.shapefile_path = None

    def search_resguardo_por_nombre(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        nombre_columna = self.combo_nombre.currentText()
        nombre_resguardo = self.name_input.text().strip()
        if not nombre_resguardo:
            QMessageBox.warning(self, "Error", "Ingresa el nombre del resguardo.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Filtrar por nombre
            resultados = gdf[gdf[nombre_columna].str.contains(nombre_resguardo, case=False, na=False)]

            if resultados.empty:
                self.result_text.setText(f"No se encontraron resguardos similares a '{nombre_resguardo}'.")
            else:
                resguardos_texto = "\n\n".join([f"Resguardo: {row[nombre_columna]}\n" +
                                                "\n".join([f"{key}: {value}" for key, value in row.drop(['geometry'], errors='ignore').items()])
                                                for idx, row in resultados.iterrows()])
                self.result_text.setText(f"Resguardos similares a '{nombre_resguardo}':\n{resguardos_texto}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

    def search_resguardos_por_municipio(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        municipio_columna = self.combo_municipio.currentText()
        codigo_municipio = self.municipio_input.text().strip()
        if not codigo_municipio:
            QMessageBox.warning(self, "Error", "Ingresa el código del municipio.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Asegurarse de que el código de municipio sea tratado como cadena y se comparen adecuadamente
            gdf[municipio_columna] = gdf[municipio_columna].astype(str).str.strip()

            resultados = gdf[gdf[municipio_columna] == codigo_municipio]

            if resultados.empty:
                self.result_text.setText(f"No se encontraron resguardos en el municipio con código '{codigo_municipio}'.")
            else:
                resguardos_texto = "\n\n".join([f"Resguardo: {row[self.combo_nombre.currentText()]}\n" +
                                                "\n".join([f"{key}: {value}" for key, value in row.drop(['geometry'], errors='ignore').items()])
                                                for idx, row in resultados.iterrows()])
                self.result_text.setText(f"Resguardos en el municipio con código '{codigo_municipio}':\n{resguardos_texto}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

    def search_resguardos_por_departamento(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        departamento_columna = self.combo_departamento.currentText()
        codigo_departamento = self.departamento_input.text().strip()
        if not codigo_departamento:
            QMessageBox.warning(self, "Error", "Ingresa el código del departamento.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Asegurarse de que el código de departamento sea tratado como cadena y se comparen adecuadamente
            gdf[departamento_columna] = gdf[departamento_columna].astype(str).str.strip()

            resultados = gdf[gdf[departamento_columna] == codigo_departamento]

            if resultados.empty:
                self.result_text.setText(f"No se encontraron resguardos en el departamento con código '{codigo_departamento}'.")
            else:
                resguardos_texto = "\n\n".join([f"Resguardo: {row[self.combo_nombre.currentText()]}\n" +
                                                "\n".join([f"{key}: {value}" for key, value in row.drop(['geometry'], errors='ignore').items()])
                                                for idx, row in resultados.iterrows()])
                self.result_text.setText(f"Resguardos en el departamento con código '{codigo_departamento}':\n{resguardos_texto}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

    def generar_mapa_por_id(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        id_columna = self.combo_id.currentText()
        id_resguardo = self.id_input.text().strip()
        if not id_resguardo:
            QMessageBox.warning(self, "Error", "Ingresa el ID del resguardo.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Reproyectar el GeoDataFrame a WGS84 (EPSG:4326) para folium
            gdf = gdf.to_crs(epsg=4326)

            # Filtrar el resguardo seleccionado por ID, pero manteniendo todas las columnas
            resguardo_seleccionado = gdf[gdf[id_columna] == id_resguardo]

            if resguardo_seleccionado.empty:
                QMessageBox.warning(self, "Error", f"No se encontró ningún resguardo con ID '{id_resguardo}'.")
            else:
                # Crear mapa centrado en el centroide del polígono
                centroid = resguardo_seleccionado.geometry.centroid.iloc[0]
                mapa = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)

                # Añadir polígono al mapa con un popup que muestra los atributos
                for _, row in resguardo_seleccionado.iterrows():
                    info = f"<b>{id_columna}:</b> {row[id_columna]}<br>"
                    info += "<br>".join([f"<b>{col}:</b> {row[col]}" for col in resguardo_seleccionado.columns if col != 'geometry'])
                    
                    folium.GeoJson(
                        row['geometry'],
                        popup=folium.Popup(info, max_width=300),
                    ).add_to(mapa)

                # Guardar mapa en archivo HTML
                map_path = f"Mapa_Resguardo_{id_resguardo}.html"
                mapa.save(map_path)

                # Abrir el mapa en el navegador
                webbrowser.open(map_path)

                self.result_text.setText(f"Mapa generado correctamente. Abierto en el navegador.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

    def generar_mapa_resguardos_municipio(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        municipio_columna = self.combo_municipio.currentText()
        codigo_municipio = self.municipio_input.text().strip()
        if not codigo_municipio:
            QMessageBox.warning(self, "Error", "Ingresa el código del municipio.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Filtrar los resguardos por el código del municipio
            resguardos_municipio = gdf[gdf[municipio_columna] == codigo_municipio]

            if resguardos_municipio.empty:
                QMessageBox.information(self, "Sin resultados", "No se encontraron resguardos en el municipio seleccionado.")
                return

            # Reproyectar el GeoDataFrame a WGS84 (EPSG:4326) para folium
            resguardos_municipio = resguardos_municipio.to_crs(epsg=4326)

            # Crear mapa centrado en el centroide del conjunto de polígonos
            centroid = resguardos_municipio.geometry.centroid.unary_union.centroid
            mapa = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)

            # Añadir polígonos al mapa con un popup que muestra los atributos
            for _, row in resguardos_municipio.iterrows():
                info = f"<b>{self.combo_nombre.currentText()}:</b> {row[self.combo_nombre.currentText()]}<br>"
                info += f"<b>{municipio_columna}:</b> {row[municipio_columna]}<br>"
                info += "<br>".join([f"<b>{col}:</b> {row[col]}" for col in resguardos_municipio.columns if col != 'geometry'])
                
                folium.GeoJson(
                    row['geometry'],
                    popup=folium.Popup(info, max_width=300),
                ).add_to(mapa)

            # Guardar mapa en archivo HTML
            map_path = f"Mapa_Resguardos_Municipio_{codigo_municipio}.html"
            mapa.save(map_path)

            # Abrir el mapa en el navegador
            webbrowser.open(map_path)

            self.result_text.setText(f"Mapa generado correctamente. Abierto en el navegador.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

    def generar_mapa_resguardos_departamento(self):
        if not hasattr(self, 'shapefile_path') or not self.shapefile_path:
            QMessageBox.warning(self, "Error", "Primero debes seleccionar un archivo shapefile.")
            return

        departamento_columna = self.combo_departamento.currentText()
        codigo_departamento = self.departamento_input.text().strip()
        if not codigo_departamento:
            QMessageBox.warning(self, "Error", "Ingresa el código del departamento.")
            return

        try:
            gdf = gpd.read_file(self.shapefile_path)

            # Filtrar los resguardos por el código del departamento
            resguardos_departamento = gdf[gdf[departamento_columna] == codigo_departamento]

            if resguardos_departamento.empty:
                QMessageBox.information(self, "Sin resultados", "No se encontraron resguardos en el departamento seleccionado.")
                return

            # Reproyectar el GeoDataFrame a WGS84 (EPSG:4326) para folium
            resguardos_departamento = resguardos_departamento.to_crs(epsg=4326)

            # Crear mapa centrado en el centroide del conjunto de polígonos
            centroid = resguardos_departamento.geometry.centroid.unary_union.centroid
            mapa = folium.Map(location=[centroid.y, centroid.x], zoom_start=10)

            # Añadir polígonos al mapa con un popup que muestra los atributos
            for _, row in resguardos_departamento.iterrows():
                info = f"<b>{self.combo_nombre.currentText()}:</b> {row[self.combo_nombre.currentText()]}<br>"
                info += f"<b>{departamento_columna}:</b> {row[departamento_columna]}<br>"
                info += "<br>".join([f"<b>{col}:</b> {row[col]}" for col in resguardos_departamento.columns if col != 'geometry'])
                
                folium.GeoJson(
                    row['geometry'],
                    popup=folium.Popup(info, max_width=300),
                ).add_to(mapa)

            # Guardar mapa en archivo HTML
            map_path = f"Mapa_Resguardos_Departamento_{codigo_departamento}.html"
            mapa.save(map_path)

            # Abrir el mapa en el navegador
            webbrowser.open(map_path)

            self.result_text.setText(f"Mapa generado correctamente. Abierto en el navegador.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el shapefile:\n{e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


# In[ ]:




