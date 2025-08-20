import json
import os
import httpx
from book import Book
from bs4 import BeautifulSoup
import re
from typing import List, Optional
import logging

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Library:
    def __init__(self, filename: str = "library.json"):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()

    def add_book(self, book: Book) -> None:
        """Kitap ekler ve dosyaya kaydeder"""
        self.books.append(book)
        self.save_books()

    def add_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """ISBN ile kitap ekler"""
        # ISBN temizleme
        isbn = self._clean_isbn(isbn)

        # Önce kitabın zaten var olup olmadığını kontrol et
        if self.find_book(isbn):
            logger.warning(f"ISBN {isbn} zaten kütüphanede mevcut")
            return None

        # Önce Open Library API'sini dene
        book = self._get_book_from_open_library(isbn)
        if book:
            return book

        # Eğer Open Library'de bulunamazsa, ISBN Search'ü dene
        book = self._get_book_from_isbnsearch(isbn)
        if book:
            return book

        logger.error(f"'{isbn}' numaralı kitap hiçbir kaynaktan bulunamadı.")
        return None

    def _clean_isbn(self, isbn: str) -> str:
        """ISBN'yi temizler ve standartlaştırır"""
        return re.sub(r'[^0-9X]', '', isbn.upper())

    def _get_book_from_open_library(self, isbn: str) -> Optional[Book]:
        """Open Library API'sinden kitap bilgilerini alır"""
        try:
            response = httpx.get(
                f"https://openlibrary.org/isbn/{isbn}.json",
                timeout=10.0,
                follow_redirects=True
            )
            response.raise_for_status()

            book_data = response.json()
            title = book_data.get("title", "Bilinmeyen Başlık")

            # Yıl bilgisini al
            publish_date = book_data.get("publish_date", "")
            year = self._extract_year_from_date(publish_date)

            # Yazar bilgisini al
            author = self._get_authors_from_open_library(book_data.get("authors", []))

            # Kitabı oluştur ama HEMEN EKLEME!
            book = Book(title, author, isbn, year)

            # Kitabı ekle ve return et
            self.add_book(book)
            logger.info(f"Open Library: '{title}' kitabı başarıyla eklendi.")
            return book

        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
            logger.info(f"Open Library API hatası: {e}")
            return None

    def _get_authors_from_open_library(self, author_objects: list) -> str:
        """Open Library'den yazar bilgilerini alır"""
        author_names = []

        for author_obj in author_objects:
            author_key = author_obj.get("key")
            if author_key:
                try:
                    author_response = httpx.get(
                        f"https://openlibrary.org{author_key}.json",
                        timeout=5.0
                    )
                    if author_response.status_code == 200:
                        author_data = author_response.json()
                        author_names.append(author_data.get("name", "Bilinmeyen Yazar"))
                except (httpx.RequestError, json.JSONDecodeError):
                    continue

        return ", ".join(author_names) if author_names else "Bilinmeyen Yazar"

    def _extract_year_from_date(self, date_string: str) -> str:
        """Tarih string'inden yıl bilgisini çıkarır"""
        if not date_string:
            return "Bilinmeyen Yıl"

        # Yıl formatını bul (4 haneli sayı)
        year_match = re.search(r'\b(\d{4})\b', date_string)
        if year_match:
            return year_match.group(1)

        return "Bilinmeyen Yıl"

    def _get_book_from_isbnsearch(self, isbn: str) -> Optional[Book]:
        """ISBN Search'ten kitap bilgilerini alır"""
        try:
            response = httpx.get(
                f"https://isbnsearch.org/isbn/{isbn}",
                timeout=10.0
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Başlık
            title_element = soup.find("h2")
            title = title_element.get_text(strip=True) if title_element else "Bilinmeyen Başlık"

            # Yazar
            author_element = soup.find("p", string=lambda s: s and "Author:" in s)
            author = "Bilinmeyen Yazar"
            if author_element:
                author_text = author_element.get_text(strip=True)
                match = re.search(r"Author:\s*(.*)", author_text)
                if match:
                    author = match.group(1).strip()

            # Yıl
            year_element = soup.find("p", string=lambda s: s and "Publication date:" in s)
            year = "Bilinmeyen Yıl"
            if year_element:
                year_text = year_element.get_text(strip=True)
                match = re.search(r"Publication date:\s*(.*)", year_text)
                if match:
                    year = self._extract_year_from_date(match.group(1).strip())

            # Veri kontrolü
            if title == "Bilinmeyen Başlık" and author == "Bilinmeyen Yazar":
                return None

            book = Book(title, author, isbn, year)
            self.add_book(book)
            logger.info(f"ISBN Search: '{title}' kitabı başarıyla eklendi.")
            return book

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.info(f"ISBN Search hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"ISBN Search beklenmedik hata: {e}")
            return None

    def remove_book(self, isbn: str) -> bool:
        """ISBN ile kitap siler"""
        initial_count = len(self.books)
        self.books = [book for book in self.books if book.isbn != isbn]

        if len(self.books) < initial_count:
            self.save_books()
            return True
        return False

    def list_books(self) -> List[Book]:
        """Tüm kitapları listeler"""
        return self.books.copy()  # Return a copy to prevent external modification

    def find_book(self, isbn: str) -> Optional[Book]:
        """ISBN ile kitap bulur"""
        isbn = self._clean_isbn(isbn)
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def load_books(self) -> None:
        """Kitapları dosyadan yükler"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    books_data = json.load(file)
                    self.books = []
                    for book_data in books_data:
                        # Eski kayıtlarla uyumluluk için
                        if "year" not in book_data:
                            book_data["year"] = "Bilinmeyen Yıl"
                        self.books.append(Book.from_dict(book_data))
                logger.info(f"{len(self.books)} kitap yüklendi.")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Kitaplar yüklenirken hata: {e}")
                self.books = []
        else:
            self.books = []

    def save_books(self) -> None:
        """Kitapları dosyaya kaydeder"""
        try:
            books_data = [book.to_dict() for book in self.books]
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(books_data, file, indent=4, ensure_ascii=False)
            logger.info(f"{len(self.books)} kitap kaydedildi.")
        except Exception as e:
            logger.error(f"Kitaplar kaydedilirken hata: {e}")