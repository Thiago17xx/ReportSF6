# generador_pdf.py
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

# Crear directorio para los reportes si no existe
os.makedirs("reportes_sf6", exist_ok=True)

class PDF(FPDF):
    def header(self):
        # Coloca una imagen en la cabecera
        self.image("static/logolds.jpg", x=10, y=4, w=30, h=15)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'REPORTE DE SF6', ln=True, align='C')
        self.ln(5)

    def footer(self):
        # Coloca el pie de página
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

    def agregar_datos(self, fila):
        # Agregar los datos del reporte
        self.set_font("Arial", size=11)
        for etiqueta in ["FECHA", "SET", "CIRCUITO", "Fase", "EQUIPO"]:
            self.cell(40, 10, f"{etiqueta}:", 0, 0)
            self.cell(100, 10, str(fila.get(etiqueta, "")), 0, 1)
        self.ln(5)

    def insertar_grafico(self, path_img):
        # Insertar un gráfico en el PDF
        self.image(path_img, x=25, y=self.get_y(), w=160, h=80)

    def agregar_tabla_mediciones(self, h2o, rocio, so2, pureza, h2o_ppmv):
        # Agregar la tabla con las mediciones
        obs_h2o = "OBSERVADO" if h2o > 25 else "OK"
        obs_rocio = "OBSERVADO" if rocio > -36 else "OK"
        obs_sf6 = "OBSERVADO" if pureza < 97 else "OK"
        obs_so2 = "OBSERVADO" if so2 >= 12 else "OK"
        obs_h2o_ppmv = "OBSERVADO" if h2o_ppmv > 200 else "OK"
        self.set_font("Arial", 'B', 11)
        self.cell(0, 10, "Mediciones Registradas", ln=True)
        self.set_font("Arial", '', 11)

        self.cell(50, 10, "H2O (ppmw)", 1)
        self.cell(40, 10, str(h2o), 1)
        self.cell(40, 10, obs_h2o, 1, ln=True)

        self.cell(50, 10, "Punto de Rocío (°C)", 1)
        self.cell(40, 10, str(rocio), 1)
        self.cell(40, 10, obs_rocio, 1, ln=True)

        self.cell(50, 10, "SO2 (ppm)", 1)
        self.cell(40, 10, str(so2), 1)
        self.cell(40, 10, obs_so2, 1, ln=True)

        self.cell(50, 10, "Pureza SF6 (%)", 1)
        self.cell(40, 10, str(pureza), 1)
        self.cell(40, 10, obs_sf6, 1, ln=True)

        self.cell(50, 10, "H2O (ppmv)", 1)
        self.cell(40, 10, str(h2o_ppmv), 1)
        self.cell(40, 10, obs_h2o_ppmv, 1, ln=True)
        self.ln(5)

    def agregar_limites_norma(self):
        # Agregar los límites según la norma IEC 60480
        self.set_font("Arial", 'B', 11)
        self.cell(0, 10, "Límites según norma IEC 60480 (presión > 2 bar)", ln=True)
        self.set_font("Arial", '', 11)
        self.cell(60, 10, "H2O <= 25 ppmw", 1)
        self.cell(60, 10, "Punto Rocío <= -36 °C", 1)
        self.cell(60, 10, "SO2 < 12 ppm", 1, ln=True)
        self.cell(60, 10, "SF6 > 97%", 1)
        self.cell(60, 10, "H2O (ppmv) <= 200", 1)
        self.cell(60, 10, "", 1, ln=True)
        self.ln(5)

def crear_grafico(h2o_ppmw, punto_rocio, so2, nombre_img):
    # Crear un gráfico y guardarlo como imagen
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axhline(y=25, color='red', linestyle='--', label='Límite H2O (25 ppmw)')
    ax.axvline(x=-36, color='blue', linestyle='--', label='Límite Punto de Rocío (-36°C)')
    ax.scatter(punto_rocio, h2o_ppmw, s=100 + float(so2) * 100, c='green', alpha=0.7, label=f'Dato SO2: {so2} ppm')
    ax.set_xlabel("Punto de Rocío (°C)")
    ax.set_ylabel("H2O (ppmw)")
    ax.set_title("Comparación Punto de Rocío vs Humedad SF6")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(nombre_img)
    plt.close()

def generar_pdf_en_memoria(datos: dict) -> BytesIO:
    # Genera el PDF en memoria (sin escribir en disco)
    
    pdf = PDF()
    pdf.add_page()
    pdf.agregar_datos(datos)
    pdf.agregar_tabla_mediciones(float(datos["H2O(ppmw)"]), float(datos["H20(Pc°)"]), float(datos["SO2"]),
                                 float(datos["SF6"]), float(datos["H20 (ppmv)"]))

    pdf.agregar_limites_norma()

    # Crear gráfico
    img_path = "grafico_temp.png"
    crear_grafico(float(datos["H2O(ppmw)"]), float(datos["H20(Pc°)"]), float(datos["SO2"]), img_path)
    pdf.insertar_grafico(img_path)

    # Guardar PDF en memoria
    buffer_pdf = BytesIO()
    pdf.output(buffer_pdf)
    buffer_pdf.seek(0)  # Volver al principio del archivo para que pueda leerse

    os.remove(img_path)  # Eliminar imagen temporal

    return buffer_pdf  # Devolver el archivo en memoria
