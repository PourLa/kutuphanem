import pytest
from fastapi.testclient import TestClient
from api import app, get_library
from library import Library
from book import Kitap
from unittest.mock import Mock, patch
import os

# Test için global library instance
_test_kutuphane_ornegi = None

def override_get_library():
    """Test için library dependency override"""
    global _test_kutuphane_ornegi
    if _test_kutuphane_ornegi is None:
        test_dosya_adi = f"test_api_kutuphane_{os.getpid()}.json"
        _test_kutuphane_ornegi = Library(test_dosya_adi)
        _test_kutuphane_ornegi.kitaplar = []
        _test_kutuphane_ornegi.kitaplari_kaydet()
    return _test_kutuphane_ornegi

# Dependency override
app.dependency_overrides[get_library] = override_get_library

client = TestClient(app)

@pytest.fixture(autouse=True)
def temiz_kutuphane():
    """Her testten önce library'yi temizle"""
    global _test_kutuphane_ornegi
    if _test_kutuphane_ornegi:
        _test_kutuphane_ornegi.kitaplar = []
        _test_kutuphane_ornegi.kitaplari_kaydet()
    yield
    # Test sonrası temizlik
    if _test_kutuphane_ornegi and os.path.exists(_test_kutuphane_ornegi.dosya_adi):
        os.remove(_test_kutuphane_ornegi.dosya_adi)
        _test_kutuphane_ornegi = None

def test_bos_kitaplari_getir():
    """Boş kütüphane testi"""
    yanit = client.get("/kitaplar")
    assert yanit.status_code == 200
    assert yanit.json() == []

def test_kitap_ekle_ve_getir():
    """Kitap ekleme ve listeleme testi"""
    # Mock API response
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

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_yanit, mock_yazar_yaniti]
        yanit = client.post("/kitaplar", json={"isbn": "1111111111"})

    assert yanit.status_code == 200
    yanit_verisi = yanit.json()
    assert yanit_verisi["baslik"] == "Test Kitabı"
    assert yanit_verisi["yazar"] == "Test Yazarı"
    assert yanit_verisi["isbn"] == "1111111111"
    assert yanit_verisi["yil"] == "2020"

    # Kitapları listele
    yanit = client.get("/kitaplar")
    assert yanit.status_code == 200
    kitaplar = yanit.json()
    assert len(kitaplar) == 1
    assert kitaplar[0]["baslik"] == "Test Kitabı"

def test_mevcut_kitap_ekle():
    """Mevcut kitap ekleme testi"""
    # Önce bir kitap ekle
    kutuphane = override_get_library()
    kitap = Kitap("Mevcut Kitap", "Test Yazarı", "2222222222", "2020")
    kutuphane.kitap_ekle(kitap)

    # Aynı ISBN ile tekrar eklemeye çalış
    yanit = client.post("/kitaplar", json={"isbn": "2222222222"})
    assert yanit.status_code == 400
    assert "zaten bir kitap mevcut" in yanit.json()["detail"]

def test_kitap_sil():
    """Kitap silme testi"""
    # Önce bir kitap ekle
    kutuphane = override_get_library()
    kitap = Kitap("Test Kitabı", "Test Yazarı", "3333333333", "2020")
    kutuphane.kitap_ekle(kitap)

    # Kitabı sil
    yanit = client.delete("/kitaplar/3333333333")
    assert yanit.status_code == 200
    assert "başarıyla silindi" in yanit.json()["mesaj"]

    # Olmayan bir kitabı silmeye çalış
    yanit = client.delete("/kitaplar/9999999999")
    assert yanit.status_code == 404

def test_bilinmeyen_yil_ile_kitap_ekle():
    """Bilinmeyen yıl testi"""
    mock_yanit = Mock()
    mock_yanit.status_code = 200
    mock_yanit.json.return_value = {
        "title": "Test Kitabı Bilinmeyen Yıl",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": ""
    }
    mock_yazar_yaniti = Mock()
    mock_yazar_yaniti.status_code = 200
    mock_yazar_yaniti.json.return_value = {"name": "Test Yazarı Bilinmeyen"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_yanit, mock_yazar_yaniti]
        yanit = client.post("/kitaplar", json={"isbn": "4444444444"})

    assert yanit.status_code == 200
    assert yanit.json()["yil"] == "Bilinmeyen Yıl"

def test_karmasik_tarih_formatli_kitap_ekle():
    """Karmaşık tarih formatı testi"""
    mock_yanit = Mock()
    mock_yanit.status_code = 200
    mock_yanit.json.return_value = {
        "title": "Test Kitabı Karmaşık Tarih",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": "15 Ocak 2020"
    }
    mock_yazar_yaniti = Mock()
    mock_yazar_yaniti.status_code = 200
    mock_yazar_yaniti.json.return_value = {"name": "Test Yazarı Karmaşık"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_yanit, mock_yazar_yaniti]
        yanit = client.post("/kitaplar", json={"isbn": "5555555555"})

    assert yanit.status_code == 200
    assert yanit.json()["yil"] == "2020"

def test_coklu_yazarlı_kitap_ekle():
    """Çoklu yazar testi"""
    mock_yanit = Mock()
    mock_yanit.status_code = 200
    mock_yanit.json.return_value = {
        "title": "Test Kitabı Çoklu Yazarlar",
        "authors": [
            {"key": "/authors/OL1234567A"},
            {"key": "/authors/OL7654321B"}
        ],
        "publish_date": "2015"
    }
    mock_yazar_yaniti1 = Mock()
    mock_yazar_yaniti1.status_code = 200
    mock_yazar_yaniti1.json.return_value = {"name": "İlk Yazar"}
    mock_yazar_yaniti2 = Mock()
    mock_yazar_yaniti2.status_code = 200
    mock_yazar_yaniti2.json.return_value = {"name": "İkinci Yazar"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_yanit, mock_yazar_yaniti1, mock_yazar_yaniti2]
        yanit = client.post("/kitaplar", json={"isbn": "6666666666"})

    assert yanit.status_code == 200
    assert "İlk Yazar, İkinci Yazar" in yanit.json()["yazar"]

def test_gecersiz_isbn_formatı():
    """Geçersiz ISBN formatı testi"""
    yanit = client.post("/kitaplar", json={"isbn": "gecersiz"})
    assert yanit.status_code == 404

def test_sunucu_hatasi_yonetimi():
    """Sunucu hatası testi"""
    with patch('library.Library.isbn_ile_kitap_ekle') as mock_method:
        mock_method.side_effect = Exception("Test hatası")
        yanit = client.post("/kitaplar", json={"isbn": "7777777777"})
        assert yanit.status_code == 500
