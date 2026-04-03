import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import json

# API ve E-posta Ayarları
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def get_etsy_trends():
    search_url = "https://www.etsy.com/search?q=handmade+handicrafts&explicit=1&ship_to=US"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        for item in soup.select(".v2-listing-card")[:10]:
            title_elem = item.select_one(".v2-listing-card__title")
            link_elem = item.find('a')
            if title_elem and link_elem:
                title = title_elem.text.strip()
                link = link_elem.get('href', 'Link bulunamadı')
                products.append(f"{title} - {link}")
        return products
    except Exception as e:
        return [f"Etsy verileri çekilirken hata oluştu: {str(e)}"]

def get_working_model():
    # STRATEJİK HAMLE: Tahmin etmiyoruz, Google'a "Hangi modelin çalışıyor?" diye soruyoruz.
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        models = response.json().get('models', [])
        
        # 'generateContent' (metin üretme) destekleyen ilk Gemini modelini bul ve seç
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name', '').lower():
                print(f"Aktif Model Bulundu: {m['name']}")
                return m['name'] # Örn: 'models/gemini-1.5-flash' döner
    except Exception as e:
        print(f"Model listesi çekilemedi, varsayılan deneniyor. Hata: {str(e)}")
        
    return "models/gemini-1.5-flash" # Hiçbir şey bulamazsa acil durum varsayılanı

def analyze_with_ai(products):
    prompt = f"""
    Sen bir Etsy ticaret stratejistisin. Aşağıdaki verileri analiz et:
    1. Ürünler: {products}
    2. Odak Noktası: Kastamonu Taş Baskısı ve Trabzon Kazaziye/Telkari sanatı.
    
    Görevlerin:
    - Listelenen ürünlerden hangileri küçük, hafif ve lojistik açıdan avantajlı?
    - Kastamonu/Trabzon sanatını bu trendlere nasıl uydurabiliriz?
    - Son 24 saatteki 3 kritik Etsy girişimcilik haberini (hayali pazar verisiyle değil, genel e-ticaret trendleriyle) analiz et.
    - Satışları artırmak için 3 somut strateji ver.
    Raporu Türkçe ve profesyonel bir dille hazırla.
    """
    
    try:
        # 1. Adım: Çalışan güncel model ismini otomatik al
        model_name = get_working_model()
        
        # 2. Adım: O modele tam isabet isteği yolla
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts":[{"text": prompt}]}]
        }
        
        response = requests.post(url
