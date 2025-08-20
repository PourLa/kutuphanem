import json
import os
import httpx
from book import Kitap
from bs4 import BeautifulSoup
import re
from typing import List, Optional
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Library:
    def __init__(self, dosya_adi: str = "kutuphane.json"):
        self.dosya_adi = dosya_adi
        self.kitaplar: List[Kitap] = []
        self.kitaplari_yukle()

    def kitap_ekle(self, kitap: Kitap) -> None:
        """Kitap ekler ve dosyaya kaydeder"""
        self.kitaplar.append(kitap)
        self.kitaplari_kaydet()

    def isbn_ile_kitap_ekle(self, isbn: str) -> Optional[Kitap]:
        """ISBN ile kitap ekler"""
        # ISBN temizleme
        isbn = self._isbn_temizle(isbn)

        # Önce kitabın zaten var olup olmadığını kontrol et
        if self.kitap_bul(isbn):
            logger.warning(f"ISBN {isbn} zaten kütüphanede mevcut")
            return None

        # Önce Open Library API'sini dene
        kitap = self._open_library_den_kitap_al(isbn)
        if kitap:
            return kitap

        # Eğer Open Library'de bulunamazsa, ISBN Search'ü dene
        kitap = self._isbn_search_den_kitap_al(isbn)
        if kitap:
            return kitap

        logger.error(f"'{isbn}' numaralı kitap hiçbir kaynaktan bulunamadı.")
        return None

    def _isbn_temizle(self, isbn: str) -> str:
        """ISBN'yi temizler ve standartlaştırır"""
        return re.sub(r'[^0-9X]', '', isbn.upper())

    def _open_library_den_kitap_al(self, isbn: str) -> Optional[Kitap]:
        """Open Library API'sinden kitap bilgilerini alır"""
        try:
            yanit = httpx.get(
                f"https://openlibrary.org/isbn/{isbn}.json",
                timeout=10.0,
                follow_redirects=True
            )
            yanit.raise_for_status()

            kitap_verisi = yanit.json()
            baslik = kitap_verisi.get("title", "Bilinmeyen Başlık")

            # Yıl bilgisini al
            yayin_tarihi = kitap_verisi.get("publish_date", "")
            yil = self._tarihten_yil_al(yayin_tarihi)

            # Yazar bilgisini al
            yazar = self._open_library_yazarlari_al(kitap_verisi.get("authors", []))

            # Kitabı oluştur ama HEMEN EKLEME!
            kitap = Kitap(baslik, yazar, isbn, yil)

            # Kitabı ekle ve return et
            self.kitap_ekle(kitap)
            logger.info(f"Open Library: '{baslik}' kitabı başarıyla eklendi.")
            return kitap

        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
            logger.info(f"Open Library API hatası: {e}")
            return None

    def _open_library_yazarlari_al(self, yazar_nesneleri: list) -> str:
        """Open Library'den yazar bilgilerini alır"""
        yazar_isimleri = []

        for yazar_nesne in yazar_nesneleri:
            yazar_anahtari = yazar_nesne.get("key")
            if yazar_anahtari:
                try:
                    yazar_yaniti = httpx.get(
                        f"https://openlibrary.org{yazar_anahtari}.json",
                        timeout=5.0
                    )
                    if yazar_yaniti.status_code == 200:
                        yazar_verisi = yazar_yaniti.json()
                        yazar_isimleri.append(yazar_verisi.get("name", "Bilinmeyen Yazar"))
                except (httpx.RequestError, json.JSONDecodeError):
                    continue

        return ", ".join(yazar_isimleri) if yazar_isimleri else "Bilinmeyen Yazar"

    def _tarihten_yil_al(self, tarih_string: str) -> str:
        """Tarih string'inden yıl bilgisini çıkarır"""
        if not tarih_string:
            return "Bilinmeyen Yıl"

        # Yıl formatını bul (4 haneli sayı)
        yil_eslesme = re.search(r'\b(\d{4})\b', tarih_string)
        if yil_eslesme:
            return yil_eslesme.group(1)

        return "Bilinmeyen Yıl"

    def _isbn_search_den_kitap_al(self, isbn: str) -> Optional[Kitap]:
        """ISBN Search'ten kitap bilgilerini alır"""
        try:
            yanit = httpx.get(
                f"https://isbnsearch.org/isbn/{isbn}",
                timeout=10.0
            )
            yanit.raise_for_status()

            corba = BeautifulSoup(yanit.text, "lxml")

            # Başlık
            baslik_elemani = corba.find("h2")
            baslik = baslik_elemani.get_text(strip=True) if baslik_elemani else "Bilinmeyen Başlık"

            # Yazar
            yazar_elemani = corba.find("p", string=lambda s: s and "Author:" in s)
            yazar = "Bilinmeyen Yazar"
            if yazar_elemani:
                yazar_metni = yazar_elemani.get_text(strip=True)
                eslesme = re.search(r"Author:\s*(.*)", yazar_metni)
                if eslesme:
                    yazar = eslesme.group(1).strip()

            # Yıl
            yil_elemani = corba.find("p", string=lambda s: s and "Publication date:" in s)
            yil = "Bilinmeyen Yıl"
            if yil_elemani:
                yil_metni = yil_elemani.get_text(strip=True)
                eslesme = re.search(r"Publication date:\s*(.*)", yil_metni)
                if eslesme:
                    yil = self._tarihten_yil_al(eslesme.group(1).strip())

            # Veri kontrolü
            if baslik == "Bilinmeyen Başlık" and yazar == "Bilinmeyen Yazar":
                return None

            kitap = Kitap(baslik, yazar, isbn, yil)
            self.kitap_ekle(kitap)
            logger.info(f"ISBN Search: '{baslik}' kitabı başarıyla eklendi.")
            return kitap

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.info(f"ISBN Search hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"ISBN Search beklenmedik hata: {e}")
            return None

    def kitap_sil(self, isbn: str) -> bool:
        """ISBN ile kitap siler"""
        baslangic_sayisi = len(self.kitaplar)
        self.kitaplar = [kitap for kitap in self.kitaplar if kitap.isbn != isbn]

        if len(self.kitaplar) < baslangic_sayisi:
            self.kitaplari_kaydet()
            return True
        return False

    def kitaplari_listele(self) -> List[Kitap]:
        """Tüm kitapları listeler"""
        return self.kitaplar.copy()  # Dışarıdan değişikliği önlemek için kopya döndür

    def kitap_bul(self, isbn: str) -> Optional[Kitap]:
        """ISBN ile kitap bulur"""
        isbn = self._isbn_temizle(isbn)
        for kitap in self.kitaplar:
            if kitap.isbn == isbn:
                return kitap
        return None

    def kitaplari_yukle(self) -> None:
        """Kitapları dosyadan yükler"""
        if os.path.exists(self.dosya_adi):
            try:
                with open(self.dosya_adi, 'r', encoding='utf-8') as dosya:
                    kitaplar_verisi = json.load(dosya)
                    self.kitaplar = []
                    for kitap_verisi in kitaplar_verisi:
                        # Eski kayıtlarla uyumluluk için
                        if "yil" not in kitap_verisi:
                            kitap_verisi["yil"] = "Bilinmeyen Yıl"
                        self.kitaplar.append(Kitap.sozlukten_olustur(kitap_verisi))
                logger.info(f"{len(self.kitaplar)} kitap yüklendi.")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Kitaplar yüklenirken hata: {e}")
                self.kitaplar = []
        else:
            self.kitaplar = []

    def kitaplari_kaydet(self) -> None:
        """Kitapları dosyaya kaydeder"""
        try:
            kitaplar_verisi = [kitap.sozluge_cevir() for kitap in self.kitaplar]
            with open(self.dosya_adi, 'w', encoding='utf-8') as dosya:
                json.dump(kitaplar_verisi, dosya, indent=4, ensure_ascii=False)
            logger.info(f"{len(self.kitaplar)} kitap kaydedildi.")
        except Exception as e:
            logger.error(f"Kitaplar kaydedilirken hata: {e}")
