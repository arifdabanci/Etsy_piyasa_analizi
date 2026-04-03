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
    
    # Kütüphane kullanmadan doğrudan sunucuya bağlanıyoruz (REST API)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts":[{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        error_detail = response.text if 'response' in locals() else 'Bağlantı kurulamadı'
        return f"Yapay zeka analizi sırasında hata oluştu:\n{str(e)}\n\nDetay:\n{error_detail}"

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
