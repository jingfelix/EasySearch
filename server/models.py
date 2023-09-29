from typing import List
from uuid import uuid4

from whoosh.index import FileIndex

from server.utils import build_index


class BookFactory:
    @staticmethod
    def create_book(name: str, content: bytes):
        book_id = str(uuid4())
        ix = build_index(book_id, content)
        if ix:
            return Book(book_id, name, ix)
        else:
            raise ValueError("Failed to create book index")


class Book:
    def __init__(self, book_id: str, name: str, ix: FileIndex) -> None:
        self._book_id = str(book_id)
        self._name = name
        self._ix = ix

    @property
    def book_id(self):
        return self._book_id

    @property
    def name(self):
        return self._name

    @property
    def ix(self):
        return self._ix


class Books:
    def __init__(self):
        self._book_list: List[Book] = []

    def add_book(self, book: Book):
        self._book_list.append(book)

    def get_book_by_id(self, book_id: str):
        for book in self._book_list:
            if book.book_id == book_id:
                return book
        return None

    def get_book_by_name(self, name: str):
        for book in self._book_list:
            if book.name == name:
                return book

    def list_books(self):
        return [{"book_id": book.book_id, "name": book.name} for book in self._book_list]

    def list_names(self):
        return [book.name for book in self._book_list]

    def list_ids(self):
        return [book.book_id for book in self._book_list]

    def book_exists(self, book_id: str):
        return book_id in self.list_ids()
