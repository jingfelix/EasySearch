
from server.app import db
from server.scheme.base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean


class BookMeta(BaseModel):
    """书籍信息"""
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), nullable=False, unique=True, comment='UUID')
    title = Column(String(80), nullable=False, comment='书名')
    md5 = Column(String(32), nullable=True, comment='文件MD5')
    index_path = Column(String(80), nullable=True, comment='索引路径')

    def __init__(self, uuid, title, md5=None, index_path=None):
        self.uuid = uuid
        self.title = title
        self.md5 = md5
        self.index_path = index_path
