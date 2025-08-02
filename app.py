import streamlit as st
import requests
import math

STABILITY_API_KEY = "sk-laNUBRTwk4ZkEbTU6lH8T9AGyubr06jOP770EgMOCmxAsF1x"

ORTALAMA_ALAN = {
    "1+1": 60,
    "2+1": 90,
    "3+1": 120,
    "4+1": 150,
}

st.set_page_config(page_title="Mimari Plan Çizici (Stability Ultra)", layout="centered")
st.title("🏗️ Mimari Kat Planı Çizici (Stability Ultra API)")

st.markdown("""
Bu araç, verdiğiniz bilgilere göre **yapay zeka ile 2D mimari kat planı görseli** oluşturur.  
Stability AI’nin v2beta ultra model endpoint’ini kullanır.
""")

with st.form("input_form"):
    toplam_alan = st.number_input("Toplam Brüt Alan (m²)", min_value=50.0, value=500.0, step=10.0)
    ortak_yuzde = st.slider("Ortak Alan Oranı (%)", 0, 50, 10)
    cephe_sayisi = st.selectbox("Caddeye Bakan Cephe Sayısı", [1, 2, 3, 4], index=0)
    daire_tipi = st.selectbox("Daire Tipi", list(ORTALAMA_ALAN.keys()), index=1)
    submit = st.form_submit_button("Planı Oluştur")

def build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi):
    net_alan = toplam_alan * (1 - ortak_yuzde / 100)
    daire_alan = ORTALAMA_ALAN[daire_tipi]
    daire_sayisi = int(net_alan // daire_alan)
    return (
        f"Top-down 2D architectural floor plan, clean black-line blueprint on white background, "
        f"minimalist CAD style, labeled rooms, approx {daire_sayisi} apartments of type {daire_tipi}, "
        f"usable area about {net_alan:.0f} square meters, "
        f"{cephe_sayisi} street-facing side{'s' if cephe_sayisi > 1 else ''}."
    )

def generate_image_ultra(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*"
    }
    files = {"none": ""}
    data = {
        "prompt": prompt,
        "output_format": "webp",
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code != 200:
        raise Exception(f"API hatası: {response.status_code} {response.text}")
    return response.content

if submit:
    prompt = build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi)
    st.info("🧠 Görsel oluşturuluyor, lütfen bekleyin...")
    try:
        img_bytes = generate_image_ultra(prompt)
        st.image(img_bytes, use_container_width=True, caption="Yapay Zeka ile Oluşturulan Kat Planı")
    except Exception as e:
        st.error(f"Görsel oluşturulamadı: {e}")
