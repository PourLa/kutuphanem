from library import Library
from book import Book
import logging

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_menu():
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


def get_valid_input(prompt, validation_func=None):
    """Geçerli kullanıcı girişi alır"""
    while True:
        try:
            user_input = input(prompt).strip()
            if validation_func and not validation_func(user_input):
                print("Geçersiz giriş. Lütfen tekrar deneyin.")
                continue
            return user_input
        except (KeyboardInterrupt, EOFError):
            print("\n\nProgramdan çıkılıyor...")
            exit(0)
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            continue


def validate_isbn(isbn):
    """ISBN doğrulama"""
    return len(isbn) >= 10  # Basit doğrulama


def main():
    library = Library()

    while True:
        try:
            display_menu()
            choice = get_valid_input("Seçiminiz (1-6): ")

            if choice == "1":
                isbn = get_valid_input("Kitap ISBN: ", validate_isbn)
                book = library.add_book_by_isbn(isbn)
                if book:
                    print(f"✅ '{book.title}' kitabı başarıyla eklendi.")
                else:
                    print("❌ Kitap bulunamadı veya bir hata oluştu.")

            elif choice == "2":
                title = get_valid_input("Kitap Başlığı: ", lambda x: len(x) > 0)
                author = get_valid_input("Yazar: ", lambda x: len(x) > 0)
                isbn = get_valid_input("ISBN: ", validate_isbn)
                year = get_valid_input("Yıl (opsiyonel): ") or "Bilinmeyen Yıl"

                book = Book(title, author, isbn, year)
                library.add_book(book)
                print(f"✅ '{title}' kitabı başarıyla eklendi.")

            elif choice == "3":
                isbn = get_valid_input("Silmek istediğiniz kitabın ISBN'si: ", validate_isbn)
                book = library.find_book(isbn)
                if book:
                    library.remove_book(isbn)
                    print(f"✅ '{book.title}' kitabı başarıyla silindi.")
                else:
                    print("❌ Bu ISBN ile kayıtlı kitap bulunamadı.")

            elif choice == "4":
                books = library.list_books()
                if books:
                    print(f"\n📖 Tüm Kitaplar ({len(books)} adet)")
                    print("-" * 80)
                    for i, book in enumerate(books, 1):
                        print(f"{i:2d}. {book}")
                    print("-" * 80)
                else:
                    print("ℹ️  Kütüphanede kitap bulunmamaktadır.")

            elif choice == "5":
                isbn = get_valid_input("Aramak istediğiniz kitabın ISBN'si: ", validate_isbn)
                book = library.find_book(isbn)
                if book:
                    print(f"✅ Kitap bulundu: {book}")
                else:
                    print("❌ Bu ISBN ile kayıtlı kitap bulunamadı.")

            elif choice == "6":
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