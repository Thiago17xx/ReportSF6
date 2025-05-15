from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import tempfile
import os

def crear_grafico(H2O_ppmw, H20_Pc, SO2, SF6, H20_ppmv):
    fig, ax = plt.subplots(figsize=(6, 6))

    # Datos para el gráfico de burbujas
    x = np.array([H2O_ppmw])  # PPMW
    y = np.array([H20_Pc])    # Punto de Rocío (°C)
    size = np.array([100])    # Tamaño de la burbuja (fijo por ahora)
    
    # Crear el gráfico de burbujas
    ax.scatter(x, y, s=size, color='blue', alpha=0.6, edgecolors="w", linewidth=2)

    # Añadir las líneas de límite
    ax.axhline(y=-36, color='r', linestyle='--', label='Límite Pcº <= -36')
    ax.axvline(x=25, color='g', linestyle='--', label='Límite PPMW <= 25')

    # Etiquetas y título
    ax.set_title('Gráfico de Burbuja: PPMW vs Punto de Rocío (Pcº)', fontsize=12)
    ax.set_xlabel('H2O (ppmw)', fontsize=10)
    ax.set_ylabel('Punto de Rocío (Pcº)', fontsize=10)
    ax.legend()

    # Guardar el gráfico en un archivo temporal
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_img.name, format='png')
    plt.close(fig)

    return temp_img.name

class PDF(FPDF):
    def header(self):
        self.image('static/logolds.jpg', x=10, y=3, w=20)
        self.set_font('Arial', 'B', 14)
        self.cell(200, 10, 'Reporte de Análisis SF6', ln=True, align='C')
         # Línea horizontal (separador)
        self.set_line_width(0.5)  # grosor línea
        self.line(10, 24, 200, 24)  # de x=10 a x=200 a altura y=35
        self.set_y(24)
        
    def agregar_datos_generales(self, datos):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Datos Generales', ln=True)
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'FECHA: {datos["FECHA"]}', ln=True)
        self.cell(0, 10, f'SET: {datos["SET"]}', ln=True)
        self.cell(0, 10, f'CIRCUITO: {datos["CIRCUITO"]}', ln=True)
        self.cell(0, 10, f'Fase: {datos["Fase"]}', ln=True)
        self.cell(0, 10, f'EQUIPO: {datos["EQUIPO"]}', ln=True)
        self.ln(1)

    def agregar_datos_medidos(self, datos):
        self.set_font('Arial', 'B', 12)
        self.ln(10)
        self.cell(0, 10, 'Datos Medidos:', ln=True)

        self.set_font('Arial', '', 10)
        self.ln(5)
        self.set_font('Arial', 'B', 10)
        
        self.cell(60, 10, 'Medición', 1, 0, 'C')
        self.cell(60, 10, 'Valor', 1, 0, 'C')
        self.cell(60, 10, 'Observación', 1, 1, 'C')
        self.set_font('Arial', '', 10)

        # Mediciones Registradas
         # H2O (ppmw) - límite <= 25
        valor = float(datos["H2O(ppmw)"])
        estado = "Aceptable" if valor <= 25 else "Observado"
        self.cell(60, 10, 'H2O (ppmw)', 1)
        self.cell(60, 10, str(datos["H2O(ppmw)"]), 1)
        self.cell(60, 10, estado, 1, 1)

        # Punto de Rocío (°C) - límite <= -36
        valor = float(datos["H20(Pc°)"])
        estado = "Aceptable" if valor <= -36 else "Observado"
        self.cell(60, 10, 'Punto de Rocío (°C)', 1)
        self.cell(60, 10, str(datos["H20(Pc°)"]), 1)
        self.cell(60, 10, estado, 1, 1)

        # SO2 (ppm) - límite < 12
        valor = float(datos["SO2"])
        estado = "Aceptable" if valor < 12 else "Observado"
        self.cell(60, 10, 'SO2 (ppm)', 1)
        self.cell(60, 10, str(datos["SO2"]), 1)
        self.cell(60, 10, estado, 1, 1)

        # SF6 (%) - límite > 97 (es % así que puede ser flotante)
        valor = float(datos["SF6"])
        estado = "Aceptable" if valor > 97 else "Observado"
        self.cell(60, 10, 'SF6 (%)', 1)
        self.cell(60, 10, str(datos["SF6"]), 1)
        self.cell(60, 10, estado, 1, 1)

        # H2O (ppmv) - límite <= 200
        valor = float(datos["H20 (ppmv)"])
        estado = "Aceptable" if valor <= 200 else "Observado"
        self.cell(60, 10, 'H2O (ppmv)', 1)
        self.cell(60, 10, str(datos["H20 (ppmv)"]), 1)
        self.cell(60, 10, estado, 1, 1)
            

    def agregar_datos_limites(self):
        self.ln(10)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Límites según norma IEC 60480 (Equipos con presión > 2 bar):', ln=True)

        self.ln(5)
        self.set_font('Arial', '', 10)

        # Fila 1
        self.cell(60, 10, 'H2O <= 25 ppmw', border=1, align='C')
        self.cell(60, 10, 'H2O <= 200 ppmv', border=1, align='C')
        self.cell(60, 10, 'SF6 > 97%', border=1, align='C')
        self.ln()

        # Fila 2
        self.cell(60, 10, 'SO2 < 12 ppm', border=1, align='C')
        self.cell(60, 10, 'Punto Rocío <= -36 °C', border=1, align='C')
        self.cell(60, 10, 'Equipos con presión > 2 bar', border=1, align='C')
        self.ln(5)

    def insertar_grafico(self, ruta_img):
        self.ln(10)
        self.image(ruta_img, x=25, y=self.get_y(), w=160, h=80)
        self.ln(85)

def generar_pdf_en_memoria(datos):
    # Crear el objeto PDF
    pdf = PDF()
    pdf.add_page()

    # Agregar los datos generales (FECHA, SET, CIRCUITO, Fase, EQUIPO)
    pdf.agregar_datos_generales(datos)

    # Agregar los datos medidos
    pdf.agregar_datos_medidos(datos)

    # Agregar los valores según norma
    pdf.agregar_datos_limites()

    # Crear el gráfico y obtener la ruta temporal
    ruta_img = crear_grafico(
        float(datos["H2O(ppmw)"]),
        float(datos["H20(Pc°)"]),
        float(datos["SO2"]),
        float(datos["SF6"]),
        float(datos["H20 (ppmv)"])
    )
    
    # Insertar el gráfico en el PDF
    pdf.insertar_grafico(ruta_img)

    # Generar el PDF como bytes en memoria
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    # Usar BytesIO para almacenar el PDF en memoria
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    # Eliminar el archivo temporal de la imagen después de usarlo
    if os.path.exists(ruta_img):
        os.remove(ruta_img)

    return buffer


