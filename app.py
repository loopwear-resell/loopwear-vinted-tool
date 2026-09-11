import base64
import openai
import streamlit as st

# Seitenkonfiguration
st.set_page_config(
    page_title="Vinted Lookbook & Reseller Assistent",
    page_icon="🛍️",
    layout="centered",
)

st.title("🛍️ Vinted Lookbook & Reseller Assistent")
st.write(
    "Lade deine Fotos hoch – die KI erkennt das Produkt *automatisch*,"
    " generiert das perfekte Bild und das suchstarke Vinted-Listing!"
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
    "Lade alle Fotos hoch (Ansichten, Details, Etikett)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

# Stil-Auswahl für das perfekte Bild
image_style = st.radio(
    "🎨 Wie soll das Präsentationsbild aussehen?",
    [
        "Professioneller Lookbook-Model-Shot",
        (
            "Glatte, perfekt ausgelegte Kleidung auf urbanem Beton"
            " (Flatlay-Stil)"
        ),
    ],
)

if st.button("✨ Produkt automatisch erkennen & Listing generieren"):
  api_key = st.session_state.get("openai_api_key", "")
  if not api_key:
    st.warning("⚠️ Bitte trage links in der Sidebar deinen OpenAI API-Key ein.")
  elif not uploaded_files:
    st.warning("⚠️ Bitte lade mindestens ein Produktfoto hoch.")
  else:
    client = openai.OpenAI(api_key=api_key)

    try:
      # Wir nehmen das erste hochgeladene Foto, um das Produkt automatisch zu erkennen
      first_image_bytes = uploaded_files[0].getvalue()
      base64_first_image = base64.b64encode(first_image_bytes).decode("utf-8")

      # 1. Automatische Produkterkennung via GPT-4o Vision
      with st.spinner("🔍 Analysiere deine Fotos automatisch..."):
        vision_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein Experte für Kleidung und Reselling. Analysiere"
                        " das hochgeladene Foto genau. Antworte AUSSCHLIESSLICH"
                        " mit einer präzisen Beschreibung auf Englisch (Marke,"
                        " genauer Kleidungsstil, Farbe, Besonderheiten), damit"
                        " man es perfekt weiterverarbeiten kann. Beispiel:"
                        " 'Armani blue denim jeans straight fit'."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Was genau ist das für ein Kleidungsstück auf"
                                " dem Foto?"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:image/jpeg;base64,{base64_first_image}"
                                )
                            },
                        },
                    ],
                },
            ],
            max_tokens=100,
        )
        detected_product = vision_response.choices[0].message.content.strip()

      st.info(f"💡 *Erkanntes Produkt:* {detected_product}")

      # 2. Bildgenerierung basierend auf dem ECHTEN, erkannten Produkt
      with st.spinner("🎨 Generiere professionelles Präsentationsbild..."):
        if "Model" in image_style:
          selected_prompt = (
              f"A professional commercial fashion lookbook photograph of a"
              f" stylish urban outfit featuring: {detected_product}, worn by a"
              " model in a modern bright minimalist studio with soft natural"
              " light, editorial fashion style, ultra-realistic, 4k."
          )
        else:
          selected_prompt = (
              "A professional high-end e-commerce product photograph of smooth,"
              " perfectly arranged clothing item ("
              f" {detected_product} ) neatly laid out on a clean, modern urban"
              " grey polished concrete floor, top-down flatlay view, perfect"
              " soft studio lighting, gorgeous aesthetic, 4k."
          )

        img_response = client.images.generate(
            model="gpt-image-1.5",
            prompt=selected_prompt,
            size="1024x1024",
            quality="high",
            n=1,
        )
        model_image_bytes = base64.b64decode(img_response.data[0].b64_json)

      st.success("✅ Bild erfolgreich erstellt!")
      st.markdown("### 🖼️ Präsentations-Bild")
      st.image(
          model_image_bytes,
          caption=f"Automatisch erstellt für: {detected_product}",
          use_container_width=True,
      )

      # 3. Vinted SEO Listing mit starken Keywords und OHNE erfundene Maße generieren
      with st.spinner("📝 Generiere keyword-optimierten Vinted-Text..."):
        seo_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein professioneller Vinted Reseller Experte."
                        " Erstelle ein verkaufsstarkes Listing basierend auf"
                        " dem erkannten Produkt.\n"
                        "REGELN:\n"
                        "1. Der TITEL muss vollgepackt sein mit wichtigen"
                        " Such-Keywords (Marke, genaue Produktart, Farbe, Stil,"
                        " Zustand, Größe).\n"
                        "2. Erstelle eine saubere, übersichtliche Beschreibung"
                        " mit Emojis (Zustand, Material etc.).\n"
                        "3. WICHTIG: Erfinde NIEMALS Maße (keine Zentimeter"
                        " angeben). Schreibe stattdessen: 'Maße siehe Fotos"
                        " (Etikett) oder bei Bedarf gerne nachfragen'.\n"
                        "4. Füge ganz unten passende SEO-Hashtags ein."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Erstelle das perfekte Vinted-Listing für dieses"
                        f" erkannte Produkt: {detected_product}"
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
