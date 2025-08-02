import os
import math
import openai
import streamlit as st

# API anahtarı doğrudan kodda (⚠️ Üretimde önerilmez!)
openai.api_key = "sk-gxWEicnVOK1Eg9WNbC22AFkOMUUcMe53v1QXJsFvah5IqV2R"

# Ortalama daire alanları (m²)
ORTALAMA_ALAN = {
    "1+1": 60,
    "2+1": 90,
    "3+1": 120,
    "4+1": 150,
}

# Sayfa ayarı
st.set_page_config(page_title="Mimari Plan Çizici", layout="centered")
st.title("🏗️ Yapay Zeka ile Kat Planı Çizici (DALL·E)")

st.markdown(
    """
Bu araç, verdiğiniz bilgilere göre **yapay zeka ile otomatik mimari kat planı çizer.**  
Planlar 2D CAD tarzında oluşturulur, 3D değildir.
"""
)

# Prompt oluşturucu
def build_floorplan_prompt(total_area: float, daire_tipi: str, cephe: int, daire_sayisi: int) -> str:
    return (
        f"Top-down 2D architectural floor plan, clean black-line blueprint on white background, "
        f"total usable area about {total_area:.0f} m², contains {daire_sayisi} apartment units of type {daire_tipi}, "
        f"building has {cephe} street-facing facade{'s' if cephe>1 else ''}, "
        "each apartment includes living room, open kitchen, bedrooms, bathroom, corridor; central common core with stairs and elevator; "
        f"label each apartment as '{daire_tipi}' and show room names with approximate area in m²; show doors with swing arcs and windows on exterior walls; "
        "minimalist CAD style, no 3-D shading, vector-like clarity."
    )

# DALL·E çağrısı
@st.cache_data(show_spinner="🧠 DALL·E ile plan çiziliyor…")
def generate_floorplan_image(prompt: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)
        try:
            response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
        except Exception:
            response = client.images.generate(model="dall-e-2", prompt=prompt, n=1, size="1024x1024")
        return response.data[0].url
    except Exception as e:
        raise RuntimeError(f"API çağrısı başarısız: {e}")

# Kullanıcı formu
with st.form("input_form"):
    toplam_alan = st.number_input("Toplam Brüt Alan (m²)", min_value=50.0, value=500.0, step=10.0)
    ortak_yuzde = st.slider("Ortak Alan Oranı (%)", 0, 50, 10)
    cephe_sayisi = st.selectbox("Caddeye Bakan Cephe Sayısı", [1, 2, 3, 4], index=0)
    daire_tipi = st.selectbox("Daire Tipi", list(ORTALAMA_ALAN.keys()), index=1)
    submit = st.form_submit_button("Planı Oluştur")

if submit:
    net_alan = toplam_alan * (1 - ortak_yuzde / 100)
    ortalama_daire_alan = ORTALAMA_ALAN[daire_tipi]
    daire_sayisi = math.floor(net_alan / ortalama_daire_alan)

    st.header("📐 Hesaplama")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Net Alan (m²)", f"{net_alan:.1f}")
    with col2:
        st.metric("Tahmini Daire Sayısı", str(daire_sayisi))

    prompt = build_floorplan_prompt(net_alan, daire_tipi, cephe_sayisi, daire_sayisi)

    st.header("🖼️ Kat Planı Görseli (DALL·E)")
    try:
        image_url = generate_floorplan_image(prompt)
        st.image(image_url, caption="Yapay Zeka ile Oluşturulan Plan", use_column_width=True)
    except Exception as e:
        st.error(f"Görsel oluşturulamadı: {e}")
