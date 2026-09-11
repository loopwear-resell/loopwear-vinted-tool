import base64
import io
import os
from PIL import Image
from openai import OpenAI
from rembg import remove
import streamlit as st

# Streamlit Layout
st.set_page_config(
    page_title="Vinted AI Reseller Assistant", page_icon="🛍️", layout="wide"
)

st.title("🛍️ Vinted AI Reseller Tool")
st.write(
    "Lade Produktfotos hoch, lass den Hintergrund entfernen und generiere"
    " perfekte SEO-Texte & Hashtags."
)

# Sidebar für API Key
st.sidebar.header("🔑 Einstellungen")
api_key_input = st.sidebar.text_input(
    "OpenAI API Key eingeben", type="password"
)

if api_key_input:
  os.environ["OPENAI_API_KEY"] = api_key_input

# Mehrere Bilder hochladen
uploaded_files = st.file_uploader(
    "Produktfotos hochladen (Vorderseite, Rückseite, Etikett etc.)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
  st.subheader("📸 Bearbeitete Bilder (Hintergrund entfernt)")
  cols = st.columns(len(uploaded_files))

  processed_images_base64 = []
  client = OpenAI()

  for idx, uploaded_file in enumerate(uploaded_files):
    image = Image.open(uploaded_file)

    # Hintergrund entfernen mit rembg
    input_bytes = io.BytesIO()
    image.save(input_bytes, format="PNG")
    output_bytes = remove(input_bytes.getvalue())
    processed_image = Image.open(io.BytesIO(output_bytes))

    # Auf weißem Hintergrund platzieren
    background = Image.new("RGB", processed_image.size, (255, 255, 255))
    background.paste(processed_image, (0, 0), processed_image)

    with cols[idx]:
      st.image(
          background,
          caption=f"Bild {idx+1} optimiert",
          use_container_width=True,
      )

    # Bild für OpenAI vorbereiten
    buffered = io.BytesIO()
    background.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    processed_images_base64.append(img_str)

  # Analyse-Button
  if st.button("🚀 Vinted-Listing generieren"):
    if not api_key_input:
      st.error("Bitte gib zuerst deinen OpenAI API-Key in der Sidebar ein.")
    else:
      with st.spinner("KI analysiert die Bilder und optimiert für SEO..."):
        content_payload = [
            {
                "type": "text",
                "text": (
                    "Du bist ein hochprofesioneller und umsatzstarker"
                    " Vinted-Reseller. Analysiere die hochgeladenen Fotos des"
                    " Artikels präzise. Antworte exakt in diesem Format, damit"
                    " ich es trennen kann:\n\n### TITEL:\n[Hier nur den"
                    " SEO-optimierten Titel einfügen, max. 80 Zeichen]\n\n###"
                    " BESCHREIBUNG:\n[Hier die ehrliche, professionelle"
                    " Beschreibung mit Zustand, Material, Maßen und den Top"
                    " 12-15 Vinted-Hashtags am Ende einfügen]"
                ),
            }
        ]

        for img_base64 in processed_images_base64:
          content_payload.append({
              "type": "image_url",
              "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
          })

        try:
          response = client.chat.completions.create(
              model="gpt-4o",
              messages=[{"role": "user", "content": content_payload}],
              max_tokens=1000,
          )

          full_response = response.choices[0].message.content

          # Text trennen in Titel und Beschreibung
          if "### TITEL:" in full_response and "### BESCHREIBUNG:" in full_response:
            parts = full_response.split("### BESCHREIBUNG:")
            titel_part = (
                parts[0].replace("### TITEL:", "").strip().strip('"')
            )
            beschreibung_part = parts[1].strip()
          else:
            titel_part = "Fehler beim Parsen"
            beschreibung_part = full_response

          st.success("Erfolgreich generiert!")

          # Ausgabe für Titel mit Kopier-Hinweis
          st.subheader("📌 Titel")
          st.text_input("Titel zum Kopieren", value=titel_part, key="titel_out")
          st.info(
              "💡 Tipp: Du kannst den Titel direkt aus dem Feld oben kopieren"
              " oder gedrückt halten."
          )

          # Ausgabe für Beschreibung
          st.subheader("📝 Beschreibung & Hashtags")
          st.text_area(
              "Beschreibung zum Kopieren",
              value=beschreibung_part,
              height=200,
              key="desc_out",
          )

        except Exception as e:
          st.error(f"Ein Fehler ist aufgetreten: {e}")
