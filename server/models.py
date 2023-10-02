import hashlib
import os
from typing import List
from uuid import uuid4

from whoosh.index import FileIndex

from server.app import db
from server.scheme.book import BookMeta
from server.utils.search import build_index, INDEX_DIR, load_index


class BookFactory:
    @staticmethod
    def create_book(name: str, content: bytes):
        try:
            book_id = str(uuid4())
            md5 = BookFactory.get_book_md5(content)

            if BookFactory.check_duplicate(md5):
                raise ValueError("Duplicate book")

            ix = build_index(book_id, content)

            if ix:
                book_index_path = BookFactory.get_book_index_path(book_id)
                book_ = BookMeta(book_id, name, md5, book_index_path)

                with db.session.begin():
                    db.session.add(book_)

                return Book(book_id, name, ix)
            else:
                raise ValueError("Failed to create book index")
        except Exception as e:
            raise ValueError(f"Failed to create book: {str(e)}")


    @staticmethod
    def get_book_md5(content: bytes):
        return hashlib.md5(content).hexdigest()

    @staticmethod
    def get_book_index_path(book_id: str):
        return os.path.join(INDEX_DIR, f"novel_index_{book_id}.pkl")

    @staticmethod
    def check_duplicate(md5: str):
        return db.session.query(BookMeta).filter_by(md5=md5).first() is not None


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
    def __init__(self) -> None:
        self.ix_map = {}

    def query_all_books(self):
        return db.session.query(BookMeta).all()

    def load_ix(self, book_id):
        try:
            ix = load_index(book_id)
            if ix:
                self.ix_map[book_id] = ix
            else:
                raise ValueError("Failed to load index")
        except Exception as e:
            raise ValueError(f"Failed to load index for book {book_id}: {str(e)}")

    def get_ix(self, book_id):
        ix = self.ix_map.get(book_id)
        if not ix:
            self.load_ix(book_id)
            ix = self.ix_map.get(book_id)
        return ix

    def get_book_by_id(self, book_id: str):
        book_ = db.session.query(BookMeta).filter_by(uuid=book_id).first()
        if book_:
            ix = self.get_ix(book_id)
            return Book(book_id, book_.title, ix)
        else:
            return None

    def list_books(self):
        all_books = self.query_all_books()
        if not all_books:
            return []
        return [{"book_id": book.uuid, "name": book.title} for book in all_books]

    def list_names(self):
        return [book.title for book in self.query_all_books()]

    def list_ids(self):
        return [book.uuid for book in self.query_all_books()]

    def book_exists(self, book_id: str):
        return book_id in self.list_ids()