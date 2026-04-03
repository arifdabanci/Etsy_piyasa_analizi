import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from google import genai # YENİ KÜTÜPHANE

# API ve E-posta Ayarları (GitHub Secrets'tan gelecek)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# YENİ İSTEMCİ (CLIENT) YAPISI
client = genai.Client(api_key=GEMINI_API_KEY)

def get_etsy_trends():
    # Stratejik Not: Etsy direkt scraping'e karşı hassastır.
    search_url = "https://www.etsy.com/search?q=handmade+handicrafts&explicit=1&ship_to=US"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status() # HTTP hatalarını yakala
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
        # YENİ MODEL VE ÇAĞRI YÖNTEMİ
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
         return f"Yapay zeka analizi sırasında hata oluştu: {str(e)}"

def send_mail(report_content):
    msg = EmailMessage()
    msg['Subject'] = "Günlük Etsy Piyasa Analiz Raporu"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg.set_content(report_content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Mail başarıyla gönderildi.")
    except Exception as e:
        print(f"Mail gönderimi başarısız: {str(e)}")

if __name__ == "__main__":
    print("Sistem başlatılıyor...")
    products = get_etsy_trends()
    report = analyze_with_ai(products)
    send_mail(report)
