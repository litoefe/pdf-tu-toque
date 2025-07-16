import streamlit as st
import requests
from PIL import Image
from fpdf import FPDF
import io
import tempfile
import os

# Mapa entre destinos y IDs de Google Drive
drive_images = {
    "00_portada.jpg": "1xR3OaBTH78WoIMQwCr4OiVVSUn7hwRsE",
    "01_intro_tu_toque.jpg": "1ki5pZBiV1g7GVYBajPXw6gVv56b95JyM",
    "Camboya 3 días.jpg": "1EvvKTJj4UNNg_7GEiR3-jOExQRgAikWJ",
    "China 15 días.jpg": "1FbU0z5PXY6q6IZf31zs1nzi4fMay7lqP",
    "Filipinas 8 Días.jpg": "1pWORsCyYu3qpC_u5pJPo9S63MxSdwcjI",
    "99_cierre.jpg": "1dl1pUESwNAxUJl1HlXJmGAeQBeIZ5dFI"
}

# Paquetes disponibles para seleccionar (excluye portada, intro y cierre)
paquetes = [
    "Camboya 3 días.jpg",
    "China 15 días.jpg",
    "Filipinas 8 Días.jpg"
]

st.title("🧳 Generador de PDF - Tu Toque")
st.markdown("Seleccioná los destinos que querés combinar en un solo PDF:")

seleccionados = st.multiselect("Destinos", paquetes)

if st.button("Generar PDF") and seleccionados:
    orden = ["00_portada.jpg", "01_intro_tu_toque.jpg"] + seleccionados + ["99_cierre.jpg"]
    
    pdf = FPDF(orientation='P', unit='pt', format=[1080, 1920])  # Tamaño real en puntos (1pt = 1px a 72dpi)
    
    for archivo in orden:
        file_id = drive_images.get(archivo)
        if not file_id:
            st.error(f"No se encontró el archivo: {archivo}")
            continue

        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url)

        try:
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
        except:
            st.error(f"No se pudo abrir la imagen: {archivo}")
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file, format="JPEG")
            tmp_path = tmp_file.name

        pdf.add_page()
        pdf.image(tmp_path, x=0, y=0)  # Inserta imagen con tamaño original

        os.remove(tmp_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)

    with open(tmp_pdf.name, "rb") as f:
        pdf_bytes = f.read()

    os.remove(tmp_pdf.name)

    st.success("✅ PDF generado correctamente.")
    st.download_button("📥 Descargar PDF", pdf_bytes, file_name="tu_toque.pdf", mime="application/pdf")
