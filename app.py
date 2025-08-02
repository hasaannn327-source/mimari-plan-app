import streamlit as st
import requests
import base64
import math

STABILITY_API_KEY = "sk-laNUBRTwk4ZkEbTU6lH8T9AGyubr06jOP770EgMOCmxAsF1x"

ORTALAMA_ALAN = {
    "1+1": 60,
    "2+1": 90,
    "3+1": 120,
    "4+1": 150,
}

st.set_page_config(page_title="Mimari Plan Çizici (Stability AI)", layout="centered")
st.title("🏗️ Stability AI ile Kat Planı Çizici (SDXL, JSON POST)")

st.markdown("""
Bu uygulama, verdiğiniz bilgilere göre **2D mimari kat planı görseli** üretmek için  
Stability API SDXL modelini **application/json** formatında çağırır.
""")

with st.form("input_form"):
    toplam_alan = st.number_input("Toplam Brüt Alan (m²)", min_value=50.0, value=500.0, step=10.0)
    ortak_yuzde = st.slider("Ortak Alan Oranı (%)", 0, 50, 10)
    daire_tipi = st.selectbox("Daire Tipi", list(ORTALAMA_ALAN.keys()), index=1)
    cephe_sayisi = st.selectbox("Caddeye Bakan Cephe Sayısı", [1, 2, 3, 4], index=0)
    submit = st.form_submit_button("Planı Oluştur")

def build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi):
    net_alan = toplam_alan * (1 - ortak_yuzde / 100)
    return (
        f"top-down 2D architectural floor plan, clean black-line blueprint on white background, "
        f"minimalist CAD style, labeled rooms, approx {daire_tipi} apartments, "
        f"usable area about {net_alan:.0f} square meters, "
        f"{cephe_sayisi} street-facing side{'s' if cephe_sayisi > 1 else ''}"
    )

def generate_image_stability(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-v1-0/text-to-image"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "text_prompts": [{"text": prompt, "weight": 1}],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"API hatası: {response.status_code} {response.text}")
    resp_json = response.json()
    img_base64 = resp_json["artifacts"][0]["base64"]
    img_bytes = base64.b64decode(img_base64)
    return img_bytes

if submit:
    prompt = build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi)
    st.info("🧠 Görsel oluşturuluyor, lütfen bekleyin...")
    try:
        img = generate_image_stability(prompt)
        st.image(img, caption="Yapay Zeka ile Oluşturulan Kat Planı", use_column_width=True)
    except Exception as e:
        st.error(f"Görsel oluşturulamadı: {e}")
