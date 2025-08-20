# 📚 Kütüphane Yönetim Sistemi

Python ile geliştirilmiş, FastAPI tabanlı modern bir kütüphane yönetim sistemi. ISBN numaraları kullanarak kitap ekleme, silme, listeleme ve arama işlemlerini otomatikleştirir.

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
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
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
GET http://localhost:8000/books
```

**Örnek Çıktı:**
```json
[
  {
    "title": "Suc ve Ceza",
    "author": "Фёдор Михайлович Достоевский",
    "isbn": "9789750516146",
    "year": "2014"
  }
]
```

##### ➕ ISBN ile Kitap Ekle

```bash
POST http://localhost:8000/books
Content-Type: application/json

{
  "isbn": "9789750516146"
}
```

**Başarılı Yanıt:**
```json
{
  "title": "Suc ve Ceza",
  "author": "Фёдор Михайлович Достоевский",
  "isbn": "9789750516146",
  "year": "2014"
}
```

##### ❌ Kitap Sil

```bash
DELETE http://localhost:8000/books/9789750516146
```

**Başarılı Yanıt:**
```json
{
  "message": "'Suc ve Ceza' kitabı başarıyla silindi"
}
```

### 🐍 Python Modülü Olarak Kullanım

```python
from library import Library
from book import Book

# Kütüphane oluştur
library = Library()

# ISBN ile kitap ekle
book = library.add_book_by_isbn("9789750516146")

# Manuel kitap ekle
manual_book = Book("Kitap Adı", "Yazar Adı", "1234567890", "2023")
library.add_book(manual_book)

# Kitapları listele
for book in library.list_books():
    print(book)

# Kitap sil
library.remove_book("1234567890")
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

- `9789750516146` - Suç ve Ceza
- `9789750714191` - Beyaz Diş
- `9789753628920` - Yabancı
- `9789750737848` - Fahrenheit 451

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
