from typing import List
from uuid import uuid4

from whoosh.index import FileIndex

from server.utils import buildindex


class Book:
    book_id: str = None
    name: str = None
    ix: FileIndex = None

    def __init__(self, book_id: str, name: str, ix: FileIndex) -> None:
        self.book_id = str(book_id)
        self.name = name
        self.ix = ix

    @classmethod
    def create(cls, name: str, content: bytes):
        book_id = str(uuid4())
        ix = buildindex(book_id, content)

        if ix:
            return cls(book_id, name, ix)
        else:
            return None


class Books:
    book_list: List[Book] = []

    def add(self, book: Book):
        self.book_list.append(book)

    def get_by_id(self, book_id: str):
        for book in self.book_list:
            if book.book_id == book_id:
                return book

        return None

    def get_by_name(self, name: str):
        for book in self.book_list:
            if book.name == name:
                return book

        return None

    def books(self):
        return [{"book_id": book.book_id, "name": book.name} for book in self.book_list]

    def names(self):
        return [book.name for book in self.book_list]

    def ids(self):
        return [book.book_id for book in self.book_list]

    def exists(self, book_id: str):
        return book_id in self.ids()
