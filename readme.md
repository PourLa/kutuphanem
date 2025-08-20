![img](https://i.imgur.com/aFQTqM3.png)

# 📚 Kütüphane Yönetim Sistemi

Global AI Hub Python 202 Bootcamp Projesi için Python ile geliştirilmiş, FastAPI tabanlı modern bir kütüphane yönetim sistemi. ISBN numaraları kullanarak kitap ekleme, silme, listeleme ve arama işlemlerini otomatikleştirir.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Özellikler

- **📖 ISBN ile Otomatik Kitap Ekleme** - Open Library ve ISBN Search API'larını kullanır
- **🌐 RESTful API** - FastAPI ile modern web servisleri
- **💻 CLI Arayüzü** - Terminal üzerinden kullanım
- **💾 Veri Kalıcılığı** - JSON dosyasında veri saklama
- **🧪 Otomatik Testler** - pytest ile kapsamlı test suite
- **👥 Çoklu Yazar Desteği** - Birden fazla yazarı otomatik algılar
- **📅 Tarih Formatı Desteği** - Farklı yayın tarihi formatlarını işler

## 🛠️ Teknoloji Stacki

- **Python 3.8+**
- **FastAPI** - Modern web framework
- **httpx** - HTTP client
- **BeautifulSoup4** - Web scraping
- **pytest** - Test framework
- **uvicorn** - ASGI server

## 📦 Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/PourLa/kutuphanem.git
cd kutuphanem
```

### 2. Sanal Ortam Oluşturun ve Aktive Edin

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### 📖 Komut Satırı Arayüzü (CLI)

```bash
python main.py
```

**Örnek Kullanım:**

```
--- Kütüphane Yönetim Sistemi ---
1. Kitap Ekle (ISBN ile)
2. Kitap Ekle (Manuel)
3. Kitap Sil
4. Kitapları Listele
5. Kitap Ara
6. Çıkış

Seçiminiz (1-6): 1
Kitap ISBN: 9789750516146
Open Library: 'Suc ve Ceza' kitabı başarıyla kütüphaneye eklendi.
```

### 🌐 Web API Kullanımı

#### API'yi Başlatma

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### API Endpoint'leri

##### 📚 Tüm Kitapları Listele

```bash
curl -X GET 127.0.0.1:8000/kitaplar
```

**Örnek Çıktı:**
```json
[
  {
        "baslik": "Vatan Yahut Silistre",
        "yazar": "Namık Kemal",
        "isbn": "9786059424172",
        "yil": "2017"
    }
]
```

##### ➕ ISBN ile Kitap Ekle

```bash
curl -X POST http://localhost:8000/kitaplar -H "Content-Type:application/json" -d '{"isbn": "9786059424172"}'
```

**Başarılı Yanıt:**
```json
{
        "baslik": "Vatan Yahut Silistre",
        "yazar": "Namık Kemal",
        "isbn": "9786059424172",
        "yil": "2017"
}

Veya {"detail":"Bu ISBN ile zaten bir kitap mevcut"}  

```

##### ❌ Kitap Sil

```bash
curl -X DELETE  127.0.0.1:8000/kitaplar/9789755705859
```

**Başarılı Yanıt:**
```json
{
  {"mesaj":"'Fareler ve insanlar' kitabı başarıyla silindi"}
}
```

### 🐍 Python Modülü Olarak Kullanım

```python
from library import Library
from book import Kitap

# Kütüphane oluştur
library = Library()

# ISBN ile kitap ekle
# Bu satır, kodun çalışması için gerçek bir ISBN kullanıyor.
# '9789750516146' ISBN'si, 'Suc ve Ceza' kitabına aittir.
print("--- ISBN ile kitap ekleniyor... ---")
kitap = library.isbn_ile_kitap_ekle("9789750516146")
if kitap:
    print(f"Eklendi: {kitap.baslik} by {kitap.yazar}")

# Manuel kitap ekle
print("\n--- Manuel kitap ekleniyor... ---")
manual_kitap = Kitap("Dune", "Frank Herbert", "9780441172719", "1965")
library.kitap_ekle(manual_kitap)
print(f"Eklendi: {manual_kitap.baslik} by {manual_kitap.yazar}")


# Kitapları listele
print("\n--- Kütüphanedeki kitaplar: ---")
for book in library.kitaplari_listele():
    print(book)

# Kitap sil
print("\n--- Bir kitap siliniyor... ---")
if library.kitap_sil("9780441172719"):
    print("Kitap başarıyla silindi.")
```

### 🔧 API Dokümantasyonu

FastAPI otomatik olarak interaktif API dokümantasyonu sağlar:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

![FastAPI Swagger UI](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

## 🧪 Testler

### Tüm Testleri Çalıştırma

```bash
pytest -v
```

### Belirli Test Modülünü Çalıştırma

```bash
pytest test_api.py -v
pytest test_library_api.py -v
```

### Test Kapsamı Raporu

```bash
pytest --cov=.
```

## 📁 Proje Yapısı

```
library-management-system/
├── api.py              # FastAPI uygulaması
├── book.py             # Book sınıfı
├── library.py          # Library sınıfı
├── main.py             # CLI arayüzü
├── library.json        # Veri dosyası (otomatik oluşur)
├── test_api.py         # API testleri
├── test_library_api.py # Library sınıfı testleri
├── requirements.txt    # Gerekli kütüphaneler
└── README.md           # Bu dosya
```

## 🎯 Örnek ISBN'ler

Test için kullanabileceğiniz örnek ISBN numaraları:

- `9789750516146` - Suç ve Ceza (2014)
- `9789750714191` - Marie Curie ve Atomlarin Sirri (2017)
- `9780061002861` - The Murder of Roger Ackroyd (1991)
- `9786059424172` - Vatan Yahut Silistre (2017)

## ⚠️ Bilinen Sınırlamalar

- **API Rate Limiting:** Open Library ve ISBN Search API'ları rate limiting uygulayabilir
- **Türkçe Kitap Desteği:** Bazı Türkçe kitaplar API'larda bulunamayabilir
- **İnternet Bağımlılığı:** ISBN ile kitap ekleme internet bağlantısı gerektirir

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 🪪 Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için `LICENSE` dosyasına bakın.

## 👨‍💻 Geliştirici

![Eren ÖZTÜRK](https://cdn2.lnk.bi/profilepics/-1626855_20230613971.jpg) 

[DAHA FAZLASI İÇİN TIKLA](https://lnk.bio/ozern)

## 🙏 Teşekkürler

- Open Library - Ücretsiz kitap API'si
- ISBN Search - ISBN arama servisi
- FastAPI - Modern web framework

![img](https://i.imgur.com/r8qmIBw.png)

