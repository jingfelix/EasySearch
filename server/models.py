import hashlib
import os
from typing import List
from uuid import uuid4

from whoosh.index import FileIndex

from server.app import db, cache, app
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
                with db.session() as session:
                    session.add(book_)

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
        with db.session() as session:
            return session.query(BookMeta).filter_by(md5=md5).first() is not None

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


# 添加一个函数来获取书籍信息，并使用缓存
@cache.cached(timeout=3600, key_prefix='book_meta')
def get_book_meta(book_id):
    return db.session.query(BookMeta).filter_by(uuid=book_id).first()



class Books:
    def __init__(self) -> None:
        self.ix_map = {}

        with app.app_context():
            self.query_all_books = db.session.query(BookMeta).all
            for book_meta in self.query_all_books():
                self.load_ix(book_meta.uuid)

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
        book_meta = get_book_meta(book_id)
        if book_meta is None:
            # 如果缓存中没有，再从数据库中获取，并存入缓存
            book_meta = db.session.query(BookMeta).filter_by(uuid=book_id).first()
            if book_meta:
                cache.set('book_meta_' + book_id, book_meta, timeout=3600)  # 存入缓存
        if book_meta:
            ix = self.get_ix(book_id)
            title = book_meta.title
            return Book(book_id, title, ix)
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