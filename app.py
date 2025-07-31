import json
import math
import streamlit as st
from pathlib import Path

# Ortalama daire alanları (m²)
ORTALAMA_ALAN = {
    "1+1": 60,
    "2+1": 90,
    "3+1": 120,
    "4+1": 150,
}

# JSON'dan plan verilerini yükle
@st.cache_data
def load_plans(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

plans = load_plans(Path(__file__).parent / "plans.json")

st.set_page_config(page_title="Mimari Kat Planı Önerici", layout="centered")

st.title("🏢 Mimari Kat Planı Önerici")

st.markdown(
    """
Bu araç, girdiğiniz **toplam inşaat alanı**, **ortak alan yüzdesi**, **cadde cephesi sayısı** ve **istediğiniz daire tipi** bilgilerinden yola çıkarak 
uygun mimari kat planını otomatik olarak önermektedir.
"""
)

with st.form("input_form"):
    toplam_alan = st.number_input("Toplam Brüt Alan (m²)", min_value=50.0, value=500.0, step=10.0, format="%f")
    ortak_yuzde = st.slider("Ortak Alan Oranı (%)", min_value=0, max_value=50, value=10)
    cephe_sayisi = st.selectbox("Caddeye Bakan Cephe Sayısı", options=[1, 2, 3, 4], index=0)
    daire_tipi = st.selectbox("Daire Tipi", options=list(ORTALAMA_ALAN.keys()), index=1)
    submit = st.form_submit_button("Planı Göster")

if submit:
    # Net alan hesapla
    net_alan = toplam_alan * (1 - ortak_yuzde / 100)
    ortalama_daire_alan = ORTALAMA_ALAN.get(daire_tipi, 90)
    daire_sayisi = math.floor(net_alan / ortalama_daire_alan)

    st.header("Hesap Sonuçları")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Net Kullanılabilir Alan (m²)", value=f"{net_alan:.1f}")
    with col2:
        st.metric(label="Tahmini Daire Sayısı", value=str(daire_sayisi))

    # Plan filtreleme
    uygun_planlar = [
        p for p in plans
        if p["cadde_cephe_sayisi"] == cephe_sayisi
        and p["daire_tipi"] == daire_tipi
        and p["min_alani"] <= net_alan <= p["max_alani"]
    ]

    # En yakın alan farkına göre sıralama
    uygun_planlar.sort(key=lambda p: abs(((p["min_alani"] + p["max_alani"]) / 2) - net_alan))

    st.header("Önerilen Kat Planı")

    if uygun_planlar:
        secilen = uygun_planlar[0]
        st.subheader(secilen["isim"])
        st.image(secilen["gorsel_url"], use_column_width=True)
        st.write(
            f"Cadde Cephesi Sayısı: **{secilen['cadde_cephe_sayisi']}**  |  "
            f"Daire Tipi: **{secilen['daire_tipi']}**  |  "
            f"Uygun Alan Aralığı: **{secilen['min_alani']} - {secilen['max_alani']} m²**"
        )
    else:
        st.warning("Maalesef kriterlerinize tam olarak uyan bir plan bulunamadı. Lütfen parametreleri değiştirin.")
