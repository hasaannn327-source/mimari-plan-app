import streamlit as st
import requests
import base64

STABILITY_API_KEY = "sk-laNUBRTwk4ZkEbTU6lH8T9AGyubr06jOP770EgMOCmxAsF1x"

ORTALAMA_ALAN = {
    "1+1": 60,
    "2+1": 90,
    "3+1": 120,
    "4+1": 150,
}

st.set_page_config(page_title="Mimari Plan Çizici (Stability AI)", layout="centered")
st.title("🏗️ Stability AI ile Kat Planı Çizici")

st.markdown("""
Bu uygulama, verdiğiniz bilgilere göre **Stable Diffusion** ile mimarî kat planı görselleri üretir.  
Planlar 2D CAD tarzında, sade ve temiz çizim olur.
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
        f"top-down 2D architectural floor plan, black lines on white background, "
        f"minimalist CAD style, labeled rooms, approx {daire_tipi} apartments layout, "
        f"usable area about {net_alan:.0f} square meters, "
        f"{cephe_sayisi} street-facing side{'s' if cephe_sayisi > 1 else ''}"
    )

def generate_image_with_model(prompt, model_url):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
        "text_prompts": [{"text": prompt, "weight": 1}],
    }
    response = requests.post(model_url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"API hatası ({model_url}): {response.text}")
    result = response.json()
    img_base64 = result["artifacts"][0]["base64"]
    return base64.b64decode(img_base64)

def generate_image(prompt):
    # Öncelikli model
    model_1 = "https://api.stability.ai/v1/generation/stable-diffusion-xl-beta-v2-2-2/text-to-image"
    # Yedek model
    model_2 = "https://api.stability.ai/v1/generation/stable-diffusion-512-v2-1/text-to-image"
    try:
        return generate_image_with_model(prompt, model_1)
    except Exception as e1:
        st.warning(f"Birinci model hatası: {e1}\nYedek modele geçiliyor...")
        try:
            return generate_image_with_model(prompt, model_2)
        except Exception as e2:
            raise Exception(f"Yedek modelde de hata oluştu: {e2}")

if submit:
    prompt = build_prompt(toplam_alan, ortak_yuzde, daire_tipi, cephe_sayisi)
    st.info("🧠 Görsel oluşturuluyor… Lütfen bekleyin.")
    try:
        img_bytes = generate_image(prompt)
        st.image(img_bytes, caption="Yapay Zeka ile Oluşturulan Kat Planı", use_column_width=True)
    except Exception as e:
        st.error(f"Görsel oluşturulamadı: {e}")        
