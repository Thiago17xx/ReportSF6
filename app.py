from flask import Flask, request, send_file, jsonify
from io import BytesIO
from generador_pdf import generar_pdf_en_memoria

app = Flask(__name__)

@app.route("/generar_reporte", methods=["POST"])
def generar_reporte():
    datos = request.json

    if not datos:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    try:
        print("✅ Datos recibidos:", datos)

        buffer_pdf = generar_pdf_en_memoria(datos)
        filename = f"{datos.get('SET', 'SET')}_{datos.get('CIRCUITO', 'CIRCUITO')}_{datos.get('FECHA', 'FECHA')}.pdf"

        buffer_pdf.seek(0)
        response = send_file(buffer_pdf, as_attachment=True, download_name=filename, mimetype='application/pdf')

        return response

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
