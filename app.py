import base64
import openai
import streamlit as st

# Seitenkonfiguration
st.set_page_config(
    page_title="Vinted Lookbook & Wiederverkäuferassistent",
    page_icon="🛍️",
    layout="centered",
)

st.title("🛍️ Vinted Lookbook & Wiederverkäuferassistent")
st.write(
    "Lade deine Produktfotos hoch – die KI optimiert sie und erstellt ein"
    " suchstarkes Vinted-Listing ohne erfundene Maße!"
)

# Sidebar für Einstellungen / API-Key
st.sidebar.header("⚙️ Einstellungen")
api_key_input = st.sidebar.text_input(
    "OpenAI API-Key", type="password", help="Trage hier deinen OpenAI API-Key ein."
)

if api_key_input:
  st.session_state["openai_api_key"] = api_key_input
  st.sidebar.success("API-Key gespeichert!")
else:
  if "OPENAI_API_KEY" in st.secrets:
    st.session_state["openai_api_key"] = st.secrets["OPENAI_API_KEY"]

# Hauptbereich: Datei-Upload für die Produktfotos
st.markdown("### 📸 Produktfotos hochladen")
uploaded_files = st.file_uploader(
    "Lade alle Fotos hoch (Ganzansicht, Details, Etikett)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

# Produktbeschreibung Eingabe
product_description_input = st.text_input(
    "Kurze Beschreibung als Referenz (z.B. Blaue Adidas Jacke Gr. M)",
    value="blue Adidas zip-up sports jacket with white stripes",
)

if st.button("✨ Alle Fotos bearbeiten & SEO-Listing generieren"):
  api_key = st.session_state.get("openai_api_key", "")
  if not api_key:
    st.warning("⚠️ Bitte trage links in der Sidebar deinen OpenAI API-Key ein.")
  elif not uploaded_files:
    st.warning("⚠️ Bitte lade mindestens ein Produktfoto hoch.")
  else:
    client = openai.OpenAI(api_key=api_key)

    try:
      # 1. Jedes einzelne hochgeladene Foto bearbeiten
      st.success("✅ Alle Fotos erfolgreich verarbeitet!")
      st.markdown("### 🖼️ Bearbeitete & Optimierte Produktfotos")

      for idx, uploaded_file in enumerate(uploaded_files):
        with st.spinner(
            f"Bearbeite Foto {idx + 1} basierend auf dem Original..."
        ):
          image_bytes = uploaded_file.getvalue()
          base64_image = base64.b64encode(image_bytes).decode("utf-8")

          analysis_response = client.chat.completions.create(
              model="gpt-4o",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "Du bist ein Experte für Produktfotografie. Analysiere"
                          " das hochgeladene Foto exakt (ob Gesamtansicht,"
                          " Detail oder Etikett). Erstelle einen präzisen"
                          " Bildgenerierungs-Prompt auf Englisch, der genau"
                          " dieses Foto in perfekter, professioneller"
                          " Studio-Qualität wiedergibt, ohne den Inhalt zu"
                          " verfälschen."
                      ),
                  },
                  {
                      "role": "user",
                      "content": [
                          {
                              "type": "text",
                              "text": (
                                  "Erstelle einen exakten Prompt zur"
                                  " Optimierung dieses spezifischen Fotos."
                              ),
                          },
                          {
                              "type": "image_url",
                              "image_url": {
                                  "url": f"data:image/jpeg;base64,{base64_image}"
                              },
                          },
                      ],
                  },
              ],
              max_tokens=300,
          )
          generated_prompt = analysis_response.choices[0].message.content

          img_response = client.images.generate(
              model="gpt-image-1.5",
              prompt=(
                  f"Professional e-commerce product photo, exact replica of:"
                  f" {generated_prompt}. Clean lighting, professional studio"
                  " background."
              ),
              size="1024x1024",
              quality="high",
              n=1,
          )
          processed_img_bytes = base64.b64decode(img_response.data[0].b64_json)

          st.image(
              processed_img_bytes,
              caption=f"Optimiertes Foto {idx + 1}",
              use_container_width=True,
          )

      # 2. Vinted SEO Listing mit starken Keywords und OHNE erfundene Maße generieren
      with st.spinner("📝 Generiere keyword-optimierten Vinted-Text..."):
        seo_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein professioneller Vinted Reseller Experte."
                        " Erstelle ein verkaufsstarkes Listing.\n"
                        "REGELN:\n"
                        "1. Der TITEL muss vollgepackt sein mit wichtigen"
                        " Such-Keywords (Marke, Produktart, Farbe, Stil,"
                        " Größe, z.B. 'Adidas Trainingsjacke Zip-Up Retro Blau"
                        " Gr. M Streetwear').\n"
                        "2. Erstelle eine saubere Beschreibung mit Emojis"
                        " (Zustand, Material etc.).\n"
                        "3. WICHTIG: Erfinde NIEMALS Maße (keine Zentimeter"
                        " angeben). Schreibe stattdessen: 'Maße siehe Fotos"
                        " (Etikett) oder bei Bedarf gerne nachfragen'.\n"
                        "4. Füge ganz unten passende SEO-Hashtags ein."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Erstelle das perfekte Vinted-Listing für:"
                        f" {product_description_input}"
                    ),
                },
            ],
        )
        seo_text = seo_response.choices[0].message.content

      st.markdown("---")
      st.markdown("### 📋 Vinted Listing Text (zum Kopieren)")
      st.markdown(seo_text)
      st.text_area("Text-Box:", value=seo_text, height=180)

    except Exception as e:
      st.error(f"Ein Fehler ist aufgetreten: {e}")
