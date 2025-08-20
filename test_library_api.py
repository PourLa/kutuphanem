import pytest
import os
import json
from library import Library
from book import Kitap
import httpx
from unittest.mock import Mock, patch
import logging

# Testler için logging'ı devre dışı bırak
logging.disable(logging.CRITICAL)

@pytest.fixture
def kutuphane_ayarla():
    """Test için kütüphane örneği oluşturur"""
    test_dosya_adi = f"test_kutuphane_{os.getpid()}.json"
    kutuphane = Library(test_dosya_adi)
    yield kutuphane
    # Test sonrası temizlik
    if os.path.exists(test_dosya_adi):
        os.remove(test_dosya_adi)


def test_isbn_ile_kitap_ekle_basarili(kutuphane_ayarla):
    """Başarılı kitap ekleme testi"""
    kutuphane = kutuphane_ayarla

    mock_yanit = Mock()
    mock_yanit.status_code = 200
    mock_yanit.json.return_value = {
        "title": "Test Kitabı",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": "2020"
    }
    mock_yazar_yaniti = Mock()
    mock_yazar_yaniti.status_code = 200
    mock_yazar_yaniti.json.return_value = {"name": "Test Yazarı"}

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = [mock_yanit, mock_yazar_yaniti]
        kitap = kutuphane.isbn_ile_kitap_ekle("1234567890")

    assert kitap is not None
    assert kitap.baslik == "Test Kitabı"
    assert kitap.yazar == "Test Yazarı"
    assert kitap.isbn == "1234567890"
    assert kitap.yil == "2020"
    assert len(kutuphane.kitaplar) == 1


def test_isbn_ile_kitap_ekle_basarisiz(kutuphane_ayarla):
    """API hatası testi"""
    kutuphane = kutuphane_ayarla

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "404 Bulunamadı",
            request=Mock(),
            response=Mock(status_code=404)
        )
        kitap = kutuphane.isbn_ile_kitap_ekle("1234567890")

    assert kitap is None
    assert len(kutuphane.kitaplar) == 0


def test_isbn_ile_kitap_ekle_zaman_asimi(kutuphane_ayarla):
    """Zaman aşımı testi"""
    kutuphane = kutuphane_ayarla

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = httpx.TimeoutException("İstek zaman aşımına uğradı")
        kitap = kutuphane.isbn_ile_kitap_ekle("1234567890")

    assert kitap is None
    assert len(kutuphane.kitaplar) == 0


def test_mevcut_kitap_ekle(kutuphane_ayarla):
    """Mevcut kitap ekleme testi"""
    kutuphane = kutuphane_ayarla

    # Önce bir kitap ekle
    kitap = Kitap("Mevcut Kitap", "Yazar", "1234567890", "2020")
    kutuphane.kitap_ekle(kitap)

    # Aynı ISBN ile tekrar eklemeye çalış
    sonuc = kutuphane.isbn_ile_kitap_ekle("1234567890")
    assert sonuc is None
    assert len(kutuphane.kitaplar) == 1  # Hala 1 kitap olmalı


def test_kitap_sil(kutuphane_ayarla):
    """Kitap silme testi"""
    kutuphane = kutuphane_ayarla

    # Kitap ekle
    kitap = Kitap("Test Kitabı", "Yazar", "1234567890", "2020")
    kutuphane.kitap_ekle(kitap)
    assert len(kutuphane.kitaplar) == 1

    # Kitabı sil
    basarili = kutuphane.kitap_sil("1234567890")
    assert basarili is True
    assert len(kutuphane.kitaplar) == 0

    # Olmayan kitabı sil
    basarili = kutuphane.kitap_sil("9999999999")
    assert basarili is False


def test_kitap_bul(kutuphane_ayarla):
    """Kitap bulma testi"""
    kutuphane = kutuphane_ayarla

    # Kitap ekle
    kitap = Kitap("Test Kitabı", "Yazar", "1234567890", "2020")
    kutuphane.kitap_ekle(kitap)

    # Kitabı bul
    bulunan = kutuphane.kitap_bul("1234567890")
    assert bulunan is not None
    assert bulunan.baslik == "Test Kitabı"

    # Olmayan kitabı bul
    bulunamayan = kutuphane.kitap_bul("9999999999")
    assert bulunamayan is None


def test_kitaplari_kaydet_ve_yukle(kutuphane_ayarla):
    """Kaydetme ve yükleme testi"""
    kutuphane = kutuphane_ayarla

    # Kitap ekle
    kitap = Kitap("Test Kitabı", "Test Yazarı", "1234567890", "2020")
    kutuphane.kitap_ekle(kitap)

    # Yeni kütüphane örneği oluştur ve yükle
    yeni_kutuphane = Library(kutuphane.dosya_adi)
    yeni_kutuphane.kitaplari_yukle()

    assert len(yeni_kutuphane.kitaplar) == 1
    assert yeni_kutuphane.kitaplar[0].baslik == "Test Kitabı"
    assert yeni_kutuphane.kitaplar[0].yil == "2020"


def test_geriye_donuk_uyumluluk(kutuphane_ayarla):
    """Geriye dönük uyumluluk testi"""
    # Eski formatı test et (yıl alanı olmadan)
    eski_format_veri = [{"baslik": "Eski Kitap", "yazar": "Eski Yazar", "isbn": "1234567894"}]

    with open(kutuphane_ayarla.dosya_adi, "w", encoding="utf-8") as f:
        json.dump(eski_format_veri, f)

    kutuphane = kutuphane_ayarla
    kutuphane.kitaplari_yukle()

    assert len(kutuphane.kitaplar) == 1
    assert kutuphane.kitaplar[0].baslik == "Eski Kitap"
    assert kutuphane.kitaplar[0].yil == "Bilinmeyen Yıl"  # Varsayılan değer


def test_isbn_temizle(kutuphane_ayarla):
    """ISBN temizleme testi"""
    kutuphane = kutuphane_ayarla

    # Farklı ISBN formatlarını test et
    test_durumlari = [
        ("978-975-0516-14-6", "9789750516146"),
        ("978 975 0516 14 6", "9789750516146"),
        ("9789750516146", "9789750516146"),
        ("123-456-789-X", "123456789X"),
    ]

    for kirli_isbn, beklenen_temiz in test_durumlari:
        temizlenmis = kutuphane._isbn_temizle(kirli_isbn)
        assert temizlenmis == beklenen_temiz


def test_tarihten_yil_al(kutuphane_ayarla):
    """Yıl çıkarma testi"""
    kutuphane = kutuphane_ayarla

    test_durumlari = [
        ("2020", "2020"),
        ("15 Ocak 2020", "2020"),
        ("2020-01-15", "2020"),
        ("15.01.2020", "2020"),
        ("Geçersiz tarih", "Bilinmeyen Yıl"),
        ("", "Bilinmeyen Yıl"),
        (None, "Bilinmeyen Yıl"),
    ]

    for tarih_string, beklenen_yil in test_durumlari:
        yil = kutuphane._tarihten_yil_al(tarih_string)
        assert yil == beklenen_yil
