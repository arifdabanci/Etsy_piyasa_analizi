import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import google.generativeai as genai

# API ve E-posta Ayarları (GitHub Secrets'tan gelecek)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_etsy_trends():
    # Stratejik Not: Etsy direkt scraping'e karşı hassastır. 
    # Bu basit bir örnektir, uzun vadede Etsy API veya SerpApi önerilir.
    search_url = "https://www.etsy.com/search?q=handmade+handicrafts&explicit=1&ship_to=US"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    products = []
    # 'Best Seller' etiketli ve küçük ürünleri filtreleme mantığı
    for item in soup.select(".v2-listing-card")[:10]:
        title = item.select_one(".v2-listing-card__title").text.strip()
        link = item.find('a')['href']
        products.append(f"{title} - {link}")
    return products

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
    response = model.generate_content(prompt)
    return response.text

def send_mail(report_content):
    msg = EmailMessage()
    msg['Subject'] = "Günlük Etsy Piyasa Analiz Raporu"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg.set_content(report_content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    products = get_etsy_trends()
    report = analyze_with_ai(products)
    send_mail(report)
