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
    "Lade deine Produktfotos hoch, optimiere deine Bilder für Vinted und erhalte"
    " perfekte SEO-Texte!"
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
    "Lade Fotos hoch (z.B. Ganzansicht & Größenschild)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

# Produktbeschreibung Eingabe
product_description_input = st.text_input(
    "Produktbeschreibung (z.B. Blaue Adidas Trainingsjacke Gr. M)",
    value="blue Adidas zip-up sports jacket with white stripes",
)

if st.button("✨ Vinted-Listing & Bilder optimieren"):
  api_key = st.session_state.get("openai_api_key", "")
  if not api_key:
    st.warning("⚠️ Bitte trage links in der Sidebar deinen OpenAI API-Key ein.")
  elif not uploaded_files:
    st.warning("⚠️ Bitte lade mindestens ein Produktfoto hoch.")
  else:
    client = openai.OpenAI(api_key=api_key)

    try:
      # 1. Hochgeladene Bilder direkt anzeigen (als saubere Galerie)
      st.success("✅ Fotos erfolgreich verarbeitet!")
      st.markdown("### 🖼️ Deine hochgeladenen Produktfotos")

      cols = st.columns(len(uploaded_files))
      for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx]:
          st.image(
              uploaded_file,
              caption=f"Foto {idx+1}",
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
      st.markdown(seo_text)

    except Exception as e:
      st.error(f"Ein Fehler ist aufgetreten: {e}")
