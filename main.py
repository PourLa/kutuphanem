from library import Library
from book import Kitap
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def menuyu_goster():
    """Menüyü gösterir"""
    print("\n" + "=" * 50)
    print("📚 Kütüphane Yönetim Sistemi")
    print("=" * 50)
    print("1. Kitap Ekle (ISBN ile)")
    print("2. Kitap Ekle (Manuel)")
    print("3. Kitap Sil")
    print("4. Kitapları Listele")
    print("5. Kitap Ara")
    print("6. Çıkış")
    print("=" * 50)


def gecerli_giris_al(prompt, dogrulama_fonksiyonu=None):
    """Geçerli kullanıcı girişi alır"""
    while True:
        try:
            kullanici_girisi = input(prompt).strip()
            if dogrulama_fonksiyonu and not dogrulama_fonksiyonu(kullanici_girisi):
                print("Geçersiz giriş. Lütfen tekrar deneyin.")
                continue
            return kullanici_girisi
        except (KeyboardInterrupt, EOFError):
            print("\n\nProgramdan çıkılıyor...")
            exit(0)
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            continue


def isbn_dogrula(isbn):
    """ISBN doğrulama"""
    return len(isbn) >= 10  # Basit doğrulama


def main():
    kutuphane = Library()

    while True:
        try:
            menuyu_goster()
            secim = gecerli_giris_al("Seçiminiz (1-6): ")

            if secim == "1":
                isbn = gecerli_giris_al("Kitap ISBN: ", isbn_dogrula)
                kitap = kutuphane.isbn_ile_kitap_ekle(isbn)
                if kitap:
                    print(f"✅ '{kitap.baslik}' kitabı başarıyla eklendi.")
                else:
                    print("❌ Kitap bulunamadı veya bir hata oluştu.")

            elif secim == "2":
                baslik = gecerli_giris_al("Kitap Başlığı: ", lambda x: len(x) > 0)
                yazar = gecerli_giris_al("Yazar: ", lambda x: len(x) > 0)
                isbn = gecerli_giris_al("ISBN: ", isbn_dogrula)
                yil = gecerli_giris_al("Yıl (opsiyonel): ") or "Bilinmeyen Yıl"

                kitap = Kitap(baslik, yazar, isbn, yil)
                kutuphane.kitap_ekle(kitap)
                print(f"✅ '{baslik}' kitabı başarıyla eklendi.")

            elif secim == "3":
                isbn = gecerli_giris_al("Silmek istediğiniz kitabın ISBN'si: ", isbn_dogrula)
                kitap = kutuphane.kitap_bul(isbn)
                if kitap:
                    kutuphane.kitap_sil(isbn)
                    print(f"✅ '{kitap.baslik}' kitabı başarıyla silindi.")
                else:
                    print("❌ Bu ISBN ile kayıtlı kitap bulunamadı.")

            elif secim == "4":
                kitaplar = kutuphane.kitaplari_listele()
                if kitaplar:
                    print(f"\n📖 Tüm Kitaplar ({len(kitaplar)} adet)")
                    print("-" * 80)
                    for i, kitap in enumerate(kitaplar, 1):
                        print(f"{i:2d}. {kitap}")
                    print("-" * 80)
                else:
                    print("ℹ️  Kütüphanede kitap bulunmamaktadır.")

            elif secim == "5":
                isbn = gecerli_giris_al("Aramak istediğiniz kitabın ISBN'si: ", isbn_dogrula)
                kitap = kutuphane.kitap_bul(isbn)
                if kitap:
                    print(f"✅ Kitap bulundu: {kitap}")
                else:
                    print("❌ Bu ISBN ile kayıtlı kitap bulunamadı.")

            elif secim == "6":
                print("👋 Programdan çıkılıyor...")
                break

            else:
                print("❌ Geçersiz seçim. Lütfen 1-6 arasında bir sayı girin.")

        except KeyboardInterrupt:
            print("\n\n👋 Programdan çıkılıyor...")
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            print("❌ Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.")


if __name__ == "__main__":
    main()
