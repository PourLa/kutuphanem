class Book:
    def __init__(self, title, author, isbn, year="Bilinmeyen Yıl"):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year

    def __str__(self):
        return f"{self.title} by {self.author} ({self.year}) (ISBN: {self.isbn})"

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', isbn='{self.isbn}', year='{self.year}')"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "year": self.year
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            year=data.get("year", "Bilinmeyen Yıl")
        )