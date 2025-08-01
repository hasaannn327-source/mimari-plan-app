# mimari-plan-app
streamlit clouddan aç güzel çalışıyor 

## DALL·E Kat Planı Üretimi

Uygulama artık OpenAI DALL·E API’sini kullanarak *dinamik* kat planı görselleri üretmektedir.  
Çalıştırmadan önce çevre değişkeni olarak `OPENAI_API_KEY` değerini tanımladığınızdan emin olun:

```bash
export OPENAI_API_KEY="sk-..."
```

Ardından uygulamayı başlatın:

```bash
streamlit run app.py
```

Formu doldurun ve **Planı Göster** düğmesine bastığınızda, seçtiğiniz kriterlere göre oluşturulan istem (prompt) DALL·E’ye gönderilir ve dönen görsel hemen sayfada gösterilir.

> İstem, kullanılabilir alan, daire adedi/tipleri, cadde cephe sayısı ve ortak alan kurgusunu içeren detaylı bir açıklamadır. Aynı parametrelerle birden fazla kez istek gönderilirse önbellekten hızla yanıt verir.

### Gereksinimler
```
pip install --break-system-packages -r requirements.txt
```

> Not: PEP 668 uyarısı olan sistemlerde `--break-system-packages` bayrağı gerekebilir (Codespaces vb.). 
