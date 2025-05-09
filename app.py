from flask import Flask, request, send_file, jsonify
from io import BytesIO
from generador_pdf import generar_pdf_en_memoria  # Asegúrate de que esta función esté bien definida
import os

app = Flask(__name__)

@app.route("/generar_reporte", methods=["POST"])
def generar_reporte():
    # Obtenemos los datos de la solicitud JSON
    datos = request.json

    if not datos:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    try:
        # Generamos el PDF en memoria
        buffer_pdf = generar_pdf_en_memoria(datos)

        # Configuramos el nombre del archivo, puedes personalizarlo
        filename = f"{datos['SET']}_{datos['CIRCUITO']}_{datos['FECHA']}.pdf"

        # Devolvemos el archivo PDF como respuesta binaria
        # Aseguramos que el buffer se cierre después de ser enviado
        buffer_pdf.seek(0)  # Nos aseguramos de que el buffer esté al principio antes de enviarlo
        response = send_file(buffer_pdf, as_attachment=True, download_name=filename, mimetype='application/pdf')

        # Cerramos el buffer después de la respuesta
        buffer_pdf.close()

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
