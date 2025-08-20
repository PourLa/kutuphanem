class Kitap:
    def __init__(self, baslik, yazar, isbn, yil="Bilinmeyen Yıl"):
        self.baslik = baslik
        self.yazar = yazar
        self.isbn = isbn
        self.yil = yil

    def __str__(self):
        return f"{self.baslik} - {self.yazar} ({self.yil}) (ISBN: {self.isbn})"

    def __repr__(self):
        return f"Kitap(baslik='{self.baslik}', yazar='{self.yazar}', isbn='{self.isbn}', yil='{self.yil}')"

    def sozluge_cevir(self):
        """Kitap bilgilerini sözlük formatına çevirir"""
        return {
            "baslik": self.baslik,
            "yazar": self.yazar,
            "isbn": self.isbn,
            "yil": self.yil
        }

    @classmethod
    def sozlukten_olustur(cls, veri):
        """Sözlükten kitap nesnesi oluşturur"""
        return cls(
            baslik=veri["baslik"],
            yazar=veri["yazar"],
            isbn=veri["isbn"],
            yil=veri.get("yil", "Bilinmeyen Yıl")
        )
