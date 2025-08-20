from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from library import Library
from book import Book
import logging
from typing import List

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kütüphane API",
    description="Kütüphane yönetimi için REST API",
    version="1.0.0"
)


# Dependency fonksiyonu
def get_library():
    return Library()


class ISBNRequest(BaseModel):
    isbn: str


class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str
    year: str

    @classmethod
    def from_book(cls, book: Book):
        return cls(
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            year=book.year
        )


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Kütüphane API'ye hoş geldiniz!", "docs": "/docs"}


@app.get("/books", response_model=List[BookResponse])
def get_books(library: Library = Depends(get_library)):
    """Tüm kitapları listeler"""
    try:
        books = library.list_books()
        return [BookResponse.from_book(book) for book in books]
    except Exception as e:
        logger.error(f"Kitaplar listelenirken hata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/books", response_model=BookResponse)
def add_book(isbn_request: ISBNRequest, library: Library = Depends(get_library)):
    """ISBN ile kitap ekler"""
    try:
        isbn = isbn_request.isbn

        # Önce kitabın zaten var olup olmadığını kontrol et
        existing_book = library.find_book(isbn)
        if existing_book:
            raise HTTPException(
                status_code=400,
                detail="Bu ISBN ile zaten bir kitap mevcut"
            )

        # Kitabı ekle
        book = library.add_book_by_isbn(isbn)
        if book:
            logger.info(f"Kitap eklendi: {book.title}")
            return BookResponse.from_book(book)
        else:
            raise HTTPException(
                status_code=404,
                detail="ISBN ile kitap bulunamadı"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kitap eklenirken hata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/books/{isbn}")
def delete_book(isbn: str, library: Library = Depends(get_library)):
    """ISBN ile kitap siler"""
    try:
        book = library.find_book(isbn)
        if not book:
            raise HTTPException(status_code=404, detail="Kitap bulunamadı")

        success = library.remove_book(isbn)
        if success:
            logger.info(f"Kitap silindi: {book.title}")
            return {"message": f"'{book.title}' kitabı başarıyla silindi"}
        else:
            raise HTTPException(status_code=404, detail="Kitap silinemedi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kitap silinirken hata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )