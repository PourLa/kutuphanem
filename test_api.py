import pytest
from fastapi.testclient import TestClient
from api import app, get_library
from library import Library
from book import Book
from unittest.mock import Mock, patch
import os

# Test için global library instance
_test_library_instance = None

def override_get_library():
    """Test için library dependency override"""
    global _test_library_instance
    if _test_library_instance is None:
        test_filename = f"test_api_library_{os.getpid()}.json"
        _test_library_instance = Library(test_filename)
        _test_library_instance.books = []
        _test_library_instance.save_books()
    return _test_library_instance

# Dependency override
app.dependency_overrides[get_library] = override_get_library

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_library():
    """Her testten önce library'yi temizle"""
    global _test_library_instance
    if _test_library_instance:
        _test_library_instance.books = []
        _test_library_instance.save_books()
    yield
    # Test sonrası temizlik
    if _test_library_instance and os.path.exists(_test_library_instance.filename):
        os.remove(_test_library_instance.filename)
        _test_library_instance = None

def test_get_books_empty():
    """Boş kütüphane testi"""
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_add_and_get_book():
    """Kitap ekleme ve listeleme testi"""
    # Mock API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Test Book",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": "2020"
    }

    mock_author_response = Mock()
    mock_author_response.status_code = 200
    mock_author_response.json.return_value = {"name": "Test Author"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_response, mock_author_response]
        response = client.post("/books", json={"isbn": "1111111111"})

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == "Test Book"
    assert response_data["author"] == "Test Author"
    assert response_data["isbn"] == "1111111111"
    assert response_data["year"] == "2020"

    # Kitapları listele
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == "Test Book"

def test_add_existing_book():
    """Mevcut kitap ekleme testi"""
    # Önce bir kitap ekle
    library = override_get_library()
    book = Book("Existing Book", "Test Author", "2222222222", "2020")
    library.add_book(book)

    # Aynı ISBN ile tekrar eklemeye çalış
    response = client.post("/books", json={"isbn": "2222222222"})
    assert response.status_code == 400
    assert "zaten bir kitap mevcut" in response.json()["detail"]

def test_delete_book():
    """Kitap silme testi"""
    # Önce bir kitap ekle
    library = override_get_library()
    book = Book("Test Book", "Test Author", "3333333333", "2020")
    library.add_book(book)

    # Kitabı sil
    response = client.delete("/books/3333333333")
    assert response.status_code == 200
    assert "başarıyla silindi" in response.json()["message"]

    # Olmayan bir kitabı silmeye çalış
    response = client.delete("/books/9999999999")
    assert response.status_code == 404

def test_add_book_with_unknown_year():
    """Bilinmeyen yıl testi"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Test Book Unknown Year",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": ""
    }
    mock_author_response = Mock()
    mock_author_response.status_code = 200
    mock_author_response.json.return_value = {"name": "Test Author Unknown"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_response, mock_author_response]
        response = client.post("/books", json={"isbn": "4444444444"})

    assert response.status_code == 200
    assert response.json()["year"] == "Bilinmeyen Yıl"

def test_add_book_with_complex_date():
    """Karmaşık tarih formatı testi"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Test Book Complex Date",
        "authors": [{"key": "/authors/OL1234567A"}],
        "publish_date": "January 15, 2020"
    }
    mock_author_response = Mock()
    mock_author_response.status_code = 200
    mock_author_response.json.return_value = {"name": "Test Author Complex"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_response, mock_author_response]
        response = client.post("/books", json={"isbn": "5555555555"})

    assert response.status_code == 200
    assert response.json()["year"] == "2020"

def test_add_book_with_multiple_authors():
    """Çoklu yazar testi"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Test Book Multiple Authors",
        "authors": [
            {"key": "/authors/OL1234567A"},
            {"key": "/authors/OL7654321B"}
        ],
        "publish_date": "2015"
    }
    mock_author_response1 = Mock()
    mock_author_response1.status_code = 200
    mock_author_response1.json.return_value = {"name": "First Author"}
    mock_author_response2 = Mock()
    mock_author_response2.status_code = 200
    mock_author_response2.json.return_value = {"name": "Second Author"}

    with patch('library.httpx.get') as mock_get:
        mock_get.side_effect = [mock_response, mock_author_response1, mock_author_response2]
        response = client.post("/books", json={"isbn": "6666666666"})

    assert response.status_code == 200
    assert "First Author, Second Author" in response.json()["author"]

def test_invalid_isbn_format():
    """Geçersiz ISBN formatı testi"""
    response = client.post("/books", json={"isbn": "invalid"})
    assert response.status_code == 404

def test_server_error_handling():
    """Sunucu hatası testi"""
    with patch('library.Library.add_book_by_isbn') as mock_method:
        mock_method.side_effect = Exception("Test error")
        response = client.post("/books", json={"isbn": "7777777777"})
        assert response.status_code == 500