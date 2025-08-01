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

cursor/generate-architectural-floor-plan-image-05fa
# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Sidebar API key input if env variable is absent
if not openai.api_key:
    st.sidebar.header("🔑 OpenAI API Ayarı")
    openai.api_key = st.sidebar.text_input(
        "OpenAI API Key*",
        type="password",
        placeholder="sk-...",
        value=st.session_state.get("user_openai_key", ""),
    )
    if openai.api_key:
        st.session_state["user_openai_key"] = openai.api_key
        st.sidebar.success("Anahtar kaydedildi—oturum boyunca geçerli.")

# Helper to generate prompt for DALL·E
def build_floorplan_prompt(total_area: float, daire_tipi: str, cephe: int, daire_sayisi: int) -> str:
    """Return a detailed text prompt to feed DALL·E for floor-plan generation."""
    return (
        f"Top-down 2D architectural floor plan, clean black-line blueprint on white background, "
        f"total usable area about {total_area:.0f} m², contains {daire_sayisi} apartment units of type {daire_tipi}, "
        f"building has {cephe} street-facing facade{'s' if cephe>1 else ''}, "
        "each apartment includes living room, open kitchen, bedrooms, bathroom, corridor; central common core with stairs and elevator; "
        f"label each apartment as '{daire_tipi}' and show room names with approximate area in m²; show doors with swing arcs and windows on exterior walls; "
        "minimalist CAD style, no 3-D shading, vector-like clarity."
    )

# Cache DALL·E results to avoid repeated API calls for the same parameters
@st.cache_data(show_spinner="Generating floor plan with DALL·E …")
def generate_floorplan_image(prompt: str) -> str:
    """Request DALL·E to create an image URL. Works with both openai<1 and >=1."""
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    # Detect major version of openai package
    version_major = int(openai.__version__.split(".")[0]) if hasattr(openai, "__version__") else 0

    if version_major >= 1:
        # New client-based interface (openai>=1.0.0)
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=openai.api_key)

            try:
                resp = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
            except Exception:
                resp = client.images.generate(model="dall-e-2", prompt=prompt, n=1, size="1024x1024")

            return resp.data[0].url  # type: ignore[attr-defined]
        except Exception as exc:
            raise RuntimeError(f"Yeni OpenAI istemci arayüzünde hata: {exc}")
    else:
        # Legacy interface (openai<1.0.0)
        try:
            response = openai.Image.create(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
        except Exception:
            response = openai.Image.create(model="dall-e-2", prompt=prompt, n=1, size="1024x1024")

        return response["data"][0]["url"]


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
