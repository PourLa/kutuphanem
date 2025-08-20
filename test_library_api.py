import pytest
import os
import json
from library import Library
from book import Book
import httpx
from unittest.mock import Mock, patch
import logging

# Testler için logging'ı devre dışı bırak
logging.disable(logging.CRITICAL)

@pytest.fixture
def setup_library():
    """Test için library instance'ı oluşturur"""
    test_filename = f"test_library_{os.getpid()}.json"
    library = Library(test_filename)
    yield library
    # Test sonrası temizlik
    if os.path.exists(test_filename):
        os.remove(test_filename)


def test_add_book_by_isbn_success(setup_library):
    """Başarılı kitap ekleme testi"""
    library = setup_library

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

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = [mock_response, mock_author_response]
        book = library.add_book_by_isbn("1234567890")

    assert book is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "1234567890"
    assert book.year == "2020"
    assert len(library.books) == 1


def test_add_book_by_isbn_failure(setup_library):
    """API hatası testi"""
    library = setup_library

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        book = library.add_book_by_isbn("1234567890")

    assert book is None
    assert len(library.books) == 0


def test_add_book_by_isbn_timeout(setup_library):
    """Timeout testi"""
    library = setup_library

    with patch('httpx.get') as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        book = library.add_book_by_isbn("1234567890")

    assert book is None
    assert len(library.books) == 0


def test_add_existing_book(setup_library):
    """Mevcut kitap ekleme testi"""
    library = setup_library

    # Önce bir kitap ekle
    book = Book("Existing Book", "Author", "1234567890", "2020")
    library.add_book(book)

    # Aynı ISBN ile tekrar eklemeye çalış
    result = library.add_book_by_isbn("1234567890")
    assert result is None
    assert len(library.books) == 1  # Hala 1 kitap olmalı


def test_remove_book(setup_library):
    """Kitap silme testi"""
    library = setup_library

    # Kitap ekle
    book = Book("Test Book", "Author", "1234567890", "2020")
    library.add_book(book)
    assert len(library.books) == 1

    # Kitabı sil
    success = library.remove_book("1234567890")
    assert success is True
    assert len(library.books) == 0

    # Olmayan kitabı sil
    success = library.remove_book("9999999999")
    assert success is False


def test_find_book(setup_library):
    """Kitap bulma testi"""
    library = setup_library

    # Kitap ekle
    book = Book("Test Book", "Author", "1234567890", "2020")
    library.add_book(book)

    # Kitabı bul
    found = library.find_book("1234567890")
    assert found is not None
    assert found.title == "Test Book"

    # Olmayan kitabı bul
    not_found = library.find_book("9999999999")
    assert not_found is None


def test_save_and_load_books(setup_library):
    """Kaydetme ve yükleme testi"""
    library = setup_library

    # Kitap ekle
    book = Book("Test Book", "Test Author", "1234567890", "2020")
    library.add_book(book)

    # Yeni library instance oluştur ve yükle
    new_library = Library(library.filename)
    new_library.load_books()

    assert len(new_library.books) == 1
    assert new_library.books[0].title == "Test Book"
    assert new_library.books[0].year == "2020"


def test_load_books_backward_compatibility(setup_library):
    """Geriye dönük uyumluluk testi"""
    # Eski formatı test et (year alanı olmadan)
    old_format_data = [{"title": "Old Book", "author": "Old Author", "isbn": "1234567894"}]

    with open(setup_library.filename, "w", encoding="utf-8") as f:
        json.dump(old_format_data, f)

    library = setup_library
    library.load_books()

    assert len(library.books) == 1
    assert library.books[0].title == "Old Book"
    assert library.books[0].year == "Bilinmeyen Yıl"  # Varsayılan değer


def test_clean_isbn(setup_library):
    """ISBN temizleme testi"""
    library = setup_library

    # Farklı ISBN formatlarını test et
    test_cases = [
        ("978-975-0516-14-6", "9789750516146"),
        ("978 975 0516 14 6", "9789750516146"),
        ("9789750516146", "9789750516146"),
        ("123-456-789-X", "123456789X"),
    ]

    for dirty_isbn, expected_clean in test_cases:
        cleaned = library._clean_isbn(dirty_isbn)
        assert cleaned == expected_clean


def test_extract_year_from_date(setup_library):
    """Yıl çıkarma testi"""
    library = setup_library

    test_cases = [
        ("2020", "2020"),
        ("January 15, 2020", "2020"),
        ("2020-01-15", "2020"),
        ("15.01.2020", "2020"),
        ("Invalid date", "Bilinmeyen Yıl"),
        ("", "Bilinmeyen Yıl"),
        (None, "Bilinmeyen Yıl"),
    ]

    for date_string, expected_year in test_cases:
        year = library._extract_year_from_date(date_string)
        assert year == expected_year