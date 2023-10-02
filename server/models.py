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
        book_id = str(uuid4())
        md5 = BookFactory.get_book_md5(content)
        if BookFactory.check_duplicate(content):
            raise ValueError("Duplicate book")
        ix = build_index(book_id, content)
        if ix:
            book_index_path = BookFactory.get_book_index_path(book_id)
            book_ = BookMeta(book_id, name, md5, book_index_path)
            db.session.add(book_)
            db.session.commit()

            return Book(book_id, name, ix)
        else:
            raise ValueError("Failed to create book index")

    def get_book_md5(content: bytes):
        return hashlib.md5(content).hexdigest()

    def get_book_index_path(book_id: str):
        return os.path.join(INDEX_DIR, f"novel_index_{book_id}.pkl")

    def check_duplicate(content: bytes):
        md5 = BookFactory.get_book_md5(content)
        book_ = db.session.query(BookMeta).filter_by(md5=md5).first()
        if book_:
            return True
        else:
            return False


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

    def query_all_book(self):
        return db.session.query(BookMeta).all()
    def load_ix(self,name):
        ix = load_index(name)
        if ix:
            self.ix_map[name] = ix
        else:
            raise ValueError("Failed to load index")

    def get_ix(self,name):
        ix = self.ix_map.get(name)
        if not ix:
            self.load_ix(name)
            ix = self.ix_map.get(name)
        return ix


    def get_book_by_id(self, book_id: str):
        book_ = db.session.query(BookMeta).filter_by(uuid=book_id).first()
        if book_:
            ix = self.get_ix(book_id)
            return Book(book_id, book_.title, ix)
        else:
            return None

    def list_books(self):
        all_ = self.query_all_book()
        if not all_:
            return []
        return [{"book_id": book.uuid, "name": book.title} for book in all_]

    def list_names(self):
        return [book.title for book in self.list_books()]

    def list_ids(self):
        return [book.uuid for book in self.list_books()]

    def book_exists(self, book_id: str):
        return book_id in self.list_ids()
