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
    "Lade deine Produktfotos hoch, generiere professionelle Lookbook-Bilder &"
    " erhalte perfekte Vinted-Texte!"
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
    "Lade Fotos hoch (Ganzansicht, Details, Etikett)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

# Produktbeschreibung Eingabe
product_description_input = st.text_input(
    "Produktbeschreibung (z.B. Blaue Adidas Trainingsjacke Gr. M)",
    value="blue Adidas zip-up sports jacket with white stripes",
)

if st.button("✨ Lookbook-Bilder & Listing generieren"):
  api_key = st.session_state.get("openai_api_key", "")
  if not api_key:
    st.warning("⚠️ Bitte trage links in der Sidebar deinen OpenAI API-Key ein.")
  elif not uploaded_files:
    st.warning("⚠️ Bitte lade mindestens ein Produktfoto hoch.")
  else:
    client = openai.OpenAI(api_key=api_key)

    try:
      # 1. Lookbook Bilder generieren (Modus mit Fehlerabfangung)
      with st.spinner(
          "🎨 Generiere Lookbook (Model-Shot) & Detail-Shot auf Beton..."
      ):
        model_prompt = (
            f"A professional high-end fashion campaign lookbook photo of a model"
            f" wearing {product_description_input}, staged in a stylish urban"
            " loft with natural window light, photorealistic, editorial style."
        )

        detail_prompt = (
            f"A professional product detail flat lay photo of"
            f" {product_description_input} showing the inner size label"
            " clearly legible, resting on a modern rough grey concrete texture"
            " background, photorealistic, sharp focus, studio lighting."
        )

        # Generierung Model-Bild
        model_res = client.images.generate(
            model="dall-e-3",
            prompt=model_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        model_url = model_res.data[0].url

        # Generierung Detail-Bild (Beton)
        detail_res = client.images.generate(
            model="dall-e-3",
            prompt=detail_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        detail_url = detail_res.data[0].url

      st.success("✅ Lookbook-Bilder erfolgreich erstellt!")

      # Bilder anzeigen
      st.markdown("### 🖼️ Generierte Lookbook-Bilder")
      col1, col2 = st.columns(2)
      with col1:
        st.image(
            model_url, caption="Lookbook Model-Shot", use_container_width=True
        )
      with col2:
        st.image(
            detail_url,
            caption="Detail-Shot (Schild auf Beton)",
            use_container_width=True,
        )

      # 2. Vinted SEO Listing generieren via GPT-4o
      with st.spinner("📝 Generiere optimierten Vinted-SEO-Text..."):
        seo_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein professioneller Vinted Reseller Experte."
                        " Erstelle einen knackigen Titel, eine detaillierte"
                        " Beschreibung und passende Hashtags für den"
                        " Artikel."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Erstelle ein verkaufsstarkes Vinted-Listing für:"
                        f" {product_description_input}"
                    ),
                },
            ],
        )
        seo_text = seo_response.choices[0].message.content

      st.markdown("### 📋 Vinted Listing Text (zum Kopieren)")
      st.text_area("SEO-Text", value=seo_text, height=180)

    except Exception as e:
      st.error(
          "Hinweis zur Bildgenerierung: Falls dein OpenAI-Account ein reines"
          " Text-Guthaben hat, blockiert OpenAI manchmal die direkte"
          f" Bild-API. Fehlerdetails: {e}"
      )
