import streamlit as st import requests import base64 import os

Stability API key (gizli tut)

STABILITY_API_KEY = "sk-laNUBRTwk4ZkEbTU6lH8T9AGyubr06jOP770EgMOCmxAsF1x"

Streamlit ayarları

st.set_page_config(page_title="Mimari Plan Çizici (Stability AI)", layout="centered") st.title("🏗️ Stability AI ile Kat Planı Çizici")

st.markdown(""" Bu uygulama, Stability AI teknolojisi ile verdiğiniz bilgilere göre mimarî kat planı görselleri üretir. Lütfen aşağıdaki formu doldurun. """)

Kullanıcı girişi

with st.form("floorplan_form"): toplam_alan = st.number_input("Toplam Brüt Alan (m²)", min_value=50.0, value=500.0, step=10.0) ortak_yuzde = st.slider("Ortak Alan Oranı (%)", 0, 50, 10) daire_tipi = st.selectbox("Daire Tipi", ["1+1", "2+1", "3+1", "4+1"], index=1) cephe_sayisi = st.selectbox("Caddeye Bakan Cephe Sayısı", [1, 2, 3, 4], index=0) submit = st.form_submit_button("Planı Oluştur")

Prompt oluşturucu

def build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi): net_alan = toplam_alan * (1 - ortak_yuzde / 100) return ( f"2D architectural floor plan, top-down view, black lines on white background, " f"minimal CAD style, clean lines, labeled rooms, approximate {daire_tipi} apartments layout, " f"usable area {net_alan:.0f} square meters, {cephe_sayisi} street-facing side(s)" )

Görsel oluşturucu (Stability API)

def generate_image(prompt): url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image" headers = { "Authorization": f"Bearer {STABILITY_API_KEY}", "Content-Type": "application/json" } data = { "cfg_scale": 7, "clip_guidance_preset": "FAST_BLUE", "height": 512, "width": 512, "samples": 1, "steps": 30, "text_prompts": [{"text": prompt, "weight": 1}] } response = requests.post(url, headers=headers, json=data) if response.status_code != 200: raise Exception(f"API hatası: {response.text}") result = response.json() img_base64 = result["artifacts"][0]["base64"] return base64.b64decode(img_base64)

Sonuç gösterme

if submit: prompt = build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi) st.info("🧠 Görsel oluşturuluyor...") try: image_bytes = generate_image(prompt) st.image(image_bytes, caption="Yapay Zeka ile Oluşturulan Plan", use_column_width=True) except Exception as e: st.error(f"Hata oluştu: {e}")

