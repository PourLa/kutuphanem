from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from library import Library
from book import Kitap
import logging
from typing import List

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kütüphane API",
    description="Kütüphane yönetimi için REST API",
    version="1.0.0"
)


# Bağımlılık fonksiyonu
def get_library():
    return Library()


class ISBNIstek(BaseModel):
    isbn: str


class KitapYanit(BaseModel):
    baslik: str
    yazar: str
    isbn: str
    yil: str

    @classmethod
    def kitaptan_olustur(cls, kitap: Kitap):
        return cls(
            baslik=kitap.baslik,
            yazar=kitap.yazar,
            isbn=kitap.isbn,
            yil=kitap.yil
        )


@app.get("/", include_in_schema=False)
async def kok():
    return {"mesaj": "Kütüphane API'ye hoş geldiniz!", "dokümanlar": "/docs"}


@app.get("/kitaplar", response_model=List[KitapYanit])
def kitaplari_getir(kutuphane: Library = Depends(get_library)):
    """Tüm kitapları listeler"""
    try:
        kitaplar = kutuphane.kitaplari_listele()
        return [KitapYanit.kitaptan_olustur(kitap) for kitap in kitaplar]
    except Exception as e:
        logger.error(f"Kitaplar listelenirken hata oluştu: {e}")
        raise HTTPException(status_code=500, detail="Sunucu hatası")


@app.post("/kitaplar", response_model=KitapYanit)
def kitap_ekle(isbn_istek: ISBNIstek, kutuphane: Library = Depends(get_library)):
    """ISBN ile kitap ekler"""
    try:
        isbn = isbn_istek.isbn

        # Önce kitabın zaten var olup olmadığını kontrol et
        mevcut_kitap = kutuphane.kitap_bul(isbn)
        if mevcut_kitap:
            raise HTTPException(
                status_code=400,
                detail="Bu ISBN ile zaten bir kitap mevcut"
            )

        # Kitabı ekle
        kitap = kutuphane.isbn_ile_kitap_ekle(isbn)
        if kitap:
            logger.info(f"Kitap eklendi: {kitap.baslik}")
            return KitapYanit.kitaptan_olustur(kitap)
        else:
            raise HTTPException(
                status_code=404,
                detail="ISBN ile kitap bulunamadı"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kitap eklenirken hata oluştu: {e}")
        raise HTTPException(status_code=500, detail="Sunucu hatası")


@app.delete("/kitaplar/{isbn}")
def kitap_sil(isbn: str, kutuphane: Library = Depends(get_library)):
    """ISBN ile kitap siler"""
    try:
        kitap = kutuphane.kitap_bul(isbn)
        if not kitap:
            raise HTTPException(status_code=404, detail="Kitap bulunamadı")

        basarili = kutuphane.kitap_sil(isbn)
        if basarili:
            logger.info(f"Kitap silindi: {kitap.baslik}")
            return {"mesaj": f"'{kitap.baslik}' kitabı başarıyla silindi"}
        else:
            raise HTTPException(status_code=404, detail="Kitap silinemedi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kitap silinirken hata oluştu: {e}")
        raise HTTPException(status_code=500, detail="Sunucu hatası")


@app.get("/saglik", include_in_schema=False)
async def saglik_kontrol():
    """Sistem durumu kontrol endpoint'i"""
    return {"durum": "SAGLIKLI"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
